# NewsGap 服务器部署快速指南

> 适用于 `server` 分支 - 生产环境一键部署

---

## ⚡ 30秒快速部署

```bash
# 1. 克隆server分支
git clone -b server https://github.com/Kyuseilee/NewsGap.git
cd NewsGap

# 2. 运行部署脚本
chmod +x deploy-production.sh
./deploy-production.sh

# 3. 配置API Keys
nano backend/.env
# 填入: GEMINI_API_KEY=your-key-here

# 4. 重启服务
sudo systemctl restart newsgap-backend

# 完成！访问 http://your-server-ip
```

---

## 📦 包含内容

### ✅ 新增文件
- `deploy-production.sh` - 一键部署脚本
- `deployment/nginx/newsgap.conf` - Nginx配置模板
- `deployment/systemd/newsgap-backend.service` - systemd服务模板
- `backend/.env.example` - 后端环境变量示例
- `frontend/.env.production` - 前端生产配置
- `docs/DEPLOYMENT.md` - 详细部署文档（必读）

### ✅ 代码修改
- `backend/main.py` - 支持环境变量和动态CORS
- `frontend/vite.config.ts` - 生产构建优化
- `frontend/src/services/api.ts` - 支持环境变量配置

---

## 🎯 部署架构

```
互联网
  ↓
Nginx :80/443 (反向代理 + 静态文件)
  ├─ /           → 前端 dist/
  └─ /api/*      → 后端 :8000
       ↓
   FastAPI Backend (systemd守护)
       ↓
   RSSHub Container :1200
```

---

## 🔧 关键配置

### 1. 后端 CORS（自动配置）
- 开发环境：localhost:5173
- 生产环境：从 `ALLOWED_ORIGINS` 环境变量读取
- 或设置 `ENV=production` 允许所有域名

### 2. 前端 API 地址
- 开发环境：`http://localhost:8000`
- 生产环境：`/api`（通过Nginx代理）
- 配置文件：`frontend/.env.production`

### 3. systemd 服务
- 服务名：`newsgap-backend`
- 自动重启：10秒间隔
- 日志路径：`/var/log/newsgap/`

---

## 💡 常用命令

```bash
# 查看服务状态
sudo systemctl status newsgap-backend

# 重启服务
sudo systemctl restart newsgap-backend

# 查看实时日志
sudo journalctl -u newsgap-backend -f

# 重载Nginx配置
sudo systemctl reload nginx

# 查看RSSHub状态
./docker.sh status
```

---

## 🔒 配置 HTTPS

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书（自动配置Nginx）
sudo certbot --nginx -d yourdomain.com

# 测试自动续期
sudo certbot renew --dry-run
```

---

## 🆘 故障排查

### 前端能访问，但API失败？
```bash
# 检查后端是否运行
sudo systemctl status newsgap-backend
curl http://localhost:8000/health

# 查看错误日志
sudo journalctl -u newsgap-backend -n 50
```

### 后端启动失败？
```bash
# 查看详细错误
sudo journalctl -u newsgap-backend --no-pager

# 手动启动查看错误
cd backend
source venv/bin/activate
python main.py
```

### Nginx 404错误？
```bash
# 检查dist目录
ls -la frontend/dist/

# 检查Nginx配置
sudo nginx -t
grep "root" /etc/nginx/sites-enabled/newsgap
```

---

## 📚 详细文档

- **完整部署指南**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **项目README**: [README.md](README.md)
- **质量跟踪设计**: [docs/quality_tracking_design.md](docs/quality_tracking_design.md)

---

## ⚙️ 分支说明

- **master** - 主分支（本地开发）
- **server** - 生产部署分支（公网访问）

### 区别
| 功能 | master | server |
|------|--------|--------|
| 本地开发 | ✅ | ✅ |
| 生产部署 | ❌ | ✅ |
| Nginx配置 | ❌ | ✅ |
| systemd服务 | ❌ | ✅ |
| 环境变量支持 | 部分 | 完整 |
| 一键部署脚本 | ❌ | ✅ |

---

## 📝 部署清单

部署完成后，确认以下项目：

- [ ] 后端服务正常运行
- [ ] 前端可通过公网访问
- [ ] API调用正常（无CORS错误）
- [ ] RSSHub容器运行中
- [ ] 防火墙端口已开放
- [ ] systemd服务已启用
- [ ] （可选）HTTPS证书已配置
- [ ] （可选）域名DNS已解析

---

**最后更新**: 2026-02-05  
**版本**: v1.0  
**分支**: server  
**作者**: Kyusei
