"""
OpenAI API 适配器
"""

import json
from typing import List, Optional
from datetime import datetime
from openai import AsyncOpenAI

from models import Article, Analysis, AnalysisType, Trend, Signal, InformationGap
from llm.adapter import BaseLLMAdapter


class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI API 适配器"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        super().__init__(api_key=api_key, model=model or "gpt-4o-mini")
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def analyze(
        self,
        articles: List[Article],
        analysis_type: AnalysisType,
        custom_prompt: Optional[str] = None
    ) -> Analysis:
        """使用 OpenAI 进行分析"""
        system_prompt = self._build_system_prompt(analysis_type)
        user_prompt = self._build_user_prompt(articles, analysis_type, custom_prompt)
        
        start_time = datetime.now()
        
        # 调用 OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # 解析响应
        response_text = response.choices[0].message.content
        
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            parsed = {
                'executive_brief': response_text[:500] if response_text else "分析生成失败"
            }
        
        # 计算成本
        token_usage = response.usage.total_tokens
        cost_per_1k = self.get_model_info()['cost_per_1k_tokens']
        estimated_cost = (token_usage / 1000) * cost_per_1k
        
        # 构建 Analysis 对象
        return Analysis(
            analysis_type=analysis_type,
            article_ids=[a.id for a in articles if a.id],
            executive_brief=parsed.get('executive_brief', ''),
            trends=[Trend(**t) for t in parsed.get('trends', [])],
            signals=[Signal(**s) for s in parsed.get('signals', [])],
            information_gaps=[InformationGap(**g) for g in parsed.get('information_gaps', [])],
            llm_backend="openai",
            llm_model=self.model,
            token_usage=token_usage,
            estimated_cost=estimated_cost,
            processing_time_seconds=processing_time
        )
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        # 价格参考（2026 年可能有变化）
        pricing = {
            'gpt-4o': 0.005,
            'gpt-4o-mini': 0.00015,
            'gpt-4-turbo': 0.01,
            'gpt-3.5-turbo': 0.0005
        }
        
        return {
            'backend': 'openai',
            'model': self.model,
            'max_tokens': 128000,
            'cost_per_1k_tokens': pricing.get(self.model, 0.001)
        }
