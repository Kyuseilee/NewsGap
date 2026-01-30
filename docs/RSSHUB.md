# RSSHub 本地部署指南

本文档说明如何在 NewsGap 项目中部署和使用本地 RSSHub 实例。

## 📋 什么是 RSSHub？

RSSHub 是一个开源、简单易用、易于扩展的 RSS 生成器，可以为任何内容生成 RSS 订阅源。通过本地部署 RSSHub，你可以：

- 为不提供 RSS 的网站生成订阅源
- 避免公共实例的访问限制
- 获得更稳定和快速的服务
- 自定义配置和缓存策略

## 🚀 快速启动

### 1. 启动 RSSHub 服务

在项目根目录执行：

```bash
docker-compose up -d
```

这将启动两个容器：
- `newsgap-rsshub`: RSSHub 主服务（端口 1200）
- `newsgap-redis`: Redis 缓存服务

### 2. 验证服务状态

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f rsshub

# 检查健康状态
docker-compose ps rsshub
```

### 3. 访问 RSSHub

在浏览器中打开：
```
http://localhost:1200
```

你应该能看到 RSSHub 的欢迎页面。

## 📝 配置说明

### 基础配置

默认配置已在 `docker-compose.yml` 中设置：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| 端口 | 1200 | RSSHub 服务端口 |
| 缓存类型 | redis | 使用 Redis 缓存 |
| 缓存过期 | 3600秒 | 1小时 |
| 重试次数 | 2 | 请求失败重试 |

### 高级配置（可选）

如需自定义配置，创建 `.env.rsshub` 文件：

```bash
# 复制示例配置
cp .env.rsshub.example .env.rsshub
```

然后编辑 `.env.rsshub` 并修改 `docker-compose.yml` 以加载环境变量：

```yaml
services:
  rsshub:
    # ...
    env_file:
      - .env.rsshub
```

#### 访问控制

为 RSSHub 添加访问密钥：

```bash
# 在 .env.rsshub 中添加
ACCESS_KEY=your_secure_key_here
```

访问时需要带上密钥：
```
http://localhost:1200/github/issue/DIYgod/RSSHub?key=your_secure_key_here
```

#### 代理配置

如需访问被墙的网站（如 Twitter、YouTube）：

```bash
# 在 .env.rsshub 中添加
PROXY_URI=socks5h://127.0.0.1:1080
PROXY_URL_REGEX=.*
```

#### 第三方服务 API

某些路由需要配置 API Key，例如：

```bash
# GitHub（提高访问频率限制）
GITHUB_ACCESS_TOKEN=your_github_token

# YouTube
YOUTUBE_KEY=your_youtube_api_key

# Twitter/X
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
```

完整配置项参考：https://docs.rsshub.app/deploy/config

## 💡 使用示例

### 常用路由

以下是一些常用的 RSSHub 路由示例：

#### 1. GitHub

```bash
# 仓库 Issues
http://localhost:1200/github/issue/DIYgod/RSSHub

# 用户动态
http://localhost:1200/github/user/activities/DIYgod

# 仓库 Trending
http://localhost:1200/github/trending/daily/python
```

#### 2. 知乎

```bash
# 热榜
http://localhost:1200/zhihu/hotlist

# 用户动态
http://localhost:1200/zhihu/people/activities/username

# 专栏
http://localhost:1200/zhihu/zhuanlan/column-id
```

#### 3. 微博

```bash
# 用户微博
http://localhost:1200/weibo/user/1195230310

# 热搜
http://localhost:1200/weibo/search/hot
```

#### 4. B站

```bash
# UP主投稿
http://localhost:1200/bilibili/user/video/2267573

# 分区排行
http://localhost:1200/bilibili/ranking/0/3/1
```

#### 5. 36氪

```bash
# 快讯
http://localhost:1200/36kr/newsflashes

# 资讯
http://localhost:1200/36kr/news/latest
```

完整路由列表：https://docs.rsshub.app/

## 🔧 管理命令

### 查看服务状态

```bash
docker-compose ps
```

### 查看日志

```bash
# 实时日志
docker-compose logs -f

