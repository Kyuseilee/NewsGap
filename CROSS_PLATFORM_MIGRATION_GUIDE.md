# NewsGap 全平台改造方案

> **项目目标**: 将 NewsGap 从 Web 应用改造为支持 Mac/Windows/iOS/Android 的全平台应用

**生成日期**: 2026-02-04  
**当前版本**: v0.1 (Web Only)  
**目标版本**: v1.0 (All Platforms)

---

## 📊 项目现状分析

### 当前技术栈

| 层级 | 技术 | 代码量 | 平台支持 |
|------|------|--------|---------|
| **后端** | Python FastAPI | ~6,500 行 | 全平台通用 ✅ |
| **前端** | React 18 + TypeScript | ~4,500 行 | Web Only |
| **数据库** | SQLite (aiosqlite) | - | 全平台通用 ✅ |
| **构建** | Vite + npm | - | Web Only |

### 平台支持现状

| 平台 | 当前状态 | 改造难度 | 代码复用率 |
|------|---------|---------|-----------|
| Web | ✅ 完全支持 | - | 100% |
| macOS | ❌ 未支持 | ⭐⭐ 低 | 85%+ |
| Windows | ❌ 未支持 | ⭐⭐ 低 | 85%+ |
| Linux | ❌ 未支持 | ⭐⭐ 低 | 85%+ |
| iOS | ❌ 未支持 | ⭐⭐⭐⭐ 中高 | 60%+ |
| Android | ❌ 未支持 | ⭐⭐⭐⭐ 中高 | 60%+ |

### 核心功能模块

```
NewsGap 功能架构
├── 新闻爬取 (RSS + Web)          ✅ 平台无关
├── AI 分析 (4 种 LLM)            ✅ 平台无关
├── 数据存储 (SQLite)             ✅ 平台无关
├── 信息源管理                    ✅ 平台无关
├── 自定义分类                    ✅ 平台无关
├── 文章搜索和归档                ✅ 平台无关
└── Web UI (React)                ⚠️ 需要平台适配
```

**关键发现**:
- ✅ 后端代码 100% 可复用
- ✅ 前端 React 组件 85%+ 可复用
- ✅ 业务逻辑完全平台无关
- ⚠️ 需要平台特定的外壳和集成

---

## 🎯 推荐方案: 混合架构

### 方案对比

| 方案 | 桌面端 | 移动端 | 包体积 | 性能 | 开发成本 | 推荐度 |
|------|--------|--------|--------|------|---------|--------|
| **方案 A: Tauri + React Native** | Tauri | RN | 小 | 高 | 中 | ⭐⭐⭐⭐⭐ |
| 方案 B: Electron + React Native | Electron | RN | 大 | 中 | 低 | ⭐⭐⭐⭐ |
| 方案 C: Flutter 全栈 | Flutter | Flutter | 中 | 高 | 高 | ⭐⭐⭐ |

### 为什么选择 Tauri + React Native?

**Tauri 优势** (桌面端):
- ✅ 包体积小 (20-50MB vs Electron 150MB+)
- ✅ 内存占用低 (使用系统 WebView)
- ✅ Rust 后端,安全高效
- ✅ 完美复用现有 React 代码
- ✅ 原生系统集成能力强

**React Native 优势** (移动端):
- ✅ 一次编写,双平台运行
- ✅ 复用 React 技能栈
- ✅ 大量成熟第三方库
- ✅ 热更新支持
- ✅ 复用 50-60% Web 代码

---

## 🚀 实施路线图

### Phase 1: 桌面端 (Mac/Windows/Linux) - Tauri

**时间估算**: 3-4 周  
**优先级**: 🔥 最高  
**代码复用率**: 85%+

#### 1.1 环境准备 (1-2 天)

```bash
# 安装 Rust 和 Tauri CLI
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
cargo install tauri-cli

# 在项目根目录初始化 Tauri
cd /Users/roson/workspace/NewsGap
cargo tauri init
```

