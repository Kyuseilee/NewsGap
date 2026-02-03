# Prompt配置化系统 - 完整指南

## 概述

NewsGap 现已支持**品类化Prompt配置系统**，允许为不同行业类别（加密货币、财经、科技等）使用差异化的分析Prompt。该系统采用配置文件驱动的方式，使得Prompt定制变得灵活且易于维护。

## 系统架构

### 目录结构

```
backend/
├── prompts/
│   ├── __init__.py                 # 模块初始化，导出PromptManager
│   ├── prompt_manager.py           # PromptManager类（核心）
│   ├── base.yaml                   # 所有品类共用的基础配置
│   └── templates/
│       ├── social.yaml             # 社交媒体Prompt配置
│       ├── news.yaml               # 新闻资讯Prompt配置
│       ├── tech.yaml               # 科技互联网Prompt配置
│       ├── developer.yaml          # 开发者Prompt配置
│       ├── finance.yaml            # 财经金融Prompt配置
│       ├── crypto.yaml             # 加密货币Prompt配置
│       ├── entertainment.yaml      # 娱乐影视Prompt配置
│       ├── gaming.yaml             # 游戏电竞Prompt配置
│       ├── anime.yaml              # 动漫二次元Prompt配置
│       ├── shopping.yaml           # 电商购物Prompt配置
│       ├── education.yaml          # 学习教育Prompt配置
│       ├── lifestyle.yaml          # 生活方式Prompt配置
│       └── other.yaml              # 其他类别Prompt配置
```

### 核心组件

#### 1. PromptManager（prompt_manager.py:18-205）

全局单例类，负责：
- 加载并缓存所有品类的Prompt配置
- 提供获取系统Prompt、报告格式、用户模板的方法
- 支持动态重新加载配置（开发环境使用）

**关键方法**：
- `get_system_prompt(industry, analysis_type)` - 获取系统提示词
- `get_report_format_prompt(industry, analysis_type)` - 获取报告格式
- `get_user_prompt_template(industry)` - 获取用户提示词模板
- `get_custom_instructions(industry)` - 获取品类特定的自定义指令

#### 2. BaseLLMAdapter修改（llm/adapter.py:61-169）

更新了两个关键方法的签名，支持`industry`参数：

```python
def _build_system_prompt(
    self, 
    analysis_type: AnalysisType,
    industry: Optional[IndustryCategory] = None
) -> str:
    """构建系统提示词 - 支持品类化配置"""

def _build_user_prompt(
    self,
    articles: List[Article],
    analysis_type: AnalysisType,
    custom_prompt: Optional[str] = None,
    industry: Optional[IndustryCategory] = None
) -> str:
    """构建用户提示词 - 支持品类化配置与智能压缩"""
```

#### 3. 各LLM适配器更新

- `deepseek_adapter.py` - 更新`analyze()`方法以传递industry参数
- `openai_adapter.py` - 更新`analyze()`方法以传递industry参数
- `ollama_adapter.py` - 更新`analyze()`方法以传递industry参数
- `gemini_adapter.py` - 更新`analyze()`、`_build_system_prompt()`、`_build_markdown_prompt()`方法

#### 4. Analyzer增强（analyzer.py:27-54）

- 支持显式指定industry参数
- **自动品类推断**：如果未指定industry，从文章列表的最常见行业自动推断

```python
async def analyze(
    self,
    articles: List[Article],
    analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE,
    custom_prompt: Optional[str] = None,
    industry: Optional[IndustryCategory] = None  # 新增参数
) -> Analysis:
```

## 配置文件格式

### base.yaml（基础配置）

所有品类共用的部分，包含：
- `system_prompt_base` - 通用系统提示词前缀
- `report_format_comprehensive` - COMPREHENSIVE分析的报告格式模板
- `report_format_default` - 默认分析的报告格式
- `user_prompt_template` - 用户提示词模板（支持{{article_count}}占位符）
- `custom_instructions` - 通用的自定义指令集

### 品类配置文件（templates/*.yaml）

每个品类包含三个主要部分：

