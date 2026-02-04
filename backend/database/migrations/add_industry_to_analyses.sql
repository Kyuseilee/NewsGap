-- 为 analyses 表添加 industry 字段
-- 执行日期: 2026-02-04

-- 1. 添加 industry 列
ALTER TABLE analyses ADD COLUMN industry TEXT DEFAULT 'other';

-- 2. 从关联的文章中推断行业分类（更新现有记录）
UPDATE analyses
SET industry = (
    SELECT articles.industry
    FROM analysis_articles
    JOIN articles ON analysis_articles.article_id = articles.id
    WHERE analysis_articles.analysis_id = analyses.id
    GROUP BY articles.industry
    ORDER BY COUNT(*) DESC
    LIMIT 1
)
WHERE industry IS NULL OR industry = 'other';

-- 3. 创建索引
CREATE INDEX IF NOT EXISTS idx_analyses_industry ON analyses(industry);

-- 4. 验证
SELECT COUNT(*) as total_analyses, 
       COUNT(CASE WHEN industry != 'other' THEN 1 END) as with_industry
FROM analyses;
