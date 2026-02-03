# 📦 NewsGap 一键部署功能说明

## ✅ 已完成的封装

我已经为 NewsGap 创建了完整的一键部署和运行脚本，让你不再需要分开窗口管理前后端服务。

---

## 🎯 核心脚本

### 1. `./deploy.sh` - 一键部署脚本

**功能**：首次部署时使用，自动完成所有初始化工作

**执行内容**：
- ✅ 检查系统依赖（Python、Node.js、npm）
- ✅ 创建 Python 虚拟环境
- ✅ 安装后端依赖（pip install）
- ✅ 安装前端依赖（npm install）
- ✅ 初始化数据库（创建 schema）
- ✅ 创建必要的目录结构
- ✅ 设置脚本执行权限

**使用方法**：
```bash
./deploy.sh
```

---

### 2. `./start.sh` - 一键启动脚本

**功能**：同时启动前后端服务，后台运行

**执行内容**：
- ✅ 停止已存在的旧服务
- ✅ 检查并释放端口（8000, 5173）
- ✅ 启动后端服务（http://localhost:8000）
- ✅ 启动前端服务（http://localhost:5173）
- ✅ 等待服务启动完成
- ✅ 显示访问地址和日志位置

**特点**：
- 🔥 **后台运行**：不占用终端窗口
- 📝 **日志输出**：自动记录到 `logs/` 目录
- 🔄 **自动重启**：如果有旧服务，自动停止并重启
- ⚡ **快速启动**：30 秒内完成

**使用方法**：
```bash
./start.sh
```

**输出示例**：
```
==================================
✅ NewsGap 已成功启动！
==================================

📊 服务信息：
  - 后端: http://localhost:8000
  - 前端: http://localhost:5173
  - API文档: http://localhost:8000/docs

📝 进程信息：
  - 后端 PID: 12345
  - 前端 PID: 12346

📋 日志文件：
  - 后端: logs/backend.log
  - 前端: logs/frontend.log

💡 使用说明：
  - 查看日志: tail -f logs/backend.log
  - 停止服务: ./stop.sh
  - 查看状态: ./status.sh

🌐 现在可以在浏览器中访问: http://localhost:5173
```

---

### 3. `./stop.sh` - 一键停止脚本

**功能**：停止所有运行中的服务

**执行内容**：
- ✅ 停止后端进程
- ✅ 停止前端进程
- ✅ 强制释放端口（如果需要）
- ✅ 清理 PID 文件

**使用方法**：
```bash
./stop.sh
```

---

### 4. `./status.sh` - 状态查看脚本

**功能**：查看服务运行状态和日志

**执行内容**：
- ✅ 检查后端服务状态
- ✅ 检查前端服务状态
- ✅ 显示进程 PID 和资源占用
- ✅ 显示端口监听情况
- ✅ 显示访问地址
- ✅ 显示常用命令

**使用方法**：
```bash
# 查看状态
./status.sh

# 查看状态 + 最近日志
./status.sh -v
```

**输出示例**：
```
==================================
  NewsGap 服务状态
==================================

━━━ 后端服务 ━━━
状态: ✅ 运行中
PID: 12345
端口: ✅ 8000 (监听中)
启动时间: Mon Feb  3 14:16:00 2026
CPU: 2.5%
内存: 3.2%

━━━ 前端服务 ━━━
状态: ✅ 运行中
PID: 12346
端口: ✅ 5173 (监听中)
启动时间: Mon Feb  3 14:16:05 2026
CPU: 0.8%
内存: 1.5%

━━━ 访问地址 ━━━
🔗 后端 API: http://localhost:8000
📚 API 文档: http://localhost:8000/docs
🌐 前端界面: http://localhost:5173
```

---

## 📂 目录结构

```
NewsGap/
├── start.sh          # ⭐ 一键启动脚本
├── stop.sh           # 🛑 一键停止脚本
├── status.sh         # 📊 状态查看脚本
├── deploy.sh         # 📦 一键部署脚本
├── .backend.pid      # 后端进程 PID（自动生成）
├── .frontend.pid     # 前端进程 PID（自动生成）
├── logs/             # 📝 日志目录
│   ├── backend.log   # 后端日志
│   ├── frontend.log  # 前端日志
│   └── .gitkeep
├── backend/          # 后端代码
│   ├── venv/         # Python 虚拟环境（自动创建）
│   ├── data/         # 数据库文件
│   ├── config/       # 配置文件
│   └── ...
└── frontend/         # 前端代码
    ├── node_modules/ # npm 依赖（自动安装）
    └── ...
```

---

## 🚀 完整使用流程

### 首次部署

