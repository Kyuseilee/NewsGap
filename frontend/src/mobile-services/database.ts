// 移动端 SQLite 数据库服务
import { CapacitorSQLite, SQLiteConnection, SQLiteDBConnection } from '@capacitor-community/sqlite';
import { Capacitor } from '@capacitor/core';
import type { Article, ArticleFilters, Analysis, RSSSource, CustomCategory } from './types';

export class MobileDatabase {
  private sqlite: SQLiteConnection;
  private db: SQLiteDBConnection | null = null;
  private readonly dbName = 'newsgap.db';

  constructor() {
    this.sqlite = new SQLiteConnection(CapacitorSQLite);
  }

  async initialize(): Promise<void> {
    try {
      // 检查平台支持
      const platform = Capacitor.getPlatform();
      if (platform !== 'ios' && platform !== 'android') {
        console.warn('SQLite only supported on iOS and Android');
        return;
      }

      // 检查是否已经存在连接
      const isConnection = await this.sqlite.isConnection(this.dbName, false);
      if (isConnection.result) {
        this.db = await this.sqlite.retrieveConnection(this.dbName, false);
      } else {
        this.db = await this.sqlite.createConnection(this.dbName, false, 'no-encryption', 1, false);
      }

      await this.db.open();
      await this.createTables();
      console.log('Database initialized successfully');
    } catch (error) {
      console.error('Failed to initialize database:', error);
      throw error;
    }
  }

  private async createTables(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const statements = `
      CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        content TEXT,
        published_at TEXT,
        source_name TEXT,
        industry TEXT,
        archived INTEGER DEFAULT 0,
        tags TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      );

      CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at DESC);
      CREATE INDEX IF NOT EXISTS idx_articles_industry ON articles(industry);
      CREATE INDEX IF NOT EXISTS idx_articles_archived ON articles(archived);

      CREATE TABLE IF NOT EXISTS analyses (
        id TEXT PRIMARY KEY,
        executive_brief TEXT,
        markdown_report TEXT,
        article_ids TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        analysis_type TEXT,
        llm_model TEXT,
        llm_backend TEXT
      );

      CREATE TABLE IF NOT EXISTS sources (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        industry TEXT,
        enabled INTEGER DEFAULT 1,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS custom_categories (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        custom_prompt TEXT,
        enabled INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS category_sources (
        category_id TEXT,
        source_id TEXT,
        PRIMARY KEY (category_id, source_id),
        FOREIGN KEY (category_id) REFERENCES custom_categories(id),
        FOREIGN KEY (source_id) REFERENCES sources(id)
      );
    `;

    await this.db.execute(statements);
  }

  // ========== Articles ==========

  async createArticle(article: Article): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const sql = `
      INSERT OR REPLACE INTO articles (id, title, url, content, published_at, source_name, industry, tags)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `;

