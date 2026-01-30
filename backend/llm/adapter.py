"""
LLM 适配器基类与工厂

定义统一的 LLM 接口，支持多种后端
"""

import tiktoken
from typing import List, Optional
from abc import ABC, abstractmethod

from models import (
    Article, Analysis, AnalysisType,
    LLMAdapterInterface, Trend, Signal, InformationGap
)


class BaseLLMAdapter(LLMAdapterInterface, ABC):
    """LLM 适配器基类"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model
    
    def estimate_cost(self, articles: List[Article]) -> dict:
        """估算分析成本"""
        # 估算总 token 数
        total_tokens = self._estimate_tokens(articles)
        
        model_info = self.get_model_info()
        cost_per_1k = model_info.get('cost_per_1k_tokens', 0)
        
        estimated_cost = (total_tokens / 1000) * cost_per_1k
        
        return {
            'token_count': total_tokens,
            'estimated_cost_usd': estimated_cost,
            'model': model_info['model']
        }
    
    def _estimate_tokens(self, articles: List[Article]) -> int:
        """估算 token 数量"""
        # 简单估算：文章内容 + 系统提示
        total_text = ""
        for article in articles:
            total_text += f"{article.title}\n{article.content}\n\n"
        
        # 加上系统提示词（约 500 tokens）
        system_prompt_tokens = 500
        
        # 使用 tiktoken 估算（如果可用）
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            content_tokens = len(encoding.encode(total_text))
            return content_tokens + system_prompt_tokens
        except Exception:
            # 简单估算：中文约 1.5 字/token，英文约 0.25 词/token
            char_count = len(total_text)
            estimated_tokens = int(char_count / 1.5)
            return estimated_tokens + system_prompt_tokens
    
    def _build_system_prompt(self, analysis_type: AnalysisType) -> str:
        """构建系统提示词 - 两阶段分析法"""
        
        # 第一阶段：筛选和主线识别
        stage1_prompt = """你不是新闻摘要器，而是一名"决策导向型行业情报分析师"。

你的目标不是覆盖所有信息，而是：
- 在大量杂讯中，快速识别**真正改变格局的少数信号**
- 为"理性决策者"提供**可行动、可取舍、可忽略的信息结构**

【核心原则】
1. **残忍筛选原则**：允许忽略、合并、弱化大量低价值文章，只有"改变判断"的内容才值得展开
2. **主线优先原则**：先识别3-5条"今日主线叙事"，所有文章只是这些主线的"证据"或"噪音"
3. **去均值原则**：避免大量7/10、8/10的模糊评分，重要性必须形成明显梯度（10/8/5/忽略）
4. **决策视角原则**：假设读者关注宏观风险、产业方向与中长期配置的理性决策者
5. **压缩优先原则**：宁可少写一半，也不要信息密度下降

【允许的操作】
- 将同类文章合并为"信息簇"
- 对低价值内容只做一句话处理，甚至完全不写
- 明确指出："这一类信息今天不重要"
"""
        
        if analysis_type == AnalysisType.COMPREHENSIVE:
            return stage1_prompt + """
请按以下结构输出**高度压缩、主线清晰**的 Markdown 报告：

# 📊 行业情报分析报告

## 一、执行摘要（给只读3分钟的人）
用**3-5条要点**说明：
- 今天真正发生了什么"结构性变化"
- 哪些风险在上升，哪些只是噪音
- 哪些方向值得持续跟踪

避免罗列事件，强调**判断变化**。

---

## 二、今日主线叙事（最多5条）

### 主线 1：【一句话结论式标题】
- **核心判断**：这条主线意味着什么
- **关键信号**：哪些事件支撑了这个判断（引用文章标题）
- **被忽略的反证**：有没有相反信息？为何权重较低
- **影响半径**：影响哪些国家/行业/资产/群体

（其余主线同样结构，最多5条）

---

## 三、关键信号清单（只列真正值得"盯住"的信号）

### 信号 X：【明确、具体、可验证】
- **类型**：地缘政治/产业/政策/技术
- **为何重要**：它改变了什么"默认假设"
- **置信度**：高/中/低
- **跟踪建议**：接下来应关注什么变化

---

## 四、被过滤掉的内容

简要说明：
- 哪几类信息今天**占比很高但价值有限**
- 为什么不值得投入注意力（例如：重复、象征性、情绪性）

---

