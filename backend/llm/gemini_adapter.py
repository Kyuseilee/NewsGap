"""
Google Gemini API 适配器
"""

import json
import asyncio
import logging
from typing import List, Optional
from datetime import datetime
import google.generativeai as genai

from models import Article, Analysis, AnalysisType, Trend, Signal, InformationGap
from llm.adapter import BaseLLMAdapter

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class GeminiAdapter(BaseLLMAdapter):
    """Google Gemini API 适配器（使用官方 Google GenAI SDK）"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        # 使用最新稳定的 Gemini 2.5 Flash 模型
        super().__init__(api_key=api_key, model=model or "gemini-2.5-flash")
        
        if not self.api_key:
            raise ValueError("Gemini API Key is required. Please configure it in Settings.")
        
        # 配置 Google GenAI
        genai.configure(api_key=self.api_key)
        
        # Gemini 2.5 Flash支持最多8192输出tokens
        # 设置candidate_count=1确保生成完整单一候选
        self.client = genai.GenerativeModel(
            model_name=self.model,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=8192,  # Gemini 2.5 Flash的最大输出token
                candidate_count=1,  # 只生成1个候选，避免分散token
                # 如果使用Gemini 2.5 Pro，可以设置到更高
            )
        )
    
    async def analyze(
        self,
        articles: List[Article],
        analysis_type: AnalysisType,
        custom_prompt: Optional[str] = None
    ) -> Analysis:
        """使用 Gemini 进行分析"""
        system_prompt = self._build_system_prompt(analysis_type)
        user_prompt = self._build_markdown_prompt(articles, custom_prompt)
        
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
            
            # 记录完整响应到日志
            logger.info(f"Gemini 响应长度: {len(response_text)} 字符")
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
    
    def _build_system_prompt(self, analysis_type: AnalysisType) -> str:
        """构建系统提示词 - 信号优先版"""
        return """你不是新闻摘要器，而是一名"决策导向型行业情报分析师"。

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

输出要求：
1. 使用清晰的 Markdown 格式
2. 信息密度 > 覆盖率
3. 判断清晰 > 面面俱到
4. 不要截断内容，确保报告完整"""
    
    def _build_markdown_prompt(
        self,
        articles: List[Article],
        custom_prompt: Optional[str] = None
    ) -> str:
        """构建 Markdown 报告提示词 - 压缩版"""
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
        
        task_desc = custom_prompt or f"""
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
        
        return f"""{task_desc}

{articles_text}

---

请按以下结构生成**高度压缩、主线清晰**的报告：

# 📊 行业情报分析报告

## 一、执行摘要（给只读3分钟的人）
用**3-5条要点**说明：
- 今天真正发生了什么"结构性变化"
- 哪些风险在上升，哪些只是噪音
- 哪些方向值得持续跟踪

避免罗列事件，强调**判断变化**。

## 二、今日主线叙事（最多5条）

### 主线 1：【一句话结论式标题】
- **核心判断**：这条主线意味着什么
- **关键信号**：哪些事件支撑了这个判断（引用文章编号如[1][5][12]）
- **被忽略的反证**：有没有相反信息？为何权重较低
- **影响半径**：影响哪些国家/行业/资产/群体

（其余主线同样结构，最多5条）

## 三、关键信号清单

只列**真正值得"盯住"的信号**，每个信号：
- **类型**：地缘政治/产业/政策/技术
- **为何重要**：它改变了什么"默认假设"
- **置信度**：高/中/低
- **跟踪建议**：接下来应关注什么

## 四、被过滤掉的内容

简要说明：
- 哪几类信息今天占比很高但价值有限
- 为什么不值得投入注意力

## 五、行动提示

从以下角度给出**明确但克制**的建议：
- **风险规避**
- **机会布局**
- **信息跟踪**

---
*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*
*原始信息数量：{article_count} 条*

⚠️ **提醒**：直接输出 Markdown，不要用代码块包裹。确保报告完整，不中途截断。
"""
    
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
