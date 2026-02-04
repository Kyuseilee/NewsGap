"""
Prompt配置管理器 - 支持不同品类的差异化prompt配置
"""

import os
import yaml
from typing import Dict, Optional, Any
from pathlib import Path
from functools import lru_cache

from models import IndustryCategory, AnalysisType


class PromptManager:
    """统一管理所有品类的prompt配置"""
    
    def __init__(self):
        """初始化PromptManager，加载所有配置"""
        self.prompt_dir = Path(__file__).parent
        self.templates_dir = self.prompt_dir / "templates"
        self._config_cache: Dict[str, Dict[str, Any]] = {}
        self._base_config: Optional[Dict[str, Any]] = None
        
        # 品类到文件名的映射
        self.industry_to_file = {
            IndustryCategory.SOCIAL: "socialmedia.yaml",
            IndustryCategory.NEWS: "news.yaml",
            IndustryCategory.TECH: "tech.yaml",
            IndustryCategory.DEVELOPER: "developer.yaml",
            IndustryCategory.FINANCE: "finance.yaml",
            IndustryCategory.ENTERTAINMENT: "entertainment.yaml",
            IndustryCategory.GAMING: "gaming.yaml",
            IndustryCategory.ANIME: "anime.yaml",
            IndustryCategory.SHOPPING: "shopping.yaml",
            IndustryCategory.EDUCATION: "education.yaml",
            IndustryCategory.LIFESTYLE: "lifestyle.yaml",
            IndustryCategory.OTHER: "other.yaml",
        }
        
        # 初始化加载
        self._load_base_config()
    
    def _load_base_config(self) -> None:
        """加载基础配置（所有品类共用部分）"""
        base_path = self.prompt_dir / "base.yaml"
        if base_path.exists():
            with open(base_path, 'r', encoding='utf-8') as f:
                self._base_config = yaml.safe_load(f) or {}
        else:
            self._base_config = {}
    
    @lru_cache(maxsize=13)  # 缓存所有品类的配置
    def _load_industry_config(self, industry: str) -> Dict[str, Any]:
        """加载特定品类的配置"""
        if industry not in self.industry_to_file:
            # 未知品类，使用默认配置
            industry = IndustryCategory.OTHER
        
        config_path = self.templates_dir / self.industry_to_file[industry]
        
        if not config_path.exists():
            # 配置文件不存在，返回空配置
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        
        return config
    
    def get_system_prompt(
        self,
        industry: Optional[IndustryCategory] = None,
        analysis_type: Optional[AnalysisType] = None
    ) -> str:
        """获取系统提示词
        
        Args:
            industry: 品类类型，如果为None使用通用提示词
            analysis_type: 分析类型
        
        Returns:
            完整的系统提示词
        """
        # 基础系统提示词
        base_system = self._base_config.get("system_prompt_base", "")
        
        if industry is None:
            return base_system
        
        # 加载品类特定配置
        industry_config = self._load_industry_config(industry.value)
        industry_system = industry_config.get("system_prompt_addition", "")
        
        # 合并基础和品类特定部分
        if industry_system:
            return f"{base_system}\n\n{industry_system}"
        
        return base_system
    
    def get_report_format_prompt(
        self,
        industry: Optional[IndustryCategory] = None,
        analysis_type: Optional[AnalysisType] = None
    ) -> str:
        """获取报告格式提示词
        
        Args:
            industry: 品类类型
            analysis_type: 分析类型
        
        Returns:
            报告格式提示词
        """
        # 对于COMPREHENSIVE分析，使用基础报告格式
        if analysis_type and analysis_type.value == "COMPREHENSIVE":
            base_format = self._base_config.get("report_format_comprehensive", "")
        else:
            base_format = self._base_config.get("report_format_default", "")
        
        if industry is None:
            return base_format
        
        # 加载品类特定的报告格式
        industry_config = self._load_industry_config(industry.value)
        industry_format = industry_config.get("report_format_addition", "")
        
        # 合并格式
        if industry_format:
            return f"{base_format}\n\n{industry_format}"
        
        return base_format
    
    def get_user_prompt_template(
        self,
        industry: Optional[IndustryCategory] = None
    ) -> str:
        """获取用户提示词模板
        
        Args:
            industry: 品类类型
        
        Returns:
            用户提示词模板（包含占位符）
        """
        base_template = self._base_config.get("user_prompt_template", "")
        
        if industry is None:
            return base_template
        
        # 加载品类特定模板
        industry_config = self._load_industry_config(industry.value)
        industry_template = industry_config.get("user_prompt_template", "")
        
        # 如果品类有特定模板则使用，否则使用基础模板
        if industry_template:
            return industry_template
        
        return base_template
    
    def get_custom_instructions(
        self,
        industry: Optional[IndustryCategory] = None
    ) -> Dict[str, Any]:
        """获取品类特定的自定义指令
        
        Args:
            industry: 品类类型
        
        Returns:
            自定义指令字典
        """
        if industry is None:
            return {}
        
        industry_config = self._load_industry_config(industry.value)
        return industry_config.get("custom_instructions", {})
    
    def get_all_industries_config(self) -> Dict[str, Dict[str, Any]]:
        """获取所有品类的完整配置
        
        用于调试和配置验证
        """
        result = {}
        for industry in IndustryCategory:
            result[industry.value] = self._load_industry_config(industry.value)
        return result
    
    def reload_configs(self) -> None:
        """重新加载所有配置（用于开发环境实时更新）"""
        self._config_cache.clear()
        self._load_industry_config.cache_clear()
        self._load_base_config()


# 全局单例
_prompt_manager_instance: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """获取全局PromptManager单例"""
    global _prompt_manager_instance
    if _prompt_manager_instance is None:
        _prompt_manager_instance = PromptManager()
    return _prompt_manager_instance
