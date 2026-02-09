"""
分析结果查询路由
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from models import Analysis
from storage.database import Database

router = APIRouter(prefix="/api/analyses", tags=["analyses"])


async def get_db():
    """依赖注入：数据库"""
    db = Database()
    await db.initialize()
    return db


@router.get("/{analysis_id}", response_model=Analysis)
async def get_analysis(
    analysis_id: str,
    db: Database = Depends(get_db)
):
    """获取单个分析结果"""
    analysis = await db.get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"未找到分析 {analysis_id}"
        )
    
    return analysis


@router.get("", response_model=List[Analysis])
async def list_analyses(
    limit: int = 20,
    offset: int = 0,
    db: Database = Depends(get_db)
):
    """获取分析列表"""
    import aiosqlite
    
    async with db._get_connection() as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("""
            SELECT * FROM analyses 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        rows = await cursor.fetchall()
        
        analyses = []
        for row in rows:
            # 获取关联的文章ID（按 position 排序以保持引用顺序）
            article_cursor = await conn.execute("""
                SELECT article_id FROM analysis_articles
                WHERE analysis_id = ?
                ORDER BY position ASC
            """, (row['id'],))
            article_rows = await article_cursor.fetchall()
            article_ids = [r['article_id'] for r in article_rows]
            
            # 转换为 Analysis 对象
            analysis = db._row_to_analysis(row, article_ids)
            analyses.append(analysis)
        
        return analyses