```bash
# 1. 克隆项目
git clone <repository-url>
cd NewsGap

# 2. 一键部署（安装依赖、初始化数据库）
./deploy.sh

# 3. 启动服务
./start.sh

# 4. 在浏览器中访问
open http://localhost:5173
```

### 日常使用

```bash
# 启动
./start.sh

# 查看状态
./status.sh

# 停止
./stop.sh
```

---

## 💡 特色功能

### 1. 智能端口管理

- ✅ 自动检测端口占用
- ✅ 自动释放被占用的端口
- ✅ 避免端口冲突

### 2. 进程管理

- ✅ 后台运行（daemon 模式）
- ✅ PID 文件管理
- ✅ 优雅停止（SIGTERM → SIGKILL）
- ✅ 自动清理僵尸进程

### 3. 日志管理

- ✅ 分离的前后端日志
- ✅ 持久化日志文件
- ✅ 实时日志查看：`tail -f logs/backend.log`
- ✅ 日志轮转（自动清理旧日志）

### 4. 错误处理

- ✅ 详细的错误提示
- ✅ 彩色输出（成功/警告/错误）
- ✅ 自动回滚（部署失败时）
- ✅ 超时保护（30秒启动超时）

### 5. 开发友好

- ✅ 支持热重载（Vite HMR）
- ✅ 虚拟环境自动管理
- ✅ 依赖自动安装
- ✅ 数据库自动初始化

---

## 📋 常见操作

### 查看实时日志

```bash
# 后端日志
tail -f logs/backend.log

# 前端日志
tail -f logs/frontend.log

# 同时查看（使用 tmux 或多个终端）
tmux new -s logs
tmux split-window -h
# 左侧: tail -f logs/backend.log
# 右侧: tail -f logs/frontend.log
```

### 重启服务

```bash
# 方法1：停止后启动
./stop.sh && ./start.sh

# 方法2：直接启动（自动停止旧服务）
./start.sh
```

### 仅启动后端

```bash
cd backend
source venv/bin/activate
python3 main.py
```

### 仅启动前端

```bash
cd frontend
npm run dev
```

---

## 🔧 故障排查

### 问题1：启动失败

**症状**：`./start.sh` 执行后报错

**排查**：
```bash
# 1. 查看详细状态
./status.sh -v

# 2. 检查日志
tail -n 50 logs/backend.log
tail -n 50 logs/frontend.log

# 3. 检查端口
lsof -i :8000
lsof -i :5173
```

### 问题2：端口被占用

**症状**：提示端口 8000 或 5173 被占用

**解决**：
```bash
# 手动释放端口
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9

# 重新启动
./start.sh
```

### 问题3：服务状态异常

**症状**：PID 文件存在但进程不存在

**解决**：
```bash
# 清理 PID 文件
rm -f .backend.pid .frontend.pid

# 强制停止并重启
./stop.sh
./start.sh
```

### 问题4：日志文件过大

**解决**：
```bash
# 清理日志
rm logs/*.log

# 或保留最近的日志
tail -n 1000 logs/backend.log > logs/backend.log.tmp
mv logs/backend.log.tmp logs/backend.log
```

---

## 🎨 进阶配置

### 修改端口

编辑 `start.sh`，找到以下行并修改：

```bash
# 后端端口（默认 8000）
# 在 backend/main.py 中修改
port=8000

# 前端端口（默认 5173）
# 在 frontend/vite.config.ts 中修改
port=5173
```

### 修改日志路径

编辑 `start.sh`：

```bash
LOG_DIR="$SCRIPT_DIR/logs"  # 修改为其他路径
```

### 添加启动参数

编辑 `start.sh`，在启动命令中添加参数：

```bash
# 后端
nohup python3 main.py --port 8000 --host 0.0.0.0 > "$BACKEND_LOG" 2>&1 &

# 前端
nohup npm run dev -- --port 5173 --host 0.0.0.0 > "$FRONTEND_LOG" 2>&1 &
```

---

## 📚 相关文档

- **快速开始**: [QUICK_START.md](QUICK_START.md)
- **项目说明**: [README.md](README.md)
- **报告修复**: [REPORT_TRUNCATION_FIX.md](REPORT_TRUNCATION_FIX.md)
- **后端重启**: [RESTART_BACKEND.md](RESTART_BACKEND.md)

---

## ✨ 总结

现在你可以：

✅ **一键部署**：`./deploy.sh` - 首次使用  
✅ **一键启动**：`./start.sh` - 启动前后端  
✅ **一键停止**：`./stop.sh` - 停止所有服务  
✅ **一键查看**：`./status.sh` - 查看运行状态  

**不再需要**：
- ❌ 打开多个终端窗口
- ❌ 手动管理进程 PID
- ❌ 记忆复杂的启动命令
- ❌ 担心端口冲突

**享受全自动化的开发体验！** 🚀
