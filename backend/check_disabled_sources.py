#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查所有禁用的信息源，分析原因并尝试修复
"""

import asyncio
import urllib.request
import urllib.error
from storage.database import Database
from collections import defaultdict


def test_source_url(url: str) -> dict:
    """
    测试信息源URL是否可访问
    
    Returns:
        {
            'accessible': bool,
            'status_code': int or None,
            'error': str or None
        }
    """
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            return {
                'accessible': status_code == 200,
                'status_code': status_code,
                'error': None if status_code == 200 else f'HTTP {status_code}'
            }
    except urllib.error.HTTPError as e:
        return {'accessible': False, 'status_code': e.code, 'error': f'HTTP {e.code}'}
    except urllib.error.URLError as e:
        return {'accessible': False, 'status_code': None, 'error': f'连接错误: {str(e.reason)}'}
    except Exception as e:
        return {'accessible': False, 'status_code': None, 'error': f'错误: {str(e)}'}


async def main():
    db = Database()
    await db.initialize()
    
    # 获取所有信息源
    all_sources = await db.get_sources(enabled_only=False)
    
    enabled_sources = [s for s in all_sources if s.enabled]
    disabled_sources = [s for s in all_sources if not s.enabled]
    
    print(f"总信息源数: {len(all_sources)}")
    print(f"启用: {len(enabled_sources)}")
    print(f"禁用: {len(disabled_sources)}")
    print("\n" + "="*80)
    
    if not disabled_sources:
        print("\n✅ 没有禁用的信息源！")
        return
    
    print(f"\n检查 {len(disabled_sources)} 个禁用的信息源...\n")
    
    # 按行业分组
    by_industry = defaultdict(list)
    for source in disabled_sources:
        by_industry[source.industry].append(source)
    
    # 检查每个禁用的源
    issues = {
        'duplicate': [],      # 重复（已有启用的相同源）
        'accessible': [],     # 可访问（应该启用）
        'inaccessible': [],   # 不可访问（需要修复）
    }
    
    for industry, sources in sorted(by_industry.items()):
        print(f"\n【{industry}】分类 - {len(sources)} 个禁用源")
        print("-" * 80)
        
        for source in sources:
            print(f"\n源名称: {source.name}")
            print(f"URL: {source.url}")
            
            # 检查是否有启用的相同URL源
            duplicate = False
            for enabled in enabled_sources:
                if enabled.url == source.url and enabled.industry == source.industry:
                    duplicate = True
                    print(f"  ⚠️  重复：已有启用的相同源 [{enabled.name}]")
                    issues['duplicate'].append((source, enabled))
                    break
            
            if duplicate:
                continue
            
            # 测试URL可访问性
            print("  正在测试连接...")
            result = test_source_url(source.url)
            
            if result['accessible']:
                print(f"  ✅ 可访问！应该启用")
                issues['accessible'].append(source)
            else:
                print(f"  ❌ 不可访问: {result['error']}")
                issues['inaccessible'].append((source, result['error']))
    
    # 总结报告
    print("\n" + "="*80)
    print("\n📊 检查结果总结：\n")
    
    print(f"1. 重复的禁用源（应删除）: {len(issues['duplicate'])}")
    if issues['duplicate']:
        for disabled, enabled in issues['duplicate']:
            print(f"   - {disabled.name} (与 {enabled.name} 重复)")
    
    print(f"\n2. 可访问的禁用源（应启用）: {len(issues['accessible'])}")
    if issues['accessible']:
        for source in issues['accessible']:
            print(f"   - {source.name}")
    
    print(f"\n3. 不可访问的源（需要修复）: {len(issues['inaccessible'])}")
    if issues['inaccessible']:
        for source, error in issues['inaccessible']:
            print(f"   - {source.name}: {error}")
    
    # 询问是否自动修复
    print("\n" + "="*80)
    print("\n🔧 自动修复选项：")
    print("1. 删除重复的禁用源")
    print("2. 启用所有可访问的源")
    print("3. 两者都执行")
    print("4. 不执行任何操作")
    
    choice = input("\n请选择 (1/2/3/4): ").strip()
    
    if choice in ['1', '3']:
        print("\n正在删除重复的禁用源...")
        for disabled, enabled in issues['duplicate']:
            success = await db.delete_source(disabled.id)
            if success:
                print(f"  ✓ 已删除: {disabled.name}")
            else:
                print(f"  ✗ 删除失败: {disabled.name}")
    
    if choice in ['2', '3']:
        print("\n正在启用可访问的源...")
        for source in issues['accessible']:
            source.enabled = True
            await db.save_source(source)
            print(f"  ✓ 已启用: {source.name}")
    
    if choice != '4':
        print("\n✅ 修复完成！")
        
        # 显示最终统计
        final_sources = await db.get_sources(enabled_only=False)
        final_enabled = [s for s in final_sources if s.enabled]
        final_disabled = [s for s in final_sources if not s.enabled]
        
        print(f"\n最终统计:")
        print(f"  总数: {len(final_sources)}")
        print(f"  启用: {len(final_enabled)}")
        print(f"  禁用: {len(final_disabled)}")


if __name__ == "__main__":
    asyncio.run(main())
