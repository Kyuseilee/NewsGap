// 移动端 RSS 爬取服务
import Parser from 'rss-parser';
import { Http } from '@capacitor-community/http';
export class MobileRSSFetcher {
    constructor() {
        Object.defineProperty(this, "parser", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        this.parser = new Parser({
            customFields: {
                item: [
                    ['description', 'description'],
                    ['content:encoded', 'contentEncoded'],
                    ['contentSnippet', 'contentSnippet']
                ]
            }
        });
    }
    /**
     * 从单个 RSS 源爬取文章
     */
    async fetchFromSource(source, hoursAgo) {
        try {
            console.log(`Fetching RSS from: ${source.name} (${source.url})`);
            // 使用 Capacitor HTTP 插件
            const response = await Http.get({
                url: source.url,
                headers: {
                    'User-Agent': 'NewsGap-Mobile/1.0',
                    'Accept': 'application/rss+xml, application/xml, text/xml'
                }
            });
            if (response.status !== 200) {
                throw new Error(`HTTP ${response.status}: ${response.url}`);
            }
            // 解析 RSS
            const feed = await this.parser.parseString(response.data);
            if (!feed.items || feed.items.length === 0) {
                console.warn(`No items found in feed: ${source.name}`);
                return [];
            }
            // 时间过滤
            const cutoffTime = hoursAgo
                ? new Date(Date.now() - hoursAgo * 60 * 60 * 1000)
                : null;
            // 转换为 Article 对象
            const articles = feed.items
                .filter(item => {
                if (!cutoffTime)
                    return true;
                const pubDate = item.pubDate ? new Date(item.pubDate) : null;
                return pubDate && pubDate >= cutoffTime;
            })
                .map(item => this.convertToArticle(item, source));
            console.log(`Fetched ${articles.length} articles from ${source.name}`);
            return articles;
        }
        catch (error) {
            console.error(`Failed to fetch ${source.url}:`, error);
            return [];
        }
    }
    /**
     * 从多个源并发爬取
     */
    async fetchMultipleSources(sources, hoursAgo) {
        console.log(`Fetching from ${sources.length} sources...`);
        const results = await Promise.allSettled(sources.map(source => this.fetchFromSource(source, hoursAgo)));
        const articles = [];
        const errors = [];
        results.forEach((result, index) => {
            if (result.status === 'fulfilled') {
                articles.push(...result.value);
            }
            else {
                const sourceName = sources[index].name;
                errors.push(`${sourceName}: ${result.reason}`);
                console.error(`Failed to fetch ${sourceName}:`, result.reason);
            }
        });
        // 去重（基于 URL）
        const uniqueArticles = this.deduplicateArticles(articles);
        console.log(`Total articles fetched: ${uniqueArticles.length} (${errors.length} errors)`);
        return { articles: uniqueArticles, errors };
    }
    /**
     * 按行业爬取（从内置配置）
     */
    async fetchByIndustry(industry, hoursAgo = 24) {
        const sources = this.getSourcesByIndustry(industry);
        const { articles } = await this.fetchMultipleSources(sources, hoursAgo);
        return articles;
    }
    /**
     * 转换 RSS item 为 Article
     */
    convertToArticle(item, source) {
        const content = this.extractContent(item);
        const publishedAt = item.pubDate ? new Date(item.pubDate).toISOString() : new Date().toISOString();
        return {
            id: this.generateArticleId(item.link || item.guid || item.title),
            title: item.title || 'Untitled',
            url: item.link || item.guid || '',
            content: content,
            published_at: publishedAt,
            source_name: source.name,
            industry: source.industry,
            tags: item.categories || [],
            created_at: new Date().toISOString()
        };
    }
    /**
     * 提取文章内容
     */
    extractContent(item) {
        // 优先级: content:encoded > content > contentSnippet > description
        return (item.contentEncoded ||
            item.content ||
            item.contentSnippet ||
            item.description ||
            '');
    }
    /**
     * 生成文章 ID
     */
    generateArticleId(uniqueString) {
        // 简单的哈希函数
        let hash = 0;
        for (let i = 0; i < uniqueString.length; i++) {
            const char = uniqueString.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return `article_${Math.abs(hash).toString(36)}`;
    }
    /**
     * 去重文章
     */
    deduplicateArticles(articles) {
        const seen = new Set();
        return articles.filter(article => {
            const key = article.url || article.title;
            if (seen.has(key)) {
                return false;
            }
            seen.add(key);
            return true;
        });
    }
    /**
     * 获取内置信息源配置（按行业）
     */
    getSourcesByIndustry(industry) {
        const allSources = {
            tech: [
                {
                    id: 'tech_36kr',
                    name: '36氪',
                    url: 'https://rsshub.app/36kr/news/latest',
                    industry: 'tech',
                    enabled: true
                },
                {
                    id: 'tech_sspai',
                    name: '少数派',
                    url: 'https://rsshub.app/sspai/series',
                    industry: 'tech',
                    enabled: true
                },
                {
                    id: 'tech_ithome',
                    name: 'IT之家',
                    url: 'https://rsshub.app/ithome/ranking/7day',
                    industry: 'tech',
                    enabled: true
                }
            ],
            developer: [
                {
                    id: 'dev_github_trending',
                    name: 'GitHub Trending',
                    url: 'https://rsshub.app/github/trending/daily',
                    industry: 'developer',
                    enabled: true
                },
                {
                    id: 'dev_hackernews',
                    name: 'Hacker News',
                    url: 'https://rsshub.app/hackernews/best',
                    industry: 'developer',
                    enabled: true
                },
                {
                    id: 'dev_juejin',
                    name: '掘金',
                    url: 'https://rsshub.app/juejin/trending/all/daily',
                    industry: 'developer',
                    enabled: true
                }
            ],
            finance: [
                {
                    id: 'fin_cls',
                    name: '财联社',
                    url: 'https://rsshub.app/cls/telegraph',
                    industry: 'finance',
                    enabled: true
                },
                {
                    id: 'fin_jin10',
                    name: '金十数据',
                    url: 'https://rsshub.app/jin10/express',
                    industry: 'finance',
                    enabled: true
                },
                {
                    id: 'fin_eastmoney',
                    name: '东方财富',
                    url: 'https://rsshub.app/eastmoney/7x24/global',
                    industry: 'finance',
                    enabled: true
                }
            ],
            crypto: [
                {
                    id: 'crypto_jinse',
                    name: '金色财经',
                    url: 'https://rsshub.app/jinse/lives',
                    industry: 'crypto',
                    enabled: true
                },
                {
                    id: 'crypto_8btc',
                    name: '律动BlockBeats',
                    url: 'https://rsshub.app/theblockbeats/express',
                    industry: 'crypto',
                    enabled: true
                }
            ],
            social: [
                {
                    id: 'social_weibo',
                    name: '微博热搜',
                    url: 'https://rsshub.app/weibo/search/hot',
                    industry: 'social',
                    enabled: true
                },
                {
                    id: 'social_zhihu',
                    name: '知乎热榜',
                    url: 'https://rsshub.app/zhihu/hot',
                    industry: 'social',
                    enabled: true
                },
                {
                    id: 'social_jike',
                    name: '即刻',
                    url: 'https://rsshub.app/jike/topic/daily',
                    industry: 'social',
                    enabled: true
                }
            ]
        };
        return allSources[industry] || [];
    }
}
