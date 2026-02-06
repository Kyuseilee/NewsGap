-- 迁移：为 analyses 表添加 industry 字段
-- 日期：2026-02-06
-- 原因：支持 daily_info_gap 等行业分类的分析记录

-- 添加 industry 字段
ALTER TABLE analyses ADD COLUMN industry TEXT;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_analyses_industry ON analyses(industry);
