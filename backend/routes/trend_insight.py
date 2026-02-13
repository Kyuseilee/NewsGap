"""
趋势洞察路由

处理跨报告趋势分析请求
"""

import yaml
import logging
from datetime import datetime
from typing import List, Optional
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from models import TrendInsight, IndustryCategory
from storage.database import Database
from config_manager import ConfigManager
from llm.adapter import create_llm_adapter

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trend-insight", tags=["trend-insight"])


# ============================================================================
# 请求模型
# ============================================================================

class TrendInsightRequest(BaseModel):
    """趋势洞察请求"""
    analysis_ids: List[str] = Field(..., min_length=2, description="要分析的报告ID列表，至少2个")
    llm_backend: str = Field(default="deepseek", description="LLM 后端")
    llm_model: Optional[str] = Field(default=None, description="具体模型名称")


# ============================================================================
# 依赖注入
# ============================================================================

async def get_db():
    """依赖注入：数据库"""
    db = Database()
    await db.initialize()
    return db


async def get_config_manager(db: Database = Depends(get_db)):
    """依赖注入：配置管理器"""
    return ConfigManager(db)


# ============================================================================
# Prompt 构建
# ============================================================================

def load_trend_insight_prompt():
    """加载趋势洞察 prompt 配置"""
    import os
    prompt_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 'prompts', 'templates', 'trend_insight.yaml'
    )
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def build_trend_insight_prompt(
    analyses: list,
    industry: str,
    date_range: str,
    prompt_config: dict
) -> tuple:
    """构建趋势洞察 prompt
    
    Returns:
        (system_prompt, user_prompt)
    """
    # 构建报告内容
    reports_content = ""
    for i, analysis in enumerate(analyses, 1):
        created_date = analysis.created_at.strftime('%Y-%m-%d')
        
        # 压缩报告内容（保留核心部分）
        report_content = analysis.markdown_report or analysis.executive_brief
        
        # 智能压缩：如果报告太长，只保留关键部分
        if len(report_content) > 3000:
            # 尝试提取主要章节
            lines = report_content.split('\n')
            compressed_lines = []
            current_section = []
            section_count = 0
            
            for line in lines:
                if line.startswith('## ') or line.startswith('### '):
                    if current_section and section_count < 5:
                        compressed_lines.extend(current_section[:30])  # 每个章节最多30行
                        section_count += 1
                    current_section = [line]
                else:
                    current_section.append(line)
            
            if current_section and section_count < 5:
                compressed_lines.extend(current_section[:30])
            
            report_content = '\n'.join(compressed_lines)
            if len(report_content) > 3000:
                report_content = report_content[:3000] + "\n...[内容已压缩]"
        
        reports_content += f"""
### 报告 {i} - {created_date}

{report_content}

---
"""
    
    # 行业中文映射
    industry_cn_map = {
        "daily_info_gap": "综合信息差",
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
        "custom": "自定义",
        "other": "其他"
    }
    industry_cn = industry_cn_map.get(industry, industry)
    
    # 构建系统提示词
    system_prompt = prompt_config.get('system_prompt', '')
    
    # 构建用户提示词
    user_template = prompt_config.get('user_prompt_template', '')
    user_prompt = user_template.replace('{{report_count}}', str(len(analyses)))
    user_prompt = user_prompt.replace('{{date_range}}', date_range)
    user_prompt = user_prompt.replace('{{industry}}', industry_cn)
    user_prompt = user_prompt.replace('{{reports_content}}', reports_content)
    
    # 构建报告格式提示
    report_format = prompt_config.get('report_format', '')
    report_format = report_format.replace('{{industry}}', industry_cn)
    report_format = report_format.replace('{{date_range}}', date_range)
    report_format = report_format.replace('{{report_count}}', str(len(analyses)))
    report_format = report_format.replace('{{generated_at}}', datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    # 合并完整提示词
    full_user_prompt = f"{user_prompt}\n\n## 输出格式参考\n\n{report_format}"
    
    return system_prompt, full_user_prompt


# ============================================================================
# API 端点
# ============================================================================

@router.post("", response_model=TrendInsight)
async def create_trend_insight(
    request: TrendInsightRequest,
    db: Database = Depends(get_db),
    config_mgr: ConfigManager = Depends(get_config_manager)
):
    """
    创建趋势洞察分析
    
    从多个分析报告中识别趋势、规律和拐点
    """
    logger.info(f"开始趋势洞察分析，报告数量: {len(request.analysis_ids)}")
    
    # 获取所有分析报告
    analyses = []
    for analysis_id in request.analysis_ids:
        analysis = await db.get_analysis(analysis_id)
        if analysis:
            analyses.append(analysis)
    
    if len(analyses) < 2:
        raise HTTPException(
            status_code=400,
            detail="趋势洞察需要至少2个有效的分析报告"
        )
    
    # 按时间排序（从早到晚）
    analyses.sort(key=lambda a: a.created_at)
    
    # 推断行业（取最常见的行业）
    industries = [a.industry.value for a in analyses if a.industry]
    if industries:
        industry_counter = Counter(industries)
        dominant_industry = industry_counter.most_common(1)[0][0]
    else:
        dominant_industry = "other"
    
    # 计算时间范围
    date_range_start = analyses[0].created_at
    date_range_end = analyses[-1].created_at
    date_range_str = f"{date_range_start.strftime('%Y-%m-%d')} 至 {date_range_end.strftime('%Y-%m-%d')}"
    
    # 获取 API Key
    api_key = await config_mgr.get_api_key(request.llm_backend)
    if request.llm_backend != 'ollama' and not api_key:
        raise HTTPException(
            status_code=400,
            detail=f"使用 {request.llm_backend.upper()} 需要先在设置页面配置 API Key"
        )
    
    # 获取代理配置
    proxy_config = await config_mgr.get_detailed_proxy_config()
    
    # 加载 prompt 配置
    prompt_config = load_trend_insight_prompt()
    
    # 构建 prompt
    system_prompt, user_prompt = build_trend_insight_prompt(
        analyses=analyses,
        industry=dominant_industry,
        date_range=date_range_str,
        prompt_config=prompt_config
    )
    
    # 创建 LLM 适配器
    adapter = create_llm_adapter(
        backend=request.llm_backend,
        api_key=api_key,
        model=request.llm_model,
        proxy_config=proxy_config
    )
    
    # 执行分析
    start_time = datetime.now()
    
    try:
        # 直接调用 LLM（不通过 Analyzer，因为这是特殊的趋势分析）
        if request.llm_backend == 'gemini':
            # Gemini 使用 generate_content
            import asyncio
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = await asyncio.to_thread(
                adapter._sync_generate,
                full_prompt
            )
            response_text = response.text
            token_usage = 0
            if hasattr(response, 'usage_metadata') and hasattr(response.usage_metadata, 'total_token_count'):
                token_usage = response.usage_metadata.total_token_count
        elif request.llm_backend == 'ollama':
            # Ollama 使用 HTTP API
            import httpx
            proxies = None
            if adapter.proxy_url:
                proxies = {
                    'http://': adapter.proxy_url,
                    'https://': adapter.proxy_url,
                }
            async with httpx.AsyncClient(timeout=300, proxies=proxies) as http_client:
                resp = await http_client.post(
                    f"{adapter.base_url}/api/generate",
                    json={
                        "model": request.llm_model or "llama3.1",
                        "prompt": f"{system_prompt}\n\n{user_prompt}",
                        "stream": False,
                        "options": {"num_predict": 32000}
                    }
                )
                resp.raise_for_status()
                result = resp.json()
            response_text = result.get('response', '')
            token_usage = result.get('eval_count', 0)
        else:
            # OpenAI/DeepSeek: 使用 adapter 中已配置好代理的客户端
            model = request.llm_model
            if not model:
                model = "deepseek-chat" if request.llm_backend == 'deepseek' else "gpt-4o-mini"
            
            response = await adapter.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=8192
            )
            
            response_text = response.choices[0].message.content
            token_usage = response.usage.total_tokens if response.usage else 0
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # 提取执行摘要（取第一段）
        lines = response_text.strip().split('\n')
        executive_summary = ""
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                executive_summary = line.strip()[:500]
                break
        if not executive_summary:
            executive_summary = response_text[:500]
        
        # 计算成本
        model_info = adapter.get_model_info()
        cost_per_1k = model_info.get('cost_per_1k_tokens', 0)
        estimated_cost = (token_usage / 1000) * cost_per_1k
        
        # 构建趋势洞察结果
        try:
            industry_enum = IndustryCategory(dominant_industry)
        except (ValueError, KeyError):
            industry_enum = IndustryCategory.OTHER
        
        insight = TrendInsight(
            source_analysis_ids=[a.id for a in analyses],
            industry=industry_enum,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            executive_summary=executive_summary,
            markdown_report=response_text,
            llm_backend=request.llm_backend,
            llm_model=request.llm_model or model_info.get('model'),
            token_usage=token_usage,
            estimated_cost=estimated_cost,
            processing_time_seconds=processing_time
        )
        
        # 保存结果
        insight_id = await db.save_trend_insight(insight)
        insight.id = insight_id
        
        logger.info(f"趋势洞察完成，ID: {insight_id}，耗时: {processing_time:.2f}s")
        
        return insight
    
    except Exception as e:
        logger.error(f"趋势洞察分析失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"趋势洞察分析失败: {str(e)}"
        )


@router.get("s", response_model=List[TrendInsight])
async def list_trend_insights(
    industry: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Database = Depends(get_db)
):
    """
    获取趋势洞察列表
    
    支持按行业筛选
    """
    insights = await db.get_trend_insights(
        industry=industry,
        limit=limit,
        offset=offset
    )
    return insights


@router.get("s/{insight_id}", response_model=TrendInsight)
async def get_trend_insight(
    insight_id: str,
    db: Database = Depends(get_db)
):
    """
    获取趋势洞察详情
    """
    insight = await db.get_trend_insight(insight_id)
    if not insight:
        raise HTTPException(
            status_code=404,
            detail=f"未找到趋势洞察 {insight_id}"
        )
    return insight
