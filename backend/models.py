"""
核心数据模型定义

使用 Pydantic 进行严格类型校验，定义系统中的核心实体：
- Article: 文章原始数据
- Source: 信息源配置
- Analysis: 分析结果
- Tag: 标签/分类
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, field_validator


class SourceType(str, Enum):
    """信息源类型"""
    RSS = "rss"
    WEB = "web"
    API = "api"


class SourcePriority(str, Enum):
    """信息源优先级"""
    OFFICIAL_RSS = "official_rss"      # 官方RSS，最稳定
    RSSHUB_STABLE = "rsshub_stable"    # RSSHub稳定路由
    RSSHUB_HIGH_RISK = "rsshub_high_risk"  # RSSHub高风险路由（国内媒体等）
    CUSTOM_CRAWLER = "custom_crawler"  # 自定义爬虫


class IndustryCategory(str, Enum):
    """行业分类 - 基于RSSHub路由体系"""
    SOCIAL = "social"           # 社交媒体：微博、知乎、即刻、豆瓣等
    NEWS = "news"               # 新闻资讯：传统媒体、新闻网站
    TECH = "tech"               # 科技互联网：36氪、少数派、IT之家等
    DEVELOPER = "developer"     # 开发者：GitHub、Hacker News、掘金等
    FINANCE = "finance"         # 财经金融：华尔街见闻、东方财富等
    ENTERTAINMENT = "entertainment"  # 娱乐影视：豆瓣电影、B站等
    GAMING = "gaming"           # 游戏电竞：Steam、TapTap等
    ANIME = "anime"             # 动漫二次元：Bangumi、ACG资讯
    SHOPPING = "shopping"       # 电商购物：淘宝、京东、小红书
    EDUCATION = "education"     # 学习教育：MOOC、知识付费
    LIFESTYLE = "lifestyle"     # 生活方式：美食、旅游、健身
    OTHER = "other"             # 其他


class AnalysisType(str, Enum):
    """分析类型"""
    TREND = "trend"              # 趋势检测
    SIGNAL = "signal"            # 信号聚类
    GAP = "gap"                  # 信息差识别
    BRIEF = "brief"              # 执行摘要
    COMPREHENSIVE = "comprehensive"  # 综合分析


# ============================================================================
# 基础数据模型
# ============================================================================

class Tag(BaseModel):
    """标签模型"""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=50)
    category: Optional[IndustryCategory] = None
    created_at: datetime = Field(default_factory=datetime.now)


class Source(BaseModel):
    """信息源模型"""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1)
    source_type: SourceType = SourceType.RSS
    priority: SourcePriority = SourcePriority.RSSHUB_STABLE  # 新增优先级
    industry: IndustryCategory = IndustryCategory.OTHER
    enabled: bool = True
    fetch_interval_hours: int = Field(default=24, ge=1, le=168)  # 1-168小时
    last_fetched_at: Optional[datetime] = None
    last_error: Optional[str] = None  # 新增：最后错误信息
    error_count: int = Field(default=0, ge=0)  # 新增：连续错误次数
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[dict] = None  # 额外的源特定配置
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """验证 URL 格式"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class Article(BaseModel):
    """文章模型"""
    id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=500)
    url: str = Field(..., min_length=1)
    source_id: Optional[str] = None  # 关联的信息源ID
    source_name: Optional[str] = None  # 冗余字段，便于显示
    
    # 内容
    content: str = Field(..., min_length=1)  # 正文内容
    summary: Optional[str] = None  # 原始摘要（如果源提供）
    
    # 分类与标签
    industry: IndustryCategory = IndustryCategory.OTHER
    tags: List[str] = Field(default_factory=list)
    
    # 时间信息
    published_at: datetime  # 文章发布时间
    fetched_at: datetime = Field(default_factory=datetime.now)  # 爬取时间
    
    # 元数据
    author: Optional[str] = None
    language: str = "zh"  # ISO 639-1 语言代码
    word_count: Optional[int] = None
    
    # 状态
    archived: bool = False
    archived_at: Optional[datetime] = None
    
    # 额外信息
    metadata: Optional[dict] = None


class Trend(BaseModel):
    """趋势项"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)  # 置信度 0-1
    supporting_article_ids: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)


class Signal(BaseModel):
    """信号项"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    importance: float = Field(..., ge=0.0, le=1.0)  # 重要性 0-1
    source_article_ids: List[str] = Field(default_factory=list)
    category: Optional[str] = None


