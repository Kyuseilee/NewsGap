"""
DeepSeek API 适配器
"""

import json
from typing import List, Optional
from datetime import datetime
from openai import AsyncOpenAI

from models import Article, Analysis, AnalysisType, IndustryCategory, Trend, Signal, InformationGap
from llm.adapter import BaseLLMAdapter


class DeepSeekAdapter(BaseLLMAdapter):
    """DeepSeek API 适配器（兼容 OpenAI SDK）"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        super().__init__(api_key=api_key, model=model or "deepseek-chat")
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
    
    async def analyze(
        self,
        articles: List[Article],
        analysis_type: AnalysisType,
        custom_prompt: Optional[str] = None,
        industry: Optional[IndustryCategory] = None
    ) -> Analysis:
        """使用 DeepSeek 进行分析
        
        Args:
            articles: 待分析的文章列表
            analysis_type: 分析类型
            custom_prompt: 自定义提示词（可选）
            industry: 品类类型（可选，用于品类化prompt配置）
        """
        system_prompt = self._build_system_prompt(analysis_type, industry)
        user_prompt = self._build_markdown_prompt(articles, custom_prompt, industry, analysis_type)
        
        start_time = datetime.now()
        
        # 调用 DeepSeek API（生成Markdown而不是JSON）
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # 获取响应文本（Markdown格式）
        response_text = response.choices[0].message.content
        
        # 提取执行摘要（取第一个有意义的段落）
        lines = response_text.strip().split('\n')
        executive_brief = ""
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                executive_brief = line.strip()[:500]
                break
        
        if not executive_brief:
            executive_brief = response_text[:500]
        
        # 计算成本
        token_usage = response.usage.total_tokens
        cost_per_1k = self.get_model_info()['cost_per_1k_tokens']
        estimated_cost = (token_usage / 1000) * cost_per_1k
        
        # 构建 Analysis 对象
        return Analysis(
            analysis_type=analysis_type,
            article_ids=[a.id for a in articles if a.id],
            executive_brief=executive_brief,
            markdown_report=response_text,  # 完整的Markdown报告
            trends=[],
            signals=[],
            information_gaps=[],
            llm_backend="deepseek",
            llm_model=self.model,
            token_usage=token_usage,
            estimated_cost=estimated_cost,
            processing_time_seconds=processing_time
        )
    
    def _build_markdown_prompt(
        self,
        articles: List[Article],
        custom_prompt: Optional[str] = None,
        industry: Optional[IndustryCategory] = None,
        analysis_type: Optional[AnalysisType] = None
    ) -> str:
        """构建 Markdown 报告提示词 - 支持品类化配置与压缩"""
        from prompts import get_prompt_manager
        prompt_manager = get_prompt_manager()
        
        article_count = len(articles)
        
        # 动态调整压缩策略
        if article_count <= 20:
            max_content = 1000
        elif article_count <= 50:
            max_content = 600
        elif article_count <= 100:
            max_content = 400
        else:
            max_content = 300
        
        # 构建文章列表（紧凑格式）
        articles_text = f"# 待分析信息源（共 {article_count} 条）\n\n"
        
        for i, article in enumerate(articles, 1):
            content = article.content[:max_content]
            if len(article.content) > max_content:
                content += "..."
            
            articles_text += f"""### [{i}] {article.title}
- 来源: {article.source_name} | 时间: {article.published_at.strftime('%m-%d %H:%M')} | 行业: {article.industry.value}
- 内容: {content}

"""
        
        # 获取品类特定的用户提示词模板
        if custom_prompt:
            task_desc = custom_prompt
        else:
            task_template = prompt_manager.get_user_prompt_template(industry)
            task_desc = task_template.replace("{{article_count}}", str(article_count))
        
        # 获取品类特定的报告格式（传入analysis_type）
        report_format = prompt_manager.get_report_format_prompt(industry, analysis_type)
        
        return f"""{task_desc}

{articles_text}

---

{report_format}

⚠️ **提醒**：直接输出 Markdown，不要用代码块包裹。确保报告完整，不中途截断。
"""
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            'backend': 'deepseek',
            'model': self.model,
            'max_tokens': 64000,
            'cost_per_1k_tokens': 0.00014  # DeepSeek 价格非常低
        }
