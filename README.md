# ⚡ F.R.I.D.A.Y. — System Monitor

> A clean, modern desktop system monitor built with **Tauri 2 + React + TypeScript + Rust**

---

## ✨ Features

### 📊 System Monitoring
- CPU and RAM usage, GPU temperature, with big-number display
- Clickable cards — tap any metric to open a 60-second history chart
- CPU & GPU temperature readings (hardware dependent)
- Disk usage with free space indicator
- System uptime
- **Top Processes** — Top 5 processes by CPU usage, live updated

### 🌐 Network
- Real-time download / upload speed
- Sparkline graph per metric card

### 🎵 Music
- Spotify integration — detects currently playing track
  - **Windows**: window title enumeration via WinAPI
  - **macOS**: AppleScript (built-in, no setup needed)
  - **Linux**: `playerctl` (recommended) or D-Bus fallback
- Live animated visualizer bars
- Real session history with album art (when connected to the Spotify API) — tracks accumulate as you listen

#### Spotify API setup (optional, adds album art and real progress bar)

1. Create an app at https://developer.spotify.com/dashboard and tick **Web API**
2. Add this Redirect URI exactly: `http://127.0.0.1:8888/callback` (`localhost` is not accepted by Spotify)
3. While the app is in development mode, add your own account under **User Management**
4. In F.R.I.D.A.Y. open the Music panel, paste the **Client ID**, press **Connect**

No client secret is used (PKCE). Tokens are stored in the app data folder. Without connecting, the window-title detection keeps working as before.

### 🌍 Language Support
- English 🇬🇧, Turkish 🇹🇷, Spanish 🇪🇸
- Language preference saved to local storage
- All UI text, settings labels, and changelog entries change with the selected language

### 🔄 AI Translator Card
- _Hidden from the UI for now — the code is kept in `components/TranslatorCard.tsx` (DeepL rework planned)_
- Inline translation card replacing the old System Info card
- Supports 8 languages with automatic debounce (no button needed)

### 📝 Notes
- Quick notes with add / edit / delete
- Notes persist via local storage

### ⏱ Timer
- Standalone Timer card (split from Notes in v4.0)
- Count-up mode or countdown mode
- Countdown triggers a system notification + alert when finished

### 💤 Idle Mode
- After 15 minutes of inactivity, switches to a minimal overlay
- Shows a large clock + CPU / RAM / GPU temperature mini metrics
- Click anywhere to resume

### 🕐 World Clock
- Click the header clock to open the world clock panel
- Search any of 20 major cities and see their local time live

### 🖼 Image Tools
- **Edit tab** — Grayscale, Invert, Sepia, Blur, Brightness, Contrast filters with live preview
- **Upscale tab** — Browser-side Lanczos-quality upscaling at ×2 / ×3 / ×4
- **Sort tab** — Sorts files by type (Images, Videos, Music, Documents, Code, Archives, Apps) with Copy or Move mode

### ⚙️ Settings
- **Light / Dark theme** toggle
- **Language** — English, Turkish, Spanish (persisted)
- **Always on top** toggle
- **Start with system** toggle
- **Performance mode** — Eco / Normal / Turbo
- **Artist Theme** — manual override independent of Spotify playback
- **Photo Rotation** — enable / disable 60-second photo cycling
- Re-launch the feature tour at any time

### ⚡ Quick Actions
- Restart / Shutdown / Sleep with confirmation dialog (all platforms)
- Open system task manager / activity monitor

### 🪟 Window
- Custom frameless window with square corners (normal Windows window look)
- Colored minimize, maximize, close controls
- Freely resizable

---

## 🖥️ Supported Platforms

