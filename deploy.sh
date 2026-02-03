#!/bin/bash

################################################################################
# NewsGap 一键部署脚本
# 功能：安装依赖、初始化数据库、配置环境
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

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

print_step() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}▶ $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# 检查系统依赖
check_system_dependencies() {
    print_step "1. 检查系统依赖"
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        echo "请安装 Python 3.10 或更高版本："
        echo "  macOS: brew install python@3.10"
        echo "  Ubuntu: sudo apt install python3.10"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python 版本: $PYTHON_VERSION"
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js 未安装"
        echo "请安装 Node.js 18 或更高版本："
        echo "  macOS: brew install node"
        echo "  Ubuntu: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs"
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    print_success "Node.js 版本: $NODE_VERSION"
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        print_error "npm 未安装"
        exit 1
    fi
    
    NPM_VERSION=$(npm --version)
    print_success "npm 版本: $NPM_VERSION"
    
    print_success "系统依赖检查完成"
}

# 安装后端依赖
install_backend_dependencies() {
    print_step "2. 安装后端依赖"
    
    cd "$SCRIPT_DIR/backend"
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        print_info "创建 Python 虚拟环境..."
        python3 -m venv venv
        print_success "虚拟环境创建完成"
    else
        print_info "虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级 pip
    print_info "升级 pip..."
    pip install --upgrade pip > /dev/null 2>&1
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        print_info "安装 Python 依赖包..."
        pip install -r requirements.txt
        print_success "Python 依赖安装完成"
    else
        print_warning "未找到 requirements.txt"
    fi
    
    deactivate
    cd "$SCRIPT_DIR"
}

# 安装前端依赖
install_frontend_dependencies() {
    print_step "3. 安装前端依赖"
    
    cd "$SCRIPT_DIR/frontend"
    
    if [ -f "package.json" ]; then
        print_info "安装 npm 依赖包..."
        npm install
        print_success "npm 依赖安装完成"
    else
        print_error "未找到 package.json"
        exit 1
    fi
    
    cd "$SCRIPT_DIR"
}

# 部署 Docker 服务（可选）
deploy_docker_services() {
    print_step "4. 部署 Docker 服务（可选）"
    
    # 检查是否需要部署 Docker
    read -p "是否部署 RSSHub Docker 服务？(推荐，用于本地 RSS 源) [Y/n]: " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        # 检查 Docker 是否安装
        if ! command -v docker &> /dev/null; then
            print_warning "Docker 未安装，跳过 RSSHub 部署"
            echo ""
            echo "如需使用本地 RSSHub，请先安装 Docker："
            echo "  macOS: https://docs.docker.com/desktop/install/mac-install/"
            echo "  Ubuntu: https://docs.docker.com/engine/install/ubuntu/"
            echo ""
        else
            print_info "启动 RSSHub Docker 服务..."
            ./docker.sh start
            print_success "RSSHub 部署完成"
            echo ""
            echo "💡 RSSHub 管理命令："
            echo "   ./docker.sh status   # 查看状态"
            echo "   ./docker.sh logs     # 查看日志"
            echo "   ./docker.sh stop     # 停止服务"
            echo ""
        fi
    else
        print_info "跳过 Docker 部署"
        echo ""
        echo "💡 如需使用完整功能，建议使用公共 RSSHub："
        echo "   https://rsshub.app"
        echo ""
    fi
}

# 初始化数据库
initialize_database() {
    print_step "5. 初始化数据库"
    
    cd "$SCRIPT_DIR/backend"
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 检查数据库文件
    if [ -f "data/newsgap.db" ]; then
        print_warning "数据库文件已存在"
        read -p "是否重新初始化数据库？(会清空所有数据) [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "备份现有数据库..."
            cp data/newsgap.db "data/newsgap.db.backup.$(date +%Y%m%d_%H%M%S)"
            rm -f data/newsgap.db
            print_info "重新初始化数据库..."
            python3 -c "import asyncio; from storage.database import Database; asyncio.run(Database().initialize())"
            print_success "数据库初始化完成"
        else
            print_info "保持现有数据库"
        fi
    else
        print_info "创建数据库..."
        mkdir -p data
        python3 -c "import asyncio; from storage.database import Database; asyncio.run(Database().initialize())"
        print_success "数据库创建完成"
    fi
    
    deactivate
    cd "$SCRIPT_DIR"
}

# 配置环境变量
configure_environment() {
    print_step "6. 配置环境变量"
    
    cd "$SCRIPT_DIR/backend"
    
    # 检查 API Keys 配置
    if [ ! -f "config/api_keys.json" ]; then
        print_warning "未找到 API Keys 配置文件"
        echo ""
        echo "请在启动后通过前端界面配置 API Keys："
        echo "  设置 -> API Keys"
        echo ""
        echo "支持的 LLM 后端："
        echo "  - Gemini (推荐)"
        echo "  - DeepSeek"
        echo "  - OpenAI"
        echo "  - Ollama (本地)"
        echo ""
    else
        print_success "API Keys 配置文件已存在"
    fi
    
    cd "$SCRIPT_DIR"
}

# 创建必要的目录
create_directories() {
    print_step "7. 创建必要的目录"
    
    mkdir -p logs
    mkdir -p backend/data
    mkdir -p backend/config
    mkdir -p backend/archives
    
    print_success "目录创建完成"
}

# 设置脚本权限
set_permissions() {
    print_step "8. 设置脚本权限"
    
    chmod +x start.sh
    chmod +x stop.sh
    chmod +x status.sh
    chmod +x deploy.sh
    chmod +x docker.sh
    
    print_success "脚本权限设置完成"
}

# 显示部署总结
show_summary() {
    echo ""
    echo "=================================="
    echo -e "${GREEN}✅ 部署完成！${NC}"
    echo "=================================="
    echo ""
    echo "📋 下一步："
    echo ""
    echo "1. 启动服务："
    echo "   ${CYAN}./start.sh${NC}"
    echo ""
    echo "2. 配置 API Keys (通过前端界面)："
    echo "   访问: http://localhost:5173"
    echo "   进入: 设置 -> API Keys"
    echo ""
    echo "3. 开始使用："
    echo "   - 一键情报: 自动爬取并分析"
    echo "   - 仅爬取: 只爬取文章"
    echo "   - 查看文章: 浏览已爬取的内容"
    echo ""
    echo "📚 常用命令："
    echo "   - 启动: ./start.sh"
    echo "   - 停止: ./stop.sh"
    echo "   - 状态: ./status.sh"
    echo ""
    echo "📖 文档："
    echo "   - README.md - 项目介绍"
    echo "   - backend/README.md - 后端文档"
    echo "   - frontend/README.md - 前端文档"
    echo ""
}

# 主函数
main() {
    echo ""
    echo "=================================="
    echo "  NewsGap 一键部署脚本"
    echo "=================================="
    echo ""
    echo "此脚本将："
    echo "  1. 检查系统依赖"
    echo "  2. 安装后端依赖"
    echo "  3. 安装前端依赖"
    echo "  4. 部署 Docker 服务（可选）"
    echo "  5. 初始化数据库"
    echo "  6. 配置环境变量"
    echo "  7. 创建必要的目录"
    echo "  8. 设置脚本权限"
    echo ""
    read -p "按 Enter 继续，或 Ctrl+C 取消..."
    
    check_system_dependencies
    install_backend_dependencies
    install_frontend_dependencies
    deploy_docker_services
    initialize_database
    configure_environment
    create_directories
    set_permissions
    show_summary
}

# 错误处理
trap 'print_error "部署失败！请查看上面的错误信息。"; exit 1' ERR

main
