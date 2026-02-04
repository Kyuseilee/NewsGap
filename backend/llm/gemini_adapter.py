"""
Google Gemini API 适配器
"""

import json
import asyncio
import logging
import os
from typing import List, Optional
from datetime import datetime
import google.generativeai as genai

from models import Article, Analysis, AnalysisType, IndustryCategory, Trend, Signal, InformationGap
from llm.adapter import BaseLLMAdapter

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class GeminiAdapter(BaseLLMAdapter):
    """Google Gemini API 适配器（使用官方 Google GenAI SDK）"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        proxy_url: Optional[str] = None,
        proxy_config: Optional[dict] = None
    ):
        # 使用最新稳定的 Gemini 2.5 Flash 模型
        super().__init__(api_key=api_key, model=model or "gemini-2.5-flash", proxy_url=proxy_url, proxy_config=proxy_config)

        if not self.api_key:
            raise ValueError("Gemini API Key is required. Please configure it in Settings.")

        # 如果提供了代理，设置环境变量（google.generativeai通过httpx使用代理）
        if self.proxy_url:
            os.environ['HTTP_PROXY'] = self.proxy_url
            os.environ['HTTPS_PROXY'] = self.proxy_url
            logger.info(f"Gemini 使用代理: {self.proxy_url}")
        
        # 配置 Google GenAI
        genai.configure(api_key=self.api_key)
        
        # Gemini 2.5 Flash支持最多65536输出tokens（官方文档confirmed）
        # 设置candidate_count=1确保生成完整单一候选
        self.client = genai.GenerativeModel(
            model_name=self.model,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=65536,  # Gemini 2.5 Flash的真实最大输出token限制
                candidate_count=1,  # 只生成1个候选，避免分散token
                stop_sequences=None,  # 不设置停止序列，让模型完整输出
            )
        )
        
        logger.info(f"Gemini 适配器初始化完成: {self.model}, max_output_tokens=65536")
    
    async def analyze(
        self,
        articles: List[Article],
        analysis_type: AnalysisType,
        custom_prompt: Optional[str] = None,
        industry: Optional[IndustryCategory] = None
    ) -> Analysis:
        """使用 Gemini 进行分析
        
        Args:
            articles: 待分析的文章列表
            analysis_type: 分析类型
            custom_prompt: 自定义提示词（可选）
            industry: 品类类型（可选，用于品类化prompt配置）
        """
        system_prompt = self._build_system_prompt(analysis_type, industry)
        user_prompt = self._build_markdown_prompt(articles, custom_prompt, industry, analysis_type)
        
        start_time = datetime.now()
        
        # 组合提示词
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        logger.info(f"开始 Gemini 分析，文章数量: {len(articles)}")
        logger.debug(f"提示词长度: {len(full_prompt)} 字符")
        
        try:
            # 使用 asyncio.to_thread 在线程池中运行同步调用
            response = await asyncio.to_thread(
                self._sync_generate,
                full_prompt
            )
            
            response_text = response.text
            
            # 清理表格中的过量空格（Gemini表格生成bug的workaround）
            response_text = self._clean_table_spaces(response_text)
            
            # 检查finish_reason，确保响应完整
            finish_reason = None
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = candidate.finish_reason
            
            # 记录完整响应到日志
            logger.info(f"Gemini 响应长度: {len(response_text)} 字符")
            logger.info(f"Finish reason: {finish_reason}")
            if finish_reason and finish_reason != 1:  # 1 = STOP (正常结束)
                logger.warning(f"⚠️ Gemini 响应未正常结束！Finish reason: {finish_reason}")
                logger.warning("可能原因：1) 达到max_output_tokens限制 2) 触发安全过滤 3) 其他限制")
            logger.debug(f"Gemini 完整响应:\n{response_text}")
            
            # 写入日志文件
            try:
                with open('gemini_response.log', 'a', encoding='utf-8') as f:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"时间: {datetime.now().isoformat()}\n")
                    f.write(f"模型: {self.model}\n")
                    f.write(f"文章数: {len(articles)}\n")
                    f.write(f"响应长度: {len(response_text)}\n")
                    f.write(f"{'='*80}\n")
                    f.write(response_text)
                    f.write(f"\n{'='*80}\n\n")
                logger.info("响应已写入 gemini_response.log")
            except Exception as log_error:
                logger.warning(f"写入日志文件失败: {log_error}")
            
            # 获取 token 使用信息
            token_usage = 0
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                if hasattr(usage, 'total_token_count'):
                    token_usage = usage.total_token_count
                    logger.info(f"Token 使用: {token_usage}")
        
        except Exception as e:
            logger.error(f"Gemini API 调用失败: {str(e)}", exc_info=True)
            # 如果调用失败，返回错误信息
            return Analysis(
                analysis_type=analysis_type,
                article_ids=[a.id for a in articles if a.id],
                executive_brief=f"❌ Gemini 分析失败: {str(e)}",
                markdown_report=f"# 分析失败\n\n错误信息：{str(e)}",
                trends=[],
                signals=[],
                information_gaps=[],
                llm_backend="gemini",
                llm_model=self.model,
                token_usage=0,
                estimated_cost=0.0,
                processing_time_seconds=(datetime.now() - start_time).total_seconds()
            )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"分析完成，耗时: {processing_time:.2f}秒")
        
        # 提取执行摘要（取第一段或前500字）
        lines = response_text.strip().split('\n')
        executive_brief = ""
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                executive_brief = line.strip()[:500]
                break
        
        if not executive_brief:
            executive_brief = response_text[:500]
        
        # 计算成本
        cost_per_1k = self.get_model_info()['cost_per_1k_tokens']
        estimated_cost = (token_usage / 1000) * cost_per_1k
        
        # 构建 Analysis 对象
        return Analysis(
            analysis_type=analysis_type,
            article_ids=[a.id for a in articles if a.id],
            executive_brief=executive_brief,
            markdown_report=response_text,  # 完整的 Markdown 报告
            trends=[],
            signals=[],
            information_gaps=[],
            llm_backend="gemini",
            llm_model=self.model,
            token_usage=token_usage,
            estimated_cost=estimated_cost,
            processing_time_seconds=processing_time
        )
    
    def _build_system_prompt(
        self, 
        analysis_type: AnalysisType,
        industry: Optional[IndustryCategory] = None
    ) -> str:
        """构建系统提示词 - 支持品类化配置"""
        from prompts import get_prompt_manager
        prompt_manager = get_prompt_manager()
        return prompt_manager.get_system_prompt(industry, analysis_type)
    
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
        
        # 使用基类方法生成标题格式
        title_format = self._get_report_title_format(industry)
        
        return f"""{task_desc}

