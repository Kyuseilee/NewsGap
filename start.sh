#!/bin/bash

################################################################################
# NewsGap 一键启动脚本
# 功能：同时启动前端和后端服务
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

# PID 文件
BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"
FRONTEND_PID_FILE="$SCRIPT_DIR/.frontend.pid"

# 日志文件
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

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

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口空闲
    fi
}

# 停止已存在的进程
stop_existing_services() {
    print_info "检查并停止已存在的服务..."
    
    # 停止后端
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            print_warning "停止已运行的后端进程 (PID: $BACKEND_PID)..."
            kill $BACKEND_PID 2>/dev/null || true
            sleep 1
            # 如果还存在，强制杀掉
            if ps -p $BACKEND_PID > /dev/null 2>&1; then
                kill -9 $BACKEND_PID 2>/dev/null || true
            fi
        fi
        rm -f "$BACKEND_PID_FILE"
    fi
    
    # 停止前端
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            print_warning "停止已运行的前端进程 (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID 2>/dev/null || true
            sleep 1
            if ps -p $FRONTEND_PID > /dev/null 2>&1; then
                kill -9 $FRONTEND_PID 2>/dev/null || true
            fi
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
    
    # 检查端口
    if check_port 8000; then
        print_warning "端口 8000 仍被占用，尝试释放..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    if check_port 5173; then
        print_warning "端口 5173 仍被占用，尝试释放..."
        lsof -ti:5173 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装，请先安装 Python 3.10+"
        exit 1
    fi
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    
    # 检查后端依赖
    if [ ! -d "backend/venv" ] && [ ! -f "backend/requirements.txt" ]; then
        print_warning "后端依赖未安装，将稍后安装..."
    fi
    
    # 检查前端依赖
    if [ ! -d "frontend/node_modules" ]; then
        print_warning "前端依赖未安装，将稍后安装..."
    fi
    
    print_success "依赖检查完成"
}

# 启动后端
start_backend() {
    print_info "启动后端服务..."
    
    cd "$SCRIPT_DIR/backend"
    
    # 检查并安装依赖
    if [ ! -d "venv" ]; then
        print_info "创建 Python 虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装/更新依赖
    if [ -f "requirements.txt" ]; then
        print_info "安装后端依赖..."
        pip install -q -r requirements.txt
    fi
    
    # 启动后端（后台运行）
    print_info "启动 FastAPI 服务 (http://localhost:8000)..."
    nohup python3 main.py > "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$BACKEND_PID_FILE"
    
    # 等待后端启动
    print_info "等待后端启动..."
    for i in {1..30}; do
        if check_port 8000; then
            print_success "后端服务已启动 (PID: $BACKEND_PID)"
            print_info "后端日志: $BACKEND_LOG"
            return 0
        fi
        sleep 1
    done
    
    print_error "后端启动失败，请查看日志: $BACKEND_LOG"
    cat "$BACKEND_LOG"
    exit 1
}

# 启动 Docker 服务（可选）
start_docker() {
    # 检查是否已有 Docker Compose 配置
    if [ ! -f "$SCRIPT_DIR/docker-compose.yml" ]; then
        return 0
    fi
    
    # 检查 Docker 是否安装
    if ! command -v docker &> /dev/null; then
        return 0
    fi
    
    # 检查 RSSHub 容器是否运行
    if docker ps | grep -q newsgap-rsshub; then
        print_info "RSSHub 容器已运行"
        return 0
    fi
    
    # 询问是否启动 RSSHub
    if [ -t 0 ]; then  # 只在交互模式下询问
        read -p "是否启动 RSSHub Docker 服务？[Y/n]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            return 0
        fi
    fi
    
    print_info "启动 RSSHub Docker 服务..."
    ./docker.sh start > /dev/null 2>&1 || print_warning "RSSHub 启动失败（可选服务）"
}

# 启动前端
start_frontend() {
    print_info "启动前端服务..."
    
    cd "$SCRIPT_DIR/frontend"
    
    # 安装依赖
    if [ ! -d "node_modules" ]; then
        print_info "安装前端依赖..."
        npm install
    fi
    
    # 启动前端（后台运行）
    print_info "启动 Vite 开发服务器 (http://localhost:5173)..."
    nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$FRONTEND_PID_FILE"
    
    # 等待前端启动
    print_info "等待前端启动..."
    for i in {1..30}; do
        if check_port 5173; then
            print_success "前端服务已启动 (PID: $FRONTEND_PID)"
            print_info "前端日志: $FRONTEND_LOG"
            return 0
        fi
        sleep 1
    done
    
    print_error "前端启动失败，请查看日志: $FRONTEND_LOG"
    cat "$FRONTEND_LOG"
    exit 1
}

# 显示状态
show_status() {
    echo ""
    echo "=================================="
    echo -e "${GREEN}✅ NewsGap 已成功启动！${NC}"
    echo "=================================="
    echo ""
    echo "📊 服务信息："
    echo "  - 后端: http://localhost:8000"
    echo "  - 前端: http://localhost:5173"
    echo "  - API文档: http://localhost:8000/docs"
    
    # 检查 RSSHub 是否运行
    if docker ps 2>/dev/null | grep -q newsgap-rsshub; then
        echo "  - RSSHub: http://localhost:1200"
    fi
    echo ""
    echo "📝 进程信息："
    if [ -f "$BACKEND_PID_FILE" ]; then
        echo "  - 后端 PID: $(cat $BACKEND_PID_FILE)"
    fi
    if [ -f "$FRONTEND_PID_FILE" ]; then
        echo "  - 前端 PID: $(cat $FRONTEND_PID_FILE)"
    fi
    echo ""
    echo "📋 日志文件："
    echo "  - 后端: $BACKEND_LOG"
    echo "  - 前端: $FRONTEND_LOG"
    echo ""
    echo "💡 使用说明："
    echo "  - 查看日志: tail -f $LOG_DIR/backend.log"
    echo "  - 停止服务: ./stop.sh"
    echo "  - 查看状态: ./status.sh"
    
    # Docker 相关命令
    if docker ps 2>/dev/null | grep -q newsgap-rsshub; then
        echo "  - RSSHub状态: ./docker.sh status"
        echo "  - RSSHub日志: ./docker.sh logs"
    fi
    echo ""
    echo "🌐 现在可以在浏览器中访问: http://localhost:5173"
    echo ""
}

# 主函数
main() {
    echo ""
    echo "=================================="
    echo "  NewsGap 一键启动脚本"
    echo "=================================="
    echo ""
    
    # 停止已存在的服务
    stop_existing_services
    
    # 检查依赖
    check_dependencies
    
    # 启动 Docker（可选）
    start_docker
    
    # 启动后端
    start_backend
    
    # 启动前端
    start_frontend
    
    # 显示状态
    show_status
    
    print_success "启动完成！"
}

# 捕获退出信号
trap 'print_warning "收到退出信号，请使用 ./stop.sh 停止服务"' INT TERM

# 运行主函数
main