# 只查看 RSSHub 日志
docker-compose logs -f rsshub

# 最近 100 行日志
docker-compose logs --tail=100 rsshub
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 只重启 RSSHub
docker-compose restart rsshub
```

### 停止服务

```bash
# 停止服务但保留容器
docker-compose stop

# 停止并删除容器
docker-compose down

# 同时删除数据卷（会清空缓存）
docker-compose down -v
```

### 更新 RSSHub

```bash
# 拉取最新镜像
docker-compose pull rsshub

# 重新启动
docker-compose up -d
```

### 清理缓存

```bash
# 重启 Redis 容器
docker-compose restart redis

# 或者手动清理
docker exec -it newsgap-redis redis-cli FLUSHALL
```

## 🔗 集成到 NewsGap

### 1. 添加 RSSHub 源到配置

编辑 `backend/config.yaml` 或通过 UI 添加：

```yaml
sources:
  - name: "GitHub Trending Python"
    url: "http://localhost:1200/github/trending/daily/python"
    type: "rss"
    category: "tech"
    enabled: true
    
  - name: "36氪快讯"
    url: "http://localhost:1200/36kr/newsflashes"
    type: "rss"
    category: "business"
    enabled: true
```

### 2. 使用 API 添加

```python
import httpx

async def add_rsshub_source():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/sources",
            json={
                "name": "GitHub Trending",
                "url": "http://localhost:1200/github/trending/daily/python",
                "type": "rss",
                "category": "tech",
                "enabled": True
            }
        )
        print(response.json())
```

### 3. 测试抓取

在 NewsGap UI 中：
1. 进入"设置"页面
2. 查看信息源列表
3. 确认 RSSHub 源已启用
4. 返回首页，点击"仅爬取"测试

## 🐛 故障排查

### 问题 1: 容器无法启动

```bash
# 检查端口是否被占用
lsof -i :1200

# 修改 docker-compose.yml 中的端口映射
ports:
  - "1201:1200"  # 改为其他端口
```

### 问题 2: 无法访问某些网站

- 检查是否需要配置代理
- 检查是否需要配置相应的 API Key
- 查看日志了解具体错误

```bash
docker-compose logs -f rsshub | grep ERROR
```

### 问题 3: 响应速度慢

- 增加 Redis 缓存时间
- 减少 `REQUEST_RETRY` 次数
- 考虑使用代理加速

### 问题 4: 内存占用过高

```bash
# 限制 RSSHub 内存使用
services:
  rsshub:
    # ...
    deploy:
      resources:
        limits:
          memory: 512M
```

## 📚 参考资源

- RSSHub 官方文档: https://docs.rsshub.app/
- 路由列表: https://docs.rsshub.app/routes/
- 配置说明: https://docs.rsshub.app/deploy/config
- GitHub 仓库: https://github.com/DIYgod/RSSHub

## ⚠️ 注意事项

1. **合规使用**: 遵守目标网站的 robots.txt 和服务条款
2. **访问频率**: 合理设置缓存时间，避免过于频繁的请求
3. **数据备份**: Redis 数据会在容器删除时丢失，如需持久化请配置
4. **安全性**: 如果暴露到公网，务必设置 `ACCESS_KEY`
5. **资源限制**: 根据实际情况调整容器资源限制

## 🔄 从公共实例迁移

如果之前使用的是公共 RSSHub 实例（如 `rsshub.app`），只需将 URL 替换为本地地址：

```bash
# 旧地址
https://rsshub.app/github/trending/daily

# 新地址
http://localhost:1200/github/trending/daily
```

批量替换可以使用脚本：

```python
import sqlite3

conn = sqlite3.connect('backend/data/newsgap.db')
cursor = conn.cursor()

# 更新所有 RSSHub 源为本地地址
cursor.execute("""
    UPDATE sources 
    SET url = REPLACE(url, 'https://rsshub.app', 'http://localhost:1200')
    WHERE url LIKE '%rsshub.app%'
""")

conn.commit()
conn.close()
```

---

现在你已经拥有了自己的 RSSHub 实例！开始探索更多的信息源吧 🚀
