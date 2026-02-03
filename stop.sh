#!/bin/bash

################################################################################
# NewsGap 一键停止脚本
# 功能：停止前端和后端服务
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# PID 文件
BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"
FRONTEND_PID_FILE="$SCRIPT_DIR/.frontend.pid"

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

# 停止后端
stop_backend() {
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            print_info "停止后端服务 (PID: $BACKEND_PID)..."
            kill $BACKEND_PID 2>/dev/null || true
            sleep 2
            
            # 检查是否还在运行
            if ps -p $BACKEND_PID > /dev/null 2>&1; then
                print_warning "后端进程未响应，强制停止..."
                kill -9 $BACKEND_PID 2>/dev/null || true
            fi
            
            print_success "后端服务已停止"
        else
            print_warning "后端进程不存在 (PID: $BACKEND_PID)"
        fi
        rm -f "$BACKEND_PID_FILE"
    else
        print_warning "未找到后端 PID 文件"
    fi
    
    # 确保端口 8000 被释放
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "端口 8000 仍被占用，释放中..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    fi
}

# 停止前端
stop_frontend() {
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            print_info "停止前端服务 (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID 2>/dev/null || true
            sleep 2
            
            # 检查是否还在运行
            if ps -p $FRONTEND_PID > /dev/null 2>&1; then
                print_warning "前端进程未响应，强制停止..."
                kill -9 $FRONTEND_PID 2>/dev/null || true
            fi
            
            print_success "前端服务已停止"
        else
            print_warning "前端进程不存在 (PID: $FRONTEND_PID)"
        fi
        rm -f "$FRONTEND_PID_FILE"
    else
        print_warning "未找到前端 PID 文件"
    fi
    
    # 确保端口 5173 被释放
    if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "端口 5173 仍被占用，释放中..."
        lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    fi
}

# 停止 Docker 服务（可选）
stop_docker() {
    # 检查 Docker 是否安装
    if ! command -v docker &> /dev/null; then
        return 0
    fi
    
    # 检查 RSSHub 容器是否运行
    if ! docker ps | grep -q newsgap-rsshub; then
        return 0
    fi
    
    # 询问是否停止 RSSHub
    if [ -t 0 ]; then  # 只在交互模式下询问
        read -p "是否同时停止 RSSHub Docker 服务？[y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "保持 RSSHub 运行"
            return 0
        fi
    fi
    
    print_info "停止 RSSHub Docker 服务..."
    ./docker.sh stop > /dev/null 2>&1 || print_warning "RSSHub 停止失败（可选服务）"
}

# 主函数
main() {
    echo ""
    echo "=================================="
    echo "  NewsGap 一键停止脚本"
    echo "=================================="
    echo ""
    
    stop_backend
    stop_frontend
    stop_docker
    
    echo ""
    print_success "所有服务已停止"
    echo ""
}

main
