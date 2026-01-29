"""
Google Gemini API 适配器
"""

import json
from typing import List, Optional
from datetime import datetime
import google.generativeai as genai

from models import Article, Analysis, AnalysisType, Trend, Signal, InformationGap
from llm.adapter import BaseLLMAdapter


class GeminiAdapter(BaseLLMAdapter):
    """Google Gemini API 适配器"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        super().__init__(api_key=api_key, model=model or "gemini-2.0-flash-exp")
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)
    
    async def analyze(
        self,
        articles: List[Article],
        analysis_type: AnalysisType,
        custom_prompt: Optional[str] = None
    ) -> Analysis:
        """使用 Gemini 进行分析"""
        system_prompt = self._build_system_prompt(analysis_type)
        user_prompt = self._build_user_prompt(articles, analysis_type, custom_prompt)
        
        start_time = datetime.now()
        
        # 组合提示词
        full_prompt = f"{system_prompt}\n\n{user_prompt}\n\n请以 JSON 格式返回结果。"
        
        # 调用 Gemini API
        response = await self.client.generate_content_async(
            full_prompt,
            generation_config={
                'temperature': 0.3,
                'response_mime_type': 'application/json'
            }
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # 解析响应
        response_text = response.text
        
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            parsed = {
                'executive_brief': response_text[:500] if response_text else "分析生成失败"
            }
        
        # 估算 token 使用（Gemini 的 usage 信息可能不同）
        token_usage = getattr(response, 'usage_metadata', None)
        total_tokens = 0
        if token_usage:
            total_tokens = getattr(token_usage, 'total_token_count', 0)
        
        # 计算成本
        cost_per_1k = self.get_model_info()['cost_per_1k_tokens']
        estimated_cost = (total_tokens / 1000) * cost_per_1k
        
        # 构建 Analysis 对象
        return Analysis(
            analysis_type=analysis_type,
            article_ids=[a.id for a in articles if a.id],
            executive_brief=parsed.get('executive_brief', ''),
            trends=[Trend(**t) for t in parsed.get('trends', [])],
            signals=[Signal(**s) for s in parsed.get('signals', [])],
            information_gaps=[InformationGap(**g) for g in parsed.get('information_gaps', [])],
            llm_backend="gemini",
            llm_model=self.model,
            token_usage=total_tokens,
            estimated_cost=estimated_cost,
            processing_time_seconds=processing_time
        )
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            'backend': 'gemini',
            'model': self.model,
            'max_tokens': 1000000,  # Gemini 2.0 支持超长上下文
            'cost_per_1k_tokens': 0.0  # Gemini Flash 免费（有限额）
        }
