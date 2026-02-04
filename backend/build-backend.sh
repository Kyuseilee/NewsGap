#!/bin/bash
# NewsGap 后端打包脚本

set -e

echo "🚀 开始打包 NewsGap 后端..."

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version)
echo "📍 Python 版本: $PYTHON_VERSION"

# 检查是否安装了 PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 安装 PyInstaller..."
    pip3 install pyinstaller
else
    echo "✅ PyInstaller 已安装"
fi

# 清理旧的构建文件
echo "🧹 清理旧的构建文件..."
rm -rf build dist *.spec.bak

# 执行打包
echo "📦 开始打包（这可能需要几分钟）..."
python3 -m PyInstaller newsgap-backend.spec --clean

# 检查打包结果
if [ -f "dist/newsgap-backend" ]; then
    echo "✅ 打包成功！"
    echo ""
    echo "📍 可执行文件位置: dist/newsgap-backend"
    
    # 显示文件大小
    FILE_SIZE=$(du -h dist/newsgap-backend | cut -f1)
    echo "📦 文件大小: $FILE_SIZE"
    
    # 测试运行（后台运行3秒）
    echo ""
    echo "🧪 测试运行后端（3秒）..."
    ./dist/newsgap-backend &
    BACKEND_PID=$!
    sleep 3
    
    # 检查是否成功启动
    if ps -p $BACKEND_PID > /dev/null; then
        echo "✅ 后端启动成功！"
        
        # 测试 API
        if curl -s http://localhost:8000/api/config/sources > /dev/null 2>&1; then
            echo "✅ API 响应正常！"
        else
            echo "⚠️  API 未响应（可能需要更长启动时间）"
        fi
        
        # 停止后端
        kill $BACKEND_PID
        wait $BACKEND_PID 2>/dev/null || true
    else
        echo "❌ 后端启动失败"
        exit 1
    fi
    
    echo ""
    echo "🎉 打包完成！可以使用以下命令运行："
    echo "   ./dist/newsgap-backend"
else
    echo "❌ 打包失败，请检查错误信息"
    exit 1
fi
