# RSSHub 集成指南

## 什么是 RSSHub？

RSSHub 是一个开源、易于使用的 RSS 生成器，可以为任何网站生成 RSS 订阅源。

官网：https://docs.rsshub.app

## 当前配置

NewsGap 已经集成了 RSSHub 支持：

- **默认使用公共 RSSHub 实例**：`https://rsshub.app`
- **SSL 验证已禁用**：避免证书不匹配问题
- **自动重试**：多个公共实例自动 fallback

## 自建 RSSHub 实例（推荐）

公共 RSSHub 实例可能会遇到：
- SSL 证书问题
- 频率限制 (514 错误)
- 访问速度慢

### Docker 快速部署

```bash
docker run -d --name rsshub -p 1200:1200 diygod/rsshub
```

然后在 `backend/config.yaml` 中配置：

```yaml
rsshub:
  custom_instance: "http://localhost:1200"
```

### 其他部署方式

参考官方文档：https://docs.rsshub.app/install/

## 已集成的 RSSHub 源

### 科技类
- IT之家 24h热榜: `https://rsshub.app/ithome/ranking/24h`
- 掘金前端: `https://rsshub.app/juejin/category/frontend`
- 酷安图文: `https://rsshub.app/coolapk/tuwen-xinxian`

### 社交媒体
- 微博热搜: `https://rsshub.app/weibo/search/hot`
- 知乎热榜: `https://rsshub.app/zhihu/hotlist`
- 知乎日报: `https://rsshub.app/zhihu/daily`

### 财经
- 雪球今日话题: `https://rsshub.app/xueqiu/today`
- 第一财经: `https://rsshub.app/yicai/brief`
- 财新博客: `https://rsshub.app/caixin/blog`

### AI
- 量子位: `https://rsshub.app/qbitai`
- AI科技大本营: `https://rsshub.app/csdn/blog/AI_era`

### 其他
- ONE·一个: `https://rsshub.app/one`
- Telegram 频道: `https://rsshub.app/telegram/channel/yszylm`
- ZAKER 精读: `https://rsshub.app/zaker/focusread`

## 添加更多 RSSHub 源

1. 浏览 RSSHub 路由文档：https://docs.rsshub.app/routes/
2. 在设置页面的"信息源管理"中添加
3. URL 格式：`https://rsshub.app/<路由>`

## 常见问题

### Q: 出现 SSL 证书错误？
A: 后端已禁用 SSL 验证（`verify_ssl: false`），应该不会再出现。如仍有问题，建议自建 RSSHub 实例。

### Q: 出现 514 频率限制？
A: 公共 RSSHub 实例有频率限制。解决方法：
   1. 自建 RSSHub 实例（推荐）
   2. 减少爬取频率
   3. 使用其他公共实例

### Q: 如何自定义 RSSHub 路由？
A: 参考官方文档，了解路由规则后直接添加到信息源中。

## 技术细节

- **SSL 验证控制**：`backend/crawler/fetcher.py` 中 `verify_ssl=False`
- **RSSHub 助手**：`backend/crawler/rsshub_helper.py`
- **配置文件**：`backend/config.yaml` → `rsshub` 部分
- **API 端点**：
  - `GET /api/config/rsshub/routes` - 获取常用路由
  - `GET /api/config/rsshub/instance` - 获取当前实例
  - `POST /api/config/rsshub/instance` - 设置自定义实例

## 最佳实践

1. **生产环境建议自建 RSSHub**
2. **定期更新 RSSHub 到最新版本**
3. **配置 Redis 缓存提升性能**
4. **使用代理突破访问限制**

更多信息：https://docs.rsshub.app
