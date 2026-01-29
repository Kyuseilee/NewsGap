#!/bin/bash

# NewsGap 后端安装和测试脚本

set -e  # 遇到错误立即退出

echo "=================================="
echo "NewsGap 后端安装和测试"
echo "=================================="
echo ""

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ 错误：请先激活虚拟环境"
    echo "   运行: source venv/bin/activate"
    exit 1
fi

echo "✓ 虚拟环境已激活: $VIRTUAL_ENV"
echo ""

# 安装依赖
echo "步骤 1: 安装依赖包..."
echo "=================================="
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "步骤 2: 验证关键包..."
echo "=================================="

python3 << 'EOF'
import sys

packages = [
    ('fastapi', 'FastAPI'),
    ('uvicorn', 'Uvicorn'),
    ('aiosqlite', 'aiosqlite'),
    ('httpx', 'httpx'),
    ('feedparser', 'feedparser'),
    ('pydantic', 'Pydantic'),
]

all_ok = True
for module, name in packages:
    try:
        __import__(module)
        print(f"✓ {name}")
    except ImportError:
        print(f"✗ {name} - 未安装")
        all_ok = False

if not all_ok:
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 部分依赖安装失败"
    exit 1
fi

echo ""
echo "步骤 3: 运行快速测试..."
echo "=================================="
python3 test_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ 安装和测试完成！"
    echo "=================================="
    echo ""
    echo "现在可以启动服务器:"
    echo "  python3 main.py"
    echo ""
    echo "或在后台运行:"
    echo "  nohup python3 main.py > server.log 2>&1 &"
else
    echo ""
    echo "❌ 测试失败"
    exit 1
fi
