# 📖 NewsGap 使用示例

## 场景 1：新用户首次使用

### 步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd NewsGap

# 2. 一键部署
./deploy.sh

# 输出示例：
# ==================================
#   NewsGap 一键部署脚本
# ==================================
# 
# ━━━ 1. 检查系统依赖 ━━━
# ✅ Python 版本: 3.10.6
# ✅ Node.js 版本: v18.17.0
# ✅ npm 版本: 9.6.7
# 
# ━━━ 2. 安装后端依赖 ━━━
# ✅ Python 依赖安装完成
# 
# ━━━ 3. 安装前端依赖 ━━━
# ✅ npm 依赖安装完成
# 
# ━━━ 4. 初始化数据库 ━━━
# ✅ 数据库创建完成

# 3. 启动服务
./start.sh

# 输出示例：
# ==================================
# ✅ NewsGap 已成功启动！
# ==================================
# 
# 📊 服务信息：
#   - 后端: http://localhost:8000
#   - 前端: http://localhost:5173
#   - API文档: http://localhost:8000/docs
# 
# 🌐 现在可以在浏览器中访问: http://localhost:5173
```

### 配置 API Key

1. 在浏览器打开 http://localhost:5173
2. 点击右上角 **设置** 图标
3. 选择 **API Keys**
4. 输入你的 Gemini API Key
5. 点击 **保存**

### 运行第一次分析

1. 回到首页
2. 选择行业：**游戏电竞**
3. 时间范围：**24 小时**
4. LLM 后端：**Gemini**
5. 点击 **⚡ 一键情报**
6. 等待 20-40 秒，自动跳转到分析报告

---

## 场景 2：日常开发

### 早上开始工作

```bash
cd NewsGap

# 启动服务（一条命令）
./start.sh

# 打开浏览器
open http://localhost:5173

# 开始使用...
```

### 查看服务状态

```bash
# 快速查看
./status.sh

# 输出：
# ━━━ 后端服务 ━━━
# 状态: ✅ 运行中
# PID: 12345
# 
# ━━━ 前端服务 ━━━
# 状态: ✅ 运行中
# PID: 12346
```

### 查看日志

```bash
# 实时查看后端日志
tail -f logs/backend.log

# 输出示例：
# INFO: 开始 Gemini 分析，文章数量: 50
# INFO: Gemini 响应长度: 8934 字符
# INFO: Finish reason: 1
# INFO: 分析完成，耗时: 23.45秒
```

### 下班停止服务

```bash
./stop.sh

# 输出：
# ==================================
#   NewsGap 一键停止脚本
# ==================================
# 
# [INFO] 停止后端服务 (PID: 12345)...
# ✅ 后端服务已停止
# [INFO] 停止前端服务 (PID: 12346)...
# ✅ 前端服务已停止
# 
# ✅ 所有服务已停止
```

---

## 场景 3：修改代码后重启

### 修改后端代码

```bash
# 1. 修改代码
vi backend/llm/gemini_adapter.py

# 2. 重启服务（自动停止旧服务）
./start.sh

# 新配置立即生效！
```

### 修改前端代码

```bash
# 1. 修改代码
vi frontend/src/pages/Home.tsx

# 2. 保存文件

# Vite 会自动热重载，无需重启！
# 浏览器会自动刷新
```

---

## 场景 4：故障排查

### 问题：启动失败

```bash
# 1. 查看详细状态
./status.sh -v

# 输出会显示：
# - 服务运行状态
# - 端口占用情况
# - 最近的日志内容

# 2. 查看完整日志
tail -n 100 logs/backend.log

# 3. 强制停止并重启
./stop.sh
./start.sh
```

### 问题：端口被占用

```bash
# 查看谁占用了端口
lsof -i :8000
lsof -i :5173

# 输出示例：
# COMMAND   PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
# Python  44093  roson   12u  IPv4 ...      0t0  TCP *:8000 (LISTEN)

# 停止占用端口的进程
kill 44093

# 重新启动
./start.sh
```

---

## 场景 5：生产环境部署

### 使用 systemd（Linux）

```bash
# 1. 创建 systemd 服务文件
sudo vi /etc/systemd/system/newsgap-backend.service