{articles_text}

---

{report_format}

⚠️ **输出要求**：
- 报告标题格式：{title_format}（例如：# 2026-02-04-财经金融-市场分析报告）
- 直接输出 Markdown 格式，不要用代码块包裹
- 必须完整输出所有章节，确保包含结尾总结
"""
    
    def _clean_table_spaces(self, text: str) -> str:
        """清理Markdown表格中的过量空格
        
        Gemini有时会在表格单元格中填充大量空格,导致输出字符数暴涨
        这个函数清理这些冗余空格
        """
        import re
        
        # 统计原始字符数
        original_len = len(text)
        
        # 查找表格行（以|开头和结尾）
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # 如果是表格行
            if line.strip().startswith('|') and line.strip().endswith('|'):
                # 分割单元格
                cells = line.split('|')
                # 清理每个单元格（保留最多3个连续空格）
                cleaned_cells = []
                for cell in cells:
                    # 压缩多余空格
                    cleaned_cell = re.sub(r' {4,}', '   ', cell)
                    cleaned_cells.append(cleaned_cell)
                cleaned_line = '|'.join(cleaned_cells)
                cleaned_lines.append(cleaned_line)
            else:
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        
        # 记录清理效果
        if len(result) < original_len:
            saved = original_len - len(result)
            logger.info(f"表格空格清理: 节省 {saved:,} 字符 ({saved/original_len*100:.1f}%)")
        
        return result
    
    def _sync_generate(self, prompt: str):
        """同步调用 Gemini API（在线程池中运行）"""
        return self.client.generate_content(prompt)
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        # 根据模型返回不同的配置
        model_configs = {
            'gemini-3-pro-preview': {
                'max_tokens': 1048576,
                'cost_per_1k_tokens': 0.0,
                'description': 'Gemini 3 Pro - 最强大的多模态理解模型'
            },
            'gemini-3-flash-preview': {
                'max_tokens': 1048576,
                'cost_per_1k_tokens': 0.0,
                'description': 'Gemini 3 Flash - 最均衡的模型，速度与智能兼顾'
            },
            'gemini-2.5-flash': {
                'max_tokens': 1048576,
                'cost_per_1k_tokens': 0.0,
                'description': 'Gemini 2.5 Flash - 性价比最佳（稳定版）'
            },
            'gemini-2.5-pro': {
                'max_tokens': 1048576,
                'cost_per_1k_tokens': 0.0,
                'description': 'Gemini 2.5 Pro - 更强大的推理能力'
            },
            'gemini-2.0-flash': {
                'max_tokens': 1048576,
                'cost_per_1k_tokens': 0.0,
                'description': 'Gemini 2.0-Flash - 将于2026年3月31日弃用'
            }
        }
        
        config = model_configs.get(self.model, model_configs['gemini-2.5-flash'])
        
        return {
            'backend': 'gemini',
            'model': self.model,
            'max_tokens': config['max_tokens'],
            'cost_per_1k_tokens': config['cost_per_1k_tokens'],
            'description': config['description']
        }
