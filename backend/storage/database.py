"""
SQLite 数据库封装

提供对 SQLite 数据库的异步访问接口
"""

import aiosqlite
import json
import uuid
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from models import (
    Article, Source, Analysis, Tag,
    IndustryCategory, AnalysisType,
    StorageInterface, CustomCategory, TrendInsight
)
from storage.custom_category_db import CustomCategoryDB


class Database(StorageInterface, CustomCategoryDB):
    """SQLite 数据库管理器"""
    
    def __init__(self, db_path: str = "./data/newsgap.db"):
        self.db_path = db_path
        self._ensure_db_dir()
    
    def _ensure_db_dir(self):
        """确保数据库目录存在"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self):
        """获取数据库连接（用于上下文管理）"""
        return aiosqlite.connect(self.db_path)
    
    async def initialize(self):
        """初始化数据库（创建表）"""
        # 使用绝对路径定位 schema.sql
        current_file = Path(__file__).resolve()
        schema_path = current_file.parent.parent / "database" / "schema.sql"
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(schema)
            await db.commit()
    
    # ========================================================================
    # Article 操作
    # ========================================================================
    
    async def save_article(self, article: Article) -> str:
        """保存文章（如果 URL 已存在则更新）"""
        if article.id is None:
            article.id = str(uuid.uuid4())
        
        async with aiosqlite.connect(self.db_path) as db:
            # 检查是否已存在（根据 URL）
            cursor = await db.execute(
                "SELECT id FROM articles WHERE url = ?",
                (article.url,)
            )
            existing = await cursor.fetchone()
            
            if existing:
                # 更新现有文章
                article.id = existing[0]
                await db.execute("""
                    UPDATE articles SET
                        title = ?, content = ?, summary = ?,
                        industry = ?, published_at = ?, fetched_at = ?,
                        author = ?, language = ?, word_count = ?,
                        source_id = ?, source_name = ?,
                        metadata = ?
                    WHERE id = ?
                """, (
                    article.title, article.content, article.summary,
                    article.industry.value, article.published_at, article.fetched_at,
                    article.author, article.language, article.word_count,
                    article.source_id, article.source_name,
                    json.dumps(article.metadata) if article.metadata else None,
                    article.id
                ))
            else:
                # 插入新文章
                await db.execute("""
                    INSERT INTO articles (
                        id, title, url, content, summary, industry,
                        published_at, fetched_at, author, language, word_count,
                        source_id, source_name, archived, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article.id, article.title, article.url, article.content,
                    article.summary, article.industry.value,
                    article.published_at, article.fetched_at,
                    article.author, article.language, article.word_count,
                    article.source_id, article.source_name,
                    1 if article.archived else 0,
                    json.dumps(article.metadata) if article.metadata else None
                ))
            
            # 保存标签
            if article.tags:
                # 删除旧标签
                await db.execute(
                    "DELETE FROM article_tags WHERE article_id = ?",
                    (article.id,)
                )
                # 插入新标签
                for tag in article.tags:
                    await db.execute(
                        "INSERT OR IGNORE INTO article_tags (article_id, tag_name) VALUES (?, ?)",
                        (article.id, tag)
                    )
            
            await db.commit()
        
        return article.id
    
    async def get_article(self, article_id: str) -> Optional[Article]:
        """根据 ID 获取文章"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM articles WHERE id = ?",
                (article_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            # 获取标签
            tag_cursor = await db.execute(
                "SELECT tag_name FROM article_tags WHERE article_id = ?",
                (article_id,)
            )
            tags = [row[0] for row in await tag_cursor.fetchall()]
            
            return self._row_to_article(row, tags)
    
    async def query_articles(
        self,
        industry: Optional[IndustryCategory] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
        archived: Optional[bool] = None
    ) -> List[Article]:
        """按条件查询文章"""
        query = "SELECT DISTINCT a.* FROM articles a"
        params = []
        conditions = []
        
        # 标签过滤需要 JOIN
        if tags:
            query += " JOIN article_tags at ON a.id = at.article_id"
            tag_conditions = " OR ".join(["at.tag_name = ?"] * len(tags))
            conditions.append(f"({tag_conditions})")
            params.extend(tags)
        
        # 其他过滤条件
        if industry:
            conditions.append("a.industry = ?")
            params.append(industry.value)
        
        if start_time:
            conditions.append("a.published_at >= ?")
            params.append(start_time)
        
        if end_time:
            conditions.append("a.published_at <= ?")
            params.append(end_time)
        
        if archived is not None:
            conditions.append("a.archived = ?")
            params.append(1 if archived else 0)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY a.fetched_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            articles = []
            for row in rows:
                # 获取每篇文章的标签
                tag_cursor = await db.execute(
                    "SELECT tag_name FROM article_tags WHERE article_id = ?",
                    (row['id'],)
                )
                article_tags = [t[0] for t in await tag_cursor.fetchall()]
                articles.append(self._row_to_article(row, article_tags))
            
            return articles
    
    async def search_articles(self, query: str, limit: int = 50) -> List[Article]:
        """全文搜索文章"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT a.* FROM articles a
                JOIN articles_fts fts ON a.rowid = fts.rowid
                WHERE articles_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))
            rows = await cursor.fetchall()
            
            articles = []
            for row in rows:
                tag_cursor = await db.execute(
                    "SELECT tag_name FROM article_tags WHERE article_id = ?",
                    (row['id'],)
                )
                article_tags = [t[0] for t in await tag_cursor.fetchall()]
                articles.append(self._row_to_article(row, article_tags))
            
            return articles
    
    # ========================================================================
    # Source 操作
    # ========================================================================
    
    async def save_source(self, source: Source) -> str:
        """保存信息源 - 根据URL进行upsert，避免重复"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # 先查找是否已存在相同URL的源
            cursor = await db.execute(
                "SELECT id FROM sources WHERE url = ? LIMIT 1",
                (source.url,)
            )
            existing_row = await cursor.fetchone()
            
            if existing_row:
                # 存在则更新，使用已有的ID
                source.id = existing_row['id']
                await db.execute("""
                    UPDATE sources SET
                        name = ?, source_type = ?, industry = ?, enabled = ?,
                        fetch_interval_hours = ?, last_fetched_at = ?, metadata = ?
                    WHERE id = ?
                """, (
                    source.name, source.source_type.value, source.industry.value,
                    1 if source.enabled else 0,
                    source.fetch_interval_hours, source.last_fetched_at,
                    json.dumps(source.metadata) if source.metadata else None,
                    source.id
                ))
            else:
                # 不存在则插入，生成新ID
                if source.id is None:
                    source.id = str(uuid.uuid4())
                await db.execute("""
                    INSERT INTO sources (
                        id, name, url, source_type, industry, enabled,
                        fetch_interval_hours, last_fetched_at, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    source.id, source.name, source.url,
                    source.source_type.value, source.industry.value,
                    1 if source.enabled else 0,
                    source.fetch_interval_hours, source.last_fetched_at,
                    json.dumps(source.metadata) if source.metadata else None
                ))
            
            await db.commit()
        
        return source.id
    
    async def get_source(self, source_id: str) -> Optional[Source]:
        """根据 ID 获取信息源"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM sources WHERE id = ?",
                (source_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_source(row)
    
    async def delete_source(self, source_id: str) -> bool:
        """删除信息源"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM sources WHERE id = ?",
                (source_id,)
            )
            await db.commit()
            return cursor.rowcount > 0
    
    async def get_sources(
        self,
        industry: Optional[IndustryCategory] = None,
        enabled_only: bool = True
    ) -> List[Source]:
        """获取信息源列表
        
        对于 DAILY_INFO_GAP 分类，返回所有 metadata 中包含 daily_info_gap:true 的源
        """
        query = "SELECT * FROM sources"
        params = []
        conditions = []
        
        if enabled_only:
            conditions.append("enabled = 1")
        
        # 特殊处理：daily_info_gap 通过 metadata 标签查询
        if industry and industry == IndustryCategory.DAILY_INFO_GAP:
            # 不添加 industry 条件，后面在 Python 层面过滤
            pass
        elif industry:
            conditions.append("industry = ?")
            params.append(industry.value)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY name"
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            sources = [self._row_to_source(row) for row in rows]
        
        # 特殊处理：过滤出带有 daily_info_gap 标签的源
        if industry and industry == IndustryCategory.DAILY_INFO_GAP:
            sources = [
                s for s in sources 
                if s.metadata and s.metadata.get('daily_info_gap') is True
            ]
        
        return sources
    
    # ========================================================================
    # Analysis 操作
    # ========================================================================
    
    async def save_analysis(self, analysis: Analysis) -> str:
        """保存分析结果"""
        if analysis.id is None:
            analysis.id = str(uuid.uuid4())
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO analyses (
                    id, analysis_type, industry, executive_brief, markdown_report,
                    trends, signals, information_gaps,
                    llm_backend, llm_model, token_usage, estimated_cost,
                    created_at, processing_time_seconds,
                    user_rating, user_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis.id, analysis.analysis_type.value,
                analysis.industry.value if analysis.industry else 'other',
                analysis.executive_brief,
                analysis.markdown_report,  # 添加 markdown_report
                json.dumps([t.model_dump() for t in analysis.trends]),
                json.dumps([s.model_dump() for s in analysis.signals]),
                json.dumps([g.model_dump() for g in analysis.information_gaps]),
                analysis.llm_backend, analysis.llm_model,
                analysis.token_usage, analysis.estimated_cost,
                analysis.created_at, analysis.processing_time_seconds,
                analysis.user_rating, analysis.user_notes
            ))
            
            # 保存文章关联（保持顺序）
            for position, article_id in enumerate(analysis.article_ids):
                await db.execute("""
                    INSERT OR REPLACE INTO analysis_articles (analysis_id, article_id, position)
                    VALUES (?, ?, ?)
                """, (analysis.id, article_id, position))
            
            await db.commit()
        
        return analysis.id
    
    async def get_analysis(self, analysis_id: str) -> Optional[Analysis]:
        """根据 ID 获取分析结果"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM analyses WHERE id = ?",
                (analysis_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            # 获取关联的文章 ID（按 position 排序以保持引用顺序）
            article_cursor = await db.execute(
                "SELECT article_id FROM analysis_articles WHERE analysis_id = ? ORDER BY position ASC",
                (analysis_id,)
            )
            article_ids = [r[0] for r in await article_cursor.fetchall()]
            
            return self._row_to_analysis(row, article_ids)
    
    # ========================================================================
    # Archive 操作
    # ========================================================================
    
    async def archive_to_markdown(
        self,
        article_ids: List[str],
        output_dir: str
    ) -> str:
        """导出文章为 Markdown 归档"""
        from storage.archive import ArchiveManager
        
        articles = []
        for article_id in article_ids:
            article = await self.get_article(article_id)
            if article:
                articles.append(article)
        
        archive_mgr = ArchiveManager(output_dir)
        return await archive_mgr.export_articles(articles)
    
    # ========================================================================
    # 辅助方法
    # ========================================================================
    
    def _row_to_article(self, row: aiosqlite.Row, tags: List[str]) -> Article:
        """将数据库行转换为 Article 对象"""
        return Article(
            id=row['id'],
            title=row['title'],
            url=row['url'],
            source_id=row['source_id'],
            source_name=row['source_name'],
            content=row['content'],
            summary=row['summary'],
            industry=IndustryCategory(row['industry']),
            tags=tags,
            published_at=datetime.fromisoformat(row['published_at']),
            fetched_at=datetime.fromisoformat(row['fetched_at']),
            author=row['author'],
            language=row['language'],
            word_count=row['word_count'],
            archived=bool(row['archived']),
            archived_at=datetime.fromisoformat(row['archived_at']) if row['archived_at'] else None,
            metadata=json.loads(row['metadata']) if row['metadata'] else None
        )
    
    def _row_to_source(self, row: aiosqlite.Row) -> Source:
        """将数据库行转换为 Source 对象"""
        from models import SourceType
        
        return Source(
            id=row['id'],
            name=row['name'],
            url=row['url'],
            source_type=SourceType(row['source_type']),
            industry=IndustryCategory(row['industry']),
            enabled=bool(row['enabled']),
            fetch_interval_hours=row['fetch_interval_hours'],
            last_fetched_at=datetime.fromisoformat(row['last_fetched_at']) if row['last_fetched_at'] else None,
            metadata=json.loads(row['metadata']) if row['metadata'] else None
        )
    
    def _row_to_analysis(self, row: aiosqlite.Row, article_ids: List[str]) -> Analysis:
        """将数据库行转换为 Analysis 对象"""
        from models import Trend, Signal, InformationGap
        
        # 处理 industry 字段
        industry = None
        if 'industry' in row.keys() and row['industry']:
            try:
                industry = IndustryCategory(row['industry'])
            except (ValueError, KeyError):
                industry = IndustryCategory.OTHER
        
        return Analysis(
            id=row['id'],
            analysis_type=AnalysisType(row['analysis_type']),
            article_ids=article_ids,
            industry=industry,
            executive_brief=row['executive_brief'],
            markdown_report=row['markdown_report'] if row['markdown_report'] else None,
            trends=[Trend(**t) for t in json.loads(row['trends'])] if row['trends'] else [],
            signals=[Signal(**s) for s in json.loads(row['signals'])] if row['signals'] else [],
            information_gaps=[InformationGap(**g) for g in json.loads(row['information_gaps'])] if row['information_gaps'] else [],
            llm_backend=row['llm_backend'],
            llm_model=row['llm_model'],
            token_usage=row['token_usage'],
            estimated_cost=row['estimated_cost'],
            created_at=datetime.fromisoformat(row['created_at']),
            processing_time_seconds=row['processing_time_seconds'],
            user_rating=row['user_rating'],
            user_notes=row['user_notes']
        )

    # ========================================================================
    # TrendInsight 趋势洞察操作
    # ========================================================================
    
    async def save_trend_insight(self, insight: TrendInsight) -> str:
        """保存趋势洞察结果"""
        if not insight.id:
            insight.id = str(uuid.uuid4())
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO trend_insights (
                    id, industry, date_range_start, date_range_end,
                    executive_summary, markdown_report,
                    llm_backend, llm_model, token_usage, estimated_cost,
                    created_at, processing_time_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                insight.id,
                insight.industry.value if insight.industry else None,
                insight.date_range_start.isoformat() if insight.date_range_start else None,
                insight.date_range_end.isoformat() if insight.date_range_end else None,
                insight.executive_summary,
                insight.markdown_report,
                insight.llm_backend,
                insight.llm_model,
                insight.token_usage,
                insight.estimated_cost,
                insight.created_at.isoformat(),
                insight.processing_time_seconds
            ))
            
            # 保存来源分析报告关联（保持顺序）
            for position, analysis_id in enumerate(insight.source_analysis_ids):
                await db.execute("""
                    INSERT OR REPLACE INTO trend_insight_sources (trend_insight_id, analysis_id, position)
                    VALUES (?, ?, ?)
                """, (insight.id, analysis_id, position))
            
            await db.commit()
        
        return insight.id
    
    async def get_trend_insight(self, insight_id: str) -> Optional[TrendInsight]:
        """根据 ID 获取趋势洞察结果"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM trend_insights WHERE id = ?",
                (insight_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            # 获取关联的分析报告 ID（按 position 排序）
            source_cursor = await db.execute(
                "SELECT analysis_id FROM trend_insight_sources WHERE trend_insight_id = ? ORDER BY position ASC",
                (insight_id,)
            )
            source_ids = [r[0] for r in await source_cursor.fetchall()]
            
            return self._row_to_trend_insight(row, source_ids)
    
    async def get_trend_insights(
        self,
        industry: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[TrendInsight]:
        """获取趋势洞察列表"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if industry and industry != 'all':
                cursor = await db.execute("""
                    SELECT * FROM trend_insights 
                    WHERE industry = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (industry, limit, offset))
            else:
                cursor = await db.execute("""
                    SELECT * FROM trend_insights 
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            
            rows = await cursor.fetchall()
            
            insights = []
            for row in rows:
                # 获取关联的分析报告 ID
                source_cursor = await db.execute(
                    "SELECT analysis_id FROM trend_insight_sources WHERE trend_insight_id = ? ORDER BY position ASC",
                    (row['id'],)
                )
                source_ids = [r[0] for r in await source_cursor.fetchall()]
                
                insight = self._row_to_trend_insight(row, source_ids)
                insights.append(insight)
            
            return insights
    
    def _row_to_trend_insight(self, row: aiosqlite.Row, source_analysis_ids: List[str]) -> TrendInsight:
        """将数据库行转换为 TrendInsight 对象"""
        industry = None
        if row['industry']:
            try:
                industry = IndustryCategory(row['industry'])
            except (ValueError, KeyError):
                industry = IndustryCategory.OTHER
        
        return TrendInsight(
            id=row['id'],
            source_analysis_ids=source_analysis_ids,
            industry=industry,
            date_range_start=datetime.fromisoformat(row['date_range_start']) if row['date_range_start'] else None,
            date_range_end=datetime.fromisoformat(row['date_range_end']) if row['date_range_end'] else None,
            executive_summary=row['executive_summary'],
            markdown_report=row['markdown_report'],
            llm_backend=row['llm_backend'],
            llm_model=row['llm_model'],
            token_usage=row['token_usage'],
            estimated_cost=row['estimated_cost'],
            created_at=datetime.fromisoformat(row['created_at']),
            processing_time_seconds=row['processing_time_seconds']
        )
