"""
自定义分类数据库操作

扩展 Database 类，添加自定义分类相关的 CRUD 操作
"""

import aiosqlite
import json
import uuid
from datetime import datetime
from typing import List, Optional

from models import CustomCategory


class CustomCategoryDB:
    """自定义分类数据库操作 Mixin"""
    
    async def save_custom_category(self, category: CustomCategory) -> str:
        """保存自定义分类"""
        if category.id is None:
            category.id = str(uuid.uuid4())
        
        category.updated_at = datetime.now()
        
        async with aiosqlite.connect(self.db_path) as db:
            # 检查是否已存在
            cursor = await db.execute(
                "SELECT id FROM custom_categories WHERE id = ?",
                (category.id,)
            )
            existing = await cursor.fetchone()
            
            if existing:
                # 更新
                await db.execute("""
                    UPDATE custom_categories SET
                        name = ?, description = ?, custom_prompt = ?,
                        enabled = ?, updated_at = ?, metadata = ?
                    WHERE id = ?
                """, (
                    category.name, category.description, category.custom_prompt,
                    1 if category.enabled else 0, category.updated_at,
                    json.dumps(category.metadata) if category.metadata else None,
                    category.id
                ))
            else:
                # 插入
                await db.execute("""
                    INSERT INTO custom_categories (
                        id, name, description, custom_prompt, enabled,
                        created_at, updated_at, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    category.id, category.name, category.description,
                    category.custom_prompt, 1 if category.enabled else 0,
                    category.created_at, category.updated_at,
                    json.dumps(category.metadata) if category.metadata else None
                ))
            
            # 更新关联的源
            # 先删除旧的关联
            await db.execute(
                "DELETE FROM custom_category_sources WHERE category_id = ?",
                (category.id,)
            )
            
            # 插入新的关联
            for source_id in category.source_ids:
                await db.execute("""
                    INSERT INTO custom_category_sources (category_id, source_id)
                    VALUES (?, ?)
                """, (category.id, source_id))
            
            await db.commit()
        
        return category.id
    
    async def get_custom_category(self, category_id: str) -> Optional[CustomCategory]:
        """根据 ID 获取自定义分类"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # 获取分类信息
            cursor = await db.execute(
                "SELECT * FROM custom_categories WHERE id = ?",
                (category_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            # 获取关联的源ID
            cursor = await db.execute(
                "SELECT source_id FROM custom_category_sources WHERE category_id = ?",
                (category_id,)
            )
            source_rows = await cursor.fetchall()
            source_ids = [r[0] for r in source_rows]
            
            return self._row_to_custom_category(row, source_ids)
    
    async def get_custom_categories(self, enabled_only: bool = True) -> List[CustomCategory]:
        """获取所有自定义分类"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            query = "SELECT * FROM custom_categories"
            params = []
            
            if enabled_only:
                query += " WHERE enabled = 1"
            
            query += " ORDER BY name"
            
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            categories = []
            for row in rows:
                # 获取每个分类的源ID
                source_cursor = await db.execute(
                    "SELECT source_id FROM custom_category_sources WHERE category_id = ?",
                    (row['id'],)
                )
                source_rows = await source_cursor.fetchall()
                source_ids = [r[0] for r in source_rows]
                
                categories.append(self._row_to_custom_category(row, source_ids))
            
            return categories
    
    async def delete_custom_category(self, category_id: str) -> bool:
        """删除自定义分类"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM custom_categories WHERE id = ?",
                (category_id,)
            )
            await db.commit()
            return cursor.rowcount > 0
    
    async def get_sources_by_custom_category(self, category_id: str):
        """获取自定义分类关联的所有源"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute("""
                SELECT s.* FROM sources s
                JOIN custom_category_sources ccs ON s.id = ccs.source_id
                WHERE ccs.category_id = ?
            """, (category_id,))
            
            rows = await cursor.fetchall()
            return [self._row_to_source(row) for row in rows]
    
    def _row_to_custom_category(self, row: aiosqlite.Row, source_ids: List[str]) -> CustomCategory:
        """将数据库行转换为 CustomCategory 对象"""
        return CustomCategory(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            custom_prompt=row['custom_prompt'],
            source_ids=source_ids,
            enabled=bool(row['enabled']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            metadata=json.loads(row['metadata']) if row['metadata'] else None
        )
