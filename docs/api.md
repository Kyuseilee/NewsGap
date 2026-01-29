# NewsGap API 文档

Base URL: `http://localhost:8000`

## 认证

当前版本不需要认证。未来版本可能添加 API Key 认证。

## 数据格式

所有请求和响应使用 JSON 格式。

时间格式：ISO 8601（`2026-01-29T12:00:00`）

## API 端点

### 1. 爬取相关

#### POST /api/fetch

爬取指定行业的文章。

**请求体**：
```json
{
  "industry": "ai",
  "hours": 24,
  "source_ids": ["source-id-1", "source-id-2"]  // 可选
}
```

**参数说明**：
- `industry`: 行业分类（ai, tech, finance, healthcare, energy, education, other）
- `hours`: 爬取最近多少小时的内容（1-168）
- `source_ids`: 可选，指定信息源 ID 列表

**响应**：
```json
{
  "article_ids": ["article-id-1", "article-id-2"],
  "count": 50,
  "sources_used": ["36氪", "少数派"],
  "fetch_time_seconds": 12.5
}
```

**示例**：
```bash
curl -X POST http://localhost:8000/api/fetch \
  -H "Content-Type: application/json" \
  -d '{"industry":"ai","hours":24}'
```

---

### 2. 分析相关

#### POST /api/analyze

对指定文章进行情报分析。

**请求体**：
```json
{
  "article_ids": ["id1", "id2", "id3"],
  "analysis_type": "comprehensive",
  "llm_backend": "deepseek",
  "custom_prompt": "请重点关注技术突破..."  // 可选
}
```

**参数说明**：
- `article_ids`: 文章 ID 列表
- `analysis_type`: 分析类型（trend, signal, gap, brief, comprehensive）
- `llm_backend`: LLM 后端（ollama, openai, deepseek, gemini）
- `custom_prompt`: 自定义提示词（可选）

**响应**：
```json
{
  "analysis_id": "analysis-uuid",
  "analysis": {
    "id": "analysis-uuid",
    "analysis_type": "comprehensive",
    "article_ids": ["id1", "id2"],
    "executive_brief": "本周 AI 领域主要关注...",
    "trends": [
      {
        "title": "多模态大模型快速发展",
        "description": "...",
        "confidence": 0.85,
        "supporting_article_ids": ["id1", "id2"],
        "keywords": ["多模态", "GPT-4", "Gemini"]
      }
    ],
    "signals": [...],
    "information_gaps": [...],
    "llm_backend": "deepseek",
    "token_usage": 1500,
    "estimated_cost": 0.00021,
    "processing_time_seconds": 8.2
  }
}
```

#### POST /api/analyze/estimate-cost

估算分析成本（在实际分析前）。

**请求体**：同 `/api/analyze`

**响应**：
```json
{
  "token_count": 1500,
  "estimated_cost_usd": 0.00021,
  "model": "deepseek-chat",
  "model_info": {
    "backend": "deepseek",
    "max_tokens": 64000,
    "cost_per_1k_tokens": 0.00014
  },
  "article_count": 10
}
```

---

### 3. 一键情报

#### POST /api/intelligence

一键执行爬取+分析。

**请求体**：
```json
{
  "industry": "ai",
  "hours": 24,
  "llm_backend": "deepseek",
  "source_ids": []  // 可选
}
```

**响应**：
```json
{
  "article_ids": ["id1", "id2", ...],
  "article_count": 15,
  "analysis_id": "analysis-uuid",
  "analysis": { /* Analysis 对象 */ },
  "total_time_seconds": 25.3
}
```

---

### 4. 文章查询

#### GET /api/articles

查询文章列表。

**查询参数**：
- `industry`: 行业过滤（可选）
- `start_time`: 开始时间（可选，ISO 8601）
- `end_time`: 结束时间（可选）
- `tags`: 标签过滤（可选，逗号分隔）
- `limit`: 返回数量（默认 100，最大 500）
- `offset`: 偏移量（默认 0）
- `archived`: 是否只看归档（可选，true/false）

**响应**：
```json
{
  "articles": [
    {
      "id": "article-uuid",
      "title": "文章标题",
      "url": "https://example.com/article",
      "source_name": "36氪",
      "content": "正文内容...",
      "summary": "摘要...",
      "industry": "ai",
      "tags": ["GPT", "OpenAI"],
      "published_at": "2026-01-29T10:00:00",
      "fetched_at": "2026-01-29T12:00:00",
      "author": "张三",
      "word_count": 1500,
      "archived": false
    }
  ],
  "total": 100,
  "limit": 100,
  "offset": 0
}
```

