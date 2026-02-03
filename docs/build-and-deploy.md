# 构建和部署指南

本文档详细说明 NewsGap 项目的构建、部署和发布流程。

## 目录

- [开发环境设置](#开发环境设置)
- [前端构建](#前端构建)
- [后端部署](#后端部署)
- [生产环境部署](#生产环境部署)
- [Docker 部署](#docker-部署)
- [移动端访问配置](#移动端访问配置)
- [性能优化](#性能优化)
- [故障排查](#故障排查)

---

## 开发环境设置

### 系统要求

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.10+ | 后端运行环境 |
| Node.js | 18+ | 前端构建工具 |
| npm | 9+ | 包管理器 |
| SQLite | 3.35+ | 数据库（系统自带） |

### 克隆项目

```bash
# HTTPS
git clone https://github.com/your-username/NewsGap.git

# SSH
git clone git@github.com:your-username/NewsGap.git

cd NewsGap
```

### 快速设置

```bash
# 一键部署脚本（推荐）
./deploy.sh

# 包含以下步骤：
# 1. 安装 Python 依赖
# 2. 安装 Node.js 依赖
# 3. 初始化数据库
# 4. 创建必要目录
```

### 手动设置

#### 后端环境

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 验证安装
python -c "import fastapi; print(fastapi.__version__)"
```

#### 前端环境

```bash
cd frontend

# 安装依赖
npm install

# 验证安装
npm list react typescript vite
```

---

## 前端构建

### 开发模式

```bash
cd frontend

# 启动开发服务器（热重载）
npm run dev

# 启动并允许局域网访问（移动端开发）
npm run dev -- --host

# 指定端口
npm run dev -- --port 3000
```

开发服务器配置：
- **地址**: `http://localhost:5173`
- **网络访问**: `http://[本机IP]:5173`
- **热重载**: 自动刷新
- **API 代理**: `/api` → `http://localhost:8000`

### 生产构建

```bash
cd frontend

# 类型检查 + 生产构建
npm run build

# 仅构建（跳过类型检查）
vite build

# 预览构建结果
npm run preview
```

**构建输出：**
```
frontend/dist/
├── index.html           # 入口 HTML
├── assets/
│   ├── index-[hash].js  # 主应用包（~465KB，gzip: ~143KB）
│   └── index-[hash].css # 样式文件（~22KB，gzip: ~5KB）
└── vite.svg             # 图标
```

### 构建优化

#### 分析包大小

```bash
npm run build -- --mode analyze

# 使用 vite-plugin-visualizer
npm install -D vite-plugin-visualizer
```

#### 修改 Vite 配置

**frontend/vite.config.ts**:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: '0.0.0.0',  // 允许局域网访问
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,  // 生产环境禁用
    minify: 'terser',  // 使用 Terser 压缩
    rollupOptions: {
      output: {
        manualChunks: {
          // 代码分割
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['lucide-react'],
          'query-vendor': ['@tanstack/react-query'],
        },
      },
    },
  },
})
```

---

## 后端部署

### 开发模式

```bash
cd backend
source venv/bin/activate

# 启动后端（自动重载）
python main.py

# 或使用 uvicorn（更多选项）
uvicorn main:app --reload --port 8000
```

### 生产模式

```bash
cd backend
source venv/bin/activate

# 单进程模式
python main.py --production

# 多进程模式（推荐）
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### 环境变量配置

创建 `.env` 文件：

```bash
# LLM API Keys
GEMINI_API_KEY=your-gemini-key
DEEPSEEK_API_KEY=your-deepseek-key
OPENAI_API_KEY=your-openai-key

# 代理配置（可选）
HTTP_PROXY=http://proxy.example.com:7890
HTTPS_PROXY=http://proxy.example.com:7890

# 数据库路径
DATABASE_PATH=../data/newsgap.db

# 日志级别
LOG_LEVEL=INFO

# RSSHub 地址（可选）
RSSHUB_BASE_URL=http://localhost:1200
```

加载环境变量：

```bash
# 方式 1: export
export GEMINI_API_KEY="your-key"

# 方式 2: dotenv
pip install python-dotenv
# 在 main.py 中添加：
# from dotenv import load_dotenv
# load_dotenv()

# 方式 3: 使用启动脚本
./start.sh
```

---

## 生产环境部署

### 部署架构

```
[用户] → [Nginx] → [前端静态文件]
              ↓
          [FastAPI] → [SQLite]
              ↓
          [LLM API]
```

### Nginx 配置

**安装 Nginx：**

```bash
# Ubuntu/Debian
sudo apt install nginx

# macOS
brew install nginx

# CentOS/RHEL
sudo yum install nginx
```

**配置文件** (`/etc/nginx/sites-available/newsgap`):

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    root /path/to/NewsGap/frontend/dist;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # 前端路由（SPA）
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**启用配置：**

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/newsgap /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### Systemd 服务配置

**后端服务** (`/etc/systemd/system/newsgap-backend.service`):

```ini
[Unit]
Description=NewsGap Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/NewsGap/backend
Environment="PATH=/path/to/NewsGap/backend/venv/bin"
Environment="GEMINI_API_KEY=your-key"
ExecStart=/path/to/NewsGap/backend/venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**启动服务：**

```bash
# 重载配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start newsgap-backend

# 开机自启
sudo systemctl enable newsgap-backend

# 查看状态
sudo systemctl status newsgap-backend

# 查看日志
sudo journalctl -u newsgap-backend -f
```

### SSL/TLS 配置（HTTPS）

使用 Let's Encrypt：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书并自动配置 Nginx
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## Docker 部署

### Dockerfile

**后端 Dockerfile** (`backend/Dockerfile`):

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**前端 Dockerfile** (`frontend/Dockerfile`):

```dockerfile
# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DATABASE_PATH=/data/newsgap.db
    volumes:
      - ./data:/data
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  data:
  logs:
```

**使用 Docker Compose：**

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 更新代码后重新构建
docker-compose up -d --build
```

---

## 移动端访问配置

### 1. 开发环境配置

**启用网络访问：**

```bash
cd frontend

# 临时启用（推荐开发时使用）
npm run dev -- --host

# 或修改 package.json
{
  "scripts": {
    "dev": "vite --host"
  }
}
```

### 2. 查找本机 IP

**macOS/Linux:**

```bash
# 方式 1
ifconfig | grep "inet "

# 方式 2（Wi-Fi）
ipconfig getifaddr en0

# 方式 3（有线）
ipconfig getifaddr en1
```

**Windows:**

```cmd
ipconfig
```

### 3. 防火墙配置

**macOS:**

```bash
# 允许端口 5173 和 8000
# 系统偏好设置 → 安全性与隐私 → 防火墙 → 防火墙选项
# 或使用命令行：
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/node
```

**Linux (ufw):**

```bash
sudo ufw allow 5173/tcp
sudo ufw allow 8000/tcp
sudo ufw reload
```

**Windows:**

```powershell
# 以管理员身份运行
New-NetFirewallRule -DisplayName "Vite Dev Server" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "FastAPI Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### 4. 移动端访问

**访问地址：**
- 前端: `http://[电脑IP]:5173`
- 后端 API: `http://[电脑IP]:8000/docs`

**示例：**
- 电脑 IP: `192.168.1.100`
- 手机访问: `http://192.168.1.100:5173`

### 5. 生产环境配置

修改 Nginx 配置以支持局域网/公网访问：

```nginx
server {
    listen 80;
    server_name _;  # 接受所有主机名

    # ... 其他配置
}
```

---

## 性能优化

### 前端优化

#### 1. 代码分割

```typescript
// 路由级别懒加载
const HomePage = lazy(() => import('./pages/Home'))
const ArticlesPage = lazy(() => import('./pages/Articles'))

// Suspense 包裹
<Suspense fallback={<Loading />}>
  <Routes>
    <Route path="/" element={<HomePage />} />
    <Route path="/articles" element={<ArticlesPage />} />
  </Routes>
</Suspense>
```

#### 2. 图片优化

```bash
# 安装图片压缩工具
npm install -D vite-plugin-imagemin

# vite.config.ts
import viteImagemin from 'vite-plugin-imagemin'

export default defineConfig({
  plugins: [
    viteImagemin({
      gifsicle: { optimizationLevel: 3 },
      optipng: { optimizationLevel: 7 },
      mozjpeg: { quality: 80 },
      webp: { quality: 75 },
    }),
  ],
})
```

#### 3. 打包分析

```bash
# 安装分析工具
npm install -D rollup-plugin-visualizer

# 构建并生成报告
npm run build
# 查看 dist/stats.html
```

### 后端优化

#### 1. 数据库索引

```sql
-- 为常用查询添加索引
CREATE INDEX idx_articles_published ON articles(published_at DESC);
CREATE INDEX idx_articles_industry ON articles(industry);
CREATE INDEX idx_articles_archived ON articles(archived);
```

#### 2. 连接池配置

```python
# backend/storage/db.py
import aiosqlite

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.pool_size = 20  # 连接池大小
```

#### 3. 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_sources(enabled_only: bool = False):
    # 缓存信息源列表
    pass
```

---

## 故障排查

### 前端构建失败

**问题：TypeScript 编译错误**

```bash
# 清理缓存
rm -rf node_modules package-lock.json
npm install

# 重新生成类型定义
npm run build -- --mode development
```

**问题：内存不足**

```bash
# 增加 Node.js 内存限制
NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

### 后端启动失败

**问题：端口被占用**

```bash
# 查找占用进程
lsof -i :8000
# 或
netstat -tulpn | grep 8000

# 结束进程
kill -9 <PID>
```

**问题：数据库锁定**

```bash
# 检查数据库文件权限
ls -l data/newsgap.db

# 删除锁文件
rm data/newsgap.db-journal
```

### 移动端无法访问

**检查清单：**

1. ✅ 确认设备在同一 Wi-Fi 网络
2. ✅ 使用 `--host` 启动 Vite
3. ✅ 检查防火墙设置
4. ✅ 确认 IP 地址正确
5. ✅ 尝试访问 `/api/health` 测试后端连接

### 生产环境调试

```bash
# 查看后端日志
tail -f logs/backend.log

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# 查看系统服务状态
sudo systemctl status newsgap-backend
sudo journalctl -u newsgap-backend -n 50
```

---

## 版本发布流程

### 1. 版本号管理

使用语义化版本 (SemVer):
- **主版本号**: 不兼容的 API 变更
- **次版本号**: 向下兼容的功能新增
- **修订号**: 向下兼容的问题修正

### 2. 发布清单

- [ ] 更新 `CHANGELOG.md`
- [ ] 运行完整测试套件
- [ ] 更新文档
- [ ] 创建 Git 标签
- [ ] 构建生产版本
- [ ] 部署到服务器
- [ ] 验证部署
- [ ] 发布 Release Notes

### 3. 发布命令

```bash
# 1. 确保在 master 分支
git checkout master
git pull origin master

# 2. 更新版本号
# 编辑 package.json 和相关文件

# 3. 提交变更
git add .
git commit -m "chore: release v0.1.0"

# 4. 创建标签
git tag -a v0.1.0 -m "Release version 0.1.0"

# 5. 推送
git push origin master
git push origin v0.1.0

# 6. 构建和部署
./deploy.sh
```

---

## 相关资源

- [Vite 官方文档](https://vitejs.dev/)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)
- [Nginx 配置文档](https://nginx.org/en/docs/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Let's Encrypt 文档](https://letsencrypt.org/docs/)

---

**最后更新**: 2026-02-03  
**维护者**: NewsGap Team
