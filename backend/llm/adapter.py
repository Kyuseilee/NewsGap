"""
LLM 适配器基类与工厂

定义统一的 LLM 接口，支持多种后端
"""

import tiktoken
from typing import List, Optional
from abc import ABC, abstractmethod
from datetime import datetime

from models import (
    Article, Analysis, AnalysisType, IndustryCategory,
    LLMAdapterInterface, Trend, Signal, InformationGap
)
from prompts import get_prompt_manager
from utils.proxy_helper import ProxyHelper


class BaseLLMAdapter(LLMAdapterInterface, ABC):
    """LLM 适配器基类"""
    
    # 行业中文名称映射
    INDUSTRY_NAME_MAP = {
        "daily_info_gap": "每日信息差",
        "socialmedia": "社交媒体",
        "news": "新闻资讯",
        "tech": "科技互联网",
        "developer": "开发者",
        "finance": "财经金融",
        "entertainment": "娱乐影视",
        "gaming": "游戏电竞",
        "anime": "动漫二次元",
        "shopping": "电商购物",
        "education": "学习教育",
        "lifestyle": "生活方式",
        "other": "其他",
        "custom": "自定义",
    }
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, proxy_url: Optional[str] = None, proxy_config: Optional[dict] = None):
        """
        Args:
            api_key: API密钥
            model: 模型名称
            proxy_url: 代理URL，格式: 'http://host:port' 或 'https://host:port' 或 'socks5://host:port'（向后兼容）
            proxy_config: 代理配置，格式: {'enabled': bool, 'http': 'http://host:port', 'https': 'https://host:port', 'socks5': 'socks5://host:port'}
        """
        self.api_key = api_key
        self.model = model
        self.proxy_config = proxy_config
        
        # 使用工具类统一处理代理配置
        self.proxy_url = ProxyHelper.get_first_available_proxy(proxy_config)
        
        # 向后兼容：如果没有 proxy_config 但有 proxy_url
        if self.proxy_url is None and proxy_url:
            self.proxy_url = proxy_url
    
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
    
    def _get_report_title_format(self, industry: Optional[IndustryCategory] = None) -> str:
        """生成报告标题格式提示
        
        Args:
            industry: 行业分类
            
        Returns:
            标题格式字符串，例如 "# 2026-02-04-财经金融-[报告主题]"
        """
        today = datetime.now().strftime("%Y-%m-%d")
        industry_cn = self.INDUSTRY_NAME_MAP.get(
            industry.value if industry else "other", 
            "综合"
        )
        return f"# {today}-{industry_cn}-[报告主题]"
    
    def _build_system_prompt(
        self, 
        analysis_type: AnalysisType,
        industry: Optional[IndustryCategory] = None
    ) -> str:
        """构建系统提示词 - 支持品类化配置
        
        Args:
            analysis_type: 分析类型
            industry: 品类类型，如果为None使用通用提示词
        
        Returns:
            完整的系统提示词
        """
        prompt_manager = get_prompt_manager()
        return prompt_manager.get_system_prompt(industry, analysis_type)
    
    def _build_user_prompt(
        self,
        articles: List[Article],
        analysis_type: AnalysisType,
        custom_prompt: Optional[str] = None,
        industry: Optional[IndustryCategory] = None
    ) -> str:
        """构建用户提示词 - 支持品类化配置与智能压缩
        
        Args:
            articles: 待分析的文章列表
            analysis_type: 分析类型
            custom_prompt: 自定义提示词（可选）
            industry: 品类类型（可选）
        
        Returns:
            完整的用户提示词
        """
        prompt_manager = get_prompt_manager()
        
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
        
        # 分析指令 - 支持自定义或品类化prompt
        if custom_prompt:
            task_description = custom_prompt
        else:
            # 获取品类特定的用户提示词模板
            task_template = prompt_manager.get_user_prompt_template(industry)
            
            # 替换占位符
            task_description = task_template.replace("{{article_count}}", str(article_count))
            
            # 如果使用COMPREHENSIVE分析类型但没有品类，添加默认指令
            if analysis_type == AnalysisType.COMPREHENSIVE and not industry:
                task_description += f"""

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
        
        # 获取品类特定的自定义指令
        custom_instructions = prompt_manager.get_custom_instructions(industry)
        
        # 根据品类决定输出格式要求
        if custom_instructions.get('no_markdown'):
            # 播报稿件模式：不用 Markdown，不用引用
            format_instructions = ""
        elif custom_instructions.get('remove_citations'):
            # 去除引用但保留 Markdown
            format_instructions = """
---
**输出格式**：直接输出 Markdown 格式的报告，不要用代码块包裹。
**质量标准**：信息密度 > 覆盖率，判断清晰 > 面面俱到。
"""
        else:
            # 默认：Markdown + 引用
            format_instructions = """
---
**输出格式**：直接输出 Markdown 格式的报告，不要用代码块包裹。
**质量标准**：信息密度 > 覆盖率，判断清晰 > 面面俱到。
**引用要求**：提到具体事实、数据或观点时，必须用 `[数字]` 标注来源（如 `[1]`、`[2][3]`），数字对应上方信息源列表的编号。
"""
        
        return f"""{task_description}

{articles_text}
{format_instructions}"""
    
    @abstractmethod
    async def analyze(
        self,
        articles: List[Article],
        analysis_type: AnalysisType,
        custom_prompt: Optional[str] = None,
        industry: Optional[IndustryCategory] = None
    ) -> Analysis:
        """子类实现具体的分析逻辑
        
        Args:
            articles: 待分析的文章列表
            analysis_type: 分析类型
            custom_prompt: 自定义提示词（可选）
            industry: 品类类型（可选，用于品类化prompt配置）
        """
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
    model: Optional[str] = None,
    proxy_url: Optional[str] = None,
    proxy_config: Optional[dict] = None
) -> BaseLLMAdapter:
    """
    创建 LLM 适配器

    Args:
        backend: "ollama", "openai", "deepseek", "gemini"
        api_key: API 密钥（本地模型不需要）
        model: 模型名称
        proxy_url: 代理URL，格式: 'http://host:port' 或 'https://host:port' 或 'socks5://host:port'
        proxy_config: 代理配置，格式: {'enabled': bool, 'http': 'http://host:port', 'https': 'https://host:port', 'socks5': 'socks5://host:port'}
    """
    backend = backend.lower()

    if backend == "ollama":
        from llm.ollama_adapter import OllamaAdapter
        return OllamaAdapter(model=model, proxy_url=proxy_url, proxy_config=proxy_config)

    elif backend == "openai":
        from llm.openai_adapter import OpenAIAdapter
        return OpenAIAdapter(api_key=api_key, model=model, proxy_url=proxy_url, proxy_config=proxy_config)

    elif backend == "deepseek":
        from llm.deepseek_adapter import DeepSeekAdapter
        return DeepSeekAdapter(api_key=api_key, model=model, proxy_url=proxy_url, proxy_config=proxy_config)

    elif backend == "gemini":
        from llm.gemini_adapter import GeminiAdapter
        return GeminiAdapter(api_key=api_key, model=model, proxy_url=proxy_url, proxy_config=proxy_config)

    else:
        raise ValueError(f"Unknown LLM backend: {backend}")