# 内容：
[Unit]
Description=NewsGap Backend Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/NewsGap/backend
ExecStart=/path/to/NewsGap/backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target

# 2. 启动服务
sudo systemctl enable newsgap-backend
sudo systemctl start newsgap-backend

# 3. 查看状态
sudo systemctl status newsgap-backend
```

### 使用 PM2（Node.js 进程管理器）

```bash
# 1. 安装 PM2
npm install -g pm2

# 2. 创建配置文件
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [
    {
      name: 'newsgap-backend',
      cwd: './backend',
      script: 'venv/bin/python',
      args: 'main.py',
      env: {
        GEMINI_API_KEY: 'your-api-key'
      }
    },
    {
      name: 'newsgap-frontend',
      cwd: './frontend',
      script: 'npm',
      args: 'run dev'
    }
  ]
}
EOF

# 3. 启动
pm2 start ecosystem.config.js

# 4. 查看状态
pm2 status

# 5. 查看日志
pm2 logs

# 6. 设置开机自启
pm2 startup
pm2 save
```

---

## 场景 6：Docker 部署

### 使用 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/data:/app/data
      - ./backend/config:/app/config
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
    restart: unless-stopped
```

```bash
# 启动
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

---

## 场景 7：性能优化

### 查看资源占用

```bash
# 使用 status.sh 查看
./status.sh

# 输出包含：
# CPU: 2.5%
# 内存: 3.2%
```

### 优化内存占用

```bash
# 限制 Python 进程内存
export PYTHONMALLOC=malloc

# 重启服务
./stop.sh && ./start.sh
```

### 清理日志文件

```bash
# 保留最近 1000 行
tail -n 1000 logs/backend.log > logs/backend.log.tmp
mv logs/backend.log.tmp logs/backend.log

tail -n 1000 logs/frontend.log > logs/frontend.log.tmp
mv logs/frontend.log.tmp logs/frontend.log
```

---

## 场景 8：数据备份

### 备份数据库

```bash
# 创建备份
cp backend/data/newsgap.db backend/data/newsgap.db.backup.$(date +%Y%m%d_%H%M%S)

# 定时备份（crontab）
crontab -e

# 添加：
# 每天凌晨 2 点备份
0 2 * * * cp /path/to/NewsGap/backend/data/newsgap.db /path/to/backups/newsgap.db.$(date +\%Y\%m\%d)
```

### 恢复数据库

```bash
# 停止服务
./stop.sh

# 恢复备份
cp backend/data/newsgap.db.backup.20260203 backend/data/newsgap.db

# 重启服务
./start.sh
```

---

## 场景 9：多环境管理

### 开发环境

```bash
# 使用开发配置
export ENV=development
./start.sh
```

### 生产环境

```bash
# 使用生产配置
export ENV=production
./start.sh
```

### 测试环境

```bash
# 使用测试数据库
export DB_PATH=./data/test.db
./start.sh
```

---

## 场景 10：团队协作

### 提交代码前

```bash
# 1. 停止服务
./stop.sh

# 2. 清理临时文件
rm -rf logs/*.log
rm -f .backend.pid .frontend.pid

# 3. 提交代码
git add .
git commit -m "feat: 添加新功能"
git push
```

### 拉取最新代码后

```bash
# 1. 拉取代码
git pull

# 2. 重新部署（如果有依赖更新）
./deploy.sh

# 3. 启动服务
./start.sh
```

---

## 💡 实用技巧

### 快速重启

```bash
# 一行命令
./stop.sh && ./start.sh
```

### 后台查看日志

```bash
# 使用 tmux 分屏
tmux new -s newsgap
tmux split-window -h
# 左侧: tail -f logs/backend.log
# 右侧: tail -f logs/frontend.log

# 退出 tmux: Ctrl+B, D
# 重新进入: tmux attach -s newsgap
```

### 快速查看错误

```bash
# 只看错误日志
grep -i error logs/backend.log
grep -i error logs/frontend.log
```

### 监控服务健康

```bash
# 每 5 秒检查一次
watch -n 5 "./status.sh"
```

---

## 📚 更多资源

- [快速开始指南](QUICK_START.md)
- [部署总结](DEPLOYMENT_SUMMARY.md)
- [项目文档](README.md)

享受使用 NewsGap！🎉