class InformationGap(BaseModel):
    """信息差识别结果"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    gap_type: str  # "missing", "conflict", "emerging", etc.
    related_article_ids: List[str] = Field(default_factory=list)
    actionable_insight: Optional[str] = None


class Analysis(BaseModel):
    """分析结果模型"""
    id: Optional[str] = None
    analysis_type: AnalysisType
    
    # 关联的文章
    article_ids: List[str] = Field(..., min_items=1)
    
    # 分析结果
    executive_brief: str  # 执行摘要（总是生成）
    markdown_report: Optional[str] = None  # 完整的Markdown格式报告
    trends: List[Trend] = Field(default_factory=list)
    signals: List[Signal] = Field(default_factory=list)
    information_gaps: List[InformationGap] = Field(default_factory=list)
    
    # 元数据
    llm_backend: str  # "ollama", "openai", "deepseek", "gemini"
    llm_model: Optional[str] = None  # 具体模型名称
    token_usage: Optional[int] = None
    estimated_cost: Optional[float] = None  # USD
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now)
    processing_time_seconds: Optional[float] = None
    
    # 用户反馈
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    user_notes: Optional[str] = None


# ============================================================================
# 模块接口定义（抽象基类）
# ============================================================================

from abc import ABC, abstractmethod


class CrawlerInterface(ABC):
    """爬虫接口"""
    
    @abstractmethod
    async def fetch(
        self,
        source: Source,
        hours: int = 24
    ) -> List[Article]:
        """
        从指定信息源爬取内容
        
        Args:
            source: 信息源配置
            hours: 爬取多少小时内的内容
            
        Returns:
            文章列表（标准化格式）
        """
        pass
    
    @abstractmethod
    async def validate_source(self, source: Source) -> bool:
        """验证信息源是否可访问"""
        pass


class StorageInterface(ABC):
    """存储接口"""
    
    @abstractmethod
    async def save_article(self, article: Article) -> str:
        """保存文章，返回 article_id"""
        pass
    
    @abstractmethod
    async def get_article(self, article_id: str) -> Optional[Article]:
        """根据ID获取文章"""
        pass
    
    @abstractmethod
    async def query_articles(
        self,
        industry: Optional[IndustryCategory] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Article]:
        """按条件查询文章"""
        pass
    
    @abstractmethod
    async def save_analysis(self, analysis: Analysis) -> str:
        """保存分析结果，返回 analysis_id"""
        pass
    
    @abstractmethod
    async def get_analysis(self, analysis_id: str) -> Optional[Analysis]:
        """根据ID获取分析结果"""
        pass
    
    @abstractmethod
    async def archive_to_markdown(
        self,
        article_ids: List[str],
        output_dir: str
    ) -> str:
        """导出文章为 Markdown 归档，返回输出路径"""
        pass


class LLMAdapterInterface(ABC):
    """LLM 适配器接口"""
    
    @abstractmethod
    async def analyze(
        self,
        articles: List[Article],
        analysis_type: AnalysisType,
        custom_prompt: Optional[str] = None
    ) -> Analysis:
        """
        执行分析
        
        Args:
            articles: 待分析的文章列表
            analysis_type: 分析类型
            custom_prompt: 自定义提示词（可选）
            
        Returns:
            结构化分析结果
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, articles: List[Article]) -> dict:
        """
        估算分析成本
        
        Returns:
            {
                "token_count": int,
                "estimated_cost_usd": float,
                "model": str
            }
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> dict:
        """
        获取模型信息
        
        Returns:
            {
                "backend": str,
                "model": str,
                "max_tokens": int,
                "cost_per_1k_tokens": float
            }
        """
        pass


# ============================================================================
# 请求/响应模型（用于 API）
# ============================================================================

class FetchRequest(BaseModel):
    """爬取请求"""
    industry: IndustryCategory
    hours: int = Field(default=24, ge=1, le=168)
    source_ids: Optional[List[str]] = None  # 如果为空，使用该行业的所有启用源


class FetchResponse(BaseModel):
    """爬取响应"""
    article_ids: List[str]
    count: int
    sources_used: List[str]
    fetch_time_seconds: float


class AnalyzeRequest(BaseModel):
    """分析请求"""
    article_ids: List[str] = Field(..., min_items=1)
    analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE
    llm_backend: str = "gemini"  # "ollama", "openai", "deepseek", "gemini"
    llm_model: Optional[str] = None
    custom_prompt: Optional[str] = None


class AnalyzeResponse(BaseModel):
    """分析响应"""
    analysis_id: str
    analysis: Analysis


class IntelligenceRequest(BaseModel):
    """一键情报请求"""
    industry: IndustryCategory
    hours: int = Field(default=24, ge=1, le=168)
    llm_backend: str = "gemini"
    llm_model: Optional[str] = None
    source_ids: Optional[List[str]] = None


class IntelligenceResponse(BaseModel):
    """一键情报响应"""
    article_ids: List[str]
    article_count: int
    analysis_id: str
    analysis: Analysis
    total_time_seconds: float


class ArticleQueryParams(BaseModel):
    """文章查询参数"""
    industry: Optional[IndustryCategory] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tags: Optional[List[str]] = None
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class ArticleListResponse(BaseModel):
    """文章列表响应"""
    articles: List[Article]
    total: int
    limit: int
    offset: int