    await this.db.run(sql, [
      article.id || this.generateId(),
      article.title,
      article.url,
      article.content,
      article.published_at,
      article.source_name,
      article.industry,
      JSON.stringify(article.tags || [])
    ]);
  }

  async getArticles(filters: ArticleFilters = {}): Promise<Article[]> {
    if (!this.db) throw new Error('Database not initialized');

    let sql = 'SELECT * FROM articles WHERE 1=1';
    const params: any[] = [];

    if (filters.industry) {
      sql += ' AND industry = ?';
      params.push(filters.industry);
    }

    if (filters.archived !== undefined) {
      sql += ' AND archived = ?';
      params.push(filters.archived ? 1 : 0);
    }

    sql += ' ORDER BY published_at DESC';

    if (filters.limit) {
      sql += ' LIMIT ?';
      params.push(filters.limit);
    }

    if (filters.offset) {
      sql += ' OFFSET ?';
      params.push(filters.offset);
    }

    const result = await this.db.query(sql, params);
    
    return (result.values || []).map(row => ({
      ...row,
      archived: Boolean(row.archived),
      tags: row.tags ? JSON.parse(row.tags) : []
    }));
  }

  async getArticleById(id: string): Promise<Article | null> {
    if (!this.db) throw new Error('Database not initialized');

    const sql = 'SELECT * FROM articles WHERE id = ?';
    const result = await this.db.query(sql, [id]);
    
    if (!result.values || result.values.length === 0) {
      return null;
    }

    const row = result.values[0];
    return {
      ...row,
      archived: Boolean(row.archived),
      tags: row.tags ? JSON.parse(row.tags) : []
    };
  }

  async updateArticle(id: string, updates: Partial<Article>): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const fields: string[] = [];
    const params: any[] = [];

    Object.entries(updates).forEach(([key, value]) => {
      if (key === 'tags') {
        fields.push('tags = ?');
        params.push(JSON.stringify(value));
      } else if (key === 'archived') {
        fields.push('archived = ?');
        params.push(value ? 1 : 0);
      } else if (key !== 'id') {
        fields.push(`${key} = ?`);
        params.push(value);
      }
    });

    if (fields.length === 0) return;

    params.push(id);
    const sql = `UPDATE articles SET ${fields.join(', ')} WHERE id = ?`;
    await this.db.run(sql, params);
  }

  async deleteArticles(ids: string[]): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');
    
    const placeholders = ids.map(() => '?').join(',');
    const sql = `DELETE FROM articles WHERE id IN (${placeholders})`;
    await this.db.run(sql, ids);
  }

  // ========== Analyses ==========

  async createAnalysis(analysis: Analysis): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const sql = `
      INSERT INTO analyses (id, executive_brief, markdown_report, article_ids, analysis_type, llm_model, llm_backend)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `;

    await this.db.run(sql, [
      analysis.id || this.generateId(),
      analysis.executive_brief,
      analysis.markdown_report,
      JSON.stringify(analysis.article_ids),
      analysis.analysis_type,
      analysis.llm_model,
      analysis.llm_backend || 'gemini'
    ]);
  }

  async getAnalyses(): Promise<Analysis[]> {
    if (!this.db) throw new Error('Database not initialized');

    const sql = 'SELECT * FROM analyses ORDER BY created_at DESC';
    const result = await this.db.query(sql);
    
    return (result.values || []).map(row => ({
      ...row,
      article_ids: JSON.parse(row.article_ids)
    }));
  }

  async getAnalysisById(id: string): Promise<Analysis | null> {
    if (!this.db) throw new Error('Database not initialized');

    const sql = 'SELECT * FROM analyses WHERE id = ?';
    const result = await this.db.query(sql, [id]);
    
    if (!result.values || result.values.length === 0) {
      return null;
    }

    const row = result.values[0];
    return {
      ...row,
      article_ids: JSON.parse(row.article_ids)
    };
  }

  // ========== Sources ==========

  async createSource(source: RSSSource): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const sql = `
      INSERT INTO sources (id, name, url, industry, enabled, description)
      VALUES (?, ?, ?, ?, ?, ?)
    `;

    await this.db.run(sql, [
      source.id || this.generateId(),
      source.name,
      source.url,
      source.industry,
      source.enabled ? 1 : 0,
      source.description || ''
    ]);
  }

  async getSources(enabledOnly: boolean = false): Promise<RSSSource[]> {
    if (!this.db) throw new Error('Database not initialized');

    let sql = 'SELECT * FROM sources';
    if (enabledOnly) {
      sql += ' WHERE enabled = 1';
    }
    sql += ' ORDER BY industry, name';

    const result = await this.db.query(sql);
    
    return (result.values || []).map(row => ({
      ...row,
      enabled: Boolean(row.enabled)
    }));
  }

  async updateSource(id: string, updates: Partial<RSSSource>): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const fields: string[] = [];
    const params: any[] = [];

    Object.entries(updates).forEach(([key, value]) => {
      if (key === 'enabled') {
        fields.push('enabled = ?');
        params.push(value ? 1 : 0);
      } else if (key !== 'id') {
        fields.push(`${key} = ?`);
        params.push(value);
      }
    });

    if (fields.length === 0) return;

    params.push(id);
    const sql = `UPDATE sources SET ${fields.join(', ')} WHERE id = ?`;
    await this.db.run(sql, params);
  }

  // ========== Custom Categories ==========

  async createCustomCategory(category: CustomCategory): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const categoryId = category.id || this.generateId();

    const sql = `
      INSERT INTO custom_categories (id, name, description, custom_prompt, enabled)
      VALUES (?, ?, ?, ?, ?)
    `;

    await this.db.run(sql, [
      categoryId,
      category.name,
      category.description || '',
      category.custom_prompt,
      category.enabled ? 1 : 0
    ]);

    // 添加关联的信息源
    if (category.sources && category.sources.length > 0) {
      for (const source of category.sources) {
        await this.addSourceToCategory(categoryId, source.id!);
      }
    }
  }

  async getCustomCategories(enabledOnly: boolean = false): Promise<CustomCategory[]> {
    if (!this.db) throw new Error('Database not initialized');

    let sql = 'SELECT * FROM custom_categories';
    if (enabledOnly) {
      sql += ' WHERE enabled = 1';
    }
    sql += ' ORDER BY name';

    const result = await this.db.query(sql);
    const categories = (result.values || []).map(row => ({
      ...row,
      enabled: Boolean(row.enabled),
      sources: [] as RSSSource[]
    }));

    // 加载每个分类的信息源
    for (const category of categories) {
      category.sources = await this.getCategorySources(category.id!);
    }

    return categories;
  }

  private async getCategorySources(categoryId: string): Promise<RSSSource[]> {
    if (!this.db) throw new Error('Database not initialized');

    const sql = `
      SELECT s.* FROM sources s
      JOIN category_sources cs ON s.id = cs.source_id
      WHERE cs.category_id = ?
    `;

    const result = await this.db.query(sql, [categoryId]);
    return (result.values || []).map(row => ({
      ...row,
      enabled: Boolean(row.enabled)
    }));
  }

  private async addSourceToCategory(categoryId: string, sourceId: string): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const sql = 'INSERT OR IGNORE INTO category_sources (category_id, source_id) VALUES (?, ?)';
    await this.db.run(sql, [categoryId, sourceId]);
  }

  // ========== Utilities ==========

  private generateId(): string {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  async close(): Promise<void> {
    if (this.db) {
      await this.db.close();
      this.db = null;
    }
  }

  async clear(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    await this.db.execute('DELETE FROM articles');
    await this.db.execute('DELETE FROM analyses');
    console.log('Database cleared');
  }
}
