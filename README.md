# ⚡ JARVIS v3 — System Monitor

> A clean, modern desktop system monitor built with **Tauri 2 + Svelte + Rust**

---

> **📢 Honest Note**
>
> I'm not very experienced with Rust, so I heavily relied on AI assistance (Claude) throughout
> this project — especially for the Rust backend, Windows API calls, and Tauri configuration.
> The overall architecture, design decisions, and UI were driven by me, but the low-level
> systems code was largely AI-generated and iteratively debugged. No shame in that. 🤖
>
> Original concept and v1 ([JARVIS v1](https://github.com/Raldexx/jarvis-v1)) was written in Python/PyQt6.
> This is a full rewrite for a lighter, faster, native-feeling experience via Tauri.

---

## ✨ Features

### 📊 System Monitoring
- CPU, RAM, GPU usage with big-number display
- Clickable cards — tap any metric to open a 60-second history chart
- CPU & GPU temperature readings (hardware dependent)
- Disk usage with free space indicator
- System uptime

### 🌐 Network
- Real-time download / upload speed
- Sparkline graph per metric card
- Total daily data usage

### 🎵 Music
- Spotify integration — detects currently playing track via Windows window title
- Live animated visualizer
- Real session history — tracks accumulate as you listen
- Apple Music support coming soon

### 📋 Process Monitor
- Top 4 processes by CPU usage, live updated

### ⚙️ Settings
- **Light / Dark theme** toggle
- **Always on top** toggle — pin JARVIS above other windows or let it sit behind
- CPU & RAM alert thresholds

### ⚡ Quick Actions
- Restart / Shutdown / Sleep
- Open Task Manager

### 🪟 Window
- Custom frameless window with minimize, maximize, close controls
- Freely resizable
- Drag anywhere on the panel to move

---

## 🖥️ Supported Platforms

| Platform | Status |
|----------|--------|
| Windows 10/11 | ✅ Full support |
| macOS | ⚠️ Limited (Spotify & some system features unavailable) |
| Linux | ⚠️ Limited |

---

## 🚀 Getting Started

### Prerequisites

```bash
# 1. Install Rust
# https://rustup.rs → download rustup-init.exe → select option 1

# 2. Verify
rustc --version
cargo --version

# 3. Node.js 18+ required
node --version
```

### Run locally

```bash
git clone https://github.com/Raldexx/Jarvis-v3.git
cd Jarvis-v3

npm install
npm run tauri dev
```

### Build .exe

```bash
npm run tauri build
# Output: src-tauri/target/release/bundle/nsis/JARVIS_3.0.0_x64-setup.exe
```

Or just push to `main` — GitHub Actions builds it automatically and publishes to Releases.

---

## 🗂️ Project Structure

```
Jarvis-v3/
├── src-tauri/              ← Backend (Rust)
│   ├── src/
│   │   ├── main.rs         ← Entry point
│   │   ├── lib.rs          ← Tauri setup + system tray
│   │   └── commands.rs     ← All Tauri commands
│   ├── capabilities/
│   │   └── default.json    ← Window & API permissions
│   ├── icons/              ← App icons
│   ├── Cargo.toml
│   ├── build.rs
│   └── tauri.conf.json
│
├── src/                    ← Frontend (Svelte)
│   ├── routes/
│   │   ├── +layout.js      ← SSR disabled (required for Tauri)
│   │   ├── +layout.svelte
│   │   └── +page.svelte    ← Entire UI (single file, self-contained)
│   └── app.html
│
├── .github/workflows/
│   └── build.yml           ← Auto-build on push to main
├── package.json
├── svelte.config.js
└── vite.config.js
```

---

## 🔧 Rust ↔ Python Mapping

| Original Python | Rust / Tauri v3 |
|----------------|-----------------|
| `psutil.cpu_percent()` | `sysinfo::System::global_cpu_usage()` |
| `psutil.virtual_memory()` | `sysinfo::System::used_memory()` |
| `psutil.disk_usage('/')` | `sysinfo::Disks` |
| `psutil.net_io_counters()` | `sysinfo::Networks` |
| `psutil.sensors_temperatures()` | `sysinfo::Components` |
| `win32gui.EnumWindows()` | `winapi::EnumWindows` (unsafe Rust) |
| `requests.get(wttr.in)` | `reqwest::get()` |
| `pyttsx3.speak()` | Removed (Web Speech API available if needed) |
| `QSystemTrayIcon` | `tauri::tray::TrayIconBuilder` |
| `PyQt6` UI | Svelte + CSS |

---

## 🎨 Themes

Switch between **Light** and **Dark** from the Settings panel inside the app.

---

## 📝 Notes

- **Spotify detection** works on Windows only, using window title enumeration
- **GPU temperature** depends on hardware and driver support via `sysinfo`
- **Session history** in the Music panel resets when JARVIS is closed
- **Daily stats** are not persisted between sessions yet (coming in future update)
- Build may take 5–15 minutes on first run as Rust compiles all dependencies

---

## 📦 Dependencies

### Rust
- `tauri` v2 — Desktop app framework
- `sysinfo` v0.33 — Cross-platform system info
- `reqwest` — Async HTTP (weather)
- `winapi` v0.3 — Windows-specific Spotify detection
- `tokio` — Async runtime

### Frontend
- `svelte` v4 + `@sveltejs/kit` — UI framework
- `@tauri-apps/api` v2 — Frontend ↔ Rust bridge
- `vite` v5 — Build tool
