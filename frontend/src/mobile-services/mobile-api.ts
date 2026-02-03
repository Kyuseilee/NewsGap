// 移动端统一 API 层
import { MobileDatabase } from './database';
import { MobileRSSFetcher } from './rss-fetcher';
import { MobileLLMClient } from './llm-client';
import type {
  Article,
  ArticleFilters,
  Analysis,
  AnalysisRequest,
  IntelligenceRequest,
  IntelligenceResponse,
  RSSSource,
  CustomCategory,
  LLMBackend,
  APIKey,
  ProxyConfig
} from './types';

export class MobileAPI {
  private db: MobileDatabase;
  private rssFetcher: MobileRSSFetcher;
  private llmClient: MobileLLMClient;
  private initialized: boolean = false;

  constructor() {
    this.db = new MobileDatabase();
    this.rssFetcher = new MobileRSSFetcher();
    this.llmClient = new MobileLLMClient();
  }

  /**
   * 初始化移动端服务
   */
  async initialize(): Promise<void> {
    if (this.initialized) return;

    try {
      console.log('Initializing mobile API...');
      await this.db.initialize();
      await this.llmClient.initialize();
      await this.initializeDefaultSources();
      this.initialized = true;
      console.log('Mobile API initialized successfully');
    } catch (error) {
      console.error('Failed to initialize mobile API:', error);
      throw error;
    }
  }

  /**
   * 初始化默认信息源
   */
  private async initializeDefaultSources(): Promise<void> {
    const existingSources = await this.db.getSources();
    if (existingSources.length > 0) {
      return; // 已有数据，跳过初始化
    }

    // 添加默认信息源
    const defaultSources: RSSSource[] = [
      // 科技
      { name: '36氪', url: 'https://rsshub.app/36kr/news/latest', industry: 'tech', enabled: true },
      { name: '少数派', url: 'https://rsshub.app/sspai/series', industry: 'tech', enabled: true },
      { name: 'IT之家', url: 'https://rsshub.app/ithome/ranking/7day', industry: 'tech', enabled: true },
      
      // 开发者
      { name: 'GitHub Trending', url: 'https://rsshub.app/github/trending/daily', industry: 'developer', enabled: true },
      { name: 'Hacker News', url: 'https://rsshub.app/hackernews/best', industry: 'developer', enabled: true },
      { name: '掘金', url: 'https://rsshub.app/juejin/trending/all/daily', industry: 'developer', enabled: true },
      
      // 财经
      { name: '财联社', url: 'https://rsshub.app/cls/telegraph', industry: 'finance', enabled: true },
      { name: '金十数据', url: 'https://rsshub.app/jin10/express', industry: 'finance', enabled: true },
      
      // 社交媒体
      { name: '微博热搜', url: 'https://rsshub.app/weibo/search/hot', industry: 'social', enabled: true },
      { name: '知乎热榜', url: 'https://rsshub.app/zhihu/hot', industry: 'social', enabled: true }
    ];

    for (const source of defaultSources) {
      await this.db.createSource(source);
    }

    console.log(`Initialized ${defaultSources.length} default sources`);
  }

  // ========== 情报分析核心功能 ==========

  /**
   * 一键情报：爬取 + 分析
   */
  async intelligence(request: IntelligenceRequest): Promise<IntelligenceResponse> {
    const startTime = Date.now();

    try {
      // 1. 爬取文章
      console.log('Step 1: Fetching articles...');
      let articles: Article[];

      if (request.custom_category_id) {
        // 使用自定义分类
        const category = (await this.db.getCustomCategories()).find(
          c => c.id === request.custom_category_id
        );
        if (!category) {
          throw new Error('Custom category not found');
        }
        const { articles: fetchedArticles } = await this.rssFetcher.fetchMultipleSources(
          category.sources,
          request.hours
        );
        articles = fetchedArticles;
      } else {
        // 使用标准行业分类
        articles = await this.rssFetcher.fetchByIndustry(
          request.industry || 'tech',
          request.hours
        );
      }

      if (articles.length === 0) {
        throw new Error('No articles fetched');
      }

      // 2. 保存文章到数据库
      console.log(`Step 2: Saving ${articles.length} articles...`);
      for (const article of articles) {
        await this.db.createArticle(article);
      }

      // 3. 分析文章
      console.log('Step 3: Analyzing articles...');
      const analysisRequest: AnalysisRequest = {
        analysis_type: 'comprehensive',
        llm_backend: request.llm_backend,
        llm_model: request.llm_model
      };

      const analysis = await this.llmClient.analyze(analysisRequest, articles);

      // 4. 保存分析结果
      console.log('Step 4: Saving analysis...');
      await this.db.createAnalysis(analysis);

      const totalTime = (Date.now() - startTime) / 1000;

      return {
        analysis,
        article_count: articles.length,
        analysis_id: analysis.id!,
        total_time_seconds: totalTime
      };

    } catch (error) {
      console.error('Intelligence operation failed:', error);
      throw error;
    }
  }

