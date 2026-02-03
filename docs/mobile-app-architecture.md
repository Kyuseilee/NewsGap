# NewsGap 移动端一体化架构方案

## 需求分析

将 NewsGap（FastAPI + React）改造为独立运行的移动应用，前后端都运行在手机上。

## 核心挑战

1. **Python 后端移植**: Python 在移动端运行受限
2. **数据存储**: SQLite 需要适配移动端
3. **LLM API 调用**: 需要网络连接
4. **RSS 爬取**: 需要网络访问

## 推荐方案: Capacitor + 本地化后端

### 架构设计

```
移动应用
├── Capacitor 容器
│   ├── React 前端 (Web技术)
│   ├── SQLite Plugin (本地数据库)
│   ├── HTTP Plugin (网络请求)
│   └── Filesystem Plugin (文件存储)
│
└── 本地化逻辑层 (TypeScript/JavaScript)
    ├── 数据管理 (SQLite)
    ├── RSS 爬取 (JavaScript)
    ├── LLM API 调用 (网络)
    └── 业务逻辑
```

### 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 容器 | Capacitor | 将 Web 应用打包为原生 App |
| 前端 | React 18 | 现有前端代码 |
| 数据库 | SQLite (Capacitor Plugin) | 本地数据存储 |
| 网络 | Capacitor HTTP Plugin | RSS 爬取和 LLM API |
| 后端逻辑 | TypeScript/JavaScript | 重写 Python 后端核心逻辑 |

### 需要重写的后端模块

#### 1. 数据存储层 (storage/)
```typescript
// backend/storage/db.py → mobile/src/services/database.ts
import { CapacitorSQLite } from '@capacitor-community/sqlite';

export class Database {
  async createArticle(article: Article) {
    // SQLite 操作
  }
  
  async getArticles(filters: ArticleFilters) {
    // 查询逻辑
  }
}
```

#### 2. RSS 爬取模块 (crawler/)
```typescript
// backend/crawler/rss_fetcher.py → mobile/src/services/rss-fetcher.ts
import { Http } from '@capacitor-community/http';
import * as RSSParser from 'rss-parser';

export class RSSFetcher {
  async fetch(sourceUrl: string) {
    const response = await Http.get({ url: sourceUrl });
    const parser = new RSSParser();
    return parser.parseString(response.data);
  }
}
```

#### 3. LLM 集成 (llm/)
```typescript
// backend/llm/ → mobile/src/services/llm-client.ts
import { Http } from '@capacitor-community/http';

export class LLMClient {
  async analyze(articles: Article[], apiKey: string) {
    const response = await Http.post({
      url: 'https://generativelanguage.googleapis.com/v1/...',
      headers: { 'Authorization': `Bearer ${apiKey}` },
      data: { /* ... */ }
    });
    return response.data;
  }
}
```

#### 4. 配置管理
```typescript
// 使用 Capacitor Storage 或 Preferences
import { Preferences } from '@capacitor/preferences';

export class Config {
  async setAPIKey(key: string) {
    await Preferences.set({ key: 'gemini_api_key', value: key });
  }
  
  async getAPIKey(): Promise<string | null> {
    const { value } = await Preferences.get({ key: 'gemini_api_key' });
    return value;
  }
}
```

## 实施步骤

### 阶段 1: 环境搭建 (1-2天)

```bash
# 1. 安装 Capacitor
cd frontend
npm install @capacitor/core @capacitor/cli
npx cap init

# 2. 添加平台
npx cap add ios
npx cap add android

# 3. 安装必要插件
npm install @capacitor-community/sqlite
npm install @capacitor-community/http
npm install @capacitor/preferences
npm install @capacitor/filesystem
```

### 阶段 2: 重写后端核心逻辑 (3-5天)

#### 2.1 数据库层
创建 `frontend/src/mobile-services/database.ts`

```typescript
import { CapacitorSQLite, SQLiteConnection, SQLiteDBConnection } from '@capacitor-community/sqlite';

export class MobileDatabase {
  private db: SQLiteDBConnection | null = null;
  
  async initialize() {
    const sqlite = new SQLiteConnection(CapacitorSQLite);
    this.db = await sqlite.createConnection('newsgap', false, 'no-encryption', 1);
    await this.db.open();
    await this.createTables();
  }
  
  private async createTables() {
    const createArticlesTable = `
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
    `;
    await this.db!.execute(createArticlesTable);
    
    // 创建其他表...
  }
  
  async createArticle(article: Article) {
    const sql = `INSERT INTO articles (id, title, url, content, published_at, source_name, industry)
                 VALUES (?, ?, ?, ?, ?, ?, ?)`;
    await this.db!.run(sql, [
      article.id,
      article.title,
      article.url,
      article.content,
      article.published_at,
      article.source_name,
      article.industry
    ]);
  }
  
  async getArticles(filters: ArticleFilters): Promise<Article[]> {
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
    
    sql += ' ORDER BY published_at DESC LIMIT ?';
    params.push(filters.limit || 100);
    
    const result = await this.db!.query(sql, params);
    return result.values || [];
  }
}
```

