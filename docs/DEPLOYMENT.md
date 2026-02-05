# NewsGap 生产环境部署指南

本文档详细说明如何将 NewsGap 部署到生产服务器。

---

## 📋 前置要求

### 服务器配置
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **内存**: 至少 2GB RAM
- **磁盘**: 至少 10GB 可用空间
- **网络**: 公网IP或域名

### 软件依赖
- Python 3.10+
- Node.js 18+
- Nginx
- Docker (可选，用于RSSHub)

### 网络要求
- 开放端口 80 (HTTP)
- 开放端口 443 (HTTPS，可选)

---

## 🚀 快速部署（推荐）

### 步骤 1: 克隆项目

```bash
# 切换到server分支
git clone -b server https://github.com/Kyuseilee/NewsGap.git
cd NewsGap
```

### 步骤 2: 运行部署脚本

```bash
# 赋予执行权限
chmod +x deploy-production.sh

# 运行部署脚本（会提示输入域名或IP）
./deploy-production.sh
```

脚本会自动完成：
- ✅ 安装系统依赖
- ✅ 安装项目依赖
- ✅ 构建前端
- ✅ 配置Nginx
- ✅ 配置systemd
- ✅ 启动服务

### 步骤 3: 配置 API Keys

编辑后端环境变量文件：

```bash
nano backend/.env
```

至少配置一个LLM的API Key：

```bash
# 推荐：Gemini（免费额度大）
GEMINI_API_KEY=your-gemini-api-key

# 或者：DeepSeek（性价比高）
DEEPSEEK_API_KEY=your-deepseek-api-key

# 或者：OpenAI
OPENAI_API_KEY=your-openai-api-key
```

### 步骤 4: 重启后端服务

```bash
sudo systemctl restart newsgap-backend
```

### 步骤 5: 访问应用

打开浏览器访问：
- **HTTP**: `http://your-domain.com` 或 `http://your-server-ip`
- **API文档**: `http://your-domain.com/api/docs`

---

## 🔧 手动部署

如果自动脚本遇到问题，可以按照以下步骤手动部署。

### 1. 安装系统依赖

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip \
                     nodejs npm nginx curl git
```

#### CentOS/RHEL

```bash
sudo yum install -y python3 python3-pip nodejs nginx curl git
```

### 2. 克隆项目

```bash
git clone -b server https://github.com/Kyuseilee/NewsGap.git
cd NewsGap
```

### 3. 安装项目依赖

#### 后端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..
```

#### 前端

```bash
cd frontend
npm install
cd ..
```

### 4. 配置环境变量

#### 后端环境变量

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

填入API Keys和其他配置。

#### 前端环境变量

```bash
# 使用Nginx反向代理时（推荐）
echo 'VITE_API_BASE_URL=/api' > frontend/.env.production

# 或者直接指定后端地址
# echo 'VITE_API_BASE_URL=http://your-server-ip:8000' > frontend/.env.production
```

### 5. 构建前端

```bash
cd frontend
npm run build
cd ..
```

验证构建产物：

```bash
ls -la frontend/dist/
```

### 6. 配置 Nginx

创建Nginx配置文件：

```bash
sudo nano /etc/nginx/sites-available/newsgap
```

粘贴以下内容（记得修改路径和域名）：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 修改为你的域名或IP
    
    access_log /var/log/nginx/newsgap-access.log;
    error_log /var/log/nginx/newsgap-error.log;
    
    # 前端静态文件
    location / {
        root /path/to/NewsGap/frontend/dist;  # 修改为实际路径
        try_files $uri $uri/ /index.html;
        
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # 后端API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        proxy_cache_bypass $http_upgrade;
    }
    
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
```

启用站点并测试：

```bash
sudo ln -s /etc/nginx/sites-available/newsgap /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. 配置 systemd 服务

创建服务文件：

```bash
sudo nano /etc/systemd/system/newsgap-backend.service
```

粘贴以下内容（修改路径和用户名）：

```ini
[Unit]
Description=NewsGap Backend Service
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
Group=YOUR_USERNAME
WorkingDirectory=/path/to/NewsGap/backend
Environment="PATH=/path/to/NewsGap/backend/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="ENV=production"
EnvironmentFile=-/path/to/NewsGap/backend/.env

ExecStart=/path/to/NewsGap/backend/venv/bin/python main.py

Restart=always
RestartSec=10

StandardOutput=append:/var/log/newsgap/backend.log
StandardError=append:/var/log/newsgap/backend-error.log

[Install]
WantedBy=multi-user.target
```

创建日志目录并启动服务：

```bash
sudo mkdir -p /var/log/newsgap
sudo chown -R $USER:$USER /var/log/newsgap

sudo systemctl daemon-reload
sudo systemctl enable newsgap-backend
sudo systemctl start newsgap-backend
sudo systemctl status newsgap-backend
```

### 8. 配置防火墙

#### Ubuntu/Debian (ufw)

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

#### CentOS/RHEL (firewalld)

```bash
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

### 9. 启动 RSSHub（可选）

```bash
./docker.sh start
```

---

## 🔒 配置 HTTPS（推荐）

使用 Let's Encrypt 免费SSL证书：

### 1. 安装 Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

### 2. 获取证书

```bash
sudo certbot --nginx -d your-domain.com
```

按提示操作，Certbot会自动配置Nginx。

### 3. 测试自动续期

```bash
sudo certbot renew --dry-run
```

证书会在过期前自动续期。

---

## 📊 服务管理

### 查看服务状态

```bash
# 后端服务
sudo systemctl status newsgap-backend

