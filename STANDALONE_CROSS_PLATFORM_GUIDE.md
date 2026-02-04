# NewsGap 全平台独立应用改造方案

> **核心目标**：将 NewsGap 打包为自包含的独立应用程序，内置 Python 后端 + RSSHub，无需外部依赖，支持 Mac/Windows/iOS/Android 全平台

**生成日期**：2026-02-04  
**方案版本**：v2.0 - 独立部署版  

---

## 📋 目录

1. [核心需求与架构设计](#1-核心需求与架构设计)
2. [技术方案选型](#2-技术方案选型)
3. [推荐方案：Tauri Sidecar + React Native](#3-推荐方案)
4. [桌面端独立打包方案](#4-桌面端独立打包方案)
5. [移动端独立打包方案](#5-移动端独立打包方案)
6. [RSSHub 集成方案](#6-rsshub-集成方案)
7. [数据库和存储方案](#7-数据库和存储方案)
8. [完整实施路线图](#8-完整实施路线图)
9. [包体积优化策略](#9-包体积优化策略)
10. [技术挑战与解决方案](#10-技术挑战与解决方案)

---

## 1. 核心需求与架构设计

### 1.1 独立部署要求

✅ **必须内置的组件**：
- Python FastAPI 后端（完整运行时）
- SQLite 数据库（嵌入式）
- RSSHub 服务（Node.js 运行时）
- React 前端 UI
- 所有依赖库

✅ **运行特性**：
- 双击即用，无需安装 Python/Node.js
- 完全离线运行（除 LLM API 调用）
- 数据存储在本地
- 自动端口管理，避免冲突

### 1.2 目标架构

```
┌─────────────────────────────────────────────────────────┐
│         NewsGap 独立应用程序（单一安装包）               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │           前端层（React UI）                    │    │
│  │  - 用户界面                                     │    │
│  │  - 本地路由                                     │    │
│  │  - 状态管理                                     │    │
│  └──────────────────┬─────────────────────────────┘    │
│                     │ HTTP (localhost)                  │
│  ┌──────────────────▼─────────────────────────────┐    │
│  │       Python FastAPI 后端（内置进程）          │    │
│  │  - REST API                                     │    │
│  │  - 爬虫引擎                                     │    │
│  │  - LLM 分析                                     │    │
│  │  - SQLite ORM                                   │    │
│  └──────────────────┬─────────────────────────────┘    │
│                     │                                   │
│  ┌──────────────────▼─────────────────────────────┐    │
│  │         SQLite 数据库（嵌入式）                 │    │
│  │  - 文章数据                                     │    │
│  │  - 分析结果                                     │    │
│  │  - 用户配置                                     │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │       RSSHub 服务（内置 Node.js 进程）          │    │
│  │  - RSS 源聚合                                    │    │
│  │  - 内容抓取                                      │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘

所有组件打包在同一个安装包中，用户只需安装一次
```

### 1.3 平台目标

| 平台 | 打包格式 | 预估大小 | 独立性 |
|------|---------|---------|--------|
| **macOS** | .dmg / .app | 180-250 MB | ✅ 完全独立 |
| **Windows** | .exe / .msi | 200-280 MB | ✅ 完全独立 |
| **Linux** | .AppImage / .deb | 180-250 MB | ✅ 完全独立 |
| **iOS** | .ipa | 60-100 MB | ⚠️ 无 RSSHub（受限） |
| **Android** | .apk / .aab | 80-120 MB | ⚠️ 无 RSSHub（受限） |

**说明**：移动端因应用商店限制，无法内置完整 RSSHub，采用精简方案（见第5节）

---

## 2. 技术方案选型

### 2.1 桌面端方案对比

| 方案 | Python打包 | Node.js打包 | 复杂度 | 包体积 | 推荐度 |
|------|-----------|------------|--------|--------|--------|
| **Tauri + Sidecar** | PyInstaller | pkg/nexe | ⭐⭐⭐ | 200MB | ⭐⭐⭐⭐⭐ |
| **Electron + 子进程** | PyInstaller | 内置 | ⭐⭐ | 300MB+ | ⭐⭐⭐⭐ |
| **Neutralino.js** | PyInstaller | pkg | ⭐⭐⭐ | 180MB | ⭐⭐⭐ |

### 2.2 Python 打包方案

| 工具 | 优点 | 缺点 | 包体积 |
|------|------|------|--------|
| **PyInstaller** ⭐⭐⭐⭐⭐ | 成熟稳定，支持复杂依赖 | 体积较大 | 80-120MB |
| **Nuitka** | 编译为 C，性能好 | 编译慢，兼容性问题 | 60-100MB |
| **PyOxidizer** | Rust 生态，安全 | 配置复杂 | 70-110MB |

### 2.3 Node.js/RSSHub 打包方案

| 工具 | 优点 | 缺点 | 包体积 |
|------|------|------|--------|
| **pkg** ⭐⭐⭐⭐⭐ | 简单易用，支持 Node 16+ | 不支持某些原生模块 | 40-60MB |
| **nexe** | 体积小 | 功能受限 | 30-50MB |
| **Docker 单文件** | 完整环境 | 需要 Docker 运行时 | - |

---

## 3. 推荐方案

### 🎯 桌面端：Tauri + PyInstaller + pkg

**架构图**：

```
NewsGap.app (macOS) / NewsGap.exe (Windows)
│
├── frontend/                    # Tauri 前端
│   └── index.html (React 构建产物)
│
├── backend-bin/                 # PyInstaller 打包的 Python 后端
│   └── newsgap-backend          # 单一可执行文件 (~100MB)
│
├── rsshub-bin/                  # pkg 打包的 RSSHub
│   └── rsshub-server            # 单一可执行文件 (~50MB)
│
├── data/                        # 用户数据目录
│   ├── newsgap.db              # SQLite 数据库
│   ├── config.yaml             # 配置文件
│   └── logs/                   # 日志
│
└── resources/                   # 静态资源
    └── icons/
```

**进程管理**：
1. Tauri 主进程启动
2. 自动启动 Python 后端（端口 18000）
3. 自动启动 RSSHub 服务（端口 11200）
4. 前端连接到本地服务
5. 应用退出时自动清理子进程

### 🎯 移动端：React Native + Python (Chaquopy/Kivy)

**架构选择**：

| 方案 | 可行性 | 复杂度 | 推荐度 |
|------|--------|--------|--------|
| **方案 A：精简后端** | ✅ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **方案 B：Chaquopy (Android)** | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **方案 C：Kivy/BeeWare** | ⚠️ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

**推荐方案 A（精简后端）**：
- 核心业务逻辑用 JavaScript 重写（轻量级）
- 直接调用公共 RSSHub 实例
- 使用设备本地 SQLite
- LLM 调用通过 HTTP 直达 API

---

## 4. 桌面端独立打包方案

### 4.1 Python 后端打包

#### 步骤 1：使用 PyInstaller 打包

```bash
# 安装 PyInstaller
cd backend
pip install pyinstaller

# 创建打包配置
cat > newsgap-backend.spec <<EOF
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.yaml', '.'),
        ('prompts/*.txt', 'prompts'),
        ('database/schema.sql', 'database'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'aiosqlite',
        'google.generativeai',
        'openai',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'PIL',
        'tkinter',
        'numpy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='newsgap-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# 执行打包（macOS）
pyinstaller newsgap-backend.spec --clean

# 产物位置
# dist/newsgap-backend (单一可执行文件，约 100MB)
```

#### 步骤 2：测试独立后端

```bash
# 测试打包后的可执行文件
./dist/newsgap-backend

# 应该看到：
# INFO:     Started server process
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### 步骤 3：跨平台打包

**macOS (Apple Silicon)**:
```bash
pyinstaller newsgap-backend.spec --target-arch arm64
```

**macOS (Intel)**:
```bash
pyinstaller newsgap-backend.spec --target-arch x86_64
```

**Windows**:
```bash
# 在 Windows 机器上
pyinstaller newsgap-backend.spec
```

**Linux**:
```bash
# 在 Linux 机器上
pyinstaller newsgap-backend.spec
```

### 4.2 RSSHub 打包

#### 步骤 1：准备 RSSHub 项目

```bash
# 克隆 RSSHub
git clone https://github.com/DIYgod/RSSHub.git
cd RSSHub

# 安装依赖
npm install

# 创建精简配置
cat > lib/config.js <<EOF
module.exports = {
    port: process.env.PORT || 11200,
    cache: {
        type: 'memory',
    },
    // 禁用不需要的功能
    puppeteer: false,
    redis: false,
};
EOF
```

#### 步骤 2：使用 pkg 打包

```bash
# 安装 pkg
npm install -g pkg

# 打包配置
cat > package.json <<EOF
{
  "name": "rsshub-standalone",
  "bin": "lib/index.js",
  "pkg": {
    "scripts": "lib/**/*.js",
    "assets": [
      "lib/**/*.art",
      "lib/**/*.js"
    ],
    "targets": [
      "node18-macos-arm64",
      "node18-macos-x64",
      "node18-win-x64",
      "node18-linux-x64"
    ],
    "outputPath": "dist"
  }
}
EOF

# 执行打包
pkg . --compress Brotli

# 产物：
# dist/rsshub-standalone-macos-arm64 (~50MB)
# dist/rsshub-standalone-macos-x64 (~50MB)
# dist/rsshub-standalone-win-x64.exe (~55MB)
# dist/rsshub-standalone-linux-x64 (~50MB)
```

#### 步骤 3：测试 RSSHub

```bash
# 测试打包的 RSSHub
./dist/rsshub-standalone-macos-arm64

# 访问 http://localhost:11200
```

### 4.3 Tauri 集成子进程

#### 步骤 1：配置 Tauri Sidecar

```toml
# src-tauri/Cargo.toml
[dependencies]
tauri = { version = "1.5", features = ["shell-sidecar"] }
tokio = { version = "1", features = ["full"] }
```

```json
// src-tauri/tauri.conf.json
{
  "tauri": {
    "bundle": {
      "externalBin": [
        "binaries/newsgap-backend",
        "binaries/rsshub-server"
      ],
      "resources": [
        "resources/*"
      ]
    }
  }
}
```

#### 步骤 2：Rust 进程管理

```rust
// src-tauri/src/main.rs
use tauri::api::process::{Command, CommandEvent};
use tauri::Manager;
use std::sync::{Arc, Mutex};

struct AppState {
    backend_child: Arc<Mutex<Option<std::process::Child>>>,
    rsshub_child: Arc<Mutex<Option<std::process::Child>>>,
}

fn main() {
    let app_state = AppState {
        backend_child: Arc::new(Mutex::new(None)),
        rsshub_child: Arc::new(Mutex::new(None)),
    };

    tauri::Builder::default()
        .setup(move |app| {
            // 启动 Python 后端
            let backend_state = app_state.backend_child.clone();
            tauri::async_runtime::spawn(async move {
                let (mut rx, child) = Command::new_sidecar("newsgap-backend")
                    .expect("failed to create backend command")
                    .spawn()
                    .expect("Failed to spawn backend");

                *backend_state.lock().unwrap() = Some(child);

                while let Some(event) = rx.recv().await {
                    match event {
                        CommandEvent::Stdout(line) => println!("Backend: {}", line),
                        CommandEvent::Stderr(line) => eprintln!("Backend Error: {}", line),
                        CommandEvent::Error(error) => eprintln!("Backend Error: {}", error),
                        CommandEvent::Terminated(payload) => {
                            println!("Backend exited with code: {:?}", payload.code);
                        }
                        _ => {}
                    }
                }
            });

            // 启动 RSSHub
            let rsshub_state = app_state.rsshub_child.clone();
            tauri::async_runtime::spawn(async move {
                let (mut rx, child) = Command::new_sidecar("rsshub-server")
                    .expect("failed to create rsshub command")
                    .spawn()
                    .expect("Failed to spawn rsshub");

                *rsshub_state.lock().unwrap() = Some(child);

                while let Some(event) = rx.recv().await {
                    match event {
                        CommandEvent::Stdout(line) => println!("RSSHub: {}", line),
                        CommandEvent::Stderr(line) => eprintln!("RSSHub Error: {}", line),
                        _ => {}
                    }
                }
            });

            // 等待服务启动
            std::thread::sleep(std::time::Duration::from_secs(3));

            Ok(())
        })
        .on_window_event(|event| {
            if let tauri::WindowEvent::Destroyed = event.event() {
                // 清理子进程
                // backend_child 和 rsshub_child 会在 Drop 时自动终止
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

#### 步骤 3：健康检查

```rust
// src-tauri/src/health.rs
use std::time::Duration;
use reqwest;

pub async fn wait_for_backend() -> Result<(), String> {
    for _ in 0..30 {
        match reqwest::get("http://localhost:18000/api/health").await {
            Ok(response) if response.status().is_success() => {
                return Ok(());
            }
            _ => {
                tokio::time::sleep(Duration::from_secs(1)).await;
            }
        }
    }
    Err("Backend failed to start".to_string())
}

pub async fn wait_for_rsshub() -> Result<(), String> {
    for _ in 0..30 {
        match reqwest::get("http://localhost:11200").await {
            Ok(_) => return Ok(()),
            _ => {
                tokio::time::sleep(Duration::from_secs(1)).await;
            }
        }
    }
    Err("RSSHub failed to start".to_string())
}
```

#### 步骤 4：前端连接本地服务

```typescript
// frontend/src/config/api.ts
export const API_CONFIG = {
  // 桌面端使用固定端口
  backend: 'http://localhost:18000',
  rsshub: 'http://localhost:11200',
  
  // 检查服务健康状态
  async checkHealth() {
    try {
      const response = await fetch(`${this.backend}/api/health`)
      return response.ok
    } catch {
      return false
    }
  }
}
```

### 4.4 完整构建脚本

```bash
#!/bin/bash
# build-desktop.sh

set -e

echo "🚀 开始构建 NewsGap 桌面端..."

# 1. 构建前端
echo "📦 构建前端..."
cd frontend
npm install
npm run build
cd ..

# 2. 打包 Python 后端
echo "🐍 打包 Python 后端..."
cd backend
pip install -r requirements.txt
pip install pyinstaller
pyinstaller newsgap-backend.spec --clean
cp dist/newsgap-backend ../src-tauri/binaries/
cd ..

# 3. 打包 RSSHub
echo "📡 打包 RSSHub..."
cd RSSHub
npm install
pkg . --compress Brotli
cp dist/rsshub-standalone-* ../src-tauri/binaries/rsshub-server
cd ..

# 4. 构建 Tauri 应用
echo "🎨 构建 Tauri 应用..."
cd src-tauri
cargo build --release

echo "✅ 构建完成！"
echo "📍 安装包位置："
echo "   - macOS: src-tauri/target/release/bundle/dmg/"
echo "   - Windows: src-tauri/target/release/bundle/msi/"
echo "   - Linux: src-tauri/target/release/bundle/appimage/"
```

### 4.5 最终产物

**macOS (Apple Silicon)**:
```
NewsGap_0.1.0_aarch64.dmg (约 220MB)
├── NewsGap.app
    ├── Contents/
        ├── MacOS/
        │   └── NewsGap (Tauri 主程序)
        ├── Resources/
        │   ├── newsgap-backend (100MB)
        │   ├── rsshub-server (50MB)
        │   ├── frontend/ (20MB)
        │   └── data/ (初始配置)
```

**Windows**:
```
NewsGap_0.1.0_x64.msi (约 250MB)
安装到 C:\Program Files\NewsGap\
├── NewsGap.exe (Tauri 主程序)
├── resources/
    ├── newsgap-backend.exe (120MB)
    ├── rsshub-server.exe (55MB)
    ├── frontend/ (20MB)
    └── data/ (初始配置)
```

---

## 5. 移动端独立打包方案

### 5.1 架构选择：精简方案（推荐）

**核心思路**：将关键业务逻辑用 JavaScript/TypeScript 重写，避免打包整个 Python 环境

```
React Native 应用
│
├── 前端 UI (React Native)
│
├── 核心业务逻辑 (TypeScript)
│   ├── RSS 解析器 (纯 JS)
│   ├── 内容提取器 (纯 JS)
│   ├── LLM API 客户端 (fetch)
│   └── 本地数据库 (SQLite)
│
├── 外部服务
│   ├── 公共 RSSHub (rsshub.app)
│   └── LLM API (用户自带 Key)
│
└── 本地存储
    ├── SQLite 数据库
    ├── 文章缓存
    └── 配置文件
```

### 5.2 核心模块 JavaScript 重写

#### RSS 解析器

```typescript
// packages/mobile-core/src/rss-parser.ts
import RSSParser from 'react-native-rss-parser'

export class MobileRSSParser {
  async parse(url: string): Promise<Article[]> {
    const response = await fetch(url)
    const text = await response.text()
    const feed = await RSSParser.parse(text)
    
    return feed.items.map(item => ({
      title: item.title,
      url: item.links[0]?.url,
      content: item.description,
      published_at: item.published,
      source_name: feed.title,
    }))
  }
}
```

#### 内容提取器

```typescript
// packages/mobile-core/src/extractor.ts
import { Readability } from '@mozilla/readability'
import { JSDOM } from 'jsdom'

export class MobileExtractor {
  async extract(url: string): Promise<string> {
    const response = await fetch(url)
    const html = await response.text()
    
    const dom = new JSDOM(html, { url })
    const reader = new Readability(dom.window.document)
    const article = reader.parse()
    
    return article?.content || ''
  }
}
```

#### LLM API 客户端

```typescript
// packages/mobile-core/src/llm-client.ts
export class MobileLLMClient {
  constructor(private apiKey: string, private baseURL: string) {}
  
  async analyze(articles: Article[], type: AnalysisType): Promise<Analysis> {
    const prompt = this.buildPrompt(articles, type)
    
    const response = await fetch(`${this.baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [{ role: 'user', content: prompt }],
      }),
    })
    
    const data = await response.json()
    return this.parseResponse(data)
  }
}
```

### 5.3 React Native 项目结构

```
apps/mobile/
├── android/                    # Android 原生代码
├── ios/                        # iOS 原生代码
├── src/
│   ├── App.tsx
│   ├── navigation/
│   ├── screens/
│   ├── components/
│   ├── services/              # 业务逻辑层
│   │   ├── rss-service.ts     # RSS 爬取
│   │   ├── llm-service.ts     # LLM 分析
│   │   ├── storage-service.ts # 本地存储
│   │   └── sync-service.ts    # 云同步（可选）
│   └── stores/                # 状态管理
├── package.json
└── metro.config.js
```

### 5.4 本地数据库（SQLite）

```typescript
// apps/mobile/src/services/database.ts
import SQLite from 'react-native-sqlite-storage'

export class MobileDatabase {
  private db: SQLite.SQLiteDatabase
  
  async init() {
    this.db = await SQLite.openDatabase({
      name: 'newsgap.db',
      location: 'default',
    })
    
    await this.createTables()
  }
  
  async createTables() {
    await this.db.executeSql(`
      CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY,
        title TEXT,
        url TEXT,
        content TEXT,
        summary TEXT,
        published_at TEXT,
        fetched_at TEXT,
        source_name TEXT,
        tags TEXT,
        archived INTEGER DEFAULT 0
      )
    `)
    
    await this.db.executeSql(`
      CREATE TABLE IF NOT EXISTS analyses (
        id TEXT PRIMARY KEY,
        analysis_type TEXT,
        article_ids TEXT,
        executive_brief TEXT,
        markdown_report TEXT,
        created_at TEXT,
        llm_backend TEXT
      )
    `)
  }
  
  async insertArticle(article: Article) {
    await this.db.executeSql(
      `INSERT OR REPLACE INTO articles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        article.id,
        article.title,
        article.url,
        article.content,
        article.summary,
        article.published_at,
        article.fetched_at,
        article.source_name,
        JSON.stringify(article.tags),
        article.archived ? 1 : 0,
      ]
    )
  }
  
  async getArticles(limit: number = 50): Promise<Article[]> {
    const [results] = await this.db.executeSql(
      `SELECT * FROM articles ORDER BY published_at DESC LIMIT ?`,
      [limit]
    )
    
    const articles: Article[] = []
    for (let i = 0; i < results.rows.length; i++) {
      const row = results.rows.item(i)
      articles.push({
        ...row,
        tags: JSON.parse(row.tags),
        archived: row.archived === 1,
      })
    }
    
    return articles
  }
}
```

### 5.5 移动端构建配置

**Android (build.gradle)**:
```gradle
android {
    defaultConfig {
        applicationId "com.newsgap.mobile"
        minSdkVersion 24
        targetSdkVersion 33
        versionCode 1
        versionName "0.1.0"
    }
    
    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    
    packagingOptions {
        pickFirst 'lib/x86/libc++_shared.so'
        pickFirst 'lib/x86_64/libc++_shared.so'
        pickFirst 'lib/armeabi-v7a/libc++_shared.so'
        pickFirst 'lib/arm64-v8a/libc++_shared.so'
    }
}
```

**iOS (Podfile)**:
```ruby
platform :ios, '13.0'
require_relative '../node_modules/react-native/scripts/react_native_pods'

target 'NewsGapMobile' do
  config = use_native_modules!

  use_react_native!(
    :path => config[:reactNativePath],
    :hermes_enabled => true,
    :fabric_enabled => false,
  )

  # SQLite
  pod 'react-native-sqlite-storage', :path => '../node_modules/react-native-sqlite-storage'
end
```

### 5.6 移动端最终产物

**iOS (.ipa)**:
```
NewsGap_0.1.0.ipa (约 60-80MB)
├── Payload/
    └── NewsGap.app/
        ├── NewsGap (二进制)
        ├── main.jsbundle (JS 代码，约 5MB)
        ├── assets/ (图片等，约 10MB)
        └── Frameworks/ (原生库，约 40MB)
```

**Android (.apk)**:
```
NewsGap_0.1.0.apk (约 80-100MB)
├── lib/
│   ├── arm64-v8a/ (约 30MB)
│   └── armeabi-v7a/ (约 25MB)
├── assets/
│   └── index.android.bundle (约 5MB)
└── res/ (约 10MB)
```

---

## 6. RSSHub 集成方案

### 6.1 桌面端：完整内置

**方案**：使用 pkg 打包 RSSHub 为单一可执行文件

**优点**：
- ✅ 完全离线运行
- ✅ 无需外部依赖
- ✅ 数据隐私保护

**配置优化**：

```javascript
// RSSHub/lib/config.js (精简配置)
module.exports = {
    port: process.env.PORT || 11200,
    
    // 使用内存缓存（避免 Redis 依赖）
    cache: {
        type: 'memory',
        routeExpire: 5 * 60, // 5 分钟
    },
    
    // 禁用不必要的功能
    feature: {
        allow_user_hotlink_template: false,
        allow_user_supply_unsafe_domain: false,
    },
    
    // 禁用 Puppeteer（减少体积）
    puppeteer: {
        wsEndpoint: null,
    },
    
    // 日志配置
    logger: {
        level: 'info',
    },
};
```

**体积优化**：
```bash
# 只打包常用路由
cat > .pkgignore <<EOF
test/
docs/
.github/
lib/routes/deprecated/
EOF

# 压缩打包
pkg . --compress Brotli --targets node18-macos-arm64
```

### 6.2 移动端：使用公共实例 + 备用方案

**主方案：公共 RSSHub 实例**

```typescript
// apps/mobile/src/config/rsshub.ts
export const RSSHUB_CONFIG = {
  // 主实例（官方）
  primary: 'https://rsshub.app',
  
  // 备用实例列表
  fallbacks: [
    'https://rsshub.rssforever.com',
    'https://hub.slarker.me',
  ],
  
  // 自动切换策略
  async getAvailableInstance(): Promise<string> {
    const instances = [this.primary, ...this.fallbacks]
    
    for (const instance of instances) {
      try {
        const response = await fetch(instance, { timeout: 3000 })
        if (response.ok) return instance
      } catch {
        continue
      }
    }
    
    throw new Error('所有 RSSHub 实例均不可用')
  }
}
```

**备用方案：内置精简爬虫**

```typescript
// apps/mobile/src/services/fallback-crawler.ts
export class FallbackCrawler {
  // 内置常用网站的爬虫规则
  private rules = {
    'twitter.com': {
      selector: '.tweet-text',
      author: '.username',
    },
    'github.com': {
      selector: '.commit-message',
      author: '.author',
    },
    // ... 其他常用站点
  }
  
  async crawl(url: string): Promise<Article[]> {
    const domain = new URL(url).hostname
    const rule = this.rules[domain]
    
    if (!rule) {
      throw new Error(`不支持的网站: ${domain}`)
    }
    
    // 使用 rule 解析页面
    // ...
  }
}
```

---

## 7. 数据库和存储方案

### 7.1 桌面端存储

**目录结构**：

```
macOS:
~/Library/Application Support/com.newsgap.desktop/
├── newsgap.db (SQLite 数据库)
├── config.yaml (用户配置)
├── logs/ (日志文件)
└── cache/ (临时缓存)

Windows:
C:\Users\{user}\AppData\Roaming\com.newsgap.desktop\
├── newsgap.db
├── config.yaml
├── logs\
└── cache\

Linux:
~/.config/newsgap/
├── newsgap.db
├── config.yaml
├── logs/
└── cache/
```

**Rust 获取数据目录**：

```rust
// src-tauri/src/storage.rs
use tauri::api::path::app_data_dir;

pub fn get_data_dir(app: &tauri::AppHandle) -> PathBuf {
    let data_dir = app_data_dir(&app.config()).unwrap();
    
    if !data_dir.exists() {
        std::fs::create_dir_all(&data_dir).unwrap();
    }
    
    data_dir
}

pub fn get_db_path(app: &tauri::AppHandle) -> String {
    let data_dir = get_data_dir(app);
    data_dir.join("newsgap.db").to_string_lossy().to_string()
}
```

**传递给 Python 后端**：

```rust
// 启动后端时传递数据目录
let data_dir = get_data_dir(&app);
let backend_child = Command::new_sidecar("newsgap-backend")
    .args(&["--data-dir", data_dir.to_str().unwrap()])
    .spawn()
    .expect("Failed to spawn backend");
```

```python
# backend/main.py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--data-dir', default='./data')
args = parser.parse_args()

# 使用指定的数据目录
DB_PATH = os.path.join(args.data_dir, 'newsgap.db')
```

### 7.2 移动端存储

**存储方案**：
- SQLite：react-native-sqlite-storage
- 配置/缓存：react-native-mmkv（高性能）
- 文件：react-native-fs

```typescript
// 数据目录
iOS: {AppDataDirectory}/Documents/
Android: {AppDataDirectory}/files/

// 文件布局
├── newsgap.db
├── config.json
├── cache/
│   ├── articles/
│   └── images/
└── exports/
```

---

## 8. 完整实施路线图

### 总周期：14-18 周

```
阶段 1: 准备和重构 (2-3 周)
├─ Week 1-2: 代码模块化重构
└─ Week 3: 打包工具预研和测试

阶段 2: 桌面端开发 (5-6 周)
├─ Week 4-5: Python 后端打包
├─ Week 6: RSSHub 打包和集成
├─ Week 7-8: Tauri 进程管理
└─ Week 9: 桌面端功能完善和测试

阶段 3: 移动端开发 (6-7 周)
├─ Week 10-11: 核心逻辑 JS 重写
├─ Week 12-13: React Native UI 开发
├─ Week 14-15: 原生功能集成
└─ Week 16: 移动端测试

阶段 4: 测试和发布 (2 周)
├─ Week 17: 跨平台测试
└─ Week 18: 应用商店上架
```

### 详细任务分解

#### 阶段 1：准备和重构（2-3 周）

| 任务 | 工作量 | 产出 |
|------|--------|------|
| Python 后端模块化 | 3 天 | 独立的 FastAPI 服务 |
| PyInstaller 配置和测试 | 3 天 | 可执行的后端文件 |
| RSSHub 精简和 pkg 打包测试 | 3 天 | 可执行的 RSSHub 文件 |
| Tauri 项目初始化 | 2 天 | 基础项目结构 |
| 进程管理方案设计 | 2 天 | 技术方案文档 |

#### 阶段 2：桌面端开发（5-6 周）

| 任务 | 工作量 | 产出 |
|------|--------|------|
| Python 后端完整打包 | 4 天 | 跨平台可执行文件 |
| RSSHub 完整打包 | 3 天 | 跨平台可执行文件 |
| Tauri Sidecar 集成 | 5 天 | 子进程管理 |
| 健康检查和错误处理 | 3 天 | 稳定的启动流程 |
| 数据目录管理 | 2 天 | 跨平台数据存储 |
| 系统托盘和菜单 | 3 天 | 原生桌面体验 |
| 自动更新机制 | 4 天 | 版本检测和升级 |
| 跨平台构建和测试 | 5 天 | DMG/MSI/AppImage |

#### 阶段 3：移动端开发（6-7 周）

| 任务 | 工作量 | 产出 |
|------|--------|------|
| RSS 解析器 JS 重写 | 4 天 | 纯 JS RSS 解析 |
| 内容提取器 JS 重写 | 4 天 | 纯 JS 内容提取 |
| LLM 客户端封装 | 3 天 | 直接 API 调用 |
| SQLite 数据库集成 | 3 天 | 本地数据持久化 |
| React Native 页面开发 | 8 天 | 完整 UI |
| 离线缓存机制 | 3 天 | 离线阅读 |
| 推送通知 | 3 天 | FCM/APNs |
| iOS 打包和签名 | 3 天 | IPA 文件 |
| Android 打包和签名 | 3 天 | APK/AAB 文件 |

---

## 9. 包体积优化策略

### 9.1 Python 后端优化

**目标**：从 150MB 压缩到 80-100MB

```python
# 排除不必要的库
excludes = [
    'matplotlib',    # 绘图库 (30MB)
    'PIL',          # 图像处理 (20MB)
    'tkinter',      # GUI (15MB)
    'numpy',        # 数值计算 (25MB)
    'scipy',        # 科学计算 (30MB)
    'pandas',       # 数据分析 (如果不用)
]

# 使用 UPX 压缩
upx = True
upx_exclude = ['vcruntime140.dll', 'python38.dll']
```

**动态库精简**：
```bash
# 移除调试符号
strip dist/newsgap-backend

# UPX 最大压缩
upx --best --lzma dist/newsgap-backend
```

### 9.2 RSSHub 优化

**目标**：从 80MB 压缩到 40-50MB

```json
// 只包含常用路由
{
  "pkg": {
    "scripts": [
      "lib/index.js",
      "lib/router.js",
      "lib/routes/twitter/**/*.js",
      "lib/routes/github/**/*.js",
      "lib/routes/bilibili/**/*.js",
      "lib/routes/weibo/**/*.js"
    ]
  }
}
```

**Brotli 压缩**：
```bash
pkg . --compress Brotli
```

### 9.3 移动端优化

**Android**：
```gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt')
        }
    }
    
    splits {
        abi {
            enable true
            reset()
            include 'arm64-v8a', 'armeabi-v7a'
            universalApk false
        }
    }
}
```

**iOS**:
```
- 启用 Bitcode
- 使用 App Thinning
- 压缩图片资源（WebP）
```

---

## 10. 技术挑战与解决方案

### 10.1 挑战：Python 依赖打包

**问题**：某些 Python 库依赖系统库，PyInstaller 无法自动打包

**解决方案**：

```python
# 方案 1：使用 --hidden-import 明确指定
hiddenimports = [
    'google.generativeai',
    'google.ai.generativelanguage_v1beta',
    'google.api_core',
]

# 方案 2：Hook 脚本
# hooks/hook-google-generativeai.py
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('google.generativeai')
```

**测试方案**：
```bash
# 在干净的虚拟环境测试
python -m venv test_env
source test_env/bin/activate
./dist/newsgap-backend
```

### 10.2 挑战：RSSHub 动态路由

**问题**：RSSHub 使用动态 require，pkg 无法静态分析

**解决方案**：

```javascript
// 生成路由清单
const fs = require('fs');
const path = require('path');

function collectRoutes(dir) {
    const routes = [];
    const files = fs.readdirSync(dir);
    
    files.forEach(file => {
        const fullPath = path.join(dir, file);
        if (fs.statSync(fullPath).isDirectory()) {
            routes.push(...collectRoutes(fullPath));
        } else if (file.endsWith('.js')) {
            routes.push(fullPath);
        }
    });
    
    return routes;
}

// 写入 package.json
const routes = collectRoutes('./lib/routes');
fs.writeFileSync('routes.json', JSON.stringify(routes));
```

### 10.3 挑战：跨平台端口冲突

**问题**：多个实例同时运行时端口冲突

**解决方案**：

```rust
// 动态端口分配
use std::net::TcpListener;

fn find_available_port(start: u16) -> u16 {
    for port in start..start + 100 {
        if TcpListener::bind(("127.0.0.1", port)).is_ok() {
            return port;
        }
    }
    panic!("No available port found");
}

// 使用
let backend_port = find_available_port(18000);
let rsshub_port = find_available_port(11200);

// 传递给子进程
Command::new_sidecar("newsgap-backend")
    .args(&["--port", &backend_port.to_string()])
    .spawn()
```

### 10.4 挑战：移动端内存限制

**问题**：iOS/Android 应用内存限制，大数据量卡顿

**解决方案**：

```typescript
// 虚拟滚动
import { FlatList } from 'react-native'

<FlatList
  data={articles}
  renderItem={renderArticle}
  keyExtractor={item => item.id}
  initialNumToRender={10}
  maxToRenderPerBatch={10}
  windowSize={5}
  removeClippedSubviews={true}
/>

// 图片懒加载
import FastImage from 'react-native-fast-image'

<FastImage
  source={{ uri: imageUrl }}
  resizeMode={FastImage.resizeMode.cover}
/>
```

---

## 总结与建议

### ✅ 独立部署方案优势

1. **用户体验极佳**：双击即用，无需配置环境
2. **数据隐私保护**：完全本地运行，无需云服务
3. **离线可用**：除 LLM API，其他功能完全离线
4. **部署简单**：一个安装包搞定所有依赖

### ⚠️ 需要注意的问题

1. **包体积较大**：桌面端 200-250MB，移动端 60-100MB
2. **维护成本**：需要维护 Python/Node.js 打包流程
3. **移动端限制**：iOS/Android 无法内置完整 RSSHub
4. **更新机制**：需要实现应用内自动更新

### 🎯 推荐实施策略

**短期（1-2 个月）**：
1. 先完成桌面端（Tauri + PyInstaller + pkg）
2. 验证独立打包可行性
3. 收集用户反馈

**中期（3-4 个月）**：
1. 开发移动端（React Native + JS重写核心逻辑）
2. 实现跨平台数据同步
3. 完善自动更新机制

**长期（6+ 个月）**：
1. 考虑 Rust 重写核心模块（进一步减小体积）
2. 支持插件系统
3. 企业版功能（多用户、权限管理）

### 📦 预期成果

**桌面端**：
- macOS/Windows/Linux 独立安装包
- 包含 Python 后端 + RSSHub + 前端
- 体积：200-250MB
- 启动时间：< 5 秒

**移动端**：
- iOS/Android 原生应用
- 纯 JS 业务逻辑
- 体积：60-100MB
- 启动时间：< 2 秒

---

**文档版本**：v2.0  
**最后更新**：2026-02-04  
**方案类型**：独立部署版  
