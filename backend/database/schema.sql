-- NewsGap 数据库 Schema
-- SQLite 3.x

-- ============================================================================
-- 标签表
-- ============================================================================
CREATE TABLE IF NOT EXISTS tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT,  -- IndustryCategory enum value
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (length(name) > 0 AND length(name) <= 50)
);

CREATE INDEX IF NOT EXISTS idx_tags_category ON tags(category);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);


-- ============================================================================
-- 信息源表
-- ============================================================================
CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    source_type TEXT NOT NULL,  -- 'rss', 'web', 'api'
    industry TEXT NOT NULL,     -- IndustryCategory enum value
    enabled INTEGER NOT NULL DEFAULT 1,  -- SQLite boolean (0/1)
    fetch_interval_hours INTEGER NOT NULL DEFAULT 24,
    last_fetched_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,  -- JSON string for extra config
    
    CHECK (length(name) > 0 AND length(name) <= 200),
    CHECK (length(url) > 0),
    CHECK (source_type IN ('rss', 'web', 'api')),
    CHECK (fetch_interval_hours >= 1 AND fetch_interval_hours <= 168),
    CHECK (enabled IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_sources_industry ON sources(industry);
CREATE INDEX IF NOT EXISTS idx_sources_enabled ON sources(enabled);
CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(source_type);


-- ============================================================================
-- 自定义分类表
-- ============================================================================
CREATE TABLE IF NOT EXISTS custom_categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    custom_prompt TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,  -- JSON string
    
    CHECK (length(name) > 0 AND length(name) <= 100),
    CHECK (length(custom_prompt) >= 10),
    CHECK (enabled IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_custom_categories_enabled ON custom_categories(enabled);
CREATE INDEX IF NOT EXISTS idx_custom_categories_name ON custom_categories(name);


-- ============================================================================
-- 自定义分类-信息源关联表（多对多）
-- ============================================================================
CREATE TABLE IF NOT EXISTS custom_category_sources (
    category_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (category_id, source_id),
    FOREIGN KEY (category_id) REFERENCES custom_categories(id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_custom_category_sources_category ON custom_category_sources(category_id);
CREATE INDEX IF NOT EXISTS idx_custom_category_sources_source ON custom_category_sources(source_id);


-- ============================================================================
-- 文章表
-- ============================================================================
CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,  -- URL 作为去重依据
    source_id TEXT,
    source_name TEXT,
    
    -- 内容
    content TEXT NOT NULL,
    summary TEXT,
    
    -- 分类
    industry TEXT NOT NULL,
    
    -- 时间
    published_at TIMESTAMP NOT NULL,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 元数据
    author TEXT,
    language TEXT NOT NULL DEFAULT 'zh',
    word_count INTEGER,
    
    -- 状态
    archived INTEGER NOT NULL DEFAULT 0,
    archived_at TIMESTAMP,
    
    -- 额外信息
    metadata TEXT,  -- JSON string
    
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE SET NULL,
    
    CHECK (length(title) > 0 AND length(title) <= 500),
    CHECK (length(content) > 0),
    CHECK (archived IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_fetched_at ON articles(fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_industry ON articles(industry);
CREATE INDEX IF NOT EXISTS idx_articles_source_id ON articles(source_id);
CREATE INDEX IF NOT EXISTS idx_articles_archived ON articles(archived);
CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url);

-- 全文搜索索引（SQLite FTS5）
CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
    title,
    content,
    summary,
    content=articles,
    content_rowid=rowid
);

-- FTS 触发器：插入
CREATE TRIGGER IF NOT EXISTS articles_fts_insert AFTER INSERT ON articles BEGIN
    INSERT INTO articles_fts(rowid, title, content, summary)
    VALUES (new.rowid, new.title, new.content, new.summary);
END;

-- FTS 触发器：更新
CREATE TRIGGER IF NOT EXISTS articles_fts_update AFTER UPDATE ON articles BEGIN
    UPDATE articles_fts
    SET title = new.title, content = new.content, summary = new.summary
    WHERE rowid = new.rowid;
END;

-- FTS 触发器：删除
CREATE TRIGGER IF NOT EXISTS articles_fts_delete AFTER DELETE ON articles BEGIN
    DELETE FROM articles_fts WHERE rowid = old.rowid;
END;


-- ============================================================================
-- 文章-标签关联表（多对多）
-- ============================================================================
CREATE TABLE IF NOT EXISTS article_tags (
    article_id TEXT NOT NULL,
    tag_name TEXT NOT NULL,  -- 直接使用标签名，便于查询
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (article_id, tag_name),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_article_tags_article ON article_tags(article_id);
CREATE INDEX IF NOT EXISTS idx_article_tags_tag ON article_tags(tag_name);


-- ============================================================================
-- 分析结果表
-- ============================================================================
CREATE TABLE IF NOT EXISTS analyses (
    id TEXT PRIMARY KEY,
    analysis_type TEXT NOT NULL,  -- 'trend', 'signal', 'gap', 'brief', 'comprehensive'
    
    -- 分析结果（JSON 存储）
    executive_brief TEXT NOT NULL,
    markdown_report TEXT,  -- 完整的Markdown报告（无长度限制）
    trends TEXT,  -- JSON array
    signals TEXT,  -- JSON array
    information_gaps TEXT,  -- JSON array
    
    -- LLM 元数据
    llm_backend TEXT NOT NULL,
    llm_model TEXT,
    token_usage INTEGER,
    estimated_cost REAL,
    
    -- 时间
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processing_time_seconds REAL,
    
    -- 用户反馈
    user_rating INTEGER,
    user_notes TEXT,
    
    CHECK (analysis_type IN ('trend', 'signal', 'gap', 'brief', 'comprehensive')),
    CHECK (user_rating IS NULL OR (user_rating >= 1 AND user_rating <= 5))
);

CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_type ON analyses(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analyses_llm_backend ON analyses(llm_backend);
CREATE INDEX IF NOT EXISTS idx_analyses_rating ON analyses(user_rating);


-- ============================================================================
-- 分析-文章关联表（多对多）
-- ============================================================================
CREATE TABLE IF NOT EXISTS analysis_articles (
    analysis_id TEXT NOT NULL,
    article_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (analysis_id, article_id),
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_analysis_articles_analysis ON analysis_articles(analysis_id);
CREATE INDEX IF NOT EXISTS idx_analysis_articles_article ON analysis_articles(article_id);


-- ============================================================================
-- 配置表（键值对存储）
-- ============================================================================
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认配置
INSERT OR IGNORE INTO config (key, value) VALUES
    ('default_llm_backend', 'deepseek'),
    ('default_fetch_hours', '24'),
    ('archive_path', './archives'),
    ('app_version', '0.1.0');


-- ============================================================================
-- 视图：带标签的文章
-- ============================================================================
CREATE VIEW IF NOT EXISTS articles_with_tags AS
SELECT 
    a.*,
    GROUP_CONCAT(at.tag_name, ',') as tags
FROM articles a
LEFT JOIN article_tags at ON a.id = at.article_id
GROUP BY a.id;


-- ============================================================================
-- 视图：带文章的分析
-- ============================================================================
CREATE VIEW IF NOT EXISTS analyses_with_articles AS
SELECT 
    an.*,
    GROUP_CONCAT(aa.article_id, ',') as article_ids,
    COUNT(aa.article_id) as article_count
FROM analyses an
LEFT JOIN analysis_articles aa ON an.id = aa.analysis_id
GROUP BY an.id;


-- ============================================================================
-- 统计视图
-- ============================================================================
CREATE VIEW IF NOT EXISTS stats_summary AS
SELECT 
    (SELECT COUNT(*) FROM articles) as total_articles,
    (SELECT COUNT(*) FROM articles WHERE archived = 1) as archived_articles,
    (SELECT COUNT(*) FROM sources WHERE enabled = 1) as active_sources,
    (SELECT COUNT(*) FROM analyses) as total_analyses,
    (SELECT COUNT(DISTINCT industry) FROM articles) as industry_count;
