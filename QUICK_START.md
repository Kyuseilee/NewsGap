# NewsGap 桌面端快速开始指南

## 🚀 立即运行应用

### 方式 1: 运行已构建的Release版本 (推荐)

```bash
# 进入项目目录
cd /Users/roson/workspace/NewsGap

# 直接运行
./src-tauri/target/release/newsgap
```

**首次运行会**:
- ✅ 自动创建数据目录
- ✅ 自动启动 Python 后端
- ✅ 打开应用窗口

---

## 🔨 重新构建

### 完整构建 (一键完成所有步骤)

```bash
./build-desktop.sh
```

### 单独构建各组件

```bash
# 1. 构建前端
cd frontend
npm run build

# 2. 打包后端
cd ../backend
source venv/bin/activate
./build-backend.sh

# 3. 构建 Tauri
cd ../src-tauri
cargo build --release
```

---

## 📦 生成安装包 (DMG)

### 安装 Tauri CLI 1.x

```bash
cargo install tauri-cli --version "^1.0"
```

### 打包

```bash
cd src-tauri
cargo tauri build
```

生成的安装包位置:
- **DMG**: `src-tauri/target/release/bundle/dmg/NewsGap_0.1.0_aarch64.dmg`
- **App**: `src-tauri/target/release/bundle/macos/NewsGap.app`

---

## 🐛 调试模式

```bash
cd src-tauri
cargo run

# 或使用 Tauri CLI
cargo tauri dev
```

---

## 📁 数据位置

应用数据存储在:
```
~/Library/Application Support/com.newsgap.desktop/
├── newsgap.db          # SQLite 数据库
├── config.yaml         # 配置文件
└── logs/              # 日志
```

---

## 🔧 常用命令

```bash
# 查看应用进程
ps aux | grep newsgap

# 查看后端日志
tail -f ~/Library/Application\ Support/com.newsgap.desktop/logs/backend.log

# 停止应用
pkill newsgap

# 清理数据
rm -rf ~/Library/Application\ Support/com.newsgap.desktop/
```

---

## ✅ 验证安装

运行后访问:
- 前端 UI: 应用窗口自动打开
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

---

## 💡 提示

1. **首次启动可能较慢** - 后端需要初始化数据库
2. **端口占用** - 确保 8000 端口未被占用
3. **权限问题** - 确保后端可执行: `chmod +x binaries/newsgap-backend-*`

---

**享受使用 NewsGap! 🎉**
