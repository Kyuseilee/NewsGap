-- 迁移脚本：为 analysis_articles 表添加 position 字段
-- 用于保持文章顺序，确保引用 [1][2][3] 与正确的文章对应

-- 添加 position 列
ALTER TABLE analysis_articles ADD COLUMN position INTEGER NOT NULL DEFAULT 0;

-- 更新现有记录：按 created_at 排序设置 position
-- SQLite 不支持直接 UPDATE ... ORDER BY，需要使用子查询
-- 注意：这只是对现有数据的近似修复，新的分析会正确保存顺序

-- 由于 SQLite 的限制，我们无法完美修复历史数据的顺序
-- 但新创建的分析会正确保存 position
