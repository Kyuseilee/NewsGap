#!/usr/bin/env python3
"""
恢复所有信息源到使用本地 RSSHub (localhost:1200)
"""

import asyncio
import aiosqlite

async def restore_localhost():
    db_path = 'data/newsgap.db'
    
    async with aiosqlite.connect(db_path) as db:
        # 查找所有使用 rsshub.app 的源
        cursor = await db.execute('SELECT id, name, url FROM sources WHERE url LIKE "%rsshub.app%"')
        sources = await cursor.fetchall()
        
        count = 0
        for source_id, name, url in sources:
            # 替换回 localhost:1200
            new_url = url.replace('https://rsshub.app', 'http://localhost:1200')
            await db.execute('UPDATE sources SET url = ? WHERE id = ?', (new_url, source_id))
            print(f'✓ {name}: {url} -> {new_url}')
            count += 1
        
        await db.commit()
        
        print(f'\n✅ 已恢复 {count} 个源到本地 RSSHub')
        
        # 验证
        cursor = await db.execute('SELECT COUNT(*) FROM sources WHERE url LIKE "%localhost:1200%"')
        local_count = (await cursor.fetchone())[0]
        
        cursor = await db.execute('SELECT COUNT(*) FROM sources WHERE url LIKE "%rsshub.app%"')
        rsshub_count = (await cursor.fetchone())[0]
        
        print(f'\n📊 localhost:1200 源数量: {local_count}')
        print(f'📊 rsshub.app 源数量: {rsshub_count}')

if __name__ == '__main__':
    asyncio.run(restore_localhost())
