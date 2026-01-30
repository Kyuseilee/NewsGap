#!/bin/bash
# NewsGap 停止脚本

echo "🛑 正在停止 NewsGap..."

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 停止后端
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID"
        echo -e "${GREEN}✓ 后端已停止 (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${RED}⚠ 后端进程不存在${NC}"
    fi
    rm .backend.pid
fi

# 停止前端
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID"
        echo -e "${GREEN}✓ 前端已停止 (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${RED}⚠ 前端进程不存在${NC}"
    fi
    rm .frontend.pid
fi

echo ""
echo "✅ NewsGap 已停止"
