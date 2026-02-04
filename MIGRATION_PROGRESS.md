# NewsGap 跨平台独立部署改造进度

## 📅 更新时间
2026-02-04

## ✅ 已完成的工作

### 1. 项目架构分析 ✓
- 分析了现有项目结构
- 确认了技术栈:
  - Backend: Python 3.10 + FastAPI + SQLite
  - Frontend: React + Vite + TypeScript
  - 当前部署方式: 独立运行 (需要手动启动)

### 2. Python 后端打包 ✓
- ✅ 安装并配置了 PyInstaller
- ✅ 创建了打包配置文件 `backend/newsgap-backend.spec`
- ✅ 成功打包后端为独立可执行文件
  - 文件位置: `backend/dist/newsgap-backend`
  - 文件大小: **46MB** (远小于预期的100MB)
  - 包含所有依赖: FastAPI, SQLite, LLM SDK等
- ✅ 创建了自动化打包脚本 `backend/build-backend.sh`

### 3. RSSHub 准备 ✓
- ✅ 克隆了 RSSHub 源码到 `rsshub-source/`
- ⚠️  暂未打包 (将在Tauri集成时处理)

### 4. Tauri 桌面端初始化 ✓
- ✅ 创建了 Tauri 项目结构:
  - `src-tauri/` - Rust 桌面应用
  - `src-tauri/src/main.rs` - 进程管理逻辑
  - `src-tauri/Cargo.toml` - 依赖配置
  - `src-tauri/tauri.conf.json` - Tauri 配置
- ✅ 实现了后端进程管理:
  - 自动启动 Python 后端
  - 管理数据目录
  - 进程清理机制
- ✅ 复制后端可执行文件到 `src-tauri/binaries/`
- ✅ 更新前端配置支持 Tauri:
  - 修改 `frontend/vite.config.ts`
  - API端口改为18000

### 5. 构建脚本 ✓
- ✅ 创建了完整的构建脚本 `build-desktop.sh`:
  - 自动构建前端
  - 自动打包后端
  - 自动构建 Tauri 应用
  - 生成安装包

## ⚠️ 遇到的问题

### 1. Rust 版本过旧
- 当前版本: `rustc 1.68.0`
- 需要版本: >= 1.70.0 (支持 edition 2024)
- **需要更新 Rust 工具链**

### 2. Cargo 镜像源问题
- 全局配置使用了 USTC 镜像，但存在网络问题
- 已临时切换为官方源
- 下载依赖成功，但遇到 Rust 版本问题

## 📋 下一步工作

### 立即需要做的:

1. **更新 Rust 工具链** (必须)
   ```bash
   rustup update stable
   rustup default stable
   ```

2. **完成 Tauri 构建测试**
   ```bash
   cd src-tauri
   cargo build --release
   ```

3. **测试完整应用**
   - 验证后端启动
   - 验证前端连接
   - 验证数据持久化

4. **生成图标资源**
   - 当前图标是空文件
   - 需要生成实际的应用图标
   - 工具推荐: `@tauri-apps/cli` 的图标生成功能

5. **配置 RSSHub 集成**
   - 决定是否内置 RSSHub
   - 或使用公共 RSSHub 实例
   - 如果内置，需要用 pkg 打包

### 后续优化:

6. **添加系统托盘支持**
   - 最小化到托盘
   - 托盘菜单

7. **实现自动更新**
   - 使用 Tauri 的 updater 功能

8. **跨平台打包**
   - macOS (已配置)
   - Windows (需要Windows环境)
   - Linux (需要Linux环境)

9. **移动端开发**
   - React Native 项目
   - 核心逻辑 JS 重写

## 📁 项目结构

```
NewsGap/
├── backend/                      # Python 后端
│   ├── dist/
│   │   └── newsgap-backend      # ✅ 打包后的可执行文件 (46MB)
│   ├── newsgap-backend.spec     # ✅ PyInstaller 配置
│   └── build-backend.sh         # ✅ 打包脚本
│
├── frontend/                     # React 前端
│   ├── dist/                    # 构建产物
│   └── vite.config.ts           # ✅ 已更新支持 Tauri
│
├── src-tauri/                   # ✅ Tauri 桌面应用
│   ├── src/
│   │   └── main.rs              # ✅ 进程管理
│   ├── binaries/
│   │   └── newsgap-backend      # ✅ 后端可执行文件
│   ├── icons/                   # ⚠️ 占位图标
│   ├── Cargo.toml               # ✅ Rust 配置
│   └── tauri.conf.json          # ✅ Tauri 配置
│
├── rsshub-source/               # ✅ RSSHub 源码
│
├── build-desktop.sh             # ✅ 完整构建脚本
└── STANDALONE_CROSS_PLATFORM_GUIDE.md  # 改造指南

```

## 🎯 改造目标回顾

### 桌面端目标
- [x] Python 后端打包为独立可执行文件
- [x] Tauri 项目初始化
- [x] 进程管理实现
- [ ] Rust 版本升级 (阻塞中)
- [ ] 完整应用构建和测试
- [ ] macOS DMG 生成
- [ ] Windows MSI 生成
- [ ] Linux AppImage 生成

### 移动端目标
- [ ] React Native 项目初始化
- [ ] 核心逻辑 JS 重写
- [ ] iOS 打包
- [ ] Android 打包

## 💡 技术亮点

1. **Python 后端优化打包**
   - 使用 PyInstaller 单文件模式
   - 排除不必要依赖 (matplotlib, PIL等)
   - 最终体积仅 46MB

2. **Tauri 进程管理**
   - 优雅的子进程启动和清理
   - 数据目录自动管理
   - 开发/生产模式分离

3. **自动化构建流程**
   - 一键构建所有组件
   - 详细的构建日志
   - 错误处理和验证

## 📊 预期最终产物

### macOS
- **格式**: .dmg 或 .app
- **预期大小**: ~180-220MB
  - Tauri 运行时: ~20MB
  - Python 后端: ~46MB
  - 前端资源: ~20MB
  - 依赖库: ~100MB
- **功能**: 完全独立，双击即用

### Windows
- **格式**: .msi 或 .exe
- **预期大小**: ~200-250MB
- **功能**: 完全独立，无需安装 Python/Node.js

### Linux
- **格式**: .AppImage 或 .deb
- **预期大小**: ~180-220MB
- **功能**: 完全独立

## 🔧 如何继续

### 1. 更新 Rust (最优先)
```bash
# 更新 rustup
rustup self update

# 更新到最新稳定版
rustup update stable

# 设置为默认
rustup default stable

# 验证版本
rustc --version  # 应该 >= 1.70
```

### 2. 继续构建
```bash
# 进入 Tauri 目录
cd src-tauri

# 构建 (调试模式)
cargo build

# 构建 (发布模式)
cargo build --release

# 运行
cargo run
```

### 3. 完整构建
```bash
# 使用自动化脚本
./build-desktop.sh
```

## 📝 备注

- 已将改造指南 `STANDALONE_CROSS_PLATFORM_GUIDE.md` 作为参考
- Python 后端打包配置经过优化，体积控制良好
- Tauri 配置遵循最佳实践
- 所有脚本都有详细注释和错误处理

---

**当前阻塞因素**: Rust 版本过旧 (1.68.0)，需要升级到 >= 1.70.0

**解决后预计**: 可以成功构建 Tauri 应用，生成独立的桌面安装包
