"""
分析逻辑编排

协调 LLM 适配器进行情报分析
"""

from typing import List, Optional
from models import Article, Analysis, AnalysisType
from llm.adapter import create_llm_adapter, BaseLLMAdapter


class Analyzer:
    """分析器"""
    
    def __init__(
        self,
        llm_backend: str = "deepseek",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.adapter: BaseLLMAdapter = create_llm_adapter(
            backend=llm_backend,
            api_key=api_key,
            model=model
        )
    
    async def analyze(
        self,
        articles: List[Article],
        analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE,
        custom_prompt: Optional[str] = None
    ) -> Analysis:
        """
        执行分析
        
        Args:
            articles: 待分析的文章列表
            analysis_type: 分析类型
            custom_prompt: 自定义提示词
            
        Returns:
            分析结果
        """
        if not articles:
            raise ValueError("文章列表不能为空")
        
        # 使用 LLM 进行分析
        analysis = await self.adapter.analyze(
            articles=articles,
            analysis_type=analysis_type,
            custom_prompt=custom_prompt
        )
        
        return analysis
    
    def estimate_cost(self, articles: List[Article]) -> dict:
        """估算分析成本"""
        return self.adapter.estimate_cost(articles)
    
    def get_model_info(self) -> dict:
        """获取当前模型信息"""
        return self.adapter.get_model_info()
