"""
Markdown 归档管理器

将文章导出为 Markdown 格式，便于长期保存和阅读
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List

from models import Article


class ArchiveManager:
    """归档管理器"""
    
    def __init__(self, base_dir: str = "./archives"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    async def export_articles(self, articles: List[Article]) -> str:
        """
        导出文章为 Markdown 归档
        
        目录结构：archives/YYYY-MM-DD/industry/article-title.md
        
        Returns:
            导出目录路径
        """
        if not articles:
            return str(self.base_dir)
        
        # 使用当前日期作为归档批次
        batch_date = datetime.now().strftime("%Y-%m-%d")
        batch_dir = self.base_dir / batch_date
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        # 按行业分类导出
        for article in articles:
            industry_dir = batch_dir / article.industry.value
            industry_dir.mkdir(exist_ok=True)
            
            # 生成文件名（清理标题中的特殊字符）
            safe_title = self._sanitize_filename(article.title)
            file_name = f"{safe_title[:100]}.md"  # 限制文件名长度
            file_path = industry_dir / file_name
            
            # 写入 Markdown
            content = self._generate_markdown(article)
            
            # 异步写入（对于大量文章更高效）
            await asyncio.to_thread(file_path.write_text, content, encoding='utf-8')
        
        # 生成索引文件
        index_path = batch_dir / "INDEX.md"
        index_content = self._generate_index(articles, batch_date)
        await asyncio.to_thread(index_path.write_text, index_content, encoding='utf-8')
        
        return str(batch_dir)
    
    def _generate_markdown(self, article: Article) -> str:
        """生成单篇文章的 Markdown 内容"""
        lines = [
            f"# {article.title}",
            "",
            "---",
            "",
            f"**来源**: {article.source_name or '未知'}",
            f"**发布时间**: {article.published_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**行业分类**: {article.industry.value}",
            f"**原文链接**: [{article.url}]({article.url})",
            "",
        ]
        
        # 作者
        if article.author:
            lines.append(f"**作者**: {article.author}")
            lines.append("")
        
        # 标签
        if article.tags:
            tags_str = ", ".join([f"`{tag}`" for tag in article.tags])
            lines.append(f"**标签**: {tags_str}")
            lines.append("")
        
        # 摘要
        if article.summary:
            lines.extend([
                "## 摘要",
                "",
                article.summary,
                "",
            ])
        
        # 正文
        lines.extend([
            "---",
            "",
            "## 正文",
            "",
            article.content,
            "",
        ])
        
        # 元数据
        lines.extend([
            "---",
            "",
            "## 元数据",
            "",
            f"- **文章 ID**: `{article.id}`",
            f"- **爬取时间**: {article.fetched_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **语言**: {article.language}",
        ])
        
        if article.word_count:
            lines.append(f"- **字数**: {article.word_count}")
        
        if article.metadata:
            lines.append(f"- **额外信息**: {article.metadata}")
        
        return "\n".join(lines)
    
    def _generate_index(self, articles: List[Article], batch_date: str) -> str:
        """生成归档索引"""
        lines = [
            f"# 归档索引 - {batch_date}",
            "",
            f"**归档时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**文章总数**: {len(articles)}",
            "",
            "---",
            "",
        ]
        
        # 按行业分组
        by_industry = {}
        for article in articles:
            industry = article.industry.value
            if industry not in by_industry:
                by_industry[industry] = []
            by_industry[industry].append(article)
        
        # 生成各行业列表
        for industry, industry_articles in sorted(by_industry.items()):
            lines.append(f"## {industry.upper()} ({len(industry_articles)}篇)")
            lines.append("")
            
            # 按发布时间倒序排列
            sorted_articles = sorted(
                industry_articles,
                key=lambda a: a.published_at,
                reverse=True
            )
            
            for article in sorted_articles:
                pub_time = article.published_at.strftime('%Y-%m-%d %H:%M')
                safe_title = self._sanitize_filename(article.title)
                file_name = f"{safe_title[:100]}.md"
                
                lines.append(
                    f"- [{article.title}]({industry}/{file_name}) "
                    f"({pub_time}) - {article.source_name or '未知来源'}"
                )
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名中的非法字符"""
        # 移除或替换非法字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # 移除前后空白
        filename = filename.strip()
        
        # 如果为空，使用默认名称
        if not filename:
            filename = "untitled"
        
        return filename
    
    async def load_archived_articles(self, batch_date: str) -> List[dict]:
        """
        加载指定日期的归档文章列表（仅元数据）
        
        Returns:
            文章元数据列表（不包含完整正文）
        """
        batch_dir = self.base_dir / batch_date
        if not batch_dir.exists():
            return []
        
        articles_meta = []
        
        # 遍历所有行业目录
        for industry_dir in batch_dir.iterdir():
            if not industry_dir.is_dir():
                continue
            
            industry = industry_dir.name
            
            # 遍历该行业的所有文章
            for md_file in industry_dir.glob("*.md"):
                # 读取文件的前几行获取元数据
                content = await asyncio.to_thread(md_file.read_text, encoding='utf-8')
                
                # 简单解析（提取标题和基本信息）
                lines = content.split('\n')
                title = lines[0].replace('# ', '').strip() if lines else md_file.stem
                
                articles_meta.append({
                    'title': title,
                    'industry': industry,
                    'file_path': str(md_file),
                    'batch_date': batch_date
                })
        
        return articles_meta
