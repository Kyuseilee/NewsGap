#!/bin/bash
# NewsGap 快速启动脚本

echo "🚀 NewsGap 启动中..."
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. 启动后端
echo -e "${BLUE}📦 启动后端服务...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 虚拟环境不存在，请先运行: python3 -m venv venv${NC}"
    exit 1
fi

# 激活虚拟环境并启动后端
./venv/bin/python3 main.py > ../backend.log 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}✓ 后端已启动 (PID: $BACKEND_PID)${NC}"
echo -e "  访问: ${BLUE}http://localhost:8000${NC}"
echo -e "  日志: ${YELLOW}backend.log${NC}"
echo ""

# 等待后端启动
sleep 3

# 2. 启动前端
echo -e "${BLUE}🎨 启动前端服务...${NC}"
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  依赖未安装，正在安装...${NC}"
    npm install
fi

npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}✓ 前端已启动 (PID: $FRONTEND_PID)${NC}"
echo -e "  访问: ${BLUE}http://localhost:5173${NC}"
echo -e "  日志: ${YELLOW}frontend.log${NC}"
echo ""

# 3. 保存 PID
cd ..
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# 4. 打印启动信息
echo ""
echo -e "${GREEN}✨ NewsGap 已成功启动！${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  后端API:  ${BLUE}http://localhost:8000${NC}"
echo -e "  前端界面: ${BLUE}http://localhost:5173${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}提示:${NC}"
echo "  - 查看后端日志: tail -f backend.log"
echo "  - 查看前端日志: tail -f frontend.log"
echo "  - 停止服务: ./stop.sh"
echo ""
