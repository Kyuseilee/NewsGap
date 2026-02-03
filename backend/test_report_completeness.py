#!/usr/bin/env python3
"""
测试分析报告完整性
检查最近的分析报告是否被截断
"""

import asyncio
import aiosqlite
from datetime import datetime

async def check_report_completeness():
    db_path = 'data/newsgap.db'
    
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        
        # 获取最近5条分析记录
        cursor = await db.execute("""
            SELECT 
                id, 
                analysis_type, 
                length(markdown_report) as report_length,
                length(executive_brief) as brief_length,
                llm_backend,
                llm_model,
                created_at,
                markdown_report
            FROM analyses 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        analyses = await cursor.fetchall()
        
        print("=" * 80)
        print("最近5条分析报告完整性检查")
        print("=" * 80)
        print()
        
        for idx, analysis in enumerate(analyses, 1):
            print(f"【分析 {idx}】")
            print(f"ID: {analysis['id']}")
            print(f"类型: {analysis['analysis_type']}")
            print(f"后端: {analysis['llm_backend']} ({analysis['llm_model'] or 'default'})")
            print(f"时间: {analysis['created_at']}")
            print(f"报告长度: {analysis['report_length']} 字符")
            print(f"摘要长度: {analysis['brief_length']} 字符")
            
            # 检查报告是否完整
            report = analysis['markdown_report'] or ""
            
            # 检查标志
            is_truncated = False
            truncation_signs = []
            
            # 1. 检查是否以不完整的句子结束
            if report and not report.rstrip().endswith(('。', '！', '？', '.', '!', '?', '\n', '#')):
                is_truncated = True
                truncation_signs.append("结尾不完整")
            
            # 2. 检查是否缺少常见的结尾章节
            common_endings = ['总结', '结语', '展望', '建议', '---', '***']
            has_ending = any(ending in report[-500:] if len(report) >= 500 else report for ending in common_endings)
            if not has_ending and len(report) > 1000:
                is_truncated = True
                truncation_signs.append("缺少结尾章节")
            
            # 3. 检查报告是否过短（少于2000字符通常是不完整的）
            if len(report) < 2000:
                is_truncated = True
                truncation_signs.append(f"报告过短 ({len(report)} < 2000)")
            
            # 4. 显示报告末尾
            if report:
                print(f"\n报告末尾 (最后200字符):")
                print("-" * 60)
                print(report[-200:])
                print("-" * 60)
            
            if is_truncated:
                print(f"\n⚠️  可能被截断！原因: {', '.join(truncation_signs)}")
            else:
                print(f"\n✅ 报告看起来完整")
            
            print()
            print("=" * 80)
            print()

if __name__ == '__main__':
    asyncio.run(check_report_completeness())
