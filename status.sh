#!/bin/bash

################################################################################
# NewsGap 服务状态查看脚本
# 功能：查看前端和后端服务的运行状态
################################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# PID 文件
BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"
FRONTEND_PID_FILE="$SCRIPT_DIR/.frontend.pid"

# 日志文件
LOG_DIR="$SCRIPT_DIR/logs"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

print_header() {
    echo ""
    echo "=================================="
    echo "  NewsGap 服务状态"
    echo "=================================="
    echo ""
}

check_service() {
    local service_name=$1
    local pid_file=$2
    local port=$3
    
    echo -e "${BLUE}━━━ $service_name ━━━${NC}"
    
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "状态: ${GREEN}✅ 运行中${NC}"
            echo "PID: $PID"
            
            # 检查端口
            if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                echo -e "端口: ${GREEN}✅ $port (监听中)${NC}"
            else
                echo -e "端口: ${YELLOW}⚠️  $port (未监听)${NC}"
            fi
            
            # 显示进程信息
            echo "启动时间: $(ps -p $PID -o lstart= 2>/dev/null)"
            echo "CPU: $(ps -p $PID -o %cpu= 2>/dev/null | xargs)%"
            echo "内存: $(ps -p $PID -o %mem= 2>/dev/null | xargs)%"
        else
            echo -e "状态: ${RED}❌ 未运行${NC} (PID 文件存在但进程不存在)"
            echo "PID 文件: $pid_file"
        fi
    else
        echo -e "状态: ${RED}❌ 未运行${NC}"
        
        # 检查端口是否被其他进程占用
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "端口: ${YELLOW}⚠️  $port (被其他进程占用)${NC}"
            PORT_PID=$(lsof -ti:$port)
            echo "占用进程: PID $PORT_PID"
        else
            echo "端口: $port (空闲)"
        fi
    fi
    echo ""
}

show_logs() {
    echo -e "${BLUE}━━━ 最近的日志 ━━━${NC}"
    
    if [ -f "$BACKEND_LOG" ]; then
        echo ""
        echo "📋 后端日志 (最后 10 行):"
        echo "---"
        tail -n 10 "$BACKEND_LOG" 2>/dev/null || echo "无法读取日志"
        echo ""
    fi
    
    if [ -f "$FRONTEND_LOG" ]; then
        echo "📋 前端日志 (最后 10 行):"
        echo "---"
        tail -n 10 "$FRONTEND_LOG" 2>/dev/null || echo "无法读取日志"
        echo ""
    fi
}

show_urls() {
    echo -e "${BLUE}━━━ 访问地址 ━━━${NC}"
    
    # 检查后端
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "🔗 后端 API: http://localhost:8000"
        echo "📚 API 文档: http://localhost:8000/docs"
    fi
    
    # 检查前端
    if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "🌐 前端界面: http://localhost:5173"
    fi
    
    echo ""
}

show_commands() {
    echo -e "${BLUE}━━━ 常用命令 ━━━${NC}"
    echo "启动服务: ./start.sh"
    echo "停止服务: ./stop.sh"
    echo "查看状态: ./status.sh"
    echo "查看后端日志: tail -f $BACKEND_LOG"
    echo "查看前端日志: tail -f $FRONTEND_LOG"
    echo ""
}

main() {
    print_header
    check_service "后端服务" "$BACKEND_PID_FILE" 8000
    check_service "前端服务" "$FRONTEND_PID_FILE" 5173
    show_urls
    
    # 如果指定了 -v 或 --verbose，显示日志
    if [[ "$1" == "-v" || "$1" == "--verbose" ]]; then
        show_logs
    fi
    
    show_commands
}

main "$@"
