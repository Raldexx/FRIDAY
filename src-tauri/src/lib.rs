mod commands;
mod spotify_api;

use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    Manager, Runtime,
};

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let show = MenuItem::with_id(app, "show", "Show / Hide", true, None::<&str>)?;
            let quit = MenuItem::with_id(app, "quit", "Quit F.R.I.D.A.Y.", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&show, &quit])?;

            // The tray icon is built here only. tauri.conf.json used to define one as well,
            // which gave two icons (one of them blank and without any menu).
            let mut tray = TrayIconBuilder::with_id("main")
                .tooltip("F.R.I.D.A.Y.")
                .menu(&menu)
                .show_menu_on_left_click(false) // left click = show/hide, right click = menu
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "show" => toggle_window(app),
                    "quit" => app.exit(0),
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event {
                        toggle_window(tray.app_handle());
                    }
                });
            if let Some(icon) = app.default_window_icon() {
                tray = tray.icon(icon.clone());
            }
            #[cfg(target_os = "macos")]
            {
                tray = tray.icon_as_template(true);
            }
            tray.build(app)?;

            #[cfg(target_os = "windows")]
            if let Some(win) = app.get_webview_window("main") {
                square_window_corners(&win);
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::get_system_stats,
            commands::get_network_stats,
            commands::get_processes,
            commands::get_process_icon,
            commands::get_weather,
            commands::get_spotify,
            commands::get_spotify_api,
            commands::spotify_login,
            commands::spotify_logout,
            commands::spotify_status,
            commands::get_system_info,
            commands::system_action,
            commands::open_folder_picker,
            commands::sort_files,
            commands::get_active_window,
            commands::get_running_apps,
            commands::detect_auto_performance_mode,
        ])
        .run(tauri::generate_context!())
        .expect("error running F.R.I.D.A.Y.");
}

/// Windows 11 rounds the corners of undecorated windows on its own. The app wants a square
/// window, so tell DWM not to (DWMWA_WINDOW_CORNER_PREFERENCE = 33, DWMWCP_DONOTROUND = 1).
/// Windows 10 does not know this setting and simply ignores the call.
#[cfg(target_os = "windows")]
fn square_window_corners<R: Runtime>(win: &tauri::WebviewWindow<R>) {
    use winapi::um::dwmapi::DwmSetWindowAttribute;
    const DWMWA_WINDOW_CORNER_PREFERENCE: u32 = 33;
    const DWMWCP_DONOTROUND: u32 = 1;
    if let Ok(hwnd) = win.hwnd() {
        let preference: u32 = DWMWCP_DONOTROUND;
        unsafe {
            DwmSetWindowAttribute(
                hwnd.0 as _,
                DWMWA_WINDOW_CORNER_PREFERENCE,
                &preference as *const u32 as *const _,
                std::mem::size_of::<u32>() as u32,
            );
        }
    }
}

fn toggle_window<R: Runtime>(app: &tauri::AppHandle<R>) {
    if let Some(win) = app.get_webview_window("main") {
        let visible   = win.is_visible().unwrap_or(false);
        let minimized = win.is_minimized().unwrap_or(false);
        // A minimized window still counts as "visible": bring it back instead of hiding it
        if visible && !minimized { let _ = win.hide(); }
        else { let _ = win.show(); let _ = win.unminimize(); let _ = win.set_focus(); }
    }
}
