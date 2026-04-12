# ⚡ F.R.I.D.A.Y. — System Monitor

> A clean, modern desktop system monitor built with **Tauri 2 + React + TypeScript + Rust**

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
- **Top Processes** — Top 4 processes by CPU usage, live updated

### 🌐 Network
- Real-time download / upload speed
- Sparkline graph per metric card

### 🎵 Music
- Spotify integration — detects currently playing track via Windows window title
- Live animated visualizer
- Real session history — tracks accumulate as you listen
- Lyrics panel (Premium — requires Spotify API token)
- Apple Music support coming soon

### 🌍 Language Support
- English 🇬🇧, Turkish 🇹🇷, Spanish 🇪🇸
- Language preference is saved to local storage

### 📝 Notes & Timer
- Quick notes with add / edit / delete
- Integrated timer: count-up mode or countdown mode
- Countdown sends a Windows notification + alert when finished

### 🕐 World Clock
- Click the header clock to open the world clock panel
- Search any city and see its local time live

### 🖼 Image Tools
- Built-in image editor: Grayscale, Invert, Sepia, Blur, Brightness, Contrast
- Download processed image with one click

### 👑 Premium
- Premium section with Discord contact for access (`Raldexx`)
- Future: Spotify lyrics, cloud sync, custom themes

### 🎨 Artist Themes
- **Madison Beer** — plays any Madison Beer song → purple night theme activates
- **Simge / İcardi** — plays *Aşkın Olayım* → blue Icardi theme activates
- Theme reverts automatically when song changes

### ⚙️ Settings
- **Light / Dark theme** toggle
- **Language** — English, Turkish, Spanish (persisted)
- **Always on top** toggle
- **Start with Windows** toggle
- **Performance mode** — eco / normal / turbo (lowercase labels)
- Re-launch the feature tour at any time

### 🗺 Feature Tour
- On first launch, a step-by-step guided tour of all features
- Can be re-triggered from Settings

### ⚡ Quick Actions
- Restart / Shutdown / Sleep
- *(Task Manager button removed — was non-functional)*

### 🪟 Window
- Custom frameless window with soft rounded corners
- Minimize, maximize, close controls
- Smaller default size (400×780) to avoid taskbar overlap
- Freely resizable

---

## 🖥️ Supported Platforms

| Platform     | Status                                              |
|--------------|-----------------------------------------------------|
| Windows 10/11| ✅ Full support                                      |
| macOS        | ⚠️ Limited (Spotify & some system features unavailable) |
| Linux        | ⚠️ Limited                                          |

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
# Output: src-tauri/target/release/bundle/nsis/JARVIS_3.2.0_x64-setup.exe
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
├── src/                    ← Frontend (React + TypeScript)
│   ├── App.tsx             ← Main UI + all modals
│   ├── store/
│   │   └── system.ts       ← Data hook + i18n + settings
│   ├── components/
│   │   ├── MetricCard.tsx
│   │   ├── ChartModal.tsx
│   │   ├── SpotifyPanel.tsx
│   │   └── ui/
│   │       ├── Card.tsx
│   │       └── Modal.tsx
│   └── index.css
│
├── .github/workflows/
│   └── build.yml           ← Auto-build on push to main
├── package.json
└── vite.config.ts
```

---

## 📝 Notes

- **Spotify detection** works on Windows only, using window title enumeration
- **GPU temperature** depends on hardware and driver support via `sysinfo`
- **Session history** in the Music panel resets when JARVIS is closed
- **Start with Windows** setting is saved but requires Tauri autostart plugin to be wired in `lib.rs` (planned)
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
- `react` v18 + TypeScript
- `@tauri-apps/api` v2 — Frontend ↔ Rust bridge
- `framer-motion` — Animations
- `lucide-react` — Icons
- `tailwindcss` v3
- `vite` v5 — Build tool

---

## 👑 Premium

Want Premium features (lyrics, cloud sync, themes)?
Contact on Discord: **Raldexx**
