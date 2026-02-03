# NewsGap - 决策导向型行业情报分析系统

<div align="center">

**NewsGap** 是一个智能化的行业情报分析系统，帮助决策者在海量信息中快速识别**真正改变格局的少数信号**。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)

[快速开始](#-快速开始) • [核心特性](#-核心特性) • [使用文档](#-使用指南) • [开发文档](docs/)

</div>

---

## ✨ 核心特性

- **🎯 信号优先** - 残忍筛选，只聚焦改变判断的关键信息
- **🧠 决策导向** - 提供可行动、可取舍的信息结构
- **🔍 智能爬取** - 支持 RSS/Web 多源爬取
- **🤖 AI 分析** - 支持多种 LLM（Gemini/DeepSeek/OpenAI/Ollama）
- **📊 主线聚合** - 自动识别核心叙事，避免信息过载
- **💾 本地优先** - SQLite + Markdown，数据完全自主可控
- **🖥️ Web UI** - React + FastAPI 现代化应用

## 🏗️ 系统架构

```
NewsGap/
├── backend/          # Python FastAPI 后端
│   ├── crawler/      # 爬取模块（RSS + 网页）
│   ├── storage/      # 存储模块（SQLite）
│   ├── llm/          # LLM 适配器
│   ├── routes/       # API 路由
│   └── main.py       # FastAPI 应用入口
│
├── frontend/         # React 前端
│   └── src/
│       ├── pages/    # 页面组件（首页/文章/分析/设置）
│       └── services/ # API 客户端
│
├── data/             # SQLite 数据库
└── docs/             # 详细文档
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.10+
- **Node.js**: 18+
- **系统**: macOS/Linux/Windows

### 一键部署（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd NewsGap

# 2. 一键部署（安装依赖 + 初始化数据库）
./deploy.sh

# 3. 配置 API Key（选择一个）
export GEMINI_API_KEY="your-gemini-api-key"        # 推荐，免费额度大
# 或
export DEEPSEEK_API_KEY="sk-your-deepseek-key"    # 性价比高

# 4. 一键启动
./start.sh

# 5. 访问应用
open http://localhost:5173
```

### 手动部署

<details>
<summary>点击展开手动部署步骤</summary>

#### 后端部署

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置 API Key
export GEMINI_API_KEY="your-api-key"

# 启动后端
python main.py
```

后端运行在 `http://localhost:8000`

#### 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 启动前端
npm run dev
```

前端运行在 `http://localhost:5173`

</details>

### 验证部署

1. 打开 `http://localhost:5173`
2. 选择行业类别（如"科技"）
3. 点击"一键情报"
4. 等待 10-30 秒查看生成的情报报告

## 📖 使用指南

### 方式 1：一键情报（推荐）

最简单的使用方式，适合快速获取行业洞察：

```
选择行业 → 点击"一键情报" → 等待分析 → 查看报告
```

**步骤：**
1. 选择行业（科技/财经/开发者等）
2. 选择时间范围（12h/24h/48h/7d）
3. 点击"一键情报"按钮
4. 查看生成的情报报告

### 方式 2：分步执行（精细控制）

适合需要精确控制的用户：

```
仅爬取 → 浏览文章 → 选择感兴趣的 → 自定义分析
```

**步骤：**
1. 点击"仅爬取"获取文章列表
2. 浏览并筛选文章
3. 勾选感兴趣的文章
4. 选择分析类型或输入自定义 Prompt
5. 点击"分析选中文章"

### 报告结构

生成的情报报告包含：

1. **执行摘要** - 3-5 条核心要点
2. **今日主线叙事** - 3-5 条主线，含证据链
3. **关键信号清单** - 高/中/低置信度分级
4. **被过滤内容** - 说明为何不重要
5. **行动提示** - 风险规避/机会布局/跟踪建议

## ⚙️ 配置说明

### LLM 后端选择

| 后端 | 推荐场景 | 成本 | 配置 |
|------|---------|------|------|
| **Gemini 2.5 Flash** | ✅ 首选 | 免费（1500次/天） | `GEMINI_API_KEY` |
| **DeepSeek** | 高频使用 | $0.14/1M tokens | `DEEPSEEK_API_KEY` |
| **OpenAI** | 最佳质量 | $0.15/1M tokens | `OPENAI_API_KEY` |
| **Ollama** | 完全离线 | 免费（本地） | 安装 Ollama |

**获取 API Key：**
- Gemini: https://ai.google.dev/
- DeepSeek: https://platform.deepseek.com/
- OpenAI: https://platform.openai.com/
- Ollama: https://ollama.com/

### 信息源管理

在"设置"页面可以：
- ✅ 查看所有信息源
- ✅ 启用/禁用特定源
- ✅ 添加自定义 RSS 源
- ✅ 管理自定义分类

## 🛠️ 常用命令

```bash
# 启动服务
./start.sh

# 停止服务
./stop.sh

# 查看状态
./status.sh

# 查看日志
tail -f logs/backend.log
tail -f logs/frontend.log
```

## 📊 API 文档

后端提供完整的 REST API：

- **FastAPI 文档**: http://localhost:8000/docs
- **核心端点**:
  - `POST /api/intelligence` - 一键情报分析
  - `POST /api/fetch` - 仅爬取文章
  - `POST /api/analyze` - 分析指定文章
  - `GET /api/articles` - 获取文章列表
  - `GET /api/config/sources` - 信息源配置

详细 API 文档：[docs/api.md](docs/api.md)

## 🛠️ 技术栈

### 后端
- **FastAPI** - 高性能 Web 框架
- **SQLite + aiosqlite** - 异步数据库
- **httpx** - 异步 HTTP 客户端
- **feedparser** - RSS 解析
- **google-generativeai** / **openai** - LLM SDK

### 前端
- **React 18 + TypeScript** - UI 框架
- **Vite** - 构建工具
- **TanStack Query** - 数据获取
- **Tailwind CSS** - 样式框架
- **Zustand** - 状态管理

## 📚 文档

- [架构设计](docs/architecture.md) - 系统架构和设计原则
- [API 文档](docs/api.md) - 完整的 API 参考
- [LLM 集成](docs/llm-integration.md) - LLM 后端配置指南
- [快速开始](QUICK_START.md) - 详细的部署指南

## 🐛 故障排查

### 常见问题

**后端启动失败**
```bash
# 检查端口占用
lsof -i :8000

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

**LLM 分析失败**
```bash
# 验证 API Key
echo $GEMINI_API_KEY

# 测试连接（Gemini 在中国需要代理）
export HTTP_PROXY=http://your-proxy:port
```

**爬取失败**
- 检查网络连接
- 在设置页面禁用失败的信息源
- 查看 `logs/backend.log` 了解详情

更多问题解决：[docs/troubleshooting.md](docs/troubleshooting.md)

## 🗺️ 开发路线图

### ✅ v0.1（当前）
- [x] 多源 RSS 爬取
- [x] 多 LLM 后端支持
- [x] 决策导向 Prompt
- [x] Web UI
- [x] 本地存储

### 🚧 v0.2（进行中）
- [ ] 报告质量评分
- [ ] 历史报告对比
- [ ] 导出功能（PDF/Markdown）
- [ ] 自定义分类增强

### 🔮 v0.3（计划中）
- [ ] 信号追踪看板
- [ ] 趋势可视化
- [ ] 多用户系统
- [ ] 邮件/Webhook 通知

## 🤝 贡献指南

欢迎所有形式的贡献！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

详细指南：[CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 许可证

本项目采用 **MIT License** 开源 - 查看 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [React](https://react.dev/) - 用户界面构建库
- [Google Gemini](https://ai.google.dev/) - 强大的多模态 AI
- [RSSHub](https://docs.rsshub.app/) - 万物皆可 RSS

## ⚠️ 免责声明

1. 本工具用于个人学习和研究，请遵守各信息源网站的服务条款
2. AI 生成的报告仅供参考，不构成投资或专业建议
3. 所有数据默认存储在本地，使用第三方 LLM API 时数据会发送到对应服务商
4. 使用付费 API 会产生费用，建议先使用免费的 Gemini 测试

---

<div align="center">

Made with ❤️ by NewsGap Contributors

**[⬆ 回到顶部](#newsgap---决策导向型行业情报分析系统)**

</div>
