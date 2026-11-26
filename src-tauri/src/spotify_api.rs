//! Spotify Web API (Authorization Code + PKCE).
//!
//! No client secret is needed. The user pastes their Client ID, we open the
//! browser, Spotify redirects to a tiny local server on 127.0.0.1:8888, and
//! the tokens are kept in `<app data dir>/spotify_auth.json`.
//!
//! This file has no `tauri` imports on purpose, so it can be unit-tested alone.
//! The `#[tauri::command]` wrappers live in `commands.rs`.

use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use rand::RngCore;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};
use std::sync::OnceLock;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpListener;

/// Must be added to the Spotify dashboard *exactly* like this.
pub const REDIRECT_URI: &str = "http://127.0.0.1:8888/callback";
const LISTEN_ADDR: &str = "127.0.0.1:8888";
const SCOPES: &str = "user-read-currently-playing user-read-playback-state";
const AUTH_FILE: &str = "spotify_auth.json";
const LOGIN_TIMEOUT: Duration = Duration::from_secs(180);
const NOW_PLAYING_URL: &str =
    "https://api.spotify.com/v1/me/player/currently-playing?additional_types=episode";

// ── Types ─────────────────────────────────────────────────────────────────────

#[derive(Serialize, Deserialize, Default, Clone)]
struct Auth {
    client_id: String,
    access_token: String,
    refresh_token: String,
    expires_at: u64, // unix seconds
}

/// Same shape as the old window-title `SpotifyInfo` (+ extra optional fields),
/// so the frontend can use either one.
#[derive(Serialize, Default, Clone, Debug, PartialEq)]
pub struct NowPlaying {
    pub playing: bool,
    pub track: String,
    pub artist: String,
    pub album_art: Option<String>,
    pub progress_ms: Option<u64>,
    pub duration_ms: Option<u64>,
}

#[derive(Serialize)]
pub struct Status {
    pub connected: bool,
    pub client_id: String,
}

#[derive(Deserialize)]
struct TokenResp {
    access_token: String,
    refresh_token: Option<String>,
    expires_in: u64,
}

enum TokenError {
    /// Spotify said no (bad/revoked token). Retrying will not help.
    Rejected(String),
    /// Network problem or 5xx/429. Try again later.
    Network(String),
}

// ── Small helpers ─────────────────────────────────────────────────────────────

fn now_secs() -> u64 {
    SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_secs()).unwrap_or(0)
}

fn http() -> &'static reqwest::Client {
    static CLIENT: OnceLock<reqwest::Client> = OnceLock::new();
    CLIENT.get_or_init(|| {
        reqwest::Client::builder().timeout(Duration::from_secs(10)).build().unwrap_or_default()
    })
}

fn auth_path(dir: &Path) -> PathBuf {
    dir.join(AUTH_FILE)
}

fn load_auth(dir: &Path) -> Option<Auth> {
    let text = std::fs::read_to_string(auth_path(dir)).ok()?;
    serde_json::from_str(&text).ok()
}

fn save_auth(dir: &Path, auth: &Auth) -> Result<(), String> {
    std::fs::create_dir_all(dir).map_err(|e| e.to_string())?;
    let text = serde_json::to_string(auth).map_err(|e| e.to_string())?;
    std::fs::write(auth_path(dir), text).map_err(|e| e.to_string())
}

fn random_b64(bytes: usize) -> String {
    let mut buf = vec![0u8; bytes];
    rand::thread_rng().fill_bytes(&mut buf);
    URL_SAFE_NO_PAD.encode(buf)
}

/// PKCE: code_challenge = BASE64URL(SHA256(code_verifier))
pub fn challenge_for(verifier: &str) -> String {
    URL_SAFE_NO_PAD.encode(Sha256::digest(verifier.as_bytes()))
}

fn authorize_url(client_id: &str, challenge: &str, state: &str) -> String {
    reqwest::Url::parse_with_params(
        "https://accounts.spotify.com/authorize",
        &[
            ("client_id", client_id),
            ("response_type", "code"),
            ("redirect_uri", REDIRECT_URI),
            ("scope", SCOPES),
            ("code_challenge_method", "S256"),
            ("code_challenge", challenge),
            ("state", state),
        ],
    )
    .expect("static URL is valid")
    .to_string()
}

