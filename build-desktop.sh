#!/bin/bash
################################################################################
# NewsGap 桌面端完整构建脚本
# 功能：自动化构建前端、打包后端、集成Tauri并生成安装包
################################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_section() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN}$1${NC}"
    echo "=========================================="
    echo ""
}

# 检查依赖
check_dependencies() {
    print_section "检查构建依赖"
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    print_info "✓ Python: $(python3 --version)"
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js 未安装"
        exit 1
    fi
    print_info "✓ Node.js: $(node --version)"
    
    # 检查 Rust
    if ! command -v cargo &> /dev/null; then
        print_error "Rust 未安装"
        exit 1
    fi
    print_info "✓ Rust: $(rustc --version)"
    
    print_success "所有依赖检查通过"
}

# 构建前端
build_frontend() {
    print_section "构建前端"
    
    cd "$SCRIPT_DIR/frontend"
    
    # 安装依赖（如果需要）
    if [ ! -d "node_modules" ]; then
        print_info "安装前端依赖..."
        npm install
    fi
    
    # 构建前端
    print_info "构建 React 应用..."
    npm run build
    
    if [ ! -d "dist" ]; then
        print_error "前端构建失败"
        exit 1
    fi
    
    print_success "前端构建完成"
    cd "$SCRIPT_DIR"
}

# 打包后端
build_backend() {
    print_section "打包 Python 后端"
    
    cd "$SCRIPT_DIR/backend"
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        print_info "创建 Python 虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    print_info "安装后端依赖..."
    pip install -q -r requirements.txt
    
    # 安装 PyInstaller
    if ! python3 -c "import PyInstaller" 2>/dev/null; then
        print_info "安装 PyInstaller..."
        pip install pyinstaller
    fi
    
    # 清理旧的构建
    print_info "清理旧的构建文件..."
    rm -rf build dist
    
    # 打包
    print_info "打包后端（这可能需要几分钟）..."
    python3 -m PyInstaller newsgap-backend.spec --clean
    
    if [ ! -f "dist/newsgap-backend" ]; then
        print_error "后端打包失败"
        exit 1
    fi
    
    # 复制到 Tauri binaries 目录
    print_info "复制后端到 Tauri binaries 目录..."
    mkdir -p "$SCRIPT_DIR/src-tauri/binaries"
    cp dist/newsgap-backend "$SCRIPT_DIR/src-tauri/binaries/"
    chmod +x "$SCRIPT_DIR/src-tauri/binaries/newsgap-backend"
    
    FILE_SIZE=$(du -h dist/newsgap-backend | cut -f1)
    print_success "后端打包完成 (大小: $FILE_SIZE)"
    
    cd "$SCRIPT_DIR"
}

# 构建 Tauri 应用
build_tauri() {
    print_section "构建 Tauri 桌面应用"
    
    cd "$SCRIPT_DIR/src-tauri"
    
    # 构建
    print_info "构建 Tauri 应用（这可能需要几分钟）..."
    cargo build --release
    
    if [ ! -f "target/release/newsgap" ]; then
        print_error "Tauri 构建失败"
        exit 1
    fi
    
    print_success "Tauri 应用构建完成"
    
    # 打包安装程序
    print_info "打包安装程序..."
    cargo tauri build || print_warning "打包安装程序失败，但可执行文件已生成"
    
    cd "$SCRIPT_DIR"
}

# 显示构建结果
show_results() {
    print_section "构建结果"
    
    echo "📦 构建产物："
    echo ""
    
    # 可执行文件
    if [ -f "src-tauri/target/release/newsgap" ]; then
        EXEC_SIZE=$(du -h src-tauri/target/release/newsgap | cut -f1)
        echo "  ✓ 可执行文件: src-tauri/target/release/newsgap ($EXEC_SIZE)"
    fi
    
    # macOS DMG
    if [ -f "src-tauri/target/release/bundle/dmg/NewsGap_0.1.0_aarch64.dmg" ]; then
        DMG_SIZE=$(du -h src-tauri/target/release/bundle/dmg/NewsGap_0.1.0_aarch64.dmg | cut -f1)
        echo "  ✓ macOS 安装包: src-tauri/target/release/bundle/dmg/NewsGap_0.1.0_aarch64.dmg ($DMG_SIZE)"
    fi
    
    # macOS App
    if [ -d "src-tauri/target/release/bundle/macos/NewsGap.app" ]; then
        APP_SIZE=$(du -sh src-tauri/target/release/bundle/macos/NewsGap.app | cut -f1)
        echo "  ✓ macOS App: src-tauri/target/release/bundle/macos/NewsGap.app ($APP_SIZE)"
    fi
    
    echo ""
    echo "🚀 运行方式："
    echo "  - 直接运行: ./src-tauri/target/release/newsgap"
    echo "  - 安装 DMG: 打开 .dmg 文件并拖拽到应用程序文件夹"
    echo ""
    
    print_success "构建完成！"
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "  NewsGap 桌面端构建工具"
    echo "  版本: 0.1.0"
    echo "=========================================="
    echo ""
    
    # 检查依赖
    check_dependencies
    
    # 构建前端
    build_frontend
    
    # 打包后端
    build_backend
    
    # 构建 Tauri
    build_tauri
    
    # 显示结果
    show_results
    
    print_success "全部完成！"
}

# 运行主函数
main
