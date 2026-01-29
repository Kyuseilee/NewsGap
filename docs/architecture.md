# NewsGap 架构设计文档

## 系统概述

NewsGap 是一个模块化的信息情报系统，采用前后端分离架构，严格遵循单一职责原则。

## 核心设计原则

### 1. 模块分离

系统分为四个独立模块：

```
┌─────────────┐
│   Frontend  │  React GUI（展示层）
└──────┬──────┘
       │ HTTP/REST
┌──────▼──────┐
│  API Layer  │  FastAPI（编排层）
└──────┬──────┘
       │
   ┌───┴────┬────────┬──────────┐
   │        │        │          │
┌──▼──┐ ┌──▼──┐ ┌───▼───┐ ┌───▼────┐
│Crawl│ │Store│ │Analyze│ │Archive │
└─────┘ └─────┘ └───────┘ └────────┘
```

每个模块：
- 有清晰的输入输出接口
- 可独立测试
- 可独立替换

### 2. 数据流

#### 分步执行流程

```
用户选择行业
    ↓
调用 Crawler 爬取
    ↓
存入 Storage
    ↓
用户查看文章列表
    ↓
用户选择文章
    ↓
调用 Analyzer 分析
    ↓
返回情报摘要
```

#### 一键执行流程

```
用户选择行业 + LLM
    ↓
并发调用 Crawler（多个源）
    ↓
批量存入 Storage
    ↓
自动调用 Analyzer
    ↓
返回情报摘要
```

### 3. 成本控制

- LLM 调用前显示 token 估算
- 缓存分析结果
- 避免重复分析
- 用户明确确认后才执行

## 模块详解

### Crawler 模块

**职责**：数据获取

**输入**：
- Source（信息源配置）
- hours（时间范围）

**输出**：
- List[Article]（标准化文章列表）

**约束**：
- 不使用 LLM
- 输出可复现
- 单源失败不影响整体

**实现**：
```python
class CrawlerService:
    async def fetch(source, hours) -> List[Article]:
        if source.type == RSS:
            return rss_parser.parse()
        elif source.type == WEB:
            return extractor.extract()
```

### Storage 模块

**职责**：数据持久化

**功能**：
- CRUD 文章
- 按条件查询
- 全文搜索
- Markdown 导出

**技术**：
- SQLite（主存储）
- FTS5（全文搜索）
- 文件系统（归档）

**Schema**：
```sql
articles (id, title, url, content, ...)
sources (id, name, url, type, ...)
analyses (id, article_ids, brief, ...)
```

### Analyzer 模块

**职责**：情报分析

**LLM 适配器接口**：
```python
class LLMAdapter:
    async def analyze(articles, type) -> Analysis
    def estimate_cost(articles) -> dict
    def get_model_info() -> dict
```

**支持的后端**：
- Ollama（本地）
- OpenAI
- DeepSeek
- Gemini

**分析类型**：
- Trend（趋势检测）
- Signal（信号识别）
- Gap（信息差）
- Brief（执行摘要）
- Comprehensive（综合）

### API Layer

**职责**：编排各模块

**路由**：
```
/api/fetch          - 爬取
/api/analyze        - 分析
/api/intelligence   - 一键
/api/articles       - 文章查询
/api/config         - 配置管理
```

**依赖注入**：
```python
@router.post("/fetch")
async def fetch(
    db: Database = Depends(get_db),
    crawler: CrawlerService = Depends(get_crawler)
):
    ...
```

## 数据模型

### 核心实体

```python
Article:
  - id, title, url
  - content, summary
  - industry, tags
  - published_at, fetched_at
  - source_id, source_name

Source:
  - id, name, url
  - source_type, industry
  - enabled, fetch_interval_hours

Analysis:
  - id, analysis_type
  - article_ids
  - executive_brief
  - trends[], signals[], gaps[]
  - llm_backend, token_usage, cost
```

### 关系

```
Source 1:N Article
Article N:M Analysis
Article N:M Tag
```

## 前端架构

### 页面结构

```
App
├── Home（首页）
│   ├── 行业选择
│   ├── 时间范围
│   ├── LLM 选择
│   └── 操作按钮
│
├── Articles（文章列表）
│   ├── 过滤器
│   └── 文章卡片
│
├── Analysis（分析结果）
│   ├── 执行摘要
│   ├── 趋势列表
│   └── 信号聚类
│
├── Archive（归档）
│   └── 时间轴
│
└── Settings（设置）
    ├── 信息源管理
    └── LLM 配置
```

### 状态管理

使用 TanStack Query 管理服务端状态：

```typescript
const { data } = useQuery({
  queryKey: ['articles', industry],
  queryFn: () => api.getArticles({ industry })
})
```

### API 客户端

```typescript
// services/api.ts
export const api = {
  fetch: (req) => POST('/api/fetch', req),
  analyze: (req) => POST('/api/analyze', req),
  getArticles: (params) => GET('/api/articles', params),
  ...
}
```

## 扩展性设计

### 添加新的 LLM 后端

1. 实现 `LLMAdapter` 接口
2. 注册到工厂函数
3. 更新配置文件

```python
class NewLLMAdapter(BaseLLMAdapter):
    async def analyze(...) -> Analysis:
        # 实现
    
    def get_model_info() -> dict:
        # 实现
```

### 添加新的信息源类型

1. 实现 Parser
2. 注册到 CrawlerService
3. 更新 SourceType enum

### 添加新的分析类型

1. 定义提示词模板
2. 更新 AnalysisType enum
3. 实现结果解析

## 部署架构

### 开发环境

```
Frontend (Vite Dev Server) :5173
    ↓ proxy /api
Backend (FastAPI) :8000
    ↓
SQLite :file
```

### 生产环境（Web）

```
Nginx
  ↓
  ├─ /      → Frontend (静态文件)
  └─ /api   → Backend (Uvicorn)
            ↓
          SQLite
```

### 桌面应用（Tauri）

```
Tauri App
  ├─ Frontend (内嵌)
  └─ Backend (内嵌 Python)
      ↓
    SQLite (用户目录)
```

## 安全考虑

- API Key 存储在环境变量
- 不记录敏感信息
- 爬虫遵守 robots.txt
- 用户数据本地存储

## 性能优化

- 异步 I/O（asyncio）
- 数据库连接池
- FTS5 全文搜索索引
- 前端虚拟滚动（大列表）
- React Query 缓存

## 可测试性

每个模块独立可测：

```python
# 测试 Crawler
articles = await crawler.fetch(mock_source, 24)
assert len(articles) > 0

# 测试 Storage
article_id = await db.save_article(article)
loaded = await db.get_article(article_id)
assert loaded.title == article.title

# 测试 Analyzer
analysis = await analyzer.analyze(articles)
assert analysis.executive_brief != ""
```

## 错误处理

- 单个源失败不影响其他源
- LLM 调用失败返回基础摘要
- 前端友好的错误提示
- 日志记录便于调试

---

这个架构确保了：
✅ 模块解耦
✅ 可独立演进
✅ 易于测试
✅ 便于扩展