/// Opens the default browser. On Windows we use rundll32 instead of
/// `cmd /c start`, because cmd treats `&` in the URL as "next command".
fn open_browser(url: &str) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    let r = std::process::Command::new("rundll32").args(["url.dll,FileProtocolHandler", url]).spawn();
    #[cfg(target_os = "macos")]
    let r = std::process::Command::new("open").arg(url).spawn();
    #[cfg(all(not(target_os = "windows"), not(target_os = "macos")))]
    let r = std::process::Command::new("xdg-open").arg(url).spawn();
    r.map(|_| ()).map_err(|e| format!("Could not open the browser: {e}"))
}

// ── Login (loopback server) ───────────────────────────────────────────────────

#[derive(Debug, PartialEq)]
enum Callback {
    Code { code: String, state: String },
    Denied(String),
    Other,
}

fn parse_request_line(req: &str) -> Callback {
    let line = req.lines().next().unwrap_or("");
    let path = line.split_whitespace().nth(1).unwrap_or("");
    if !path.starts_with("/callback") {
        return Callback::Other;
    }
    let url = match reqwest::Url::parse(&format!("http://127.0.0.1{path}")) {
        Ok(u) => u,
        Err(_) => return Callback::Other,
    };
    let (mut code, mut state, mut error) = (None, None, None);
    for (k, v) in url.query_pairs() {
        match k.as_ref() {
            "code" => code = Some(v.into_owned()),
            "state" => state = Some(v.into_owned()),
            "error" => error = Some(v.into_owned()),
            _ => {}
        }
    }
    if let Some(e) = error {
        return Callback::Denied(e);
    }
    match (code, state) {
        (Some(code), Some(state)) => Callback::Code { code, state },
        _ => Callback::Other,
    }
}

async fn respond(sock: &mut tokio::net::TcpStream, status: &str, body: &str) {
    let msg = format!(
        "HTTP/1.1 {status}\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}",
        body.len()
    );
    let _ = sock.write_all(msg.as_bytes()).await;
    let _ = sock.shutdown().await;
}

const PAGE_OK: &str = "<html><body style=\"font-family:sans-serif;text-align:center;padding-top:15vh\"><h2>F.R.I.D.A.Y. connected to Spotify \u{2705}</h2><p>You can close this tab.</p></body></html>";
const PAGE_DENIED: &str = "<html><body style=\"font-family:sans-serif;text-align:center;padding-top:15vh\"><h2>Spotify login was cancelled</h2><p>You can close this tab.</p></body></html>";

/// Browsers sometimes hit /favicon.ico too, so keep accepting until the real callback arrives.
async fn wait_for_callback(listener: &TcpListener) -> Result<(String, String), String> {
    loop {
        let (mut sock, _) = listener.accept().await.map_err(|e| e.to_string())?;
        let mut buf = vec![0u8; 4096];
        let n = match tokio::time::timeout(Duration::from_secs(5), sock.read(&mut buf)).await {
            Ok(Ok(n)) => n,
            _ => continue,
        };
        let req = String::from_utf8_lossy(&buf[..n]).to_string();
        match parse_request_line(&req) {
            Callback::Code { code, state } => {
                respond(&mut sock, "200 OK", PAGE_OK).await;
                return Ok((code, state));
            }
            Callback::Denied(e) => {
                respond(&mut sock, "200 OK", PAGE_DENIED).await;
                return Err(format!("Spotify login was denied ({e})"));
            }
            Callback::Other => respond(&mut sock, "404 Not Found", "").await,
        }
    }
}

pub async fn login(dir: &Path, client_id: &str) -> Result<(), String> {
    let client_id = client_id.trim();
    if client_id.len() != 32 || !client_id.chars().all(|c| c.is_ascii_hexdigit()) {
        return Err("Client ID should be the 32-character ID from the Spotify dashboard".into());
    }

    // Bind first, so a busy port fails before we open the browser.
    let listener = TcpListener::bind(LISTEN_ADDR)
        .await
        .map_err(|e| format!("Port 8888 is busy ({e}). Close the program using it and try again."))?;

    let verifier = random_b64(64); // 86 chars (allowed: 43-128)
    let state = random_b64(16);
    open_browser(&authorize_url(client_id, &challenge_for(&verifier), &state))?;

    let (code, got_state) = tokio::time::timeout(LOGIN_TIMEOUT, wait_for_callback(&listener))
        .await
        .map_err(|_| "Login timed out after 3 minutes".to_string())??;
    if got_state != state {
        return Err("Login cancelled: state mismatch".into());
    }

    let tok = token_request(&[
        ("grant_type", "authorization_code"),
        ("code", &code),
        ("redirect_uri", REDIRECT_URI),
        ("client_id", client_id),
        ("code_verifier", &verifier),
    ])
    .await
    .map_err(|e| match e {
        TokenError::Rejected(m) | TokenError::Network(m) => format!("Token exchange failed: {m}"),
    })?;

    save_auth(
        dir,
        &Auth {
            client_id: client_id.to_string(),
            access_token: tok.access_token,
            refresh_token: tok.refresh_token.unwrap_or_default(),
            expires_at: now_secs() + tok.expires_in,
        },
    )
}