**配置问答**:
- App name: `NewsGap`
- Window title: `NewsGap - 行业情报分析`
- Web assets: `../frontend/dist`
- Dev server: `http://localhost:5173`
- Dev command: `cd frontend && npm run dev`
- Build command: `cd frontend && npm run build`

#### 1.2 项目结构调整 (1 天)

```
NewsGap/
├── backend/                    # 保持不变
├── frontend/                   # 保持不变
├── src-tauri/                  # 新增 Tauri Rust 项目
│   ├── Cargo.toml             # Rust 依赖配置
│   ├── tauri.conf.json        # Tauri 应用配置
│   ├── build.rs               # 构建脚本
│   ├── icons/                 # 应用图标 (多尺寸)
│   └── src/
│       ├── main.rs            # Rust 入口
│       ├── commands.rs        # Tauri 命令 (前端调用后端)
│       └── menu.rs            # 应用菜单
├── scripts/                    # 新增构建脚本
│   ├── build-all-platforms.sh
│   └── package-installers.sh
└── installers/                 # 安装包输出目录
```

#### 1.3 后端集成方案 (2-3 天)

**选项 A: Sidecar 模式 (推荐)**

将 Python FastAPI 打包为独立可执行文件,由 Tauri 管理生命周期:

```toml
# tauri.conf.json
{
  "tauri": {
    "bundle": {
      "externalBin": ["binaries/newsgap-backend"]
    }
  }
}
```

**优势**:
- ✅ 完全复用现有后端代码
- ✅ 前后端解耦,独立升级
- ✅ 后端进程由 Tauri 自动管理

**实施步骤**:
```bash
# 1. 使用 PyInstaller 打包后端
cd backend
pip install pyinstaller
pyinstaller --onefile --name newsgap-backend main.py

# 2. 复制到 Tauri binaries 目录
mkdir -p ../src-tauri/binaries
cp dist/newsgap-backend ../src-tauri/binaries/

# 3. Rust 代码启动后端
// src-tauri/src/main.rs
use tauri::api::process::{Command, CommandEvent};

fn start_backend() {
    tauri::async_runtime::spawn(async move {
        let (mut rx, _child) = Command::new_sidecar("newsgap-backend")
            .expect("failed to create backend command")
            .spawn()
            .expect("Failed to spawn backend");

        while let Some(event) = rx.recv().await {
            // 处理后端输出
        }
    });
}
```

**选项 B: 嵌入式 Python (备选)**

使用 PyO3 将 Python 嵌入 Rust:
- ⚠️ 复杂度高
- ⚠️ 打包困难
- ✅ 单一可执行文件

#### 1.4 前端适配 (2-3 天)

**1.4.1 添加 Tauri API 调用**

```typescript
// frontend/src/services/tauri.ts
import { invoke } from '@tauri-apps/api/tauri';
import { appWindow } from '@tauri-apps/api/window';
import { sendNotification } from '@tauri-apps/api/notification';

export const tauriAPI = {
  // 检查是否在 Tauri 环境
  isTauri: () => '__TAURI__' in window,
  
  // 窗口控制
  minimize: () => appWindow.minimize(),
  maximize: () => appWindow.toggleMaximize(),
  close: () => appWindow.close(),
  
  // 系统通知
  notify: (title: string, body: string) => {
    sendNotification({ title, body });
  },
  
  // 文件操作
  saveFile: async (content: string) => {
    return invoke('save_file', { content });
  },
};
```

**1.4.2 更新 Vite 配置**

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  
  // Tauri 开发环境不使用 clearScreen
  clearScreen: false,
  
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  
  // 生产构建优化
  build: {
    target: 'esnext',
    minify: 'esbuild',
    sourcemap: false,
  },
});
```

**1.4.3 添加桌面端特性**

```typescript
// frontend/src/components/TitleBar.tsx (自定义标题栏)
import { tauriAPI } from '../services/tauri';

