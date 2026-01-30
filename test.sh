#!/bin/bash
# NewsGap 快速测试脚本

echo "======================================"
echo "NewsGap 系统测试"
echo "======================================"
echo ""

# 检查 RSSHub
echo "[1/4] 检查 RSSHub 状态..."
if curl -s http://localhost:1200/ > /dev/null; then
    echo "✓ RSSHub 运行正常"
else
    echo "✗ RSSHub 未运行，请执行: docker-compose up -d"
    exit 1
fi
echo ""

# 检查信息源
echo "[2/4] 检查信息源配置..."
cd backend
SOURCE_COUNT=$(./venv/bin/python3 -c "
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from storage.database import Database

async def count():
    db = Database()
    await db.initialize()
    sources = await db.get_sources(enabled_only=True)
    print(len(sources))

asyncio.run(count())
" 2>/dev/null)

if [ "$SOURCE_COUNT" -gt 0 ]; then
    echo "✓ 发现 $SOURCE_COUNT 个信息源"
else
    echo "⚠ 需要初始化信息源"
    echo "  执行: ./venv/bin/python3 setup_sources.py"
fi
echo ""

# 检查后端依赖
echo "[3/4] 检查后端依赖..."
if ./venv/bin/python3 -c "import fastapi, httpx, feedparser" 2>/dev/null; then
    echo "✓ 后端依赖完整"
else
    echo "✗ 缺少依赖，请执行: pip install -r requirements.txt"
    exit 1
fi
echo ""

# 检查前端
echo "[4/4] 检查前端..."
cd ../frontend
if [ -d "node_modules" ]; then
    echo "✓ 前端依赖已安装"
else
    echo "⚠ 需要安装前端依赖: npm install"
fi
echo ""

echo "======================================"
echo "✅ 系统检查完成！"
echo "======================================"
echo ""
echo "启动命令:"
echo "  后端: cd backend && ./venv/bin/python3 main.py"
echo "  前端: cd frontend && npm run dev"
echo ""
echo "访问地址:"
echo "  前端: http://localhost:5173"
echo "  后端: http://localhost:8000"
echo "  RSSHub: http://localhost:1200"
echo ""