# Nginx
sudo systemctl status nginx

# RSSHub Docker
docker ps | grep rsshub
```

### 查看日志

```bash
# 后端实时日志
sudo journalctl -u newsgap-backend -f

# 后端日志文件
tail -f /var/log/newsgap/backend.log

# Nginx访问日志
tail -f /var/log/nginx/newsgap-access.log

# Nginx错误日志
tail -f /var/log/nginx/newsgap-error.log

# RSSHub日志
./docker.sh logs
```

### 重启服务

```bash
# 重启后端
sudo systemctl restart newsgap-backend

# 重载Nginx（不中断连接）
sudo systemctl reload nginx

# 重启Nginx
sudo systemctl restart nginx

# 重启RSSHub
./docker.sh restart
```

### 停止服务

```bash
# 停止后端
sudo systemctl stop newsgap-backend

# 停止Nginx
sudo systemctl stop nginx

# 停止RSSHub
./docker.sh stop
```

---

## 🔧 故障排查

### 问题1: 前端可以访问，但API调用失败

**症状**: 浏览器控制台显示CORS错误或404错误

**解决方案**:

1. 检查后端是否运行：
   ```bash
   sudo systemctl status newsgap-backend
   curl http://localhost:8000/health
   ```

2. 检查Nginx配置：
   ```bash
   sudo nginx -t
   cat /etc/nginx/sites-enabled/newsgap
   ```

3. 检查后端日志：
   ```bash
   sudo journalctl -u newsgap-backend -n 50
   ```

### 问题2: 后端服务无法启动

**症状**: `systemctl status newsgap-backend` 显示失败

**解决方案**:

1. 查看详细错误：
   ```bash
   sudo journalctl -u newsgap-backend -n 100 --no-pager
   ```

2. 检查Python环境：
   ```bash
   cd backend
   source venv/bin/activate
   python main.py  # 手动启动查看错误
   ```

3. 检查端口占用：
   ```bash
   sudo lsof -i :8000
   ```

### 问题3: 前端构建失败

**症状**: `npm run build` 报错

**解决方案**:

1. 清除缓存重新安装：
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

2. 检查Node.js版本：
   ```bash
   node --version  # 需要18+
   ```

### 问题4: Nginx 404错误

**症状**: 访问页面显示404 Not Found

**解决方案**:

1. 检查前端dist目录：
   ```bash
   ls -la frontend/dist/
   ```

2. 检查Nginx配置中的root路径：
   ```bash
   grep "root" /etc/nginx/sites-enabled/newsgap
   ```

3. 检查文件权限：
   ```bash
   sudo chmod -R 755 frontend/dist
   ```

### 问题5: PDF导出报错

**症状**: 导出PDF时后端报错"reportlab not installed"

**解决方案**:

```bash
cd backend
source venv/bin/activate
pip install reportlab markdown
deactivate
sudo systemctl restart newsgap-backend
```

---

## 🔄 更新部署

当代码更新后，使用以下步骤重新部署：

```bash
# 1. 拉取最新代码
git pull origin server

# 2. 更新后端依赖（如果requirements.txt有变化）
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# 3. 更新前端依赖（如果package.json有变化）
cd frontend
npm install
npm run build
cd ..

# 4. 重启后端服务
sudo systemctl restart newsgap-backend

# 5. 重载Nginx（如果需要）
sudo systemctl reload nginx
```

---

## 📈 性能优化

### 1. 启用Gzip压缩

编辑 `/etc/nginx/nginx.conf`：

```nginx
http {
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss;
}
```

### 2. 配置Redis缓存（可选）

安装Redis：

```bash
sudo apt install redis-server
```

修改 `docker-compose.yml` 启用Redis：

```yaml
services:
  redis:
    image: redis:alpine
    restart: unless-stopped
    volumes:
      - redis-data:/data
    networks:
      - newsgap-network

  rsshub:
    environment:
      REDIS_URL: redis://redis:6379/
```

重启Docker服务：

```bash
./docker.sh restart
```

### 3. 数据库定期备份

创建备份脚本 `backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/backups/newsgap"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp backend/data/newsgap.db "$BACKUP_DIR/newsgap_$DATE.db"

# 保留最近30天的备份
find $BACKUP_DIR -name "newsgap_*.db" -mtime +30 -delete
```

添加到crontab（每天凌晨2点备份）：

```bash
crontab -e
# 添加：
0 2 * * * /path/to/NewsGap/backup.sh
```

---

## 🆘 获取帮助

如果遇到问题：

1. 查看日志文件
2. 查看 [GitHub Issues](https://github.com/Kyuseilee/NewsGap/issues)
3. 提交新Issue（附带日志和错误信息）

---

## 📚 相关文档

- [README.md](../README.md) - 项目介绍
- [质量跟踪系统设计](./quality_tracking_design.md) - 高级功能设计
- [Backend文档](../backend/README.md) - 后端详细文档
- [Frontend文档](../frontend/README.md) - 前端详细文档

---

**最后更新**: 2026-02-05  
**版本**: v1.0  
**分支**: server
