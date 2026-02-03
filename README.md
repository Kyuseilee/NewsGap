# NewsGap - 决策导向型行业情报分析系统

<div align="center">

**NewsGap** 是一个智能化的行业情报分析系统，它不是新闻摘要器，而是帮助决策者在海量信息中快速识别**真正改变格局的少数信号**。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

[快速开始](#-快速部署) • [使用文档](#-使用指南) • [API 文档](#-api-文档) • [贡献指南](#-贡献指南)

</div>

---

## 📋 目录

- [核心特性](#-核心特性)
- [系统架构](#️-系统架构)
- [快速部署](#-快速部署)
  - [🚀 一键部署（推荐）](#-一键部署推荐)
  - [手动部署](#手动部署)
  - [环境要求](#环境要求)
  - [后端部署](#一后端部署)
  - [前端部署](#二前端部署)
  - [验证部署](#三验证部署)
- [使用指南](#-使用指南)
  - [一键情报](#方式-1一键情报推荐新手)
  - [分步执行](#方式-2分步执行精细控制)
  - [报告结构说明](#报告结构说明)
  - [LLM 后端选择](#llm-后端选择)
  - [信息源管理](#信息源管理)
- [RSSHub 集成](#-rsshub-集成可选但推荐)
  - [RSSHub 部署](#rsshub-部署推荐用于生产环境)
  - [集成到 NewsGap](#将-rsshub-集成到-newsgap)
  - [常用路由推荐](#常用-rsshub-路由推荐)
  - [管理命令](#rsshub-管理命令)
- [高级配置](#-高级配置)
- [API 文档](#-api-文档)
- [测试](#-测试)
- [生产部署](#-生产部署)
- [故障排查](#-故障排查)
- [技术栈](#️-技术栈)
- [开发路线图](#️-开发路线图)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)
- [致谢](#-致谢)
- [联系与支持](#-联系与支持)

---

## ✨ 核心特性

- **🎯 信号优先**：残忍筛选，只聚焦改变判断的 20-30% 关键信息
- **🧠 决策导向**：为理性决策者提供可行动、可取舍、可忽略的信息结构
- **🔍 智能爬取**：54+ 官方 RSS 源，覆盖科技、财经、开发者等多行业
- **🤖 AI 分析**：支持多种 LLM 后端（Gemini 2.5 Flash/DeepSeek/OpenAI/Ollama）
- **📊 主线聚合**：自动识别 3-5 条今日主线叙事，避免信息过载
- **💾 本地优先**：SQLite 数据库 + Markdown 归档，数据完全自主可控
- **🖥️ Web UI**：React + FastAPI 现代化 Web 应用

## 🏗️ 系统架构

### 分析哲学

NewsGap 采用**信号优先**的情报分析方法：

```
传统新闻摘要器                NewsGap 决策导向分析
━━━━━━━━━━━━━━━━            ━━━━━━━━━━━━━━━━━━━━
143篇文章 → 143条摘要         143篇文章 → 残忍筛选
均匀评分 (7/10, 8/10)         → 20-30篇核心信息
8000字报告                    → 3-5条主线叙事
30分钟阅读                    → 2000字报告
                              → 3-5分钟阅读
```

### 5 大核心原则

1. **残忍筛选原则**：允许忽略、合并、弱化大量低价值内容
2. **主线优先原则**：先识别 3-5 条主线叙事，其他文章只是证据或噪音
3. **去均值原则**：重要性形成明显梯度（10/8/5/忽略），避免模糊评分
4. **决策视角原则**：假设读者关注宏观风险、产业方向与中长期配置
5. **压缩优先原则**：信息密度 > 覆盖率，宁可少写一半也不降低密度

### 技术架构

```
NewsGap/
├── backend/          # Python FastAPI 后端
│   ├── crawler/      # 爬取模块（RSS + 网页）
│   ├── storage/      # 存储模块（SQLite + 归档）
│   ├── llm/          # LLM 适配器（可插拔）
│   │   ├── adapter.py          # 基础适配器 + 决策导向 Prompt
│   │   └── gemini_adapter.py   # Gemini 2.5 Flash 适配器
│   ├── routes/       # API 路由
│   ├── analyzer.py   # 分析逻辑编排
│   ├── models.py     # 数据模型
│   ├── official_rss_sources.py  # 54+ 官方信息源
│   └── main.py       # FastAPI 应用
│
├── frontend/         # React + Vite 前端
│   ├── src/
│   │   ├── pages/    # 页面组件
│   │   ├── services/ # API 客户端
│   │   └── types/    # TypeScript 类型
│   └── package.json
│
├── data/             # SQLite 数据库
├── archives/         # Markdown 归档
└── README.md
```

### 设计原则

- ✅ **严格模块分离**：爬取 ≠ 分析 ≠ UI ≠ 存储
- ✅ **用户显式控制**：无自动化，每步独立可触发
- ✅ **成本意识**：LLM 分析前展示 Token 预估
- ✅ **可插拔 LLM**：统一接口支持多种后端
- ✅ **本地优先**：数据存储本地，完全自主可控

## 🚀 快速部署

### 🎯 一键部署（推荐）

最简单的方式！只需三步：

```bash
# 1. 克隆项目
git clone <repository-url>
cd NewsGap

# 2. 一键部署（安装所有依赖，初始化数据库）
./deploy.sh

# 3. 一键启动（前后端同时启动）
./start.sh
```

启动成功后，访问 http://localhost:5173 即可使用！

**常用命令**：
```bash
./start.sh   # 启动服务（后台运行）
./stop.sh    # 停止服务
./status.sh  # 查看状态
```

📖 **详细说明**: 查看 [QUICK_START.md](QUICK_START.md)

---

### 📝 手动部署

如果你想手动控制每一步，或者一键脚本遇到问题，可以使用手动部署：

### 环境要求

- **Python**: 3.10+
- **Node.js**: 18+
- **SQLite**: 3.x（Python 自带）
- **系统**: macOS/Linux/Windows

### 一、后端部署

#### 1. 克隆项目并进入后端目录

```bash
git clone <repository-url>
cd NewsGap/backend
```

#### 2. 创建并激活 Python 虚拟环境

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

核心依赖包括：
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `aiosqlite` - 异步 SQLite
- `httpx` - 异步 HTTP 客户端
- `feedparser` - RSS 解析
- `google-generativeai` - Gemini API (推荐)
- `openai` - OpenAI/DeepSeek API

#### 4. 配置 LLM API Key（必需）

选择以下任一方式：

**方式 1: 环境变量（推荐）**

```bash
# 使用 Gemini（推荐，免费额度大）
export GEMINI_API_KEY="your-gemini-api-key"
export LLM_PROVIDER="gemini"

# 或使用 DeepSeek（性价比高）
export DEEPSEEK_API_KEY="sk-your-deepseek-key"
export LLM_PROVIDER="deepseek"

# 或使用 OpenAI
export OPENAI_API_KEY="sk-your-openai-key"
export LLM_PROVIDER="openai"

# 或使用本地 Ollama（完全免费）
export LLM_PROVIDER="ollama"
# 确保 Ollama 服务运行在 http://localhost:11434
```

**方式 2: 创建 `.env` 文件**

```bash
# backend/.env
GEMINI_API_KEY=your-gemini-api-key
LLM_PROVIDER=gemini
```

**获取 API Key**：
- **Gemini**: https://ai.google.dev/ （推荐，免费额度充足）
- **DeepSeek**: https://platform.deepseek.com/
- **OpenAI**: https://platform.openai.com/
- **Ollama**: https://ollama.com/ （本地部署，无需 API Key）

#### 5. 启动后端服务

```bash
python main.py
```

成功启动后会看到：

```
INFO:     Started server process [xxxxx]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
✓ 已有 54 个信息源
```

后端 API 地址: `http://localhost:8000`
API 文档: `http://localhost:8000/docs` (FastAPI 自动生成)

### 二、前端部署

#### 1. 打开新终端，进入前端目录

```bash
cd NewsGap/frontend
```

#### 2. 安装 Node.js 依赖

```bash
npm install
```

#### 3. 启动开发服务器

```bash
npm run dev
```

成功启动后会看到：

```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

前端访问地址: `http://localhost:5173`

### 三、验证部署

打开浏览器访问 `http://localhost:5173`，你应该看到：

1. ✅ 页面正常加载
2. ✅ 右上角显示"设置"按钮
3. ✅ 可以选择行业类别
4. ✅ 可以看到"一键情报"按钮

**首次使用测试**：

1. 选择行业（如"科技"）
2. 点击"一键情报"
3. 等待 10-30 秒
4. 查看生成的情报报告

如果看到报告生成，说明部署成功！🎉

## 📖 使用指南

### 工作流程

#### 方式 1：一键情报（推荐新手）

这是最简单的使用方式，适合快速获取行业洞察：

```
选择行业 → 点击"一键情报" → 等待分析 → 查看报告
```

**详细步骤**：

1. **选择行业**: 从下拉菜单选择（科技/财经/开发者/AI/综合）
2. **选择时间范围**: 默认 24 小时（可选 12h/24h/48h/7d）
3. **点击"一键情报"**: 系统自动执行：
   - 爬取最新文章（54 个信息源）
   - AI 分析并生成报告
4. **查看报告**: 包含：
   - 📊 执行摘要（3-5 条核心要点）
   - 📈 今日主线叙事（3-5 条，含证据链）
   - 🎯 关键信号清单（高/中/低置信度）
   - 🗑️ 被过滤掉的内容（说明为何不重要）
   - ✅ 行动提示（风险规避/机会布局/信息跟踪）

#### 方式 2：分步执行（精细控制）

适合需要精确控制的用户：

```
Step 1: 仅爬取 → 浏览文章列表 → 手动筛选
Step 2: 选择文章 → 自定义 Prompt → 生成分析
```

**详细步骤**：

1. **仅爬取**: 点击"仅爬取"按钮获取文章列表
2. **浏览文章**: 查看标题、来源、摘要
3. **筛选文章**: 勾选感兴趣的文章
4. **自定义分析**: 
   - 选择分析类型（综合/趋势/信号/简报）
   - 输入自定义 Prompt（可选）
5. **生成报告**: 点击"分析选中文章"

### 报告结构说明

生成的情报报告包含以下部分：

#### 一、执行摘要（给只读 3 分钟的人）
- 今天真正发生了什么"结构性变化"
- 哪些风险在上升，哪些只是噪音
- 哪些方向值得持续跟踪

#### 二、今日主线叙事（最多 5 条）
每条主线包含：
- **核心判断**: 这条主线意味着什么
- **关键信号**: 哪些事件支撑判断（引用文章编号）
- **被忽略的反证**: 相反信息及其权重
- **影响半径**: 影响范围（国家/行业/资产/群体）

#### 三、关键信号清单
只列真正值得"盯住"的信号：
- **类型**: 地缘政治/产业/政策/技术
- **为何重要**: 改变了什么"默认假设"
- **置信度**: 高/中/低
- **跟踪建议**: 接下来应关注什么

#### 四、被过滤掉的内容
- 哪几类信息今天占比很高但价值有限
- 为什么不值得投入注意力

#### 五、行动提示
- **风险规避**: 应该避免什么
- **机会布局**: 应该关注什么
- **信息跟踪**: 应该持续监控什么

### LLM 后端选择

| 后端 | 推荐场景 | 成本 | 配置难度 | 速度 |
|------|---------|------|---------|------|
| **Gemini 2.5 Flash** | ✅ 推荐首选 | 免费（每天 1500 次） | 简单 | 快 |
| **DeepSeek** | 高频使用 | $0.14/1M tokens | 简单 | 快 |
| **OpenAI** | 追求最佳质量 | $0.15/1M tokens | 简单 | 中 |
| **Ollama** | 完全离线/隐私要求 | 免费 | 中等 | 慢 |

**推荐配置**：
- **个人学习**: Gemini（免费额度充足）
- **企业使用**: DeepSeek（性价比最高）
- **隐私敏感**: Ollama（完全本地）

### 信息源管理

系统内置 **54 个高质量官方 RSS 源**，覆盖：

- **科技媒体**: 36氪、少数派、IT之家、爱范儿、虎嗅等
- **AI/ML**: 机器之心、AI前线、Hugging Face Blog
- **开发者**: V2EX、掘金、开源中国、GitHub Blog
- **财经**: 华尔街日报、彭博社、财新、第一财经
- **国际媒体**: BBC中文、纽约时报中文、路透社、美联社
- **产品/设计**: Product Hunt、Hacker News

**在"设置"页面可以**：
- ✅ 查看所有 54 个信息源
- ✅ 启用/禁用特定源
- ✅ 添加自定义 RSS 源
- ✅ 设置爬取频率
- ✅ 配置 API Key

**添加自定义源**：
```python
# 在 official_rss_sources.py 中添加
Source(
    name="你的信息源名称",
    url="https://example.com/feed.xml",
    source_type=SourceType.RSS,
    priority=SourcePriority.OFFICIAL_RSS,
    industry=IndustryCategory.TECH,
    enabled=True
)
```

## 🔌 RSSHub 集成（可选但推荐）

### 什么是 RSSHub？

**RSSHub** 是一个开源的万物皆可 RSS 的项目，可以为**任何网站**生成 RSS 订阅源。通过集成 RSSHub，NewsGap 可以：

- ✅ 订阅不提供 RSS 的网站（如微博、知乎、B站）
- ✅ 避免公共实例的频率限制和不稳定性
- ✅ 自定义配置和缓存策略
- ✅ 扩展到 **1000+ 网站支持**

### RSSHub 部署（推荐用于生产环境）

#### 方式 1: Docker 快速部署（推荐）

项目已包含 `docker-compose.yml`，一键启动：

```bash
# 在项目根目录执行
docker-compose up -d

# 验证服务
docker-compose ps
curl http://localhost:1200
```

服务说明：
- **RSSHub 服务**: `http://localhost:1200`
- **容器名称**: `newsgap-rsshub`
- **缓存类型**: 内存缓存（可选 Redis）

#### 方式 2: 启用 Redis 缓存（性能优化）

编辑 `docker-compose.yml`，取消 Redis 相关注释：

```yaml
services:
  rsshub:
    environment:
      CACHE_TYPE: redis
      REDIS_URL: 'redis://redis:6379/'
    depends_on:
      - redis

  redis:
    image: redis:alpine
    container_name: newsgap-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data
    networks:
      - newsgap-network

volumes:
  redis-data:
```

然后重启：
```bash
docker-compose down
docker-compose up -d
```

#### 高级配置（可选）

创建 `.env.rsshub` 文件进行高级配置：

```bash
# 访问控制（推荐生产环境）
ACCESS_KEY=your_secure_random_key

# 代理配置（访问被墙网站）
PROXY_URI=socks5h://127.0.0.1:1080
PROXY_URL_REGEX=twitter\.com|youtube\.com

# GitHub Token（提高访问频率）
GITHUB_ACCESS_TOKEN=ghp_your_github_token

# 缓存配置
CACHE_EXPIRE=3600

# 请求重试
REQUEST_RETRY=2
```

修改 `docker-compose.yml` 加载环境变量：
```yaml
services:
  rsshub:
    env_file:
      - .env.rsshub
```

### 将 RSSHub 集成到 NewsGap

#### 1. 在设置页面添加 RSSHub 源

访问 `http://localhost:5173/settings`，添加新源：

- **名称**: GitHub Trending Python
- **URL**: `http://localhost:1200/github/trending/daily/python`
- **类型**: RSS
- **行业**: 科技

#### 2. 通过配置文件批量添加

编辑 `backend/official_rss_sources.py`，添加 RSSHub 路由：

```python
# RSSHub 本地实例源
RSSHUB_LOCAL_SOURCES = [
    Source(
        name="知乎热榜",
        url="http://localhost:1200/zhihu/hotlist",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.TECH,
        enabled=True
    ),
    Source(
        name="微博热搜",
        url="http://localhost:1200/weibo/search/hot",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.SOCIAL,
        enabled=True
    ),
    Source(
        name="GitHub Trending",
        url="http://localhost:1200/github/trending/daily",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.DEVELOPER,
        enabled=True
    ),
    Source(
        name="36氪快讯",
        url="http://localhost:1200/36kr/newsflashes",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.BUSINESS,
        enabled=True
    ),
    Source(
        name="B站科技区",
        url="http://localhost:1200/bilibili/ranking/0/188/3",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.TECH,
        enabled=True
    ),
]
```

#### 3. 从公共实例迁移到本地

如果之前使用公共 RSSHub 实例（`https://rsshub.app`），批量替换为本地地址：

```bash
# 使用 SQLite 批量更新
sqlite3 backend/data/newsgap.db "
UPDATE sources 
SET url = REPLACE(url, 'https://rsshub.app', 'http://localhost:1200')
WHERE url LIKE '%rsshub.app%';
"
```

### 常用 RSSHub 路由推荐

#### 社交媒体
```
知乎热榜:     http://localhost:1200/zhihu/hotlist
微博热搜:     http://localhost:1200/weibo/search/hot
微博用户:     http://localhost:1200/weibo/user/1195230310
```

#### 开发者
```
GitHub Trending:        http://localhost:1200/github/trending/daily/python
GitHub 仓库 Issues:     http://localhost:1200/github/issue/DIYgod/RSSHub
Hacker News:            http://localhost:1200/hackernews
```

#### 视频平台
```
B站UP主:      http://localhost:1200/bilibili/user/video/2267573
B站排行榜:    http://localhost:1200/bilibili/ranking/0/3/1
YouTube频道:  http://localhost:1200/youtube/user/@channel_id
```

#### 科技媒体
```
36氪快讯:     http://localhost:1200/36kr/newsflashes
虎嗅网:       http://localhost:1200/huxiu/article
少数派专栏:   http://localhost:1200/sspai/series/70
```

#### AI/ML
```
机器之心:     http://localhost:1200/jiqizhixin
量子位:       http://localhost:1200/qbitai
AI前线:       http://localhost:1200/infoq/ai
```

**完整路由列表**: https://docs.rsshub.app/routes/

### RSSHub 管理命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f rsshub

# 重启服务
docker-compose restart rsshub

# 停止服务
docker-compose stop

# 更新 RSSHub 到最新版
docker-compose pull rsshub
docker-compose up -d

# 完全清理（包括缓存）
docker-compose down -v
```

### RSSHub 故障排查

#### 问题 1: 端口冲突

```bash
# 检查端口占用
lsof -i :1200

# 修改 docker-compose.yml
ports:
  - "1201:1200"  # 使用其他端口
```

#### 问题 2: 无法访问某些网站

- 检查是否需要配置代理（`.env.rsshub` 中配置 `PROXY_URI`）
- 查看日志了解具体错误: `docker-compose logs -f rsshub | grep ERROR`

#### 问题 3: 响应慢

- 启用 Redis 缓存（见上文）
- 增加缓存时间: `CACHE_EXPIRE=7200`（2小时）
- 使用代理加速国外网站访问

#### 问题 4: 频率限制

RSSHub 本地部署**没有频率限制**。如果遇到目标网站限制，可以：
- 调整缓存时间减少请求
- 配置 `REQUEST_RETRY`
- 使用代理 IP 池

### 为什么推荐自建 RSSHub？

| 对比项 | 公共实例 | 本地部署 |
|--------|---------|---------|
| **稳定性** | ⚠️ 不稳定，经常宕机 | ✅ 完全可控 |
| **速度** | ⚠️ 慢，共享带宽 | ✅ 本地访问，极快 |
| **频率限制** | ❌ 514 错误频繁 | ✅ 无限制 |
| **隐私** | ⚠️ 请求经过第三方 | ✅ 完全本地 |
| **自定义** | ❌ 无法配置 | ✅ 完全可定制 |
| **成本** | 免费 | 免费（仅需 Docker） |

**建议**: 
- **学习/测试**: 可以先用公共实例（`https://rsshub.app`）
- **生产/个人**: 强烈推荐自建（5 分钟部署，一劳永逸）

### RSSHub 参考资源

- 📖 **官方文档**: https://docs.rsshub.app/
- 🗺️ **路由大全**: https://docs.rsshub.app/routes/
- 🔧 **配置指南**: https://docs.rsshub.app/deploy/config
- 💻 **GitHub 仓库**: https://github.com/DIYgod/RSSHub
- 🎓 **部署教程**: https://docs.rsshub.app/install/



## 🔧 高级配置

### 编辑配置文件

编辑 `backend/config.yaml`：

```yaml
llm:
  default_backend: gemini
  
database:
  path: ./data/newsgap.db

archive:
  path: ./archives

crawler:
  default_fetch_hours: 24
  timeout_seconds: 30
```

### 自定义 Prompt 策略

如果你想调整分析策略，可以编辑：

**文件**: `backend/llm/adapter.py`

核心 Prompt 位于 `_build_system_prompt()` 方法中，包含：
- 分析哲学（决策导向 vs 新闻摘要）
- 5 大核心原则
- 允许的操作（合并、忽略、弱化）
- 输出要求

**文件**: `backend/llm/adapter.py` 中的 `_build_markdown_prompt()`

动态压缩策略：
```python
if article_count <= 20:
    max_content = 1000  # 少量文章，保留更多细节
elif article_count <= 50:
    max_content = 600
elif article_count <= 100:
    max_content = 400
else:
    max_content = 300   # 大量文章，极限压缩
```

### 性能优化

**1. 调整爬取并发数**：

编辑 `backend/crawler/rss_crawler.py`：
```python
# 默认并发 10 个请求
semaphore = asyncio.Semaphore(10)
```

**2. 调整 LLM Token 限制**：

编辑 `backend/llm/gemini_adapter.py`：
```python
generation_config=genai.types.GenerationConfig(
    max_output_tokens=8192,  # 增加输出长度
    temperature=0.3,
)
```

**3. 数据库性能**：

```bash
# 定期优化数据库
cd backend
sqlite3 data/newsgap.db "VACUUM;"
```

## 📊 API 文档

### 核心 API 端点

#### 1. 一键情报分析

```bash
POST /api/intelligence
Content-Type: application/json

{
  "industry": "tech",           # 行业类别
  "hours": 24,                  # 时间范围
  "llm_backend": "gemini",      # LLM 后端
  "api_key": "your-api-key",    # API Key（可选，优先使用环境变量）
  "model": "gemini-2.5-flash",  # 模型名称（可选）
  "custom_prompt": "..."        # 自定义 Prompt（可选）
}
```

**响应**：
```json
{
  "report": "# 📊 行业情报分析报告\n...",
  "articles_count": 143,
  "analysis_time": "2026-01-30 10:30",
  "token_usage": {
    "input_tokens": 15234,
    "output_tokens": 2456,
    "total_tokens": 17690
  }
}
```

#### 2. 仅爬取文章

```bash
POST /api/fetch
Content-Type: application/json

{
  "industry": "tech",
  "hours": 24
}
```

#### 3. 分析现有文章

```bash
POST /api/analyze
Content-Type: application/json

{
  "article_ids": [1, 5, 12, 34],
  "analysis_type": "comprehensive",
  "llm_backend": "gemini",
  "custom_prompt": "..."
}
```

#### 4. 获取文章列表

```bash
GET /api/articles?industry=tech&hours=24&limit=100
```

#### 5. 获取信息源列表

```bash
GET /api/config/sources
```

#### 6. 更新信息源状态

```bash
PUT /api/config/sources/{source_id}
Content-Type: application/json

{
  "enabled": true
}
```

### API 交互示例

**使用 curl**:
```bash
# 一键情报
curl -X POST http://localhost:8000/api/intelligence \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "tech",
    "hours": 24,
    "llm_backend": "gemini"
  }'

# 仅爬取
curl -X POST http://localhost:8000/api/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "tech",
    "hours": 24
  }'
```

**使用 Python**:
```python
import requests

# 一键情报
response = requests.post(
    "http://localhost:8000/api/intelligence",
    json={
        "industry": "tech",
        "hours": 24,
        "llm_backend": "gemini"
    }
)
report = response.json()["report"]
print(report)
```

完整 API 文档: `http://localhost:8000/docs` (FastAPI 自动生成)

## 🧪 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_crawler.py
pytest tests/test_analyzer.py

# 查看测试覆盖率
pytest --cov=. --cov-report=html
```

### 前端测试

```bash
cd frontend

# 运行单元测试
npm test

# 运行 E2E 测试
npm run test:e2e
```

### 手动测试检查清单

- [ ] 后端成功启动并显示"✓ 已有 54 个信息源"
- [ ] 前端页面正常加载
- [ ] 可以选择行业并点击"仅爬取"
- [ ] 爬取成功返回文章列表
- [ ] 可以选择 LLM 后端
- [ ] 一键情报生成完整报告
- [ ] 报告包含所有 5 个部分（摘要、主线、信号、过滤内容、行动提示）
- [ ] 可以在设置页面查看和管理信息源

## 📦 生产部署

### 方式 1: Docker 部署（推荐）

#### 1. 创建 Dockerfile

**后端 Dockerfile** (`backend/Dockerfile`):
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**前端 Dockerfile** (`frontend/Dockerfile`):
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### 2. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - LLM_PROVIDER=gemini
    volumes:
      - ./data:/app/data
      - ./archives:/app/archives
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

#### 3. 启动服务

```bash
# 设置环境变量
export GEMINI_API_KEY="your-api-key"

# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 方式 2: 传统部署

#### 后端部署（生产模式）

```bash
cd backend

# 使用 uvicorn 生产模式
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info

# 或使用 gunicorn + uvicorn
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

#### 前端部署（Nginx）

```bash
cd frontend

# 构建生产版本
npm run build

# 生成的静态文件在 dist/ 目录
```

**Nginx 配置** (`/etc/nginx/sites-available/newsgap`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    root /path/to/NewsGap/frontend/dist;
    index index.html;

    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### 使用 Systemd 管理后端服务

创建 `/etc/systemd/system/newsgap-backend.service`:

```ini
[Unit]
Description=NewsGap Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/NewsGap/backend
Environment="PATH=/path/to/NewsGap/backend/venv/bin"
Environment="GEMINI_API_KEY=your-api-key"
Environment="LLM_PROVIDER=gemini"
ExecStart=/path/to/NewsGap/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable newsgap-backend
sudo systemctl start newsgap-backend
sudo systemctl status newsgap-backend
```

### 方式 3: Serverless 部署（未来支持）

计划支持：
- Vercel (前端)
- Railway/Render (后端)
- AWS Lambda (无服务器)

## 🐛 故障排查

### 常见问题

#### 1. 后端启动失败

**症状**: `Address already in use` 或 `ModuleNotFoundError`

**解决**:
```bash
# 检查端口占用
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 杀死占用进程
kill -9 <PID>

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

#### 2. LLM 分析失败

**症状**: `API key invalid` 或 `Timeout`

**解决**:
```bash
# 验证 API Key
echo $GEMINI_API_KEY

# 测试 API 连接
curl -H "Authorization: Bearer $GEMINI_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models

# 检查网络（如在中国大陆，Gemini 可能需要代理）
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
```

#### 3. 爬取失败

**症状**: `SSL: WRONG_VERSION_NUMBER` 或 `Connection timeout`

**解决**:
```bash
# 检查网络连接
ping rsshub.app
curl -I https://36kr.com/feed

# 禁用失败的信息源
# 在设置页面手动禁用，或编辑数据库：
sqlite3 data/newsgap.db "UPDATE sources SET enabled=0 WHERE name='BBC中文';"
```

#### 4. 前端无法连接后端

**症状**: `Network Error` 或 `CORS Error`

**解决**:
```bash
# 检查后端是否运行
curl http://localhost:8000/api/config/sources

# 检查前端 vite.config.ts 中的 proxy 配置
# 确保 proxy.target 指向 http://localhost:8000
```

#### 5. 数据库锁定

**症状**: `database is locked`

**解决**:
```bash
# 关闭所有访问数据库的进程
pkill -f "python main.py"

# 清理 WAL 文件
rm data/newsgap.db-wal data/newsgap.db-shm

# 重启后端
python main.py
```

### 日志查看

**后端日志**:
```bash
# 开发模式（终端直接输出）
python main.py

# 生产模式（保存到文件）
python main.py > logs/backend.log 2>&1
tail -f logs/backend.log
```

**前端日志**:
- 浏览器开发者工具 → Console
- Network 标签查看 API 请求

### 性能问题

**症状**: 分析速度慢、内存占用高

**解决**:
```bash
# 1. 减少爬取时间范围
# 从 24h 改为 12h

# 2. 减少并发请求数
# 编辑 backend/crawler/rss_crawler.py
# semaphore = asyncio.Semaphore(5)  # 从 10 改为 5

# 3. 启用数据库索引
sqlite3 data/newsgap.db "CREATE INDEX IF NOT EXISTS idx_published_at ON articles(published_at);"

# 4. 清理旧数据
sqlite3 data/newsgap.db "DELETE FROM articles WHERE published_at < datetime('now', '-30 days');"
```

## 🛠️ 技术栈

### 后端技术
- **FastAPI** - 高性能 Python Web 框架
- **SQLite + aiosqlite** - 轻量级异步数据库
- **httpx** - 现代异步 HTTP 客户端
- **feedparser** - RSS/Atom 解析器
- **readability-lxml** - 网页正文提取
- **google-generativeai** - Gemini API SDK
- **openai** - OpenAI/DeepSeek API SDK

### 前端技术
- **React 18** - 声明式 UI 框架
- **TypeScript** - 类型安全的 JavaScript
- **Vite** - 下一代前端构建工具
- **TanStack Query** - 强大的数据获取和缓存
- **Tailwind CSS** - 实用优先的 CSS 框架
- **Zustand** - 轻量级状态管理

### AI/LLM 集成
- **Gemini 2.5 Flash** - Google 最新多模态模型（推荐）
- **DeepSeek** - 高性价比中文优化模型
- **OpenAI GPT** - 行业标准 LLM
- **Ollama** - 本地开源模型运行时

## 🗺️ 开发路线图

### ✅ v0.1 (当前版本)
- [x] 54 个官方 RSS 源集成
- [x] 决策导向型 Prompt 系统
- [x] 多 LLM 后端支持（Gemini/DeepSeek/OpenAI/Ollama）
- [x] 动态压缩策略（20/50/100+ 文章）
- [x] SQLite 本地存储
- [x] Markdown 归档
- [x] React Web UI
- [x] 一键情报分析

### 🚧 v0.2 (开发中)
- [ ] Tauri 桌面应用打包
- [ ] 报告质量评分系统
- [ ] 历史报告对比功能
- [ ] 自定义信息源 UI 管理
- [ ] 导出功能（PDF/Markdown/JSON）
- [ ] 单元测试覆盖 80%+

### 🔮 v0.3 (计划中)
- [ ] 多用户系统
- [ ] 信号追踪看板（持续监控特定信号）
- [ ] 趋势可视化图表
- [ ] 自定义分析模板
- [ ] 批量分析历史数据
- [ ] 邮件/Webhook 通知
- [ ] 多语言支持（英文/中文）
- [ ] RAG 增强（向量数据库集成）

### 💡 未来愿景
- [ ] 移动应用（React Native）
- [ ] 协作功能（团队共享报告）
- [ ] API 开放平台
- [ ] 市场/插件生态
- [ ] 深度学习微调（Fine-tuning）

## 🤝 贡献指南

欢迎所有形式的贡献！

### 如何贡献

1. **Fork 项目**
2. **创建特性分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **提交 Pull Request**

### 贡献方向

- 🐛 **Bug 修复**: 修复已知问题
- ✨ **新功能**: 实现路线图中的功能
- 📝 **文档**: 改进文档和示例
- 🧪 **测试**: 增加测试覆盖率
- 🌐 **信息源**: 添加新的高质量 RSS 源
- 🎨 **UI/UX**: 改进用户界面和体验
- 🚀 **性能**: 优化爬取和分析速度

### 代码规范

**Python**:
```bash
# 使用 black 格式化
black backend/

# 使用 flake8 检查
flake8 backend/

# 类型检查
mypy backend/
```

**TypeScript/React**:
```bash
# 使用 ESLint
npm run lint

# 格式化
npm run format

# 类型检查
npm run type-check
```

## 📄 许可证

本项目采用 **MIT License** 开源。

查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

### 开源项目
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [React](https://react.dev/) - 用户界面构建库
- [Vite](https://vitejs.dev/) - 下一代前端工具
- [Tailwind CSS](https://tailwindcss.com/) - CSS 框架
- [Google Gemini](https://ai.google.dev/) - 强大的多模态 AI
- [RSSHub](https://docs.rsshub.app/) - 万物皆可 RSS

### 灵感来源
- [Hacker News](https://news.ycombinator.com/) - 技术资讯聚合
- [Product Hunt](https://www.producthunt.com/) - 产品发现平台
- [Feedly](https://feedly.com/) - RSS 阅读器
- [Inoreader](https://www.inoreader.com/) - 智能 RSS 服务

### 社区贡献者
感谢所有为 NewsGap 做出贡献的开发者！

## 📞 联系与支持

### 获取帮助
- 📖 **文档**: 查看 `docs/` 目录
- 💬 **讨论**: [GitHub Discussions](https://github.com/your-repo/discussions)
- 🐛 **Bug 报告**: [GitHub Issues](https://github.com/your-repo/issues)
- ✨ **功能建议**: [GitHub Issues](https://github.com/your-repo/issues)

### 社交媒体
- 🐦 **Twitter**: [@NewsGap_AI](https://twitter.com/NewsGap_AI)
- 📧 **邮件**: contact@newsgap.dev
- 💬 **Discord**: [加入社区](https://discord.gg/newsgap)

## ⚠️ 免责声明

1. **使用条款遵守**: 本工具用于个人学习和研究。使用时请遵守各信息源网站的服务条款和 robots.txt 规范。

2. **内容准确性**: AI 生成的分析报告仅供参考，不构成投资、法律或其他专业建议。请独立验证关键信息。

3. **数据隐私**: 所有数据默认存储在本地。使用第三方 LLM API 时，数据会发送到对应服务商。

4. **API 成本**: 使用付费 API（DeepSeek/OpenAI）会产生费用。建议先使用免费的 Gemini 或本地 Ollama 测试。

5. **法律责任**: 本项目开发者不对因使用本工具产生的任何直接或间接损失承担责任。

---

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone <repository-url>
cd NewsGap

# 2. 启动后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="your-api-key"
python main.py

# 3. 启动前端（新终端）
cd frontend
npm install
npm run dev

# 4. 访问 http://localhost:5173
```

**开始你的第一次情报分析** 🎉

---

<div align="center">

Made with ❤️ by NewsGap Contributors

[⬆ 回到顶部](#newsgap---决策导向型行业情报分析系统)

</div>