| Platform              | Status         | Notes                                                                 |
|-----------------------|----------------|-----------------------------------------------------------------------|
| Windows 10/11 (x64)  | ✅ Full         |                                                                       |
| macOS (Intel x64)    | ✅ Full         | First launch: right-click → Open to bypass Gatekeeper                |
| macOS (Apple Silicon) | ✅ Full        | Native arm64 build, M1/M2/M3/M4 supported                            |
| Linux (x64)          | ✅ Full         | AppImage or .deb; see [Linux notes](#-linux-notes) below             |

### Feature availability by platform

| Feature                     | Windows | macOS | Linux |
|-----------------------------|:-------:|:-----:|:-----:|
| CPU / RAM / Disk monitoring | ✅       | ✅     | ✅     |
| GPU temperature             | ✅       | ⚠️¹   | ⚠️¹   |
| Network stats               | ✅       | ✅     | ✅     |
| Spotify detection           | ✅       | ✅     | ✅²    |
| System actions (power)      | ✅       | ✅     | ✅³    |
| Task manager shortcut       | ✅       | ✅     | ✅⁴   |
| Folder picker dialog        | ✅       | ✅     | ✅⁵   |
| Image Tools CLI             | ✅       | ✅     | ✅     |
| F.R.I.D.A.Y. AI             | ✅       | ✅     | ✅     |

¹ GPU temp depends on driver/hardware exposing sensors via `sysinfo`  
² Linux Spotify requires `playerctl` (`sudo apt install playerctl`)  
³ Linux power actions use `systemctl`; requires appropriate sudo/polkit rules  
⁴ Linux opens the first available task manager: gnome-system-monitor, xfce4-taskmanager, ksysguard, or htop  
⁵ Linux folder picker uses `zenity` (GNOME) or `kdialog` (KDE)  

---

## 🚀 Getting Started

### Prerequisites

```bash
# 1. Install Rust
# https://rustup.rs

# 2. Verify
rustc --version
cargo --version

# 3. Node.js 18+ required
node --version
```

#### Linux extra dependencies

```bash
sudo apt-get update
sudo apt-get install -y \
  libwebkit2gtk-4.1-dev \
  libappindicator3-dev \
  librsvg2-dev \
  patchelf \
  libgtk-3-dev \
  libssl-dev \
  pkg-config \
  zenity          # folder picker
  
# Optional but recommended:
sudo apt install playerctl   # Spotify detection
```

#### macOS extra dependencies

Xcode Command Line Tools are required:
```bash
xcode-select --install
```

### Run locally

```bash
git clone https://github.com/Raldexx/FRIDAY.git
cd FRIDAY

npm install
npm run tauri dev
```

### Build

**Windows**
```bash
npm run tauri build
# Output: src-tauri/target/release/bundle/nsis/FRIDAY_4.0.0_x64-setup.exe
```

**macOS (native arch)**
```bash
npm run tauri build
# Output: src-tauri/target/release/bundle/dmg/FRIDAY_4.0.0_*.dmg
```

**macOS Universal (Intel + Apple Silicon)**
```bash
rustup target add x86_64-apple-darwin aarch64-apple-darwin
npm run tauri build -- --target universal-apple-darwin
```

**Linux**
```bash
npm run tauri build
# Output: src-tauri/target/release/bundle/appimage/FRIDAY_4.0.0_amd64.AppImage
#         src-tauri/target/release/bundle/deb/FRIDAY_4.0.0_amd64.deb
```

Or push to `main` — GitHub Actions builds automatically for **Windows, macOS (Intel + Apple Silicon), and Linux** and publishes all artifacts to Releases.

---

## 🐧 Linux Notes

- **Spotify**: Install `playerctl` for the best experience. Without it, F.R.I.D.A.Y. falls back to D-Bus directly, which may vary by distro.
- **AppImage**: `chmod +x FRIDAY_*.AppImage && ./FRIDAY_*.AppImage`
- **Power actions**: Sleep/Restart/Shutdown call `systemctl`. On desktops with polkit configured (most modern distros), this works without sudo.
- **Folder picker**: Uses `zenity` on GNOME or `kdialog` on KDE. Install one if neither is present.
- **Task manager shortcut**: Tries `gnome-system-monitor`, `xfce4-taskmanager`, `ksysguard`, then `htop` in order.

## 🍎 macOS Notes

- **Gatekeeper**: Since the app is unsigned, right-click → Open on first launch.
- **Spotify**: Detection uses AppleScript — no extra install needed. Spotify must be running.
- **Sleep**: Uses `pmset sleepnow` — works without sudo.
- **Power actions**: Restart/Shutdown use AppleScript `System Events` — may prompt for accessibility permissions on first use.

---

## 🗂️ Project Structure

```
FRIDAY/
├── src-tauri/                  ← Backend (Rust)
│   ├── src/
│   │   ├── main.rs             ← Entry point
│   │   ├── lib.rs              ← Tauri setup + system tray
│   │   └── commands.rs         ← All Tauri commands (cross-platform)
│   ├── capabilities/
│   │   └── default.json        ← Window & API permissions
│   ├── icons/                  ← App icons
│   ├── Cargo.toml
│   ├── build.rs
│   └── tauri.conf.json
│
├── src/                        ← Frontend (React + TypeScript)
│   ├── App.tsx                 ← Main UI + all modals
│   ├── store/
│   │   └── system.ts           ← Data hook + i18n (EN/TR/ES) + settings
│   ├── components/
│   │   ├── MetricCard.tsx
│   │   ├── ChartModal.tsx
│   │   ├── SpotifyPanel.tsx
│   │   ├── TranslatorCard.tsx
│   │   └── ui/
│   │       ├── Card.tsx
│   │       └── Modal.tsx
│   ├── assets/
│   │   ├── icardi.ts           ← İcardi theme photos (base64)
│   │   └── madison.ts          ← Madison Beer theme photos (base64)
│   └── index.css
│
├── .github/workflows/
│   └── build.yml               ← Auto-build on push to main (Windows + macOS + Linux)
├── package.json
└── vite.config.ts
```

---

## 📝 Notes

- **Spotify detection** works on all platforms — see platform notes above
- **GPU temperature** depends on hardware and driver support via `sysinfo`
- **Session history** in the Music panel resets when F.R.I.D.A.Y. is closed
- Build may take 5–15 minutes on first run as Rust compiles all dependencies

---

## 📦 Dependencies

### Rust
- `tauri` v2 — Desktop app framework (cross-platform)
- `sysinfo` v0.33 — Cross-platform system info
- `reqwest` — Async HTTP (weather)
- `winapi` v0.3 — Windows-only Spotify detection (conditionally compiled)
- `tokio` — Async runtime

### Frontend
- `react` v18 + TypeScript
- `@tauri-apps/api` v2 — Frontend ↔ Rust bridge
- `framer-motion` — Animations
- `lucide-react` — Icons
- `tailwindcss` v3
- `vite` v5 — Build tool

---

## 👑 Premium

Want Premium features (cloud sync, themes)?
Contact on Discord: **Raldexx**

---

## 📋 Changelog

### v4.2.0 — Bug-fix release
- 🌿 Eco mode no longer covers the screen — it only lowers the refresh rate; the overlay appears only on real idle
- 🤖 Auto Mode matches exact app names and ignores background launchers; pauses for 10 min after a manual mode change
- 📈 GPU card now shows the real GPU temperature (it used to show a fake 0%)
- 💤 Idle / timer hint texts follow the app language; idle GPU tile fixed
- 🎵 Fixed wrong artist in music history and the fake 35% progress bar
- 🎧 Optional Spotify Web API login (album art, real progress/time) and album art in recently played
- ⚙️ Top processes without `.exe`, full-width card; colored window buttons
- 🔲 Square-corner look across the whole app (radius is set in `tailwind.config.js`)
- 🔢 Version numbers in sync (package, Cargo, Tauri, UI)
- 🗑 Removed: F.R.I.D.A.Y. AI voice assistant (and `run_command` / `kill_process` / `open_url`), Spotify stats window, lyrics card, `image_upscaler.py` launcher
- 🔄 AI Translator card hidden from the UI (code kept)

### v4.1.0 — Cross-Platform
- 🐧 Full Linux support: Spotify via `playerctl`/D-Bus, power actions via `systemctl`, folder picker via `zenity`/`kdialog`
- 🍎 Full macOS support: Spotify via AppleScript, power actions via `System Events`, folder picker via `osascript`
- 🔨 GitHub Actions now builds Windows + macOS (Intel & Apple Silicon) + Linux in parallel
- 🐛 Image Tools CLI terminal launcher fixed for macOS (Terminal.app) and Linux (auto-detects terminal emulator)
- 🐛 Process list filter updated for Unix process names
- 🐛 "Start with Windows" renamed to "Start with system" (cross-platform)

### v4.0.0 — F.R.I.D.A.Y. (Previous)
- 🤖 Renamed: JARVIS → F.R.I.D.A.Y. (Female Replacement Intelligent Digital Assistant Youth)
- 🎙 Real-time voice assistant via OpenAI Realtime API (WebRTC, `gpt-4o-realtime-preview`)
- 🌀 Animated 72-bar audio ring visualizer reacting to mic volume
- 🚀 Protocol commands: start / work / gaming / night
- 🧠 Semantic memory — automatic learning from conversations
- 📝 Google Meet integration + Obsidian `.md` note template + AI meeting summary
- 🔄 AI Translator card (replaces System Info card) — 8 languages, auto-debounce
- ⏱ Timer split into its own standalone card
- 💤 Idle mode — 15 min inactivity triggers large clock + mini metrics overlay

### v3.2.0 — Last JARVIS release
- Language support: English, Turkish, Spanish
- World Clock, Image Tools, Notes + Timer, Artist themes (Madison / İcardi)
- OpenAI Realtime API first integration

### v3.0.0 — Initial release
- Full rewrite from Python/PyQt6 to Tauri + React + Rust
- Spotify integration
- GitHub Actions CI/CD