#### 2.2 RSS 爬取层
创建 `frontend/src/mobile-services/rss-fetcher.ts`

```typescript
import { Http } from '@capacitor-community/http';
import Parser from 'rss-parser';

export interface RSSSource {
  url: string;
  name: string;
  industry: string;
}

export class MobileRSSFetcher {
  private parser: Parser;
  
  constructor() {
    this.parser = new Parser({
      customFields: {
        item: ['description', 'content:encoded', 'contentSnippet']
      }
    });
  }
  
  async fetchFromSource(source: RSSSource): Promise<Article[]> {
    try {
      const response = await Http.get({
        url: source.url,
        headers: {
          'User-Agent': 'NewsGap-Mobile/1.0'
        }
      });
      
      const feed = await this.parser.parseString(response.data);
      
      return feed.items.map(item => ({
        id: this.generateId(item.link || ''),
        title: item.title || '',
        url: item.link || '',
        content: this.extractContent(item),
        published_at: item.pubDate || new Date().toISOString(),
        source_name: source.name,
        industry: source.industry,
        tags: item.categories || []
      }));
    } catch (error) {
      console.error(`Failed to fetch ${source.url}:`, error);
      return [];
    }
  }
  
  async fetchMultipleSources(sources: RSSSource[]): Promise<Article[]> {
    const results = await Promise.allSettled(
      sources.map(source => this.fetchFromSource(source))
    );
    
    return results
      .filter(result => result.status === 'fulfilled')
      .flatMap(result => (result as PromiseFulfilledResult<Article[]>).value);
  }
  
  private extractContent(item: any): string {
    return item['content:encoded'] || 
           item.content || 
           item.contentSnippet || 
           item.description || 
           '';
  }
  
  private generateId(url: string): string {
    // 简单的哈希函数
    let hash = 0;
    for (let i = 0; i < url.length; i++) {
      hash = ((hash << 5) - hash) + url.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(36);
  }
}
```

#### 2.3 LLM 客户端层
创建 `frontend/src/mobile-services/llm-client.ts`

```typescript
import { Http } from '@capacitor-community/http';
import { Preferences } from '@capacitor/preferences';

export interface AnalysisRequest {
  articles: Article[];
  analysisType: string;
  customPrompt?: string;
}

export class MobileLLMClient {
  private apiKey: string = '';
  private baseUrl = 'https://generativelanguage.googleapis.com/v1beta';
  
  async initialize() {
    const { value } = await Preferences.get({ key: 'gemini_api_key' });
    this.apiKey = value || '';
  }
  
  async analyze(request: AnalysisRequest): Promise<Analysis> {
    if (!this.apiKey) {
      throw new Error('API Key not configured');
    }
    
    const prompt = this.buildPrompt(request);
    
    const response = await Http.post({
      url: `${this.baseUrl}/models/gemini-2.0-flash-exp:generateContent?key=${this.apiKey}`,
      headers: {
        'Content-Type': 'application/json'
      },
      data: {
        contents: [{
          parts: [{
            text: prompt
          }]
        }],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 8000
        }
      }
    });
    
    const content = response.data.candidates[0].content.parts[0].text;
    
    return {
      id: this.generateId(),
      executive_brief: this.extractBrief(content),
      markdown_report: content,
      article_ids: request.articles.map(a => a.id),
      created_at: new Date().toISOString(),
      analysis_type: request.analysisType,
      llm_model: 'gemini-2.0-flash-exp'
    };
  }
  
  private buildPrompt(request: AnalysisRequest): string {
    const articlesText = request.articles
      .map((a, i) => `[${i + 1}] ${a.title}\n${a.content.substring(0, 500)}...\n`)
      .join('\n');
    
    return `${request.customPrompt || this.getDefaultPrompt()}\n\n${articlesText}`;
  }
  
  private getDefaultPrompt(): string {
    return `你是一个专业的信息分析师。请分析以下文章，生成情报报告：

1. **执行摘要** (3-5个要点)
2. **核心主线** (识别2-3条主要叙事)
3. **关键信号** (高/中/低置信度)
4. **行动建议**

要求：
- 只关注真正重要的信号
- 提供可操作的建议
- 标明证据来源`;
  }
  
  private extractBrief(content: string): string {
    const lines = content.split('\n');
    return lines.slice(0, 3).join(' ');
  }
  
  private generateId(): string {
    return `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
