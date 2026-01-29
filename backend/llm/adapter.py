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
        """构建系统提示词"""
        base_prompt = """你是一个专业的信息情报分析专家。你的任务是分析提供的文章集合，提取关键信息和洞察。

请以结构化、客观、准确的方式进行分析。避免主观臆测，基于文章内容得出结论。"""
        
        if analysis_type == AnalysisType.TREND:
            return base_prompt + """

重点关注：
- 识别跨文章的共同趋势
- 标注趋势的置信度
- 提供支持证据"""
        
        elif analysis_type == AnalysisType.SIGNAL:
            return base_prompt + """

重点关注：
- 识别重要信号和事件
- 评估信号的重要性
- 分类信号类型"""
        
        elif analysis_type == AnalysisType.GAP:
            return base_prompt + """

重点关注：
- 识别信息空白和矛盾
- 标注信息差类型（缺失、冲突、新兴）
- 提供可执行洞察"""
        
        elif analysis_type == AnalysisType.BRIEF:
            return base_prompt + """

重点关注：
- 生成简洁的执行摘要
- 突出最重要的信息
- 便于决策者快速理解"""
        
        else:  # COMPREHENSIVE
            return base_prompt + """

请进行全面分析，包括：
1. 趋势检测
2. 关键信号识别
3. 信息差分析
4. 执行摘要生成"""
    
    def _build_user_prompt(
        self,
        articles: List[Article],
        analysis_type: AnalysisType,
        custom_prompt: Optional[str] = None
    ) -> str:
        """构建用户提示词"""
        # 文章内容
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"""
## 文章 {i}: {article.title}

**来源**: {article.source_name}
**发布时间**: {article.published_at.strftime('%Y-%m-%d %H:%M')}
**行业**: {article.industry.value}

{article.content}

---
"""
        
        # 分析要求
        task_description = ""
        if custom_prompt:
            task_description = custom_prompt
        else:
            if analysis_type == AnalysisType.TREND:
                task_description = "请识别以下文章中的主要趋势。"
            elif analysis_type == AnalysisType.SIGNAL:
                task_description = "请提取以下文章中的关键信号。"
            elif analysis_type == AnalysisType.GAP:
                task_description = "请识别以下文章中的信息差和空白。"
            elif analysis_type == AnalysisType.BRIEF:
                task_description = "请为以下文章生成执行摘要。"
            else:
                task_description = "请对以下文章进行全面分析。"
        
        return f"""{task_description}

{articles_text}

请以 JSON 格式返回分析结果，包含以下字段：
- executive_brief: 执行摘要（字符串）
- trends: 趋势列表（可选）
- signals: 信号列表（可选）
- information_gaps: 信息差列表（可选）

每个趋势应包含：title, description, confidence, supporting_article_ids, keywords
每个信号应包含：title, description, importance, source_article_ids, category
每个信息差应包含：title, description, gap_type, related_article_ids, actionable_insight
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