export function TitleBar() {
  if (!tauriAPI.isTauri()) return null;
  
  return (
    <div className="titlebar" data-tauri-drag-region>
      <span>NewsGap</span>
      <div className="titlebar-buttons">
        <button onClick={tauriAPI.minimize}>─</button>
        <button onClick={tauriAPI.maximize}>□</button>
        <button onClick={tauriAPI.close}>✕</button>
      </div>
    </div>
  );
}
```

#### 1.5 Tauri 配置详解 (1 天)

```json
// src-tauri/tauri.conf.json
{
  "package": {
    "productName": "NewsGap",
    "version": "1.0.0"
  },
  "build": {
    "distDir": "../frontend/dist",
    "devPath": "http://localhost:5173",
    "beforeDevCommand": "cd frontend && npm run dev",
    "beforeBuildCommand": "cd frontend && npm run build"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "shell": { "open": true },
      "dialog": { "all": true },
      "fs": {
        "scope": ["$APPDATA/*", "$RESOURCE/*"]
      },
      "notification": { "all": true },
      "window": {
        "all": true,
        "close": true,
        "hide": true,
        "show": true,
        "minimize": true,
        "maximize": true
      }
    },
    "windows": [
      {
        "title": "NewsGap",
        "width": 1400,
        "height": 900,
        "minWidth": 1000,
        "minHeight": 600,
        "resizable": true,
        "fullscreen": false,
        "decorations": true,
        "transparent": false
      }
    ],
    "security": {
      "csp": "default-src 'self'; connect-src 'self' http://localhost:8000"
    },
    "systemTray": {
      "iconPath": "icons/icon.png",
      "menuOnLeftClick": false
    }
  }
}
```

#### 1.6 跨平台构建 (2-3 天)

**macOS 构建**:
```bash
cargo tauri build --target aarch64-apple-darwin  # Apple Silicon
cargo tauri build --target x86_64-apple-darwin   # Intel Mac
```

**Windows 构建**:
```bash
cargo tauri build --target x86_64-pc-windows-msvc
```

**Linux 构建**:
```bash
cargo tauri build --target x86_64-unknown-linux-gnu
```

**产物位置**:
```
src-tauri/target/release/bundle/
├── dmg/          # macOS 安装包
├── msi/          # Windows 安装包
├── deb/          # Debian/Ubuntu 包
├── appimage/     # Linux 通用包
└── rpm/          # RedHat/Fedora 包
```

#### 1.7 桌面端特性增强 (2-3 天)

**系统托盘**:
```rust
// src-tauri/src/main.rs
use tauri::{CustomMenuItem, SystemTray, SystemTrayMenu, SystemTrayEvent};

fn create_system_tray() -> SystemTray {
    let tray_menu = SystemTrayMenu::new()
        .add_item(CustomMenuItem::new("show", "显示窗口"))
        .add_item(CustomMenuItem::new("quit", "退出"));
    
    SystemTray::new().with_menu(tray_menu)
}

fn handle_system_tray_event(app: &tauri::AppHandle, event: SystemTrayEvent) {
    match event {
        SystemTrayEvent::LeftClick { .. } => {
            let window = app.get_window("main").unwrap();
            window.show().unwrap();
            window.set_focus().unwrap();
        }
        SystemTrayEvent::MenuItemClick { id, .. } => {
            match id.as_str() {
                "quit" => std::process::exit(0),
                "show" => {
                    let window = app.get_window("main").unwrap();
                    window.show().unwrap();
                }
                _ => {}
            }
        }
        _ => {}
    }
}
```

**全局快捷键**:
```rust
use tauri::GlobalShortcutManager;

app.global_shortcut_manager()
    .register("CmdOrCtrl+Shift+N", move || {
        // 唤醒窗口
    })
    .unwrap();