```yaml
# system_prompt_addition：品类特定的系统提示词补充
# 会与base.yaml中的system_prompt_base合并
system_prompt_addition: |
  【加密货币分析背景】
  你正在分析加密货币与区块链领域的信息。
  ...

# report_format_addition：品类特定的报告格式补充
# 为COMPREHENSIVE分析提供额外的结构指导
report_format_addition: |
  ### 加密货币要素
  - **政策风险**：...
  - **技术进展**：...
  ...

# custom_instructions：品类特定的自定义指令
# 用于控制分析的特定行为
custom_instructions:
  highlight_regulation_risk: true
  track_protocol_upgrades: true
  monitor_large_transactions: true
```

## 工作流程

### 1. 初始化阶段

```
应用启动
    ↓
PromptManager.get_prompt_manager()（全局单例）
    ↓
加载base.yaml
    ↓
（品类配置延迟加载，使用@lru_cache缓存）
```

### 2. 分析请求流程

```
用户发起分析请求（含article_ids）
    ↓
获取articles
    ↓
Analyzer.analyze(articles, analysis_type, custom_prompt?, industry?)
    ↓
如果industry=None，自动推断最常见的行业
    ↓
BaseLLMAdapter.analyze(articles, analysis_type, custom_prompt, industry)
    ↓
_build_system_prompt(analysis_type, industry)
    └─→ PromptManager.get_system_prompt(industry, analysis_type)
        └─→ base.yaml系统提示词 + templates/[industry].yaml的补充
    ↓
_build_user_prompt(articles, analysis_type, custom_prompt, industry)
    ├─→ 如果custom_prompt存在，使用custom_prompt
    ├─→ 否则从PromptManager.get_user_prompt_template(industry)获取
    └─→ 替换{{article_count}}占位符
    ↓
将system_prompt和user_prompt发送给LLM
    ↓
处理LLM响应并返回Analysis结果
```

### 3. Prompt继承关系

```
通用Prompt（base.yaml）
    ↓
Crypto品类Prompt（templates/crypto.yaml）
    ├─ system_prompt_addition
    ├─ report_format_addition
    └─ custom_instructions
    ↓
最终Prompt（合并后）
```

## 使用场景

### 场景1：自动品类推断

```python
from analyzer import Analyzer
from models import AnalysisType

analyzer = Analyzer(llm_backend='deepseek')

# 不指定industry，系统自动推断
analysis = await analyzer.analyze(
    articles=articles,  # 假设大多数是crypto文章
    analysis_type=AnalysisType.COMPREHENSIVE
    # industry参数不指定 → 自动推断为crypto
)
```

### 场景2：显式指定品类

```python
analysis = await analyzer.analyze(
    articles=articles,
    analysis_type=AnalysisType.COMPREHENSIVE,
    industry=IndustryCategory.FINANCE  # 明确使用财经Prompt
)
```

### 场景3：自定义Prompt优先

```python
custom_prompt = "请特别关注监管风险..."

analysis = await analyzer.analyze(
    articles=articles,
    analysis_type=AnalysisType.COMPREHENSIVE,
    custom_prompt=custom_prompt  # custom_prompt优先级最高
    # industry参数会被忽略
)
```

## 优先级规则

Prompt选择的优先级（从高到低）：

1. **自定义Prompt**（custom_prompt参数）- 如果提供，完全覆盖所有默认Prompt
2. **品类特定Prompt**（industry参数或自动推断）- 使用templates/[industry].yaml配置
3. **基础Prompt**（base.yaml）- 所有品类的后备方案

## 当前品类配置说明

### 已配置的13个品类

| 品类 | 文件名 | 关键特征 |
|------|------|--------|
| social | social.yaml | 舆论焦点、情绪分析、参与度 |
| news | news.yaml | 跨领域趋势、政策信号、事件因果链 |
| tech | tech.yaml | 技术突破、竞争格局、监管影响、长期趋势 |
| developer | developer.yaml | 技术栈、框架采纳、社区热点、项目成熟度 |
| finance | finance.yaml | 宏观数据、市场异动、风险预警、配置建议 |
| crypto | crypto.yaml | **监管风险（最优先）**、技术进展、市场流动性 |
| entertainment | entertainment.yaml | 爆款内容、平台竞争、舆论热点、商业机会 |
| gaming | gaming.yaml | 新作发布、电竞赛事、版本更新、社区反馈 |
| anime | anime.yaml | 热门作品、衍生文化、IP商业化、审美趋势 |
| shopping | shopping.yaml | 销售热点、平台竞争、消费趋势、品牌动向 |
| education | education.yaml | 政策变化、技术创新、平台竞争、市场机会 |
| lifestyle | lifestyle.yaml | 生活趋势、消费热点、KOL影响、审美变化 |
| other | other.yaml | 通用配置 |

