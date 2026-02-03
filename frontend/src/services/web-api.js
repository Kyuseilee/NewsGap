/**
 * API 客户端
 */
import axios from 'axios';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 300000, // 5 分钟超时
    headers: {
        'Content-Type': 'application/json',
    },
});
export const api = {
    // 爬取相关
    fetch: async (request) => {
        const { data } = await client.post('/api/fetch', request);
        return data;
    },
    // 分析相关
    analyze: async (request) => {
        const { data } = await client.post('/api/analyze', request);
        return data;
    },
    estimateCost: async (request) => {
        const { data } = await client.post('/api/analyze/estimate-cost', request);
        return data;
    },
    // 一键情报
    intelligence: async (request) => {
        const { data } = await client.post('/api/intelligence', request);
        return data;
    },
    // 文章相关
    getArticles: async (params) => {
        const { data } = await client.get('/api/articles', { params });
        return data;
    },
    getArticle: async (id) => {
        const { data } = await client.get(`/api/articles/${id}`);
        return data;
    },
    searchArticles: async (query, limit) => {
        const { data } = await client.get(`/api/articles/search/${query}`, {
            params: { limit },
        });
        return data;
    },
    archiveArticle: async (id) => {
        await client.post(`/api/articles/${id}/archive`);
    },
    exportArticles: async (articleIds) => {
        const { data } = await client.post('/api/articles/export', {
            article_ids: articleIds,
        });
        return data;
    },
    // 配置相关
    getSources: async (params) => {
        const { data } = await client.get('/api/config/sources', { params });
        return data;
    },
    createSource: async (source) => {
        const { data } = await client.post('/api/config/sources', source);
        return data;
    },
    addSource: async (source) => {
        const { data } = await client.post('/api/config/sources', source);
        return data;
    },
    updateSource: async (id, source) => {
        const { data } = await client.put(`/api/config/sources/${id}`, source);
        return data;
    },
    deleteSource: async (id) => {
        await client.delete(`/api/config/sources/${id}`);
    },
    getLLMBackends: async () => {
        const { data } = await client.get('/api/config/llm-backends');
        return data;
    },
    // API Key 管理
    getAPIKeys: async () => {
        const { data } = await client.get('/api/config/api-keys');
        return data;
    },
    setAPIKey: async (backend, apiKey) => {
        const { data } = await client.post('/api/config/api-keys', {
            backend,
            api_key: apiKey
        });
        return data;
    },
    deleteAPIKey: async (backend) => {
        const { data } = await client.delete(`/api/config/api-keys/${backend}`);
        return data;
    },
    // 分析结果相关（需要在后端添加对应路由）
    getAnalysis: async (id) => {
        const { data } = await client.get(`/api/analyses/${id}`);
        return data;
    },
    getAnalysesList: async () => {
        const { data } = await client.get('/api/analyses');
        return data;
    },
    // 自定义分类相关
    getCustomCategories: async (params) => {
        const { data } = await client.get('/api/custom-categories', { params });
        return data;
    },
    getCustomCategory: async (id) => {
        const { data } = await client.get(`/api/custom-categories/${id}`);
        return data;
    },
    createCustomCategory: async (request) => {
        const { data } = await client.post('/api/custom-categories', request);
        return data;
    },
    updateCustomCategory: async (id, request) => {
        const { data } = await client.put(`/api/custom-categories/${id}`, request);
        return data;
    },
    deleteCustomCategory: async (id) => {
        await client.delete(`/api/custom-categories/${id}`);
    },
    getCustomCategorySources: async (categoryId) => {
        const { data } = await client.get(`/api/custom-categories/${categoryId}/sources`);
        return data;
    },
    addSourceToCustomCategory: async (categoryId, sourceId) => {
        await client.post(`/api/custom-categories/${categoryId}/sources/${sourceId}`);
    },
    removeSourceFromCustomCategory: async (categoryId, sourceId) => {
        await client.delete(`/api/custom-categories/${categoryId}/sources/${sourceId}`);
    },
    // 代理配置
    getProxyConfig: async () => {
        const { data } = await client.get('/api/config/proxy');
        return data;
    },
    setProxyConfig: async (config) => {
        const { data } = await client.post('/api/config/proxy', config);
        return data;
    },
    deleteProxyConfig: async () => {
        const { data } = await client.delete('/api/config/proxy');
        return data;
    },
};