```

**自动更新**:
```toml
# Cargo.toml
[dependencies]
tauri = { version = "1.5", features = ["updater"] }
```

---

### Phase 2: 移动端 (iOS/Android) - React Native

**时间估算**: 6-8 周  
**优先级**: 🔥 高  
**代码复用率**: 60%+

#### 2.1 环境准备 (2-3 天)

```bash
# 创建 React Native 项目
npx react-native init NewsGapMobile --template react-native-template-typescript

# 或使用 Expo (更简单,但限制更多)
npx create-expo-app NewsGapMobile --template
```

**安装依赖**:
```bash
cd NewsGapMobile
npm install @react-navigation/native @react-navigation/stack
npm install react-native-screens react-native-safe-area-context
npm install axios zustand @tanstack/react-query
npm install date-fns react-native-markdown-display
```

#### 2.2 项目结构

```
NewsGapMobile/
├── android/                    # Android 原生代码
├── ios/                        # iOS 原生代码
├── src/
│   ├── App.tsx                # 入口
│   ├── navigation/            # 导航配置
│   ├── screens/               # 页面 (复用 Web 页面逻辑)
│   │   ├── HomeScreen.tsx
│   │   ├── ArticlesScreen.tsx
│   │   ├── AnalysisScreen.tsx
│   │   └── SettingsScreen.tsx
│   ├── components/            # 组件 (复用 Web 组件)
│   ├── services/              # API 服务 (100% 复用)
│   │   └── api.ts
│   ├── stores/                # 状态管理 (100% 复用)
│   ├── types/                 # 类型定义 (100% 复用)
│   └── utils/                 # 工具函数 (100% 复用)
├── package.json
└── metro.config.js
```

#### 2.3 代码复用策略

**方案: Monorepo 架构**

```
NewsGap/
├── packages/                   # 共享代码包
│   ├── shared/                # 平台无关代码
│   │   ├── services/          # API 客户端 (100% 复用)
│   │   ├── stores/            # Zustand 状态 (100% 复用)
│   │   ├── types/             # TypeScript 类型 (100% 复用)
│   │   ├── utils/             # 工具函数 (100% 复用)
│   │   └── hooks/             # 自定义 Hooks (90% 复用)
│   └── ui-primitives/         # UI 原语
│       ├── Button.tsx
│       ├── Input.tsx
│       └── Card.tsx
├── apps/
│   ├── web/                   # Web 应用 (原 frontend)
│   ├── desktop/               # 桌面应用 (Tauri)
│   └── mobile/                # 移动应用 (React Native)
└── package.json               # Workspace 配置
```

**配置 Yarn Workspaces**:
```json
// 根目录 package.json
{
  "private": true,
  "workspaces": [
    "packages/*",
    "apps/*"
  ]
}
```

#### 2.4 移动端特定适配

**导航**:
```typescript
// src/navigation/AppNavigator.tsx
import { createStackNavigator } from '@react-navigation/stack';
import { NavigationContainer } from '@react-navigation/native';

const Stack = createStackNavigator();

