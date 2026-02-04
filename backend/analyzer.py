"""
分析逻辑编排

协调 LLM 适配器进行情报分析
"""

from typing import List, Optional
from models import Article, Analysis, AnalysisType, IndustryCategory
from llm.adapter import create_llm_adapter, BaseLLMAdapter
from utils.proxy_helper import ProxyHelper


class Analyzer:
    """分析器"""
    
    def __init__(
        self,
        llm_backend: str = "deepseek",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        proxy_url: Optional[str] = None,
        proxy_config: Optional[dict] = None
    ):
        # 使用工具类统一处理代理配置
        effective_proxy = ProxyHelper.get_first_available_proxy(proxy_config)
        
        # 如果没有 proxy_config 但有 proxy_url，使用 proxy_url（向后兼容）
        if effective_proxy is None and proxy_url:
            effective_proxy = proxy_url

        self.adapter: BaseLLMAdapter = create_llm_adapter(
            backend=llm_backend,
            api_key=api_key,
            model=model,
            proxy_url=effective_proxy,
            proxy_config=proxy_config
        )
    
    async def analyze(
        self,
        articles: List[Article],
        analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE,
        custom_prompt: Optional[str] = None,
        industry: Optional[IndustryCategory] = None
    ) -> Analysis:
        """
        执行分析
        
        Args:
            articles: 待分析的文章列表
            analysis_type: 分析类型
            custom_prompt: 自定义提示词
            industry: 品类类型（可选）。如果为None，则自动从文章列表推断
            
        Returns:
            分析结果
        """
        if not articles:
            raise ValueError("文章列表不能为空")
        
        # 如果未指定品类，则自动推断（选择最常见的行业）
        if industry is None:
            industry_counts = {}
            for article in articles:
                industry_key = article.industry.value
                industry_counts[industry_key] = industry_counts.get(industry_key, 0) + 1
            
            # 获取最常见的行业
            if industry_counts:
                most_common_industry = max(industry_counts, key=industry_counts.get)
                try:
                    industry = IndustryCategory(most_common_industry)
                except (ValueError, KeyError):
                    # 如果无法识别，保持为None
                    industry = None
        
        # 使用 LLM 进行分析
        analysis = await self.adapter.analyze(
            articles=articles,
            analysis_type=analysis_type,
            custom_prompt=custom_prompt,
            industry=industry
        )
        
        # 设置行业分类到分析结果中
        if industry:
            analysis.industry = industry
        
        return analysis
    
    def estimate_cost(self, articles: List[Article]) -> dict:
        """估算分析成本"""
        return self.adapter.estimate_cost(articles)
    
    def get_model_info(self) -> dict:
        """获取当前模型信息"""
        return self.adapter.get_model_info()