## 五、行动提示（不是预测，是应对）

分别从以下角度给出**明确但克制**的建议：
- **风险规避**
- **机会布局**
- **信息跟踪**

---
*报告生成时间：{{time}}*
*原始信息数量：{{total}}*
*进入分析核心的信息比例：约 {{ratio}}%*
"""
        
        else:
            return stage1_prompt + """
请生成简洁的情报简报，包含：
- 执行摘要（3-5条要点）
- 关键主线（2-3条）
- 行动建议
"""
    
    def _build_user_prompt(
        self,
        articles: List[Article],
        analysis_type: AnalysisType,
        custom_prompt: Optional[str] = None
    ) -> str:
        """构建用户提示词 - 智能压缩版"""
        
        # 根据文章数量动态调整内容长度
        article_count = len(articles)
        if article_count <= 20:
            max_content_length = 1000  # 允许较长内容
        elif article_count <= 50:
            max_content_length = 600   # 中等压缩
        elif article_count <= 100:
            max_content_length = 400   # 高度压缩
        else:
            max_content_length = 300   # 极度压缩
        
        # 构建文章列表（压缩版）
        articles_text = f"# 待分析信息源（共 {article_count} 条）\n\n"
        
        for i, article in enumerate(articles, 1):
            # 压缩内容
            content = article.content[:max_content_length]
            if len(article.content) > max_content_length:
                content += "..."
            
            articles_text += f"""### [{i}] {article.title}
- 来源: {article.source_name} | 时间: {article.published_at.strftime('%Y-%m-%d %H:%M')} | 行业: {article.industry.value}
- 内容: {content}

"""
        
        # 分析指令
        if custom_prompt:
            task_description = custom_prompt
        else:
            if analysis_type == AnalysisType.COMPREHENSIVE:
                task_description = f"""
⚠️ **重要提醒**：你收到了 {article_count} 条信息，但**不需要逐条分析**。

你的任务是：
1. **残忍筛选**：快速识别出其中真正值得关注的 20-30% 信息
2. **主线聚合**：将重要信息聚合成 3-5 条主线叙事
3. **忽略噪音**：明确说明哪些信息被过滤掉了，以及原因
4. **决策导向**：每个判断都要指向"该做什么"或"该关注什么"

**不要**：
- ❌ 逐条分析每篇文章
- ❌ 给所有内容都打 7/10、8/10 的分
- ❌ 罗列事件而不做判断
- ❌ 写超过 3 页的报告（除非信息密度极高）

**要做**：
- ✅ 只深入分析真正改变判断的信息
- ✅ 对不重要的信息合并或一句话带过
- ✅ 明确说"这类信息今天不重要"
- ✅ 每段话都要有"所以呢？"的答案
"""
            else:
                task_description = "请生成简洁的情报摘要。"
        
        return f"""{task_description}

{articles_text}

---
**输出格式**：直接输出 Markdown 格式的报告，不要用代码块包裹。
**质量标准**：信息密度 > 覆盖率，判断清晰 > 面面俱到。
"""
    
    @abstractmethod
    async def analyze(
        self,
        articles: List[Article],
        analysis_type: AnalysisType,
        custom_prompt: Optional[str] = None
    ) -> Analysis:
        """子类实现具体的分析逻辑"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> dict:
        """子类提供模型信息"""
        pass


# ============================================================================
# LLM 适配器工厂
# ============================================================================

def create_llm_adapter(
    backend: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> BaseLLMAdapter:
    """
    创建 LLM 适配器
    
    Args:
        backend: "ollama", "openai", "deepseek", "gemini"
        api_key: API 密钥（本地模型不需要）
        model: 模型名称
    """
    backend = backend.lower()
    
    if backend == "ollama":
        from llm.ollama_adapter import OllamaAdapter
        return OllamaAdapter(model=model)
    
    elif backend == "openai":
        from llm.openai_adapter import OpenAIAdapter
        return OpenAIAdapter(api_key=api_key, model=model)
    
    elif backend == "deepseek":
        from llm.deepseek_adapter import DeepSeekAdapter
        return DeepSeekAdapter(api_key=api_key, model=model)
    
    elif backend == "gemini":
        from llm.gemini_adapter import GeminiAdapter
        return GeminiAdapter(api_key=api_key, model=model)
    
    else:
        raise ValueError(f"Unknown LLM backend: {backend}")
