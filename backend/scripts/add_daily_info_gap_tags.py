#!/usr/bin/env python3
"""
为精选的源添加 daily_info_gap 标签
"""

import yaml
import sys

# 43个精选源的名称列表（从备份文件中提取的准确名称）
DAILY_INFO_GAP_SOURCES = [
    "36氪",
    "少数派",
    "IT之家",
    "虎嗅网",
    "极客公园",
    "机器之心",
    "量子位",
    "华尔街日报中文网",
    "FT中文网",
    "财联社电报",
    "金十数据-重要资讯",
    "格隆汇实时快讯",
    "财联社深度",
    "智通财经推荐",
    "雪球今日话题",
    "BBC中文网",
    "AP News 美联社主站",
    "路透社中文",
    "纽约时报中文网",
    "澎湃新闻-时事",
    "财新网-要闻",
    "经济学人",
    "知乎每日精选",
    "微博热搜榜",
    "知乎热榜",
    "B站综合热门",
    "B站每周必看",
    "豆瓣一周口碑榜",
    "V2EX",
    "阮一峰的网络日志",
    "酷壳 CoolShell",
    "GitHub Trending",
    "Hacker News",
    "Huggingface Daily Papers",
    "V2EX 最热主题",
    "Epic Games免费游戏",
    "Steam特惠",
    "游戏打折情报-Steam历史低价",
    "豆瓣电影即将上映",
    "豆瓣电影北美票房榜",
    "什么值得买",
    "得到每天听本书",
    "小红书热榜",
]

def main():
    sources_file = "../config/sources.yaml"
    
    print(f"📖 读取 {sources_file}...")
    with open(sources_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    modified_count = 0
    not_found = []
    total_sources = 0
    
    # 遍历所有优先级分组
    for priority_key in data:
        if not isinstance(data[priority_key], list):
            continue
        
        sources = data[priority_key]
        total_sources += len(sources)
        
        for source in sources:
            name = source.get('name', '')
            
            # 检查是否在精选列表中
            if name in DAILY_INFO_GAP_SOURCES:
                # 确保metadata字段存在
                if 'metadata' not in source or source['metadata'] is None:
                    source['metadata'] = {}
                
                # 添加标记
                if not source['metadata'].get('daily_info_gap'):
                    source['metadata']['daily_info_gap'] = True
                    modified_count += 1
                    print(f"  ✓ {name}")
    
    print(f"\n🔍 总共扫描了 {total_sources} 个信息源")
    
    # 检查哪些源没找到
    for name in DAILY_INFO_GAP_SOURCES:
        found = False
        for priority_key in data:
            if not isinstance(data[priority_key], list):
                continue
            for source in data[priority_key]:
                if source.get('name') == name:
                    found = True
                    break
            if found:
                break
        if not found:
            not_found.append(name)
    
    if not_found:
        print(f"\n⚠️  以下 {len(not_found)} 个源未找到：")
        for name in not_found:
            print(f"  - {name}")
    
    print(f"\n✅ 共标记了 {modified_count} 个源")
    print(f"💾 保存到 {sources_file}...")
    
    with open(sources_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    
    print("✨ 完成！")

if __name__ == "__main__":
    main()