  /**
   * 仅爬取文章
   */
  async fetch(params: { industry: string; hours: number }): Promise<{ count: number }> {
    const articles = await this.rssFetcher.fetchByIndustry(params.industry, params.hours);
    
    for (const article of articles) {
      await this.db.createArticle(article);
    }

    return { count: articles.length };
  }

  /**
   * 分析指定文章
   */
  async analyze(request: AnalysisRequest): Promise<{ analysis: Analysis }> {
    let articles: Article[];

    if (request.article_ids) {
      // 从数据库加载文章
      articles = [];
      for (const id of request.article_ids) {
        const article = await this.db.getArticleById(id);
        if (article) {
          articles.push(article);
        }
      }
    } else if (request.articles) {
      articles = request.articles;
    } else {
      throw new Error('No articles provided');
    }

    if (articles.length === 0) {
      throw new Error('No valid articles found');
    }

    const analysis = await this.llmClient.analyze(request, articles);
    await this.db.createAnalysis(analysis);

    return { analysis };
  }

  // ========== 文章管理 ==========

  async getArticles(filters: ArticleFilters = {}): Promise<{ articles: Article[]; total: number }> {
    const articles = await this.db.getArticles(filters);
    return {
      articles,
      total: articles.length
    };
  }

  async exportArticles(articleIds: string[]): Promise<{ success: boolean; output_path: string }> {
    // 移动端暂不支持文件导出，仅标记为已归档
    for (const id of articleIds) {
      await this.db.updateArticle(id, { archived: true });
    }
    
    return {
      success: true,
      output_path: 'local_database'
    };
  }

  async deleteArticles(articleIds: string[]): Promise<{ success: boolean }> {
    await this.db.deleteArticles(articleIds);
    return { success: true };
  }

  // ========== 分析管理 ==========

  async getAnalysesList(): Promise<Analysis[]> {
    return await this.db.getAnalyses();
  }

  async getAnalysis(id: string): Promise<Analysis | null> {
    return await this.db.getAnalysisById(id);
  }

  // ========== 信息源管理 ==========

  async getSources(params?: { enabled_only?: boolean }): Promise<RSSSource[]> {
    return await this.db.getSources(params?.enabled_only || false);
  }

  async updateSource(id: string, updates: Partial<RSSSource>): Promise<{ success: boolean }> {
    await this.db.updateSource(id, updates);
    return { success: true };
  }

  async createSource(source: RSSSource): Promise<{ success: boolean; source: RSSSource }> {
    await this.db.createSource(source);
    return { success: true, source };
  }

  // ========== 自定义分类 ==========

  async getCustomCategories(params?: { enabled_only?: boolean }): Promise<CustomCategory[]> {
    return await this.db.getCustomCategories(params?.enabled_only || false);
  }

  async createCustomCategory(category: CustomCategory): Promise<{ success: boolean }> {
    await this.db.createCustomCategory(category);
    return { success: true };
  }

  // ========== LLM 配置 ==========

  async getLLMBackends(): Promise<{ backends: LLMBackend[] }> {
    return {
      backends: this.llmClient.getLLMBackends()
    };
  }

  async getAPIKeys(): Promise<{ api_keys: APIKey[] }> {
    const backends = this.llmClient.getLLMBackends();
    const apiKeys: APIKey[] = [];

    for (const backend of backends) {
      if (backend.requires_api_key) {
        const key = await this.llmClient.getAPIKey(backend.id);
        apiKeys.push({
          backend: backend.id,
          has_key: !!key,
          masked_key: key ? this.maskAPIKey(key) : undefined
        });
      }
    }

    return { api_keys: apiKeys };
  }

  async setAPIKey(backend: string, apiKey: string): Promise<{ message: string }> {
    await this.llmClient.setAPIKey(backend, apiKey);
    return { message: 'API Key saved successfully' };
  }

  async deleteAPIKey(backend: string): Promise<{ message: string }> {
    await this.llmClient.deleteAPIKey(backend);
    return { message: 'API Key deleted successfully' };
  }

  private maskAPIKey(key: string): string {
    if (key.length <= 8) return '***';
    return `${key.substring(0, 4)}...${key.substring(key.length - 4)}`;
  }

  // ========== 代理配置 (移动端暂不支持) ==========

  async getProxyConfig(): Promise<ProxyConfig> {
    return {
      enabled: false,
      protocol: 'http',
      host: '',
      port: 0
    };
  }

  async setProxyConfig(_config: ProxyConfig): Promise<{ message: string }> {
    return { message: 'Proxy not supported on mobile' };
  }

  async deleteProxyConfig(): Promise<{ message: string }> {
    return { message: 'Proxy not supported on mobile' };
  }

  // ========== 健康检查 ==========

  async health(): Promise<{ status: string; version: string }> {
    return {
      status: 'ok',
      version: '1.0.0-mobile'
    };
  }

  // ========== 清理和重置 ==========

  async clearAllData(): Promise<void> {
    await this.db.clear();
  }

  async close(): Promise<void> {
    await this.db.close();
  }
}