**示例**：
```bash
# 查询 AI 行业最近 24 小时的文章
curl "http://localhost:8000/api/articles?industry=ai&limit=50"

# 查询包含特定标签的文章
curl "http://localhost:8000/api/articles?tags=GPT,OpenAI"
```

#### GET /api/articles/{article_id}

获取单篇文章详情。

**响应**：Article 对象

#### GET /api/articles/search/{query}

全文搜索文章。

**查询参数**：
- `limit`: 返回数量（默认 50）

**响应**：
```json
{
  "query": "GPT-5",
  "count": 3,
  "articles": [ /* Article 对象列表 */ ]
}
```

#### POST /api/articles/{article_id}/archive

归档单篇文章。

**响应**：
```json
{
  "success": true,
  "message": "文章已归档"
}
```

#### POST /api/articles/export

导出多篇文章为 Markdown。

**请求体**：
```json
{
  "article_ids": ["id1", "id2", "id3"],
  "output_dir": "./archives"  // 可选
}
```

**响应**：
```json
{
  "success": true,
  "archive_path": "./archives/2026-01-29",
  "count": 3
}
```

---

### 5. 配置管理

#### GET /api/config/sources

获取信息源列表。

**查询参数**：
- `industry`: 行业过滤（可选）
- `enabled_only`: 只返回启用的源（默认 true）

**响应**：
```json
[
  {
    "id": "source-uuid",
    "name": "36氪",
    "url": "https://36kr.com/feed",
    "source_type": "rss",
    "industry": "tech",
    "enabled": true,
    "fetch_interval_hours": 24,
    "last_fetched_at": "2026-01-29T12:00:00"
  }
]
```

#### POST /api/config/sources

创建新信息源。

**请求体**：
```json
{
  "name": "新源",
  "url": "https://example.com/feed",
  "source_type": "rss",
  "industry": "ai",
  "enabled": true,
  "fetch_interval_hours": 24
}
```

**响应**：创建的 Source 对象

#### PUT /api/config/sources/{source_id}

更新信息源。

**请求体**：完整的 Source 对象

**响应**：更新后的 Source 对象

#### GET /api/config/llm-backends

获取支持的 LLM 后端列表。

**响应**：
```json
{
  "backends": [
    {
      "id": "ollama",
      "name": "Ollama (本地)",
      "requires_api_key": false,
      "cost": 0.0
    },
    {
      "id": "deepseek",
      "name": "DeepSeek",
      "requires_api_key": true,
      "cost": 0.00014
    }
  ]
}
```

---

### 6. 系统信息

#### GET /

根路径，返回 API 信息。

**响应**：
```json
{
  "name": "NewsGap API",
  "version": "0.1.0",
  "status": "running"
}
```

#### GET /health

健康检查。

**响应**：
```json
{
  "status": "healthy"
}
```

---

## 错误处理

所有错误响应遵循以下格式：

```json
{
  "detail": "错误描述信息"
}
```

常见 HTTP 状态码：
- `200 OK` - 成功
- `400 Bad Request` - 请求参数错误
- `404 Not Found` - 资源不存在
- `500 Internal Server Error` - 服务器内部错误

**示例**：
```json
{
  "detail": "未找到文章 abc123"
}
```

---

## 数据模型

### Article

```typescript
{
  id: string
  title: string
  url: string
  source_id?: string
  source_name?: string
  content: string
  summary?: string
  industry: "ai" | "tech" | "finance" | ...
  tags: string[]
  published_at: string  // ISO 8601
  fetched_at: string
  author?: string
  language: string
  word_count?: number
  archived: boolean
  archived_at?: string
}
```

### Analysis

```typescript
{
  id: string
  analysis_type: "trend" | "signal" | "gap" | "brief" | "comprehensive"
  article_ids: string[]
  executive_brief: string
  trends: Trend[]
  signals: Signal[]
  information_gaps: InformationGap[]
  llm_backend: string
  llm_model?: string
  token_usage?: number
  estimated_cost?: number
  created_at: string
  processing_time_seconds?: number
}
```

### Trend

```typescript
{
  title: string
  description: string
  confidence: number  // 0-1
  supporting_article_ids: string[]
  keywords: string[]
}
```

---

## 速率限制

当前版本无速率限制。

## WebSocket

当前版本不支持 WebSocket。未来可能添加实时更新。

## 批量操作

大多数端点支持批量操作（如批量分析、批量导出）。

## 版本控制

API 版本通过 URL 路径指定。当前为 v1（隐式）。

未来版本示例：`/api/v2/articles`

---

更多信息请参考源代码或联系开发者。