## 后续改进方向

### 即将支持的功能

1. **Prompt版本控制**
   - 支持多个Prompt版本并行
   - A/B测试不同Prompt效果

2. **动态Prompt调整**
   - 基于LLM反馈的自适应Prompt优化
   - 成本和质量的自动平衡

3. **品类混合分析**
   - 对多品类文章的智能分割分析
   - 跨品类关联识别

4. **Prompt性能指标**
   - 追踪每个品类Prompt的效果
   - 自动推荐最优Prompt

## 测试验证

所有功能已通过以下测试：

- ✅ PromptManager配置加载（13个品类）
- ✅ BaseLLMAdapter品类化Prompt生成
- ✅ 不同品类Prompt差异化确认（crypto、finance、tech）
- ✅ Analyzer自动品类推断逻辑
- ✅ 向后兼容性（不指定industry时的默认行为）

## 常见问题

### Q1: 如何修改某个品类的Prompt？

编辑对应的`templates/[industry].yaml`文件，修改相应部分即可：

```yaml
system_prompt_addition: |
  新的系统提示词...
```

修改立即生效（PromptManager支持缓存更新）。

### Q2: 如何添加新品类？

1. 在`models.py`的`IndustryCategory`中添加新枚举值
2. 在`prompts/templates/`下创建新的yaml文件
3. PromptManager会自动识别

### Q3: 为什么某个文章没有使用预期的Prompt？

检查以下顺序：
1. 是否设置了custom_prompt（优先级最高）
2. 是否显式指定了industry参数
3. 如果都没有，检查文章的industry字段是否正确

### Q4: 如何在开发环境实时更新Prompt配置？

```python
from prompts import get_prompt_manager

pm = get_prompt_manager()
pm.reload_configs()  # 重新加载所有配置
```

## 技术细节

### 缓存机制

PromptManager使用`@lru_cache`对品类配置进行缓存，提高性能：

```python
@lru_cache(maxsize=13)
def _load_industry_config(self, industry: str) -> Dict[str, Any]:
    # 首次加载时读取YAML文件，之后从缓存返回
```

### 占位符替换

用户模板中的占位符自动替换：

```
{{article_count}} → 文章数量
{{time}} → 当前时间（Gemini适配器）
{{total}} → 总数（报告格式）
{{ratio}} → 比例（报告格式）
```

### 品类推断算法

当未指定industry时，Analyzer选择最常见的品类：

```python
industry_counts = {}
for article in articles:
    industry_counts[industry.value] = industry_counts.get(industry.value, 0) + 1
most_common = max(industry_counts, key=industry_counts.get)
```

## 文件修改清单

本次实现修改的文件：

| 文件 | 修改内容 | 关键行号 |
|------|--------|--------|
| backend/prompts/__init__.py | 新建 | - |
| backend/prompts/prompt_manager.py | 新建 | 18-205 |
| backend/prompts/base.yaml | 新建 | - |
| backend/prompts/templates/*.yaml | 新建 | 13个品类文件 |
| backend/llm/adapter.py | 添加industry参数支持 | 11-15, 62-76, 152-188 |
| backend/llm/deepseek_adapter.py | 更新analyze方法签名 | 10, 28-36 |
| backend/llm/openai_adapter.py | 更新analyze方法签名 | 10, 25-33 |
| backend/llm/ollama_adapter.py | 更新analyze方法签名 | 10, 25-33 |
| backend/llm/gemini_adapter.py | 更新analyze、系统Prompt、markdown Prompt | 12, 49-57, 155-162, 181-214 |
| backend/analyzer.py | 添加industry参数和自动推断逻辑 | 8, 27-54 |

## 性能考量

- **启动时间**：base.yaml在PromptManager初始化时加载，品类配置延迟加载
- **内存占用**：所有配置均缓存在内存中，总计<1MB
- **响应时间**：Prompt生成通常<1ms，大部分时间在LLM调用

---

**最后更新**：2026-01-30  
**版本**：1.0  
**作者**：NewsGap开发团队