// ── Tokens ────────────────────────────────────────────────────────────────────

async fn token_request(params: &[(&str, &str)]) -> Result<TokenResp, TokenError> {
    let resp = http()
        .post("https://accounts.spotify.com/api/token")
        .form(params)
        .send()
        .await
        .map_err(|e| TokenError::Network(e.to_string()))?;
    let status = resp.status();
    if status.is_success() {
        return resp.json::<TokenResp>().await.map_err(|e| TokenError::Network(e.to_string()));
    }
    let body = resp.text().await.unwrap_or_default();
    let msg = format!("{status}: {body}");
    if status.is_client_error() && status.as_u16() != 429 {
        Err(TokenError::Rejected(msg))
    } else {
        Err(TokenError::Network(msg))
    }
}

// One refresh at a time: Spotify may rotate the refresh token, and two refreshes
// racing each other could leave us with a dead one.
static REFRESH_LOCK: tokio::sync::Mutex<()> = tokio::sync::Mutex::const_new(());

/// Returns a usable access token, refreshing it if it is (almost) expired.
/// `None` = not connected, or the connection was revoked (file is deleted then).
async fn valid_token(dir: &Path, force: bool) -> Option<String> {
    let _guard = REFRESH_LOCK.lock().await;
    let mut auth = load_auth(dir)?; // read under the lock, someone may have just refreshed
    if !force && auth.expires_at > now_secs() + 60 {
        return Some(auth.access_token);
    }
    if auth.refresh_token.is_empty() {
        return None;
    }
    match token_request(&[
        ("grant_type", "refresh_token"),
        ("refresh_token", &auth.refresh_token),
        ("client_id", &auth.client_id),
    ])
    .await
    {
        Ok(t) => {
            auth.access_token = t.access_token;
            if let Some(r) = t.refresh_token {
                auth.refresh_token = r;
            }
            auth.expires_at = now_secs() + t.expires_in;
            let _ = save_auth(dir, &auth);
            Some(auth.access_token)
        }
        Err(TokenError::Rejected(_)) => {
            let _ = std::fs::remove_file(auth_path(dir));
            None
        }
        Err(TokenError::Network(_)) => None,
    }
}

// ── Public API used by the commands ───────────────────────────────────────────

pub fn status(dir: &Path) -> Status {
    match load_auth(dir) {
        Some(a) => Status { connected: true, client_id: a.client_id },
        None => Status { connected: false, client_id: String::new() },
    }
}

pub fn logout(dir: &Path) {
    let _ = std::fs::remove_file(auth_path(dir));
}

/// `None`  = not connected / API error (caller should fall back to window-title detection).
/// `Some`  = Spotify answered (`playing: false` when nothing is playing).
pub async fn now_playing(dir: &Path) -> Option<NowPlaying> {
    let mut token = valid_token(dir, false).await?;
    for attempt in 0..2 {
        let resp = http().get(NOW_PLAYING_URL).bearer_auth(&token).send().await.ok()?;
        match resp.status().as_u16() {
            200 => {
                let v: Value = resp.json().await.ok()?;
                return Some(parse_now_playing(&v));
            }
            204 => return Some(NowPlaying::default()),
            401 if attempt == 0 => token = valid_token(dir, true).await?,
            _ => return None,
        }
    }
    None
}

fn parse_now_playing(v: &Value) -> NowPlaying {
    let playing = v["is_playing"].as_bool().unwrap_or(false);
    let item = &v["item"];
    if item.is_null() {
        // e.g. an ad is playing
        return NowPlaying { playing, ..Default::default() };
    }
    let track = item["name"].as_str().unwrap_or("").to_string();
    let artist = match item["artists"].as_array() {
        Some(arr) => arr.iter().filter_map(|a| a["name"].as_str()).collect::<Vec<_>>().join(", "),
        None => item["show"]["name"].as_str().unwrap_or("").to_string(), // podcast episode
    };
    let images = item["album"]["images"].as_array().or_else(|| item["images"].as_array());
    // Spotify lists images big -> small (640, 300, 64). The middle one fits the UI.
    let album_art = images
        .and_then(|a| a.get(1).or_else(|| a.first()))
        .and_then(|i| i["url"].as_str())
        .map(String::from);
    NowPlaying {
        playing,
        track,
        artist,
        album_art,
        progress_ms: v["progress_ms"].as_u64(),
        duration_ms: item["duration_ms"].as_u64(),
    }
}