export function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Articles" component={ArticlesScreen} />
        <Stack.Screen name="Analysis" component={AnalysisScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

**API 地址配置**:
```typescript
// packages/shared/services/config.ts
import { Platform } from 'react-native';

export const API_BASE_URL = Platform.select({
  ios: 'http://localhost:8000',      // iOS 模拟器
  android: 'http://10.0.2.2:8000',   // Android 模拟器
  default: 'http://localhost:8000',
});

// 生产环境使用云服务
if (process.env.NODE_ENV === 'production') {
  API_BASE_URL = 'https://api.newsgap.app';
}
```

**本地存储**:
```typescript
// 替换 localStorage
import AsyncStorage from '@react-native-async-storage/async-storage';

export const storage = {
  getItem: (key: string) => AsyncStorage.getItem(key),
  setItem: (key: string, value: string) => AsyncStorage.setItem(key, value),
  removeItem: (key: string) => AsyncStorage.removeItem(key),
};
```

#### 2.5 移动端增强功能

**离线支持**:
```typescript
import NetInfo from '@react-native-community/netinfo';
import { useQuery } from '@tanstack/react-query';

function useArticles() {
  const netInfo = NetInfo.useNetInfo();
  
  return useQuery({
    queryKey: ['articles'],
    queryFn: fetchArticles,
    enabled: netInfo.isConnected,
    staleTime: 5 * 60 * 1000,  // 5 分钟
  });
}
```

**推送通知**:
```typescript
import messaging from '@react-native-firebase/messaging';

async function requestPermission() {
  const authStatus = await messaging().requestPermission();
  const enabled =
    authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
    authStatus === messaging.AuthorizationStatus.PROVISIONAL;

  if (enabled) {
    console.log('Authorization status:', authStatus);
  }
}
```

**生物识别**:
```typescript
import ReactNativeBiometrics from 'react-native-biometrics';

const rnBiometrics = new ReactNativeBiometrics();

async function authenticateWithBiometrics() {
  const { success } = await rnBiometrics.simplePrompt({
    promptMessage: '验证以访问 NewsGap'
  });
  
  return success;
}
```

#### 2.6 iOS 构建和发布

**配置 Xcode**:
```bash
cd ios
pod install
open NewsGapMobile.xcworkspace
```

**关键配置**:
- Bundle Identifier: `com.newsgap.mobile`
- Team: 选择开发者账号
- Signing: Automatic
- Deployment Target: iOS 13.0+

**构建**:
```bash
# 开发版本
npx react-native run-ios

# 生产版本
npx react-native run-ios --configuration Release
```

**发布到 App Store**:
1. 在 App Store Connect 创建应用
2. 上传截图和描述
3. Archive 并上传到 App Store Connect
4. 提交审核

#### 2.7 Android 构建和发布

**配置 Android Studio**:
```bash
cd android
./gradlew assembleDebug
```

**签名配置**:
```bash
# 生成密钥
keytool -genkeypair -v -storetype PKCS12 -keystore newsgap.keystore \
  -alias newsgap -keyalg RSA -keysize 2048 -validity 10000
```

```gradle
// android/app/build.gradle
android {
    signingConfigs {
        release {
            storeFile file('newsgap.keystore')
            storePassword 'your_password'
            keyAlias 'newsgap'
            keyPassword 'your_password'
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
}
```

**构建 APK**:
```bash
cd android
./gradlew assembleRelease
```

**发布到 Google Play**:
1. 在 Google Play Console 创建应用
2. 上传截图和描述
3. 上传 AAB 文件
4. 提交审核

---

### Phase 3: 后端优化 (可选)

**时间估算**: 2-3 周  
**优先级**: 🔵 中  

#### 3.1 认证和授权

**添加用户系统**:
```python
# backend/auth/jwt_handler.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
```

**保护 API 端点**:
```python
@router.get("/api/articles")
async def get_articles(user = Depends(verify_token)):
    # 只返回该用户的文章
    pass
```

#### 3.2 云同步

**同步 API**:
```python
@router.post("/api/sync/pull")
async def pull_changes(last_sync_time: datetime, user = Depends(verify_token)):
    """拉取自上次同步以来的所有更改"""
    articles = await db.get_articles_after(last_sync_time, user.id)
    analyses = await db.get_analyses_after(last_sync_time, user.id)
    return {"articles": articles, "analyses": analyses}

@router.post("/api/sync/push")
async def push_changes(changes: SyncChanges, user = Depends(verify_token)):
    """推送本地更改到云端"""
    await db.merge_changes(changes, user.id)
    return {"status": "success"}
```

#### 3.3 云部署

**Docker 化**:
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**部署选项**:
- Railway (推荐,简单易用)
- Fly.io (边缘计算)
- AWS ECS (企业级)
- Google Cloud Run (按需付费)

---

## 📋 详细任务清单

### 桌面端任务 (Tauri)

- [ ] **环境搭建** (1 天)
  - [ ] 安装 Rust 和 Tauri CLI
  - [ ] 初始化 Tauri 项目
  - [ ] 配置 VS Code 开发环境

- [ ] **后端集成** (3 天)
  - [ ] 使用 PyInstaller 打包 Python 后端
  - [ ] 配置 Sidecar 模式
  - [ ] 实现后端进程生命周期管理
  - [ ] 测试前后端通信

- [ ] **前端适配** (3 天)
  - [ ] 安装 @tauri-apps/api
  - [ ] 添加 Tauri API 调用封装
  - [ ] 实现自定义标题栏
  - [ ] 更新 Vite 配置

- [ ] **桌面特性** (3 天)
  - [ ] 实现系统托盘
  - [ ] 添加全局快捷键
  - [ ] 实现桌面通知
  - [ ] 文件拖放支持

- [ ] **应用配置** (2 天)
  - [ ] 完善 tauri.conf.json
  - [ ] 设计应用图标 (多尺寸)
  - [ ] 配置应用菜单
  - [ ] 设置应用权限

- [ ] **构建和打包** (3 天)
  - [ ] macOS 构建测试
  - [ ] Windows 构建测试
  - [ ] Linux 构建测试
  - [ ] 生成安装包

- [ ] **测试和优化** (3 天)
  - [ ] 多平台功能测试
  - [ ] 性能优化
  - [ ] 内存泄漏检查
  - [ ] 用户体验优化

### 移动端任务 (React Native)

- [ ] **环境搭建** (2 天)
  - [ ] 配置 React Native 开发环境
  - [ ] 安装 Android Studio 和 Xcode
  - [ ] 创建 React Native 项目
  - [ ] 配置导航和状态管理

- [ ] **代码复用** (5 天)
  - [ ] 重构为 Monorepo 架构
  - [ ] 抽离共享代码到 packages/shared
  - [ ] 创建平台无关的 UI 组件
  - [ ] 迁移业务逻辑

- [ ] **页面开发** (8 天)
  - [ ] 首页 (文章流)
  - [ ] 文章详情页
  - [ ] 分析结果页
  - [ ] 设置页
  - [ ] 信息源管理页
  - [ ] 搜索页

- [ ] **移动端特性** (5 天)
  - [ ] 离线缓存
  - [ ] 推送通知
  - [ ] 生物识别登录
  - [ ] 分享功能
  - [ ] 深色模式

- [ ] **iOS 开发** (5 天)
  - [ ] Xcode 项目配置
  - [ ] iOS 特定适配
  - [ ] TestFlight 测试
  - [ ] App Store 准备

- [ ] **Android 开发** (5 天)
  - [ ] Android Studio 配置
  - [ ] Android 特定适配
  - [ ] 签名配置
  - [ ] Google Play 准备

- [ ] **测试和优化** (5 天)
  - [ ] 功能测试
  - [ ] 性能测试
  - [ ] UI/UX 优化
  - [ ] Bug 修复

### 后端优化任务 (可选)

- [ ] **用户系统** (5 天)
  - [ ] JWT 认证实现
  - [ ] 用户注册/登录 API
  - [ ] 权限管理
  - [ ] 数据隔离

- [ ] **云同步** (5 天)
  - [ ] 同步协议设计
  - [ ] 冲突解决策略
  - [ ] 增量同步 API
  - [ ] 客户端同步逻辑

- [ ] **云部署** (3 天)
  - [ ] Docker 化
  - [ ] CI/CD 配置
  - [ ] 部署到云平台
  - [ ] 监控和日志

---

## 🔧 技术细节和最佳实践

### 1. 平台检测

```typescript
// packages/shared/utils/platform.ts
export const Platform = {
  isWeb: typeof window !== 'undefined' && !('__TAURI__' in window),
  isTauri: typeof window !== 'undefined' && '__TAURI__' in window,
  isMobile: typeof navigator !== 'undefined' && /iPhone|iPad|iPod|Android/i.test(navigator.userAgent),
  isIOS: typeof navigator !== 'undefined' && /iPhone|iPad|iPod/i.test(navigator.userAgent),
  isAndroid: typeof navigator !== 'undefined' && /Android/i.test(navigator.userAgent),
};
```

### 2. 统一 API 客户端

```typescript
// packages/shared/services/api.ts
import axios from 'axios';
import { Platform } from '../utils/platform';

const getBaseURL = () => {
  if (Platform.isWeb || Platform.isTauri) {
    return 'http://localhost:8000';
  }
  // 移动端
  return Platform.isIOS ? 'http://localhost:8000' : 'http://10.0.2.2:8000';
};

export const apiClient = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### 3. 响应式布局

```typescript
// packages/ui-primitives/ResponsiveLayout.tsx
import { useWindowDimensions } from 'react-native';

export function ResponsiveLayout({ children }) {
  const { width } = useWindowDimensions();
  
  const isMobile = width < 768;
  const isTablet = width >= 768 && width < 1024;
  const isDesktop = width >= 1024;
  
  return children({ isMobile, isTablet, isDesktop });
}
```

### 4. 离线存储策略

```typescript
// packages/shared/services/offline.ts
import { Platform } from '../utils/platform';

export const storage = {
  async getItem(key: string): Promise<string | null> {
    if (Platform.isWeb || Platform.isTauri) {
      return localStorage.getItem(key);
    } else {
      const AsyncStorage = await import('@react-native-async-storage/async-storage');
      return AsyncStorage.default.getItem(key);
    }
  },
  
  async setItem(key: string, value: string): Promise<void> {
    if (Platform.isWeb || Platform.isTauri) {
      localStorage.setItem(key, value);
    } else {
      const AsyncStorage = await import('@react-native-async-storage/async-storage');
      await AsyncStorage.default.setItem(key, value);
    }
  },
};
```

---

## 📦 依赖清单

### 桌面端新增依赖

```toml
# src-tauri/Cargo.toml
[dependencies]
tauri = { version = "1.5", features = ["shell-open", "dialog-all", "fs-all", "notification-all", "window-all", "system-tray", "global-shortcut", "updater"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1", features = ["full"] }
```

```json
// frontend/package.json (新增)
{
  "dependencies": {
    "@tauri-apps/api": "^1.5.0"
  }
}
```

### 移动端新增依赖

```json
// apps/mobile/package.json
{
  "dependencies": {
    "react-native": "0.73.0",
    "@react-navigation/native": "^6.1.9",
    "@react-navigation/stack": "^6.3.20",
    "react-native-screens": "^3.29.0",
    "react-native-safe-area-context": "^4.8.2",
    "@react-native-async-storage/async-storage": "^1.21.0",
    "@react-native-community/netinfo": "^11.1.0",
    "react-native-markdown-display": "^7.0.2",
    "@react-native-firebase/app": "^19.0.0",
    "@react-native-firebase/messaging": "^19.0.0",
    "react-native-biometrics": "^3.0.1"
  }
}
```

---

## 💰 成本估算

| 项目 | 桌面端 | 移动端 | 云服务 | 总计 |
|------|--------|--------|--------|------|
| **开发时间** | 3-4 周 | 6-8 周 | 2-3 周 | 11-15 周 |
| **开发成本** | ¥15,000-20,000 | ¥30,000-40,000 | ¥10,000-15,000 | ¥55,000-75,000 |
| **工具成本** | ¥0 (开源) | ¥688/年 (Apple) | ¥0-500/月 | ¥688/年 + 云费用 |
| **发布成本** | ¥0 | ¥688/年 (iOS)<br>¥175 (Android 一次性) | - | ¥863/年 |

**备注**:
- 开发成本假设 1 人独立开发,时薪 ¥200-250
- 云服务成本取决于用户量 (Railway 免费版可支持 500 用户)
- Apple Developer Program: ¥688/年 (必需)
- Google Play 开发者: ¥175 一次性

---

## ⚠️ 风险和挑战

### 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| PyInstaller 打包失败 | 高 | 中 | 提前测试,准备 Docker 方案 |
| React Native 性能问题 | 中 | 中 | 使用 Hermes 引擎,代码优化 |
| iOS 审核被拒 | 高 | 低 | 严格遵守 App Store 指南 |
| 跨平台 UI 一致性 | 中 | 高 | 使用设计系统,详细测试 |

### 业务风险

- **用户迁移**: 现有 Web 用户可能不愿下载应用
  - 缓解: 保留 Web 版本,提供增量价值
- **维护成本**: 多平台意味着更多维护工作
  - 缓解: 最大化代码复用,自动化测试

---

## 🎯 里程碑和时间表

```
Week 1-2:   Tauri 环境搭建 + 后端集成
Week 3-4:   桌面端前端适配 + 特性开发
Week 5:     桌面端测试 + 打包
Week 6:     移动端环境搭建 + Monorepo 重构
Week 7-9:   移动端页面开发
Week 10-11: 移动端特性开发
Week 12-13: iOS/Android 构建和测试
Week 14:    发布准备和上线
Week 15:    文档和培训
```

**关键检查点**:
- ✅ Week 2: 桌面端后端成功启动
- ✅ Week 5: 桌面端可安装包生成
- ✅ Week 9: 移动端核心功能完成
- ✅ Week 13: 通过 TestFlight 和内部测试
- ✅ Week 14: 提交 App Store 和 Google Play

---

## 📚 参考资源

### 官方文档
- [Tauri 文档](https://tauri.app/)
- [React Native 文档](https://reactnative.dev/)
- [Expo 文档](https://docs.expo.dev/)

### 示例项目
- [Tauri + React 示例](https://github.com/tauri-apps/tauri/tree/dev/examples)
- [React Native + TypeScript 模板](https://github.com/react-native-community/react-native-template-typescript)

### 工具和库
- [PyInstaller](https://pyinstaller.org/)
- [React Navigation](https://reactnavigation.org/)
- [Zustand](https://github.com/pmndrs/zustand)
- [TanStack Query](https://tanstack.com/query)

---

## 🤝 下一步行动

1. **确认方案**: 与团队讨论并确认技术方案
2. **环境搭建**: 开始搭建 Tauri 开发环境
3. **后端打包**: 测试 PyInstaller 打包 FastAPI 应用
4. **原型开发**: 创建桌面端 MVP (最小可行产品)
5. **用户测试**: 邀请早期用户测试桌面版

---

## 💡 总结

**NewsGap 全平台改造是完全可行的**,主要优势:

✅ **高代码复用率** - 85%+ 桌面端, 60%+ 移动端  
✅ **现代技术栈** - React/TypeScript/FastAPI 完美契合跨平台开发  
✅ **清晰架构** - 前后端分离,易于平台扩展  
✅ **渐进式迁移** - 可按阶段实施,降低风险  

**推荐路线**:
1. 先完成桌面端 (Tauri) - 快速验证,低成本
2. 再开发移动端 (React Native) - 扩大用户群
3. 最后优化云服务 - 支撑用户增长

**预期收益**:
- 覆盖 Mac/Windows/iOS/Android 全平台用户
- 提供原生应用体验
- 支持离线使用
- 打开更广阔的市场空间

---

**文档版本**: v1.0  
**最后更新**: 2026-02-04  
**作者**: CodeBuddy AI  
**联系方式**: 项目 GitHub Issues
