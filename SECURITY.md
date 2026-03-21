# Security Policy

## Supported Versions

Only the latest release of JARVIS is actively maintained and receives security updates.

| Version | Supported |
|---------|-----------|
| 3.x (latest) | ✅ |
| 2.x | ❌ |
| 1.x | ❌ |

---

## Scope

JARVIS is a **local desktop application** — it does not run a server, expose network ports, or transmit personal data to any remote service. The attack surface is intentionally minimal.

### In scope

- Privilege escalation via system action commands (`shutdown`, `restart`, `sleep`)
- Unsafe use of Windows API (`winapi` / `EnumWindows`) allowing process injection or data leakage
- Tauri IPC command exposure — unauthorized frontend → backend command invocation
- Dependency vulnerabilities in Rust crates (`sysinfo`, `reqwest`, `winapi`, `tauri`) or npm packages
- Malicious input via Tauri `invoke()` calls leading to unintended system behavior

### Out of scope

- Vulnerabilities in WebView2, Chromium, or the underlying OS
- Physical access attacks
- Issues in officially archived versions (v1, v2)
- Social engineering

---

## Data & Privacy

JARVIS collects **no personal data** and makes **no telemetry calls**.

| What | Where it goes |
|------|--------------|
| CPU / RAM / GPU / Disk stats | Local display only — never leaves the device |
| Network speed | Local display only |
| Spotify track info | Read from Windows window title, displayed locally, never transmitted |
| Weather | Fetched from [wttr.in](https://wttr.in) — your IP is sent to wttr.in as part of the HTTP request. No other data is sent. |
| App config / daily stats | Stored in `localStorage` inside the WebView2 sandbox — local only |

---

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Report security issues privately via one of these methods:

1. **GitHub Private Vulnerability Reporting** *(preferred)*
   Go to: `Security` → `Advisories` → `Report a vulnerability`

2. **Email**
   If GitHub's private reporting is unavailable, contact the maintainer directly through the GitHub profile.

### What to include

- A clear description of the vulnerability
- Steps to reproduce
- Potential impact (what an attacker could achieve)
- Your suggested fix, if any

### Response timeline

| Stage | Target time |
|-------|-------------|
| Acknowledgement | Within 72 hours |
| Initial assessment | Within 7 days |
| Fix or mitigation | Within 30 days for critical, 90 days for others |

---

## Known Limitations

### Unsafe Rust code

The Spotify detection feature uses `unsafe` Rust to call Windows API functions (`EnumWindows`, `GetWindowTextW`, `OpenProcess`). This code:

- Runs with the **same privileges as the user** who launched JARVIS (no elevation)
- Only reads window titles — it does not inject code or modify other processes
- Is isolated to `src-tauri/src/commands.rs` in the `find_spotify_title()` function

This is a known architectural limitation. A future version may replace this with a safer alternative (e.g. Windows Accessibility API or a dedicated COM interface).

### System actions

The `system_action` Tauri command can trigger `shutdown`, `restart`, and `sleep`. These commands:

- Are only invokable from the JARVIS frontend (same machine, same user)
- Require explicit user confirmation in the UI before execution
- Run with user-level privileges — no UAC elevation

### No code signing

Released `.exe` and `.msi` files are currently **not code-signed**. Windows Defender SmartScreen may warn on first launch. This is a known limitation of the current CI/CD setup and will be addressed in a future release.

---

## Dependencies

Security-relevant dependencies are listed below. Please report vulnerabilities in these upstream — we will update our dependency versions promptly.

| Package | Type | Purpose |
|---------|------|---------|
| `tauri` v2 | Rust | Desktop framework & IPC |
| `sysinfo` v0.33 | Rust | System metrics |
| `reqwest` v0.12 | Rust | HTTP (weather fetch) |
| `winapi` v0.3 | Rust | Windows Spotify detection |
| `@tauri-apps/api` v2 | npm | Frontend ↔ Rust bridge |

To audit current dependency versions, run:
```bash
cargo audit        # Rust
npm audit          # Node
```
