"""
Ollama 本地模型适配器
"""

import json
import httpx
from typing import List, Optional
from datetime import datetime

from models import Article, Analysis, AnalysisType, Trend, Signal, InformationGap
from llm.adapter import BaseLLMAdapter


class OllamaAdapter(BaseLLMAdapter):
    """Ollama 本地模型适配器"""
    
    def __init__(
        self,
        model: Optional[str] = None,
        base_url: str = "http://localhost:11434"
    ):
        super().__init__(api_key=None, model=model or "llama3.1")
        self.base_url = base_url
    
    async def analyze(
        self,
        articles: List[Article],
        analysis_type: AnalysisType,
        custom_prompt: Optional[str] = None
    ) -> Analysis:
        """使用 Ollama 进行分析"""
        system_prompt = self._build_system_prompt(analysis_type)
        user_prompt = self._build_user_prompt(articles, analysis_type, custom_prompt)
        
        start_time = datetime.now()
        
        # 调用 Ollama API
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt}\n\n{user_prompt}",
                    "stream": False,
                    "format": "json"
                }
            )
            response.raise_for_status()
            result = response.json()
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # 解析响应
        response_text = result.get('response', '{}')
        
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            # 如果解析失败，创建基本响应
            parsed = {
                'executive_brief': response_text[:500] if response_text else "分析生成失败"
            }
        
        # 构建 Analysis 对象
        return Analysis(
            analysis_type=analysis_type,
            article_ids=[a.id for a in articles if a.id],
            executive_brief=parsed.get('executive_brief', ''),
            trends=[Trend(**t) for t in parsed.get('trends', [])],
            signals=[Signal(**s) for s in parsed.get('signals', [])],
            information_gaps=[InformationGap(**g) for g in parsed.get('information_gaps', [])],
            llm_backend="ollama",
            llm_model=self.model,
            token_usage=result.get('eval_count'),
            estimated_cost=0.0,  # 本地模型免费
            processing_time_seconds=processing_time
        )
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            'backend': 'ollama',
            'model': self.model,
            'max_tokens': 4096,  # 根据具体模型调整
            'cost_per_1k_tokens': 0.0  # 本地模型免费
        }