// ── Tests ─────────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pkce_matches_rfc7636_example() {
        // Test vector from RFC 7636, Appendix B
        assert_eq!(
            challenge_for("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"),
            "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
        );
    }

    #[test]
    fn verifier_length_is_valid() {
        let v = random_b64(64);
        assert!((43..=128).contains(&v.len()));
        assert_ne!(v, random_b64(64));
    }

    #[test]
    fn authorize_url_is_encoded() {
        let u = authorize_url("abc", "chal", "st");
        assert!(u.contains("redirect_uri=http%3A%2F%2F127.0.0.1%3A8888%2Fcallback"));
        assert!(u.contains("scope=user-read-currently-playing+user-read-playback-state")
            || u.contains("scope=user-read-currently-playing%20user-read-playback-state"));
        assert!(u.contains("code_challenge_method=S256"));
    }

    #[test]
    fn callback_parsing() {
        assert_eq!(
            parse_request_line("GET /callback?code=AQB%2Fx&state=zz HTTP/1.1\r\nHost: x\r\n"),
            Callback::Code { code: "AQB/x".into(), state: "zz".into() }
        );
        assert_eq!(
            parse_request_line("GET /callback?error=access_denied&state=zz HTTP/1.1"),
            Callback::Denied("access_denied".into())
        );
        assert_eq!(parse_request_line("GET /favicon.ico HTTP/1.1"), Callback::Other);
        assert_eq!(parse_request_line("GET /callback HTTP/1.1"), Callback::Other);
        assert_eq!(parse_request_line(""), Callback::Other);
    }

    #[test]
    fn parses_track() {
        let v: Value = serde_json::from_str(
            r#"{"is_playing":true,"progress_ms":61000,"item":{"name":"Song","duration_ms":200000,
            "artists":[{"name":"A"},{"name":"B"}],
            "album":{"images":[{"url":"big"},{"url":"mid"},{"url":"small"}]}}}"#,
        )
        .unwrap();
        let n = parse_now_playing(&v);
        assert_eq!(
            n,
            NowPlaying {
                playing: true,
                track: "Song".into(),
                artist: "A, B".into(),
                album_art: Some("mid".into()),
                progress_ms: Some(61000),
                duration_ms: Some(200000),
            }
        );
    }

    #[test]
    fn parses_podcast_and_ad() {
        let ep: Value = serde_json::from_str(
            r#"{"is_playing":true,"progress_ms":5,"item":{"name":"Ep 1","duration_ms":10,
            "show":{"name":"My Show"},"images":[{"url":"only"}]}}"#,
        )
        .unwrap();
        let n = parse_now_playing(&ep);
        assert_eq!(n.artist, "My Show");
        assert_eq!(n.album_art.as_deref(), Some("only"));

        let ad: Value = serde_json::from_str(r#"{"is_playing":true,"item":null}"#).unwrap();
        let n = parse_now_playing(&ad);
        assert!(n.playing && n.track.is_empty() && n.progress_ms.is_none());
    }

    #[tokio::test]
    async fn loopback_server_skips_favicon_and_returns_code() {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let addr = listener.local_addr().unwrap();
        let client = tokio::spawn(async move {
            for req in [
                "GET /favicon.ico HTTP/1.1\r\n\r\n",
                "GET /callback?code=thecode&state=thestate HTTP/1.1\r\n\r\n",
            ] {
                let mut s = tokio::net::TcpStream::connect(addr).await.unwrap();
                s.write_all(req.as_bytes()).await.unwrap();
                let mut out = String::new();
                s.read_to_string(&mut out).await.unwrap();
                assert!(out.starts_with("HTTP/1.1 "));
            }
        });
        let got = wait_for_callback(&listener).await.unwrap();
        assert_eq!(got, ("thecode".to_string(), "thestate".to_string()));
        client.await.unwrap();
    }

    #[test]
    fn rejects_bad_client_id() {
        let rt = tokio::runtime::Builder::new_current_thread().enable_all().build().unwrap();
        let dir = std::env::temp_dir();
        let err = rt.block_on(login(&dir, "not-a-client-id")).unwrap_err();
        assert!(err.contains("32-character"));
    }
}
