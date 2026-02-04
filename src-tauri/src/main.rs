// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Child, Command as StdCommand};
use std::sync::{Arc, Mutex};
use tauri::{Manager, State};

// 应用状态
struct AppState {
    backend_child: Arc<Mutex<Option<Child>>>,
}

impl AppState {
    fn new() -> Self {
        Self {
            backend_child: Arc::new(Mutex::new(None)),
        }
    }
}

// 启动后端进程
fn start_backend(app_handle: &tauri::AppHandle) -> Result<Child, String> {
    let data_dir = app_handle
        .path_resolver()
        .app_data_dir()
        .ok_or("Failed to get app data dir")?;
    
    // 确保数据目录存在
    std::fs::create_dir_all(&data_dir)
        .map_err(|e| format!("Failed to create data dir: {}", e))?;
    
    let data_dir_str = data_dir
        .to_str()
        .ok_or("Failed to convert data dir to string")?;
    
    println!("📂 Data directory: {}", data_dir_str);
    
    // 获取后端可执行文件路径
    let backend_path = app_handle
        .path_resolver()
        .resolve_resource("binaries/newsgap-backend")
        .ok_or("Failed to resolve backend binary path")?;
    
    println!("🚀 Starting backend: {:?}", backend_path);
    
    // 启动后端进程
    let child = StdCommand::new(backend_path)
        .spawn()
        .map_err(|e| format!("Failed to spawn backend: {}", e))?;
    
    println!("✅ Backend process started with PID: {}", child.id());
    
    Ok(child)
}

fn main() {
    let app_state = AppState::new();
    
    tauri::Builder::default()
        .manage(app_state)
        .setup(|app| {
            let app_handle = app.handle();
            
            // 启动后端
            match start_backend(&app_handle) {
                Ok(child) => {
                    // 保存子进程句柄
                    let state: State<AppState> = app_handle.state();
                    *state.backend_child.lock().unwrap() = Some(child);
                    
                    println!("✅ Backend started successfully");
                }
                Err(e) => {
                    eprintln!("❌ Failed to start backend: {}", e);
                    // 在开发环境中继续运行,允许连接外部后端
                    #[cfg(debug_assertions)]
                    {
                        eprintln!("⚠️  Running in dev mode, you can start backend manually");
                    }
                    #[cfg(not(debug_assertions))]
                    {
                        panic!("Cannot start without backend");
                    }
                }
            }
            
            Ok(())
        })
        .on_window_event(|event| {
            if let tauri::WindowEvent::Destroyed = event.event() {
                // 清理后端进程
                if let Some(state) = event.window().try_state::<AppState>() {
                    if let Some(mut child) = state.backend_child.lock().unwrap().take() {
                        println!("🛑 Stopping backend process...");
                        let _ = child.kill();
                        let _ = child.wait();
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
