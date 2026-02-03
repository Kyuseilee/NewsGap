# 如何添加更多信息源

NewsGap 支持多种方式添加信息源，本文档将详细介绍每种方法。

## 📋 目录

1. [通过 Web UI 添加](#1-通过-web-ui-添加推荐)
2. [通过初始化脚本批量添加](#2-通过初始化脚本批量添加)
3. [通过 API 编程添加](#3-通过-api-编程添加)
4. [直接编辑数据库](#4-直接编辑数据库不推荐)
5. [RSSHub 信息源推荐](#5-rsshub-信息源推荐)

---

## 1. 通过 Web UI 添加（推荐）

这是最简单直观的方式。

### 步骤：

1. **启动 NewsGap 服务**
   ```bash
   # 启动后端
   cd backend
   python main.py
   
   # 启动前端（新终端）
   cd frontend
   npm run dev
   ```

2. **访问设置页面**
   - 打开浏览器访问 `http://localhost:5173`
   - 点击导航栏的"设置"按钮

3. **添加新信息源**
   - 点击"添加信息源"按钮
   - 填写以下信息：
     - **名称**: 信息源的显示名称（例如："GitHub Trending Python"）
     - **URL**: RSS 或网页地址
     - **类型**: 选择 RSS、Web 或 API
     - **行业分类**: AI、技术、金融、医疗、能源、教育、娱乐或其他
     - **抓取间隔**: 1-168 小时（默认 24 小时）
     - **启用状态**: 是否立即启用

4. **保存并验证**
   - 点击"保存"按钮
   - 系统会自动验证 URL 是否可访问
   - 如果验证通过，信息源将被添加到列表中

### UI 添加的优点：
- ✅ 可视化操作，简单直观
- ✅ 自动验证 URL 可用性
- ✅ 实时反馈错误信息
- ✅ 可以立即测试抓取效果

---

## 2. 通过初始化脚本批量添加

适合一次性添加大量信息源。

### 步骤：

1. **编辑初始化脚本**

打开 `backend/init_rss_sources.py`，在 `sources` 列表中添加新的信息源：

```python
sources = [
    # 现有的信息源...
    
    # ===== 你的新信息源 =====
    Source(
        name="信息源名称",
        url="https://example.com/rss",
        source_type=SourceType.RSS,
        industry=IndustryCategory.TECH,  # 选择合适的分类
        enabled=True
    ),
    
    # 更多信息源...
]
```

2. **运行初始化脚本**

```bash
cd backend
python init_rss_sources.py
```

3. **查看结果**

脚本会输出每个信息源的添加状态：
```
开始初始化 89 个 RSS 源...
============================================================
✓ [tech] GitHub Trending Python
  URL: http://localhost:1200/github/trending/daily/python
✓ [ai] 机器之心
  URL: https://www.jiqizhixin.com/rss
...
============================================================

初始化完成！
成功: 89 个
失败: 0 个
总计: 89 个
```

### 脚本添加的优点：
- ✅ 适合批量添加
- ✅ 可以版本控制
- ✅ 便于团队协作
- ✅ 支持注释和分类

---

## 3. 通过 API 编程添加

适合需要动态添加或自动化场景。

### 方法 A: 使用 curl

```bash
curl -X POST "http://localhost:8000/api/config/sources" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GitHub Trending Python",
    "url": "http://localhost:1200/github/trending/daily/python",
    "source_type": "rss",
    "industry": "tech",
    "enabled": true,
    "fetch_interval_hours": 24
  }'
```

### 方法 B: 使用 Python

```python
import httpx
import asyncio

async def add_source():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/config/sources",
            json={
                "name": "GitHub Trending Python",
                "url": "http://localhost:1200/github/trending/daily/python",
                "source_type": "rss",
                "industry": "tech",
                "enabled": True,
                "fetch_interval_hours": 24
            }
        )
        print(response.json())

asyncio.run(add_source())
```

### 方法 C: 批量添加脚本

创建 `add_sources.py`：

```python
import httpx
import asyncio

SOURCES = [
    {
        "name": "GitHub Trending Python",
        "url": "http://localhost:1200/github/trending/daily/python",
        "source_type": "rss",
        "industry": "tech",
        "enabled": True
    },
    {
        "name": "GitHub Trending JavaScript",
        "url": "http://localhost:1200/github/trending/daily/javascript",
        "source_type": "rss",
        "industry": "tech",
        "enabled": True
    },
    # 添加更多...
]

async def add_sources():
    async with httpx.AsyncClient() as client:
        for source in SOURCES:
            try:
                response = await client.post(
                    "http://localhost:8000/api/config/sources",
                    json=source
                )
                if response.status_code == 200:
                    print(f"✓ 成功添加: {source['name']}")
                else:
                    print(f"✗ 失败: {source['name']} - {response.text}")
            except Exception as e:
                print(f"✗ 错误: {source['name']} - {str(e)}")

if __name__ == "__main__":
    asyncio.run(add_sources())
```

运行：
```bash
cd backend
python add_sources.py
```

### API 添加的优点：
- ✅ 可以集成到自动化流程
- ✅ 支持远程调用
- ✅ 便于批量操作
- ✅ 可以与其他系统集成

---

## 4. 直接编辑数据库（不推荐）

⚠️ **警告**: 直接操作数据库可能导致数据不一致，仅在必要时使用。

```bash
cd backend/data
sqlite3 newsgap.db
```

```sql
-- 查看现有信息源
SELECT * FROM sources;

-- 插入新信息源
INSERT INTO sources (id, name, url, source_type, industry, enabled, fetch_interval_hours, created_at)
VALUES (
    'source_' || hex(randomblob(8)),
    'GitHub Trending Python',
    'http://localhost:1200/github/trending/daily/python',
    'rss',
    'tech',
    1,
    24,
    datetime('now')
);

-- 退出
.quit
```

---

## 5. RSSHub 信息源推荐

使用本地 RSSHub 实例可以为几乎任何网站生成 RSS 源。

### 启动 RSSHub

```bash
docker-compose up -d
```

### 常用 RSSHub 路由

#### 技术类

```python
# GitHub
Source(name="GitHub Trending Python", 
       url="http://localhost:1200/github/trending/daily/python",
       source_type=SourceType.RSS, industry=IndustryCategory.TECH, enabled=True),

Source(name="GitHub Trending JavaScript",
       url="http://localhost:1200/github/trending/daily/javascript",
       source_type=SourceType.RSS, industry=IndustryCategory.TECH, enabled=True),

Source(name="GitHub 仓库 Issues",
       url="http://localhost:1200/github/issue/owner/repo",
       source_type=SourceType.RSS, industry=IndustryCategory.TECH, enabled=True),

# 掘金
Source(name="掘金前端",
       url="http://localhost:1200/juejin/category/frontend",
       source_type=SourceType.RSS, industry=IndustryCategory.TECH, enabled=True),

# V2EX
Source(name="V2EX 最热",
       url="http://localhost:1200/v2ex/topics/hot",
       source_type=SourceType.RSS, industry=IndustryCategory.TECH, enabled=True),

# Hacker News
Source(name="Hacker News 热门",
       url="http://localhost:1200/hackernews/best",
       source_type=SourceType.RSS, industry=IndustryCategory.TECH, enabled=True),
```

#### AI 类

```python
# Papers with Code
Source(name="Papers with Code Latest",
       url="http://localhost:1200/paperswithcode/latest",
       source_type=SourceType.RSS, industry=IndustryCategory.AI, enabled=True),

# Hugging Face
Source(name="Hugging Face Daily Papers",
       url="http://localhost:1200/huggingface/daily-papers",
       source_type=SourceType.RSS, industry=IndustryCategory.AI, enabled=True),

# OpenAI Blog
Source(name="OpenAI Blog",
       url="http://localhost:1200/openai/blog",
       source_type=SourceType.RSS, industry=IndustryCategory.AI, enabled=True),
```

#### 金融类

```python
# 雪球
Source(name="雪球今日话题",
       url="http://localhost:1200/xueqiu/today",
       source_type=SourceType.RSS, industry=IndustryCategory.FINANCE, enabled=True),

Source(name="雪球用户动态",
       url="http://localhost:1200/xueqiu/user/1234567890",
       source_type=SourceType.RSS, industry=IndustryCategory.FINANCE, enabled=True),

# 东方财富
Source(name="东方财富要闻",
       url="http://localhost:1200/eastmoney/important",
       source_type=SourceType.RSS, industry=IndustryCategory.FINANCE, enabled=True),
```

#### 社交媒体

```python
# Twitter/X
Source(name="Twitter 用户推文",
       url="http://localhost:1200/twitter/user/username",
       source_type=SourceType.RSS, industry=IndustryCategory.OTHER, enabled=True),

# 微博
Source(name="微博热搜",
       url="http://localhost:1200/weibo/search/hot",
       source_type=SourceType.RSS, industry=IndustryCategory.OTHER, enabled=True),

Source(name="微博用户",
       url="http://localhost:1200/weibo/user/1234567890",
       source_type=SourceType.RSS, industry=IndustryCategory.OTHER, enabled=True),

# Telegram
Source(name="Telegram 频道",
       url="http://localhost:1200/telegram/channel/channelname",
       source_type=SourceType.RSS, industry=IndustryCategory.OTHER, enabled=True),
```

#### 新闻媒体

```python
# 知乎
Source(name="知乎热榜",
       url="http://localhost:1200/zhihu/hotlist",
       source_type=SourceType.RSS, industry=IndustryCategory.OTHER, enabled=True),

Source(name="知乎日报",
       url="http://localhost:1200/zhihu/daily",
       source_type=SourceType.RSS, industry=IndustryCategory.OTHER, enabled=True),

# B站
Source(name="B站UP主",
       url="http://localhost:1200/bilibili/user/video/userid",
       source_type=SourceType.RSS, industry=IndustryCategory.OTHER, enabled=True),

Source(name="B站排行榜",
       url="http://localhost:1200/bilibili/ranking/0/3/1",
       source_type=SourceType.RSS, industry=IndustryCategory.OTHER, enabled=True),

# YouTube
Source(name="YouTube 频道",
       url="http://localhost:1200/youtube/user/@username",
       source_type=SourceType.RSS, industry=IndustryCategory.OTHER, enabled=True),
```

### 查找更多 RSSHub 路由

1. **访问 RSSHub 文档**: https://docs.rsshub.app/routes/
2. **浏览本地 RSSHub**: http://localhost:1200
3. **使用 RSSHub Radar 浏览器插件**: 自动发现网页的 RSS 源

---

## 📝 信息源配置参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✓ | 信息源显示名称（1-200字符） |
| `url` | string | ✓ | RSS/网页地址（必须以 http:// 或 https:// 开头） |
| `source_type` | enum | ✓ | 类型：`rss`、`web` 或 `api` |
| `industry` | enum | ✓ | 行业分类：`ai`、`tech`、`finance`、`healthcare`、`energy`、`education`、`entertainment`、`other` |
| `enabled` | boolean |  | 是否启用（默认：true） |
| `fetch_interval_hours` | integer |  | 抓取间隔：1-168小时（默认：24） |
| `metadata` | object |  | 额外配置（可选） |

### 行业分类说明

```python
class IndustryCategory(str, Enum):
    AI = "ai"                    # 人工智能
    TECH = "tech"                # 技术/互联网
    FINANCE = "finance"          # 金融/财经
    HEALTHCARE = "healthcare"    # 医疗健康
    ENERGY = "energy"            # 能源
    EDUCATION = "education"      # 教育
    ENTERTAINMENT = "entertainment"  # 娱乐
    OTHER = "other"              # 其他
```

---

## 🔍 如何找到 RSS 源

### 方法 1: 网站自带 RSS

很多网站提供原生 RSS 订阅：

```bash
# 常见 RSS 地址模式
https://example.com/feed
https://example.com/rss
https://example.com/feed.xml
https://example.com/rss.xml
https://example.com/atom.xml
https://blog.example.com/index.xml
```

查看网页源代码，搜索 `<link rel="alternate" type="application/rss+xml"`

### 方法 2: 使用 RSSHub

为不提供 RSS 的网站生成订阅源：

```bash
# 先查阅 RSSHub 文档
https://docs.rsshub.app/routes/

# 然后使用对应路由
http://localhost:1200/路由/参数
```

### 方法 3: RSS 发现工具

- **浏览器插件**: RSSHub Radar、RSS Subscription Extension
- **在线工具**: Feed43、RSS.app、FetchRSS
- **命令行工具**: `curl -sL url | grep -i rss`

### 方法 4: Feed 聚合网站

- Feedly
- Inoreader
- NewsBlur

---

## ⚠️ 常见问题

### Q1: 添加信息源后无法抓取？

**解决方法**:
1. 检查 URL 是否可访问：`curl -I "URL"`
2. 查看后端日志：`cd backend && python main.py`
3. 验证 RSS 格式是否正确
4. 检查是否需要配置代理或 API Key

### Q2: RSSHub 路由返回 404？

**解决方法**:
1. 确认 RSSHub 服务已启动：`docker-compose ps`
2. 检查路由是否正确：访问 https://docs.rsshub.app/
3. 查看 RSSHub 日志：`docker-compose logs rsshub`

### Q3: 信息源验证失败？

**可能原因**:
- URL 格式错误（必须以 http:// 或 https:// 开头）
- 网站需要登录或验证
- 网站屏蔽了爬虫请求
- 需要配置 User-Agent 或代理

**解决方法**:
1. 使用 RSSHub 作为中间层
2. 在 `backend/config.yaml` 中配置代理
3. 调整 `user_agent` 设置

### Q4: 如何批量启用/禁用信息源？

**方法 A: 通过 UI**
- 在设置页面勾选/取消勾选信息源

**方法 B: 通过 SQL**
```sql
-- 禁用所有金融类信息源
UPDATE sources SET enabled = 0 WHERE industry = 'finance';

-- 启用所有 AI 类信息源
UPDATE sources SET enabled = 1 WHERE industry = 'ai';
```

### Q5: 如何修改抓取间隔？

**方法 A: 通过 UI**
- 在设置页面编辑信息源，修改"抓取间隔"

**方法 B: 通过 API**
```bash
curl -X PUT "http://localhost:8000/api/config/sources/SOURCE_ID" \
  -H "Content-Type: application/json" \
  -d '{"fetch_interval_hours": 12}'
```

---

## 📚 推荐阅读

- [RSSHub 使用文档](./RSSHUB.md)
- [信息源最佳实践](https://docs.rsshub.app/guide/best-practices)
- [RSS 规范说明](https://www.rssboard.org/rss-specification)
- [NewsGap API 文档](./api.md)

---

## 💡 最佳实践

1. **分类明确**: 为信息源选择准确的行业分类，便于后续筛选和分析
2. **合理间隔**: 根据信息源更新频率设置抓取间隔，避免过于频繁
3. **定期维护**: 定期检查失效的信息源，及时更新或删除
4. **使用 RSSHub**: 优先使用本地 RSSHub 实例，避免依赖公共服务
5. **测试验证**: 添加后先测试抓取，确保能正常获取内容
6. **备份配置**: 定期导出信息源列表，便于迁移和恢复

---

现在你已经掌握了添加信息源的所有方法！选择最适合你的方式开始吧 🚀
