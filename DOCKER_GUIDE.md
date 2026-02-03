# 🐳 NewsGap Docker 部署指南

## 📋 概述

NewsGap 支持通过 Docker 部署 RSSHub 服务，提供本地 RSS 源聚合能力。

---

## 🚀 快速开始

### 方式一：部署时自动安装（推荐）

```bash
# 运行部署脚本时会询问是否部署 Docker
./deploy.sh

# 按提示选择 Y 即可自动部署 RSSHub
```

### 方式二：手动部署

```bash
# 启动 RSSHub
./docker.sh start

# 查看状态
./docker.sh status

# 查看日志
./docker.sh logs
```

---

## 📦 Docker 服务说明

### RSSHub 服务

- **镜像**: `diygod/rsshub:latest`
- **端口**: 1200
- **访问地址**: http://localhost:1200
- **文档**: http://localhost:1200/docs

### 功能

- ✅ 聚合各种网站的 RSS 订阅源
- ✅ 支持数百个网站和服务
- ✅ 自动缓存，提升性能
- ✅ 支持自定义路由

---

## 🔧 Docker 命令

### 基本操作

```bash
# 启动服务
./docker.sh start

# 停止服务
./docker.sh stop

# 重启服务
./docker.sh restart

# 查看状态
./docker.sh status

# 查看日志（实时）
./docker.sh logs
```

### 高级操作

```bash
# 更新到最新版本
./docker.sh update

# 清理容器和镜像
./docker.sh clean

# 查看帮助
./docker.sh help
```

---

## 📊 服务状态检查

### 检查容器状态

```bash
./docker.sh status
```

**输出示例**：
```
━━━ 容器状态 ━━━
newsgap-rsshub   Up 2 hours   0.0.0.0:1200->1200/tcp

━━━ 服务健康检查 ━━━
✅ RSSHub 服务运行正常
访问地址: http://localhost:1200
```

### 使用 Docker 原生命令

```bash
# 查看容器列表
docker ps

# 查看容器日志
docker logs newsgap-rsshub

# 查看容器详情
docker inspect newsgap-rsshub

# 进入容器
docker exec -it newsgap-rsshub sh
```

---

## 🌐 RSSHub 使用示例

### 1. 访问 RSSHub 首页

打开浏览器访问：http://localhost:1200

### 2. 查看 API 文档

访问：http://localhost:1200/docs

### 3. 使用 RSS 路由

#### GitHub Trending

```
http://localhost:1200/github/trending/daily
http://localhost:1200/github/trending/daily/python
```

#### 微博热搜

```
http://localhost:1200/weibo/search/hot
```

#### 知乎热榜

```
http://localhost:1200/zhihu/hotlist
```

#### B站热门

```
http://localhost:1200/bilibili/ranking/0/3/1
```

### 4. 在 NewsGap 中使用

进入 NewsGap 前端 → 设置 → 信息源管理

添加信息源时，使用 `http://localhost:1200` 作为 RSSHub 地址：

```
名称: GitHub Python Trending
URL: http://localhost:1200/github/trending/daily/python
类型: RSS
分类: developer
```

---

## ⚙️ 配置说明

### docker-compose.yml

```yaml
version: '3.8'

services:
  rsshub:
    image: diygod/rsshub:latest
    container_name: newsgap-rsshub
    restart: unless-stopped
    ports:
      - "1200:1200"
    environment:
      NODE_ENV: production
      CACHE_TYPE: memory
    networks:
      - newsgap-network
```

### 自定义配置

编辑 `docker-compose.yml` 可以修改：

#### 1. 修改端口

```yaml
ports:
  - "3000:1200"  # 宿主机端口:容器端口
```

#### 2. 添加 Redis 缓存

取消注释 Redis 服务：

```yaml
services:
  rsshub:
    environment:
      CACHE_TYPE: redis
      REDIS_URL: redis://redis:6379/
  
  redis:
    image: redis:alpine
    container_name: newsgap-redis
    restart: unless-stopped
```

#### 3. 配置代理

```yaml
environment:
  PROXY_URI: http://proxy.example.com:1080
```

#### 4. 配置访问控制

```yaml
environment:
  ACCESS_KEY: your-secret-key
```

---

## 🔍 故障排查

### 问题1：容器无法启动

**症状**：`./docker.sh start` 失败

**排查**：
```bash
# 查看详细日志
docker logs newsgap-rsshub

# 检查端口占用
lsof -i :1200

# 检查 Docker 状态
docker ps -a
```

**解决**：
```bash
# 停止冲突容器
docker stop newsgap-rsshub
docker rm newsgap-rsshub

# 重新启动
./docker.sh start
```

### 问题2：端口被占用

**症状**：提示端口 1200 被占用

**解决**：
```bash
# 方法1：修改端口
vi docker-compose.yml
# 修改 ports: - "3000:1200"

# 方法2：释放端口
lsof -ti:1200 | xargs kill -9
```

