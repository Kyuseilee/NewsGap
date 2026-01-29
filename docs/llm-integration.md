# LLM 接入指南

本文档说明如何在 NewsGap 中配置和使用不同的 LLM 后端。

## 支持的 LLM 后端

| 后端 | 类型 | 成本 | 优势 | 劣势 |
|------|------|------|------|------|
| Ollama | 本地 | 免费 | 无成本、隐私好 | 需要本地硬件、速度较慢 |
| DeepSeek | API | $0.14/1M tokens | 超低成本 | 需要 API Key |
| OpenAI | API | $0.15-5/1M tokens | 效果最好 | 成本较高 |
| Gemini | API | 免费（有限额） | 免费、上下文长 | 有限额限制 |

## 1. Ollama（本地模型）

### 安装

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# 下载安装包: https://ollama.com/download/windows
```

### 下载模型

```bash
# 推荐模型
ollama pull llama3.1      # Meta Llama 3.1 (8B)
ollama pull qwen2.5:7b    # Qwen 2.5
ollama pull gemma2:9b     # Google Gemma 2

# 查看已下载模型
ollama list
```

### 启动服务

```bash
# Ollama 会自动在后台运行
# 默认端口：11434

# 验证服务
curl http://localhost:11434/api/version
```

### 配置 NewsGap

编辑 `backend/config.yaml`:

```yaml
llm:
  default_backend: ollama
  
  ollama:
    base_url: http://localhost:11434
    model: llama3.1  # 使用你下载的模型
```

**优点**：
- ✅ 完全免费
- ✅ 数据不出本地
- ✅ 无网络依赖

**缺点**：
- ❌ 需要 8GB+ 内存
- ❌ 分析速度较慢
- ❌ 效果不如商业模型

---

## 2. DeepSeek（推荐）

### 获取 API Key

1. 访问 [DeepSeek 官网](https://platform.deepseek.com/)
2. 注册账号
3. 进入"API Keys"页面
4. 创建新 API Key

### 配置环境变量

```bash
# Linux/macOS
export DEEPSEEK_API_KEY="sk-..."

# Windows PowerShell
$env:DEEPSEEK_API_KEY="sk-..."

# 或添加到 .env 文件
echo "DEEPSEEK_API_KEY=sk-..." >> .env
```

### 配置 NewsGap

```yaml
llm:
  default_backend: deepseek
  
  deepseek:
    model: deepseek-chat  # 或 deepseek-reasoner
```

### 定价

- **DeepSeek-V3**: $0.14 / 1M input tokens, $0.28 / 1M output tokens
- **新用户赠送**: ¥30 免费额度

**示例成本**：
- 分析 10 篇文章（约 5K tokens）: $0.0007
- 每天分析 3 次：$0.002/天，约 $0.06/月

**优点**：
- ✅ 成本超低
- ✅ 中文效果好
- ✅ 速度快

**缺点**：
- ❌ 需要网络
- ❌ 需要信用卡充值

---

## 3. OpenAI（ChatGPT）

### 获取 API Key

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册/登录
3. 进入"API Keys"
4. 创建新 Key

### 配置

```bash
export OPENAI_API_KEY="sk-..."
```

```yaml
llm:
  default_backend: openai
  
  openai:
    model: gpt-4o-mini  # 或 gpt-4o, gpt-4-turbo
```

### 定价

| 模型 | Input | Output | 适用场景 |
|------|-------|--------|----------|
| gpt-4o-mini | $0.15/1M | $0.60/1M | 日常分析（推荐） |
| gpt-4o | $2.50/1M | $10/1M | 高质量分析 |
| gpt-4-turbo | $10/1M | $30/1M | 复杂任务 |

**示例成本**（gpt-4o-mini）：
- 分析 10 篇文章：$0.0015
- 每天 3 次：$0.13/月

**优点**：
- ✅ 效果最佳
- ✅ 功能强大
- ✅ 稳定可靠

**缺点**：
- ❌ 成本较高
- ❌ 中国大陆访问受限

---

## 4. Google Gemini

### 获取 API Key

1. 访问 [Google AI Studio](https://aistudio.google.com/apikey)
2. 创建 API Key

### 配置

```bash
export GEMINI_API_KEY="..."
```

```yaml
llm:
  default_backend: gemini
  
  gemini:
    model: gemini-2.0-flash-exp  # 或 gemini-1.5-pro
```

### 定价

- **Gemini Flash**: 免费（每分钟 15 次请求）
- **Gemini Pro**: 付费（具体见官网）

**优点**：
- ✅ 免费使用
- ✅ 上下文超长（1M tokens）
- ✅ 多模态支持

**缺点**：
- ❌ 有速率限制
- ❌ 中国大陆访问受限

---

## 切换 LLM 后端

### 方式 1：修改配置文件

编辑 `backend/config.yaml`:

```yaml
llm:
  default_backend: deepseek  # 改为你想用的后端
```

### 方式 2：前端选择

在 NewsGap 前端界面的"首页"，选择你想使用的 LLM 后端。

### 方式 3：API 请求

在 API 请求中指定：

```bash
curl -X POST http://localhost:8000/api/analyze \
  -d '{
    "article_ids": ["..."],
    "llm_backend": "deepseek"
  }'
```

---

## 成本对比

假设每天分析 3 次，每次 10 篇文章（约 5K tokens）：

| 后端 | 每次成本 | 每月成本 | 年成本 |
|------|---------|---------|--------|
| Ollama | $0 | $0 | $0 |
| DeepSeek | $0.0007 | $0.06 | $0.72 |
| GPT-4o-mini | $0.0015 | $0.13 | $1.56 |
| GPT-4o | $0.025 | $2.25 | $27 |
| Gemini Flash | $0 | $0 | $0 |

---

## 性能对比

| 后端 | 速度 | 质量 | 中文 | 推荐度 |
|------|------|------|------|--------|
| Ollama (llama3.1) | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 适合本地测试 |
| DeepSeek | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **强烈推荐** |
| GPT-4o-mini | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 性价比高 |
| GPT-4o | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 追求质量 |
| Gemini Flash | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 免费方案 |

---

## 故障排查

### Ollama 无法连接

```bash
# 检查服务状态
curl http://localhost:11434/api/version

# 重启 Ollama
ollama serve
```

### API Key 无效

```bash
# 验证 API Key
echo $DEEPSEEK_API_KEY

# 测试 API
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

### 速率限制

- **Gemini**: 等待 1 分钟后重试
- **OpenAI**: 升级到付费账户
- **DeepSeek**: 充值或降低请求频率

---

## 最佳实践

1. **开发环境**：使用 Ollama（免费测试）
2. **生产环境**：使用 DeepSeek（成本低）
3. **高质量需求**：使用 GPT-4o
4. **预算有限**：使用 Gemini Flash

---

更多问题请查看 [FAQ](faq.md) 或提交 Issue。
