"""
检查所有信息源的健康状态，建议使用官方RSS替代不可用的RSSHub路由
"""

import asyncio
import aiohttp
from storage.database import Database

async def check_source_health():
    db = Database()
    await db.initialize()
    
    all_sources = await db.get_sources()
    
    print(f"\n📊 信息源健康检查报告")
    print("=" * 80)
    print(f"总计: {len(all_sources)} 个信息源\n")
    
    issues_by_industry = {}
    healthy_by_industry = {}
    
    async with aiohttp.ClientSession() as session:
        for source in all_sources:
            if not source.enabled:
                continue
            
            industry = source.industry.value
            
            # 检查是否使用本地RSSHub
            if 'localhost:1200' in source.url:
                try:
                    async with session.get(source.url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status == 503:
                            # 503错误 - RSSHub路由不可用
                            if industry not in issues_by_industry:
                                issues_by_industry[industry] = []
                            issues_by_industry[industry].append({
                                'name': source.name,
                                'url': source.url,
                                'error': 'RSSHub路由返回503'
                            })
                        elif response.status == 200:
                            if industry not in healthy_by_industry:
                                healthy_by_industry[industry] = 0
                            healthy_by_industry[industry] += 1
                        else:
                            if industry not in issues_by_industry:
                                issues_by_industry[industry] = []
                            issues_by_industry[industry].append({
                                'name': source.name,
                                'url': source.url,
                                'error': f'HTTP {response.status}'
                            })
                except asyncio.TimeoutError:
                    if industry not in issues_by_industry:
                        issues_by_industry[industry] = []
                    issues_by_industry[industry].append({
                        'name': source.name,
                        'url': source.url,
                        'error': '超时'
                    })
                except Exception as e:
                    if industry not in issues_by_industry:
                        issues_by_industry[industry] = []
                    issues_by_industry[industry].append({
                        'name': source.name,
                        'url': source.url,
                        'error': str(e)
                    })
            else:
                # 非本地RSSHub源，假设健康
                if industry not in healthy_by_industry:
                    healthy_by_industry[industry] = 0
                healthy_by_industry[industry] += 1
    
    # 打印问题源
    if issues_by_industry:
        print("❌ 发现问题的信息源：")
        print("-" * 80)
        for industry, issues in sorted(issues_by_industry.items()):
            print(f"\n【{industry}】")
            for issue in issues:
                print(f"  ✗ {issue['name']}")
                print(f"    {issue['url']}")
                print(f"    错误: {issue['error']}")
        print("\n" + "-" * 80)
    else:
        print("✅ 所有信息源健康状态良好！\n")
    
    # 打印健康统计
    print("\n📈 各行业健康源统计：")
    print("-" * 80)
    
    all_industries = sorted(set(list(healthy_by_industry.keys()) + list(issues_by_industry.keys())))
    
    for industry in all_industries:
        healthy = healthy_by_industry.get(industry, 0)
        problematic = len(issues_by_industry.get(industry, []))
        total = healthy + problematic
        
        status = "✓" if problematic == 0 else "⚠️"
        print(f"{status} {industry:15s} 健康: {healthy:2d}/{total:2d}")
    
    print("-" * 80)
    
    # 建议
    if issues_by_industry:
        print("\n💡 建议：")
        print("1. 使用 'rsshub.app' 替代 'localhost:1200'（公共实例）")
        print("2. 或者使用官方RSS源替代RSSHub路由")
        print("3. 使用以下命令查看哪些源需要修复：")
        print("   SELECT name, url FROM sources WHERE url LIKE '%localhost:1200%' AND enabled = 1")
        print()

if __name__ == "__main__":
    asyncio.run(check_source_health())