```

### 阶段 3: 前端适配 (2-3天)

#### 3.1 修改 API 服务层

```typescript
// frontend/src/services/mobile-api.ts
import { MobileDatabase } from '../mobile-services/database';
import { MobileRSSFetcher } from '../mobile-services/rss-fetcher';
import { MobileLLMClient } from '../mobile-services/llm-client';

export class MobileAPI {
  private db: MobileDatabase;
  private rssFetcher: MobileRSSFetcher;
  private llmClient: MobileLLMClient;
  
  constructor() {
    this.db = new MobileDatabase();
    this.rssFetcher = new MobileRSSFetcher();
    this.llmClient = new MobileLLMClient();
  }
  
  async initialize() {
    await this.db.initialize();
    await this.llmClient.initialize();
  }
  
  // 实现所有原来的 API 方法
  async fetch(params: { industry: string; hours: number }) {
    const sources = await this.getSources(params.industry);
    const articles = await this.rssFetcher.fetchMultipleSources(sources);
    
    for (const article of articles) {
      await this.db.createArticle(article);
    }
    
    return { count: articles.length };
  }
  
  async getArticles(filters: ArticleFilters) {
    return await this.db.getArticles(filters);
  }
  
  async analyze(request: AnalysisRequest) {
    const analysis = await this.llmClient.analyze(request);
    await this.db.createAnalysis(analysis);
    return analysis;
  }
  
  // ... 其他方法
}
```

#### 3.2 条件编译

```typescript
// frontend/src/services/api.ts
import { Capacitor } from '@capacitor/core';
import { MobileAPI } from './mobile-api';
import { WebAPI } from './web-api';

export const api = Capacitor.isNativePlatform() 
  ? new MobileAPI() 
  : new WebAPI(); // 原来的 axios 实现
```

### 阶段 4: 配置和打包 (1-2天)

#### 4.1 Capacitor 配置

**capacitor.config.ts**:
```typescript
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.newsgap.app',
  appName: 'NewsGap',
  webDir: 'dist',
  bundledWebRuntime: false,
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#ffffff'
    }
  }
};

export default config;
```

#### 4.2 构建脚本

**package.json**:
```json
{
  "scripts": {
    "build:mobile": "vite build && cap sync",
    "ios:dev": "cap run ios",
    "android:dev": "cap run android",
    "ios:build": "cap build ios",
    "android:build": "cap build android"
  }
}
```

### 阶段 5: 测试和优化 (2-3天)

1. 功能测试
2. 性能优化
3. 离线支持
4. 错误处理

## 预估工作量

| 阶段 | 工作量 | 说明 |
|------|--------|------|
| 环境搭建 | 1-2天 | Capacitor 安装配置 |
| 后端重写 | 3-5天 | 核心逻辑改造 |
| 前端适配 | 2-3天 | API 切换、条件编译 |
| 配置打包 | 1-2天 | iOS/Android 配置 |
| 测试优化 | 2-3天 | 功能测试、性能优化 |
| **总计** | **9-15天** | 约 2-3 周 |

## 技术依赖

```json
{
  "dependencies": {
    "@capacitor/core": "^5.0.0",
    "@capacitor/cli": "^5.0.0",
    "@capacitor/ios": "^5.0.0",
    "@capacitor/android": "^5.0.0",
    "@capacitor-community/sqlite": "^5.0.0",
    "@capacitor-community/http": "^2.0.0",
    "@capacitor/preferences": "^5.0.0",
    "@capacitor/filesystem": "^5.0.0",
    "rss-parser": "^3.13.0"
  }
}
```

## 优势

1. ✅ **前端代码复用**: 90%+ 的前端代码不需要改动
2. ✅ **离线优先**: 数据本地存储，无需后端服务器
3. ✅ **跨平台**: 一套代码支持 iOS 和 Android
4. ✅ **原生功能**: 可以访问原生 API
5. ✅ **开发效率**: 相比完全重写节省 80% 时间

## 劣势

1. ❌ **需要重写后端**: Python 逻辑需要用 TypeScript 重写
2. ❌ **性能**: 不如原生应用
3. ❌ **包体积**: 比纯原生应用大

## 替代方案

### 方案 B: Tauri Mobile (实验性)
- 使用 Rust 后端
- 更轻量，更接近原生
- 但需要学习 Rust

### 方案 C: Flutter + Python
- 用 Flutter 重写前端
- Python 后端通过 Chaquopy (Android) 或 Python-iOS 运行
- 需要完全重写前端

## 建议

**推荐采用 Capacitor 方案**，理由：
1. 前端代码改动最小
2. 技术栈相近（都是 Web 技术）
3. 社区成熟，文档齐全
4. 开发周期可控

## 下一步

1. 确认方案
2. 创建 `mobile` 分支
3. 按阶段实施
4. 持续测试和迭代

---

**文档版本**: v1.0  
**最后更新**: 2026-02-03  
**负责人**: NewsGap Team
