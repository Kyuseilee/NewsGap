# NewsGap - 信息差情报工具

**NewsGap** 是一个自动化的信息情报系统，帮助你快速收集、归档和分析行业信息，发现关键趋势和信息差。

## ✨ 核心特性

- **🔍 自动爬取**：从 RSS 和网页源自动抓取最新行业资讯
- **💾 智能存储**：SQLite 本地数据库 + Markdown 归档
- **🤖 AI 分析**：支持多种 LLM 后端（Ollama/OpenAI/DeepSeek/Gemini）
- **📊 趋势检测**：自动识别跨文章的趋势和信号
- **🎯 信息差识别**：发现信息空白和矛盾
- **🖥️ 桌面应用**：React + Tauri 跨平台桌面 GUI

## 🏗️ 架构设计

### 系统架构

```
NewsGap/
├── backend/          # Python FastAPI 后端
│   ├── crawler/      # 爬取模块（RSS + 网页）
│   ├── storage/      # 存储模块（SQLite + 归档）
│   ├── llm/          # LLM 适配器（可插拔）
│   ├── routes/       # API 路由
│   └── main.py       # FastAPI 应用
│
├── frontend/         # React + Vite 前端
│   ├── src/
│   │   ├── pages/    # 页面组件
│   │   ├── services/ # API 客户端
│   │   └── types/    # TypeScript 类型
│   └── package.json
│
├── data/             # 数据库文件
├── archives/         # Markdown 归档
└── README.md
```

### 核心原则

- ✅ **严格模块分离**：爬取 ≠ 分析 ≠ UI ≠ 存储
- ✅ **用户显式控制**：无自动化，每步独立可触发
- ✅ **成本意识**：LLM 分析前展示成本预估
- ✅ **可插拔 LLM**：统一接口支持多种后端

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- Node.js 18+
- SQLite 3

### 2. 后端安装

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选）
export DEEPSEEK_API_KEY=your_api_key
export OPENAI_API_KEY=your_api_key
export GEMINI_API_KEY=your_api_key

# 启动后端
python main.py
```

后端将在 `http://localhost:8000` 运行

### 3. 前端安装

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 运行

### 4. 使用

1. 打开浏览器访问 `http://localhost:5173`
2. 在首页选择行业和时间范围
3. 点击"一键情报"或"仅爬取"
4. 查看文章列表和分析结果

## 📖 功能说明

### 工作流程

#### 方式 1：分步执行
1. 选择行业 + 时间范围
2. 点击"仅爬取" → 获取文章列表
3. 浏览文章内容
4. 选择文章进行分析

#### 方式 2：一键情报
1. 选择行业 + LLM 后端
2. 点击"一键情报"
3. 自动爬取并生成情报摘要

### LLM 后端配置

| 后端 | 描述 | API Key | 成本 |
|------|------|---------|------|
| Ollama | 本地模型 | 不需要 | 免费 |
| DeepSeek | DeepSeek API | 需要 | $0.14/1M tokens |
| OpenAI | ChatGPT | 需要 | $0.15/1M tokens |
| Gemini | Google Gemini | 需要 | 免费（有限额） |

### 信息源管理

在"设置"页面可以：
- 添加新的 RSS 源
- 启用/禁用信息源
- 配置爬取频率

默认已包含示例源（36氪、少数派、机器之心）。

## 🔧 配置

编辑 `backend/config.yaml`：

```yaml
llm:
  default_backend: deepseek
  
database:
  path: ./data/newsgap.db

archive:
  path: ./archives

crawler:
  default_fetch_hours: 24
  timeout_seconds: 30
```

## 📊 API 文档

### 主要端点

```
POST /api/fetch          # 爬取文章
POST /api/analyze        # 分析文章
POST /api/intelligence   # 一键情报
GET  /api/articles       # 获取文章列表
GET  /api/config/sources # 获取信息源
```

完整 API 文档见 [docs/api.md](docs/api.md)

## 🧪 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

## 📦 打包部署

### 方式 1：Docker

```bash
docker-compose up -d
```

### 方式 2：独立部署

后端：
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

前端：
```bash
cd frontend
npm run build
# 生成的静态文件在 dist/ 目录
```

## 🛠️ 技术栈

### 后端
- **FastAPI** - 现代 Python Web 框架
- **SQLite** - 轻量级数据库
- **aiosqlite** - 异步 SQLite 访问
- **httpx** - 异步 HTTP 客户端
- **feedparser** - RSS 解析
- **readability-lxml** - 网页正文提取

### 前端
- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **TanStack Query** - 数据获取
- **Tailwind CSS** - 样式框架
- **Zustand** - 状态管理

### LLM
- **OpenAI SDK** - OpenAI/DeepSeek API
- **google-generativeai** - Gemini API
- **httpx** - Ollama 本地模型

## 🗺️ 路线图

### MVP (当前)
- [x] 核心爬取功能
- [x] LLM 分析集成
- [x] 基础 GUI
- [x] SQLite 存储
- [x] Markdown 归档

### v0.2
- [ ] Tauri 桌面打包
- [ ] 完善分析页面
- [ ] 归档管理 UI
- [ ] 单元测试覆盖

### v0.3
- [ ] 自定义分析模板
- [ ] 趋势可视化
- [ ] 批量导出
- [ ] 多语言支持

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有开源项目的贡献者。

---

**注意**：这是一个情报分析工具，请遵守相关网站的 robots.txt 和使用条款。
