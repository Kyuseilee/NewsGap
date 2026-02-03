"""
信息源配置加载器

从 YAML 配置文件加载信息源定义
"""

import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from models import Source, SourceType, SourcePriority, IndustryCategory


def log(message: str):
    """带时间戳的日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


class SourceConfigLoader:
    """信息源配置加载器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化加载器
        
        Args:
            config_path: 配置文件路径，默认为 config/sources.yaml
        """
        if config_path is None:
            current_dir = Path(__file__).parent
            config_path = current_dir / "sources.yaml"
        
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
    
    def load_sources(self) -> List[Source]:
        """
        从配置文件加载所有信息源
        
        Returns:
            List[Source]: 信息源列表
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        sources = []
        
        # 加载各个分类的源
        for category_key in config:
            if category_key.startswith('_'):  # 跳过注释键
                continue
            
            category_sources = config[category_key]
            if not isinstance(category_sources, list):
                continue
            
            for source_data in category_sources:
                try:
                    source = self._create_source(source_data)
                    sources.append(source)
                except Exception as e:
                    log(f"⚠️  加载信息源失败: {source_data.get('name', 'unknown')} - {str(e)}")
        
        return sources
    
    def _create_source(self, data: Dict[str, Any]) -> Source:
        """
        从字典创建 Source 对象
        
        Args:
            data: 源配置字典
            
        Returns:
            Source: 信息源对象
        """
        # 类型转换
        source_type = SourceType(data['type'])
        priority = SourcePriority(data['priority'])
        industry = IndustryCategory(data['industry'])
        
        return Source(
            name=data['name'],
            url=data['url'],
            source_type=source_type,
            priority=priority,
            industry=industry,
            enabled=data.get('enabled', True),
            fetch_interval_hours=data.get('fetch_interval_hours', 24),
            metadata=data.get('metadata')
        )
    
    def get_sources_by_category(self, category: str) -> List[Source]:
        """
        获取特定分类的信息源
        
        Args:
            category: 分类名称（如 'official_rss', 'rsshub_general' 等）
            
        Returns:
            List[Source]: 该分类下的信息源列表
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if category not in config:
            return []
        
        sources = []
        for source_data in config[category]:
            try:
                source = self._create_source(source_data)
                sources.append(source)
            except Exception as e:
                log(f"⚠️  加载信息源失败: {source_data.get('name', 'unknown')} - {str(e)}")
        
        return sources
    
    def get_sources_by_industry(self, industry: IndustryCategory) -> List[Source]:
        """
        获取特定行业的信息源
        
        Args:
            industry: 行业分类
            
        Returns:
            List[Source]: 该行业的信息源列表
        """
        all_sources = self.load_sources()
        return [s for s in all_sources if s.industry == industry]
    
    def get_enabled_sources(self) -> List[Source]:
        """
        获取所有启用的信息源
        
        Returns:
            List[Source]: 启用的信息源列表
        """
        all_sources = self.load_sources()
        return [s for s in all_sources if s.enabled]


def load_sources_from_config(config_path: str = None) -> List[Source]:
    """
    便捷函数：从配置文件加载信息源
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        List[Source]: 信息源列表
    """
    loader = SourceConfigLoader(config_path)
    return loader.load_sources()


def get_all_sources() -> List[Source]:
    """
    获取所有信息源（仅从 YAML 配置文件加载）
    
    Returns:
        List[Source]: 信息源列表
    """
    return load_sources_from_config()


if __name__ == "__main__":
    # 测试加载
    loader = SourceConfigLoader()
    sources = loader.load_sources()
    
    print(f"📦 从配置文件加载了 {len(sources)} 个信息源")
    
    # 按行业统计
    from collections import Counter
    industries = Counter(s.industry.value for s in sources)
    print("\n📊 按行业分类:")
    for industry, count in sorted(industries.items(), key=lambda x: -x[1]):
        print(f"  {industry:15s}: {count:3d} 个源")
    
    # 启用/禁用统计
    enabled_count = sum(1 for s in sources if s.enabled)
    disabled_count = len(sources) - enabled_count
    print(f"\n✅ 启用: {enabled_count} 个")
    print(f"⏸️  禁用: {disabled_count} 个")