### 问题3：访问超时

**症状**：http://localhost:1200 无法访问

**排查**：
```bash
# 检查容器是否运行
docker ps | grep rsshub

# 检查容器日志
./docker.sh logs

# 检查网络
docker network inspect newsgap-network
```

**解决**：
```bash
# 重启服务
./docker.sh restart

# 或重新部署
./docker.sh stop
./docker.sh clean
./docker.sh start
```

### 问题4：镜像拉取失败

**症状**：国内网络无法拉取 Docker 镜像

**解决**：
```bash
# 配置 Docker 镜像加速
# 编辑 /etc/docker/daemon.json (Linux)
# 或 Docker Desktop 设置 (macOS/Windows)

{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://dockerhub.azk8s.cn",
    "https://reg-mirror.qiniu.com"
  ]
}

# 重启 Docker
sudo systemctl restart docker  # Linux
# 或重启 Docker Desktop (macOS/Windows)
```

---

## 📈 性能优化

### 1. 启用 Redis 缓存

编辑 `docker-compose.yml`，取消注释 Redis 服务：

```yaml
services:
  rsshub:
    environment:
      CACHE_TYPE: redis
      REDIS_URL: redis://redis:6379/
  
  redis:
    image: redis:alpine
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

**启动**：
```bash
./docker.sh stop
docker-compose up -d
```

### 2. 调整缓存时间

```yaml
environment:
  CACHE_EXPIRE: 300  # 缓存过期时间（秒）
```

### 3. 限制内存使用

```yaml
services:
  rsshub:
    mem_limit: 512m
    mem_reservation: 256m
```

---

## 🔒 安全建议

### 1. 配置访问密钥

```yaml
environment:
  ACCESS_KEY: your-secret-key-here
```

访问时需要带上密钥：
```
http://localhost:1200/github/trending/daily?key=your-secret-key-here
```

### 2. 使用内网访问

如果只在本地使用，修改端口绑定：

```yaml
ports:
  - "127.0.0.1:1200:1200"  # 只监听本地
```

### 3. 配置防火墙

```bash
# 只允许本地访问
sudo ufw allow from 127.0.0.1 to any port 1200

# 或允许特定 IP
sudo ufw allow from 192.168.1.0/24 to any port 1200
```

---

## 🚀 生产环境部署

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name rsshub.example.com;
    
    location / {
        proxy_pass http://localhost:1200;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 配置 SSL

```bash
# 使用 Certbot 获取证书
sudo certbot --nginx -d rsshub.example.com
```

### 配置自动更新

```bash
# 创建更新脚本
cat > /usr/local/bin/update-rsshub.sh << 'EOF'
#!/bin/bash
cd /path/to/NewsGap
./docker.sh update
EOF

chmod +x /usr/local/bin/update-rsshub.sh

# 添加到 crontab（每周更新）
0 2 * * 0 /usr/local/bin/update-rsshub.sh
```

---

## 📚 更多资源

### RSSHub 官方文档

- **官网**: https://docs.rsshub.app/
- **GitHub**: https://github.com/DIYgod/RSSHub
- **路由列表**: https://docs.rsshub.app/routes/

### NewsGap 文档

- [快速开始](QUICK_START.md)
- [部署指南](DEPLOYMENT_SUMMARY.md)
- [使用示例](EXAMPLE_USAGE.md)

---

## 💡 常见使用场景

### 场景1：开发环境

```bash
# 启动 RSSHub
./docker.sh start

# 启动 NewsGap
./start.sh

# 在 NewsGap 中使用 localhost:1200 作为 RSS 源
```

### 场景2：生产环境

```bash
# 使用 systemd 管理
sudo systemctl enable docker
sudo systemctl start docker

# 配置自动启动
docker update --restart unless-stopped newsgap-rsshub
```

### 场景3：团队协作

```bash
# 团队成员统一使用本地 RSSHub
# 每个人独立部署
./docker.sh start

# 或使用共享服务器
# 修改 NewsGap 配置指向服务器地址
```

---

## ✅ 最佳实践

1. ✅ **定期更新** - 使用 `./docker.sh update` 保持最新版本
2. ✅ **启用缓存** - 配置 Redis 提升性能
3. ✅ **监控日志** - 定期查看 `./docker.sh logs`
4. ✅ **备份配置** - 保存 `docker-compose.yml` 配置
5. ✅ **资源限制** - 设置内存和 CPU 限制
6. ✅ **安全访问** - 配置访问密钥或内网访问

---

## 🎉 总结

现在你可以：
- ✅ 一键部署 RSSHub Docker 服务
- ✅ 方便地管理 RSSHub 容器
- ✅ 在 NewsGap 中使用本地 RSS 源
- ✅ 享受更快速、更稳定的信息源聚合

**开始使用 Docker 部署 RSSHub，提升 NewsGap 体验！** 🚀
