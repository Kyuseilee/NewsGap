"""
RSSHub 集成助手

支持使用自定义 RSSHub 实例，以及将普通网站转换为 RSS 源
"""

from typing import Optional
from urllib.parse import urlparse, quote


class RSSHubHelper:
    """RSSHub 助手类"""
    
    # 默认公共 RSSHub 实例
    DEFAULT_INSTANCES = [
        "https://rsshub.app",
        "https://rss.shab.fun",
        "https://rsshub.rssforever.com",
    ]
    
    def __init__(self, custom_instance: Optional[str] = None):
        """
        初始化 RSSHub 助手
        
        Args:
            custom_instance: 自定义 RSSHub 实例地址（如 http://localhost:1200）
        """
        self.instance = custom_instance or self.DEFAULT_INSTANCES[0]
    
    def get_instance_url(self) -> str:
        """获取当前使用的 RSSHub 实例地址"""
        return self.instance
    
    def replace_rsshub_domain(self, rss_url: str) -> str:
        """
        替换 RSS URL 中的 RSSHub 域名为自定义实例
        
        例如：https://rsshub.app/github/trending/daily 
             → http://localhost:1200/github/trending/daily
        """
        for default_instance in self.DEFAULT_INSTANCES:
            if rss_url.startswith(default_instance):
                return rss_url.replace(default_instance, self.instance, 1)
        return rss_url
    
    # ===== 常用 RSSHub 路由生成器 =====
    
    def github_trending(self, since: str = "daily", language: str = "") -> str:
        """
        GitHub Trending
        
        Args:
            since: daily/weekly/monthly
            language: 语言（如 python, javascript）
        """
        if language:
            return f"{self.instance}/github/trending/{since}/{language}"
        return f"{self.instance}/github/trending/{since}"
    
    def weibo_user(self, uid: str) -> str:
        """微博用户动态"""
        return f"{self.instance}/weibo/user/{uid}"
    
    def weibo_search(self, keyword: str) -> str:
        """微博搜索"""
        return f"{self.instance}/weibo/search/hot"
    
    def zhihu_hotlist(self) -> str:
        """知乎热榜"""
        return f"{self.instance}/zhihu/hotlist"
    
    def bilibili_user_dynamic(self, uid: str) -> str:
        """B站用户动态"""
        return f"{self.instance}/bilibili/user/dynamic/{uid}"
    
    def twitter_user(self, username: str) -> str:
        """Twitter 用户"""
        return f"{self.instance}/twitter/user/{username}"
    
    def youtube_channel(self, channel_id: str) -> str:
        """YouTube 频道"""
        return f"{self.instance}/youtube/channel/{channel_id}"
    
    def sspai(self) -> str:
        """少数派"""
        return f"{self.instance}/sspai/index"
    
    def juejin_category(self, category: str = "frontend") -> str:
        """掘金分类"""
        return f"{self.instance}/juejin/category/{category}"
    
    def v2ex_hot(self) -> str:
        """V2EX 热门"""
        return f"{self.instance}/v2ex/topics/hot"
    
    def douban_movie_coming(self) -> str:
        """豆瓣即将上映电影"""
        return f"{self.instance}/douban/movie/coming"
    
    def cnbeta(self) -> str:
        """cnBeta"""
        return f"{self.instance}/cnbeta"
    
    def ithome(self) -> str:
        """IT之家"""
        return f"{self.instance}/ithome/ranking/24h"
    
    @staticmethod
    def is_rsshub_url(url: str) -> bool:
        """判断是否是 RSSHub URL"""
        parsed = urlparse(url)
        return any(instance in url for instance in RSSHubHelper.DEFAULT_INSTANCES) or \
               '/rsshub' in parsed.path.lower()
    
    @staticmethod
    def get_available_routes() -> dict:
        """
        获取常用 RSSHub 路由列表
        
        Returns:
            分类路由字典
        """
        return {
            "社交媒体": [
                {"name": "微博热搜", "route": "/weibo/search/hot"},
                {"name": "知乎热榜", "route": "/zhihu/hotlist"},
                {"name": "知乎日报", "route": "/zhihu/daily"},
                {"name": "V2EX 热门", "route": "/v2ex/topics/hot"},
            ],
            "科技资讯": [
                {"name": "IT之家 24h", "route": "/ithome/ranking/24h"},
                {"name": "36氪", "route": "/36kr"},
                {"name": "掘金前端", "route": "/juejin/category/frontend"},
                {"name": "少数派", "route": "/sspai/index"},
                {"name": "cnBeta", "route": "/cnbeta"},
            ],
            "开发者": [
                {"name": "GitHub Trending Daily", "route": "/github/trending/daily"},
                {"name": "GitHub Trending Python", "route": "/github/trending/daily/python"},
                {"name": "Hacker News", "route": "/hackernews"},
            ],
            "财经": [
                {"name": "雪球今日话题", "route": "/xueqiu/today"},
                {"name": "第一财经", "route": "/yicai/brief"},
                {"name": "财新博客", "route": "/caixin/blog"},
            ],
            "视频": [
                {"name": "B站排行榜", "route": "/bilibili/ranking"},
                {"name": "抖音热搜", "route": "/douyin/hot"},
            ],
        }


# 全局 RSSHub 实例
_rsshub_helper: Optional[RSSHubHelper] = None


def get_rsshub_helper(custom_instance: Optional[str] = None) -> RSSHubHelper:
    """获取全局 RSSHub 助手实例"""
    global _rsshub_helper
    if _rsshub_helper is None or custom_instance:
        _rsshub_helper = RSSHubHelper(custom_instance)
    return _rsshub_helper


def set_rsshub_instance(instance_url: str):
    """设置全局 RSSHub 实例地址"""
    global _rsshub_helper
    _rsshub_helper = RSSHubHelper(instance_url)
