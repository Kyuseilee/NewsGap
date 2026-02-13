/**
 * API 客户端
 */

import axios from 'axios'
import type {
  Article,
  Source,
  FetchResponse,
  AnalyzeRequest,
  AnalyzeResponse,
  IntelligenceRequest,
  IntelligenceResponse,
  Analysis,
  CustomCategory,
  CreateCustomCategoryRequest,
  UpdateCustomCategoryRequest,
} from '@/types/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 分钟超时
  headers: {
    'Content-Type': 'application/json',
  },
})

export const api = {
  // 爬取相关
  fetch: async (request: { industry: string; hours: number; source_ids?: string[] }): Promise<FetchResponse> => {
    const { data } = await client.post('/api/fetch', request)
    return data
  },

  // 分析相关
  analyze: async (request: AnalyzeRequest): Promise<AnalyzeResponse> => {
    const { data } = await client.post('/api/analyze', request)
    return data
  },

  estimateCost: async (request: AnalyzeRequest): Promise<any> => {
    const { data } = await client.post('/api/analyze/estimate-cost', request)
    return data
  },

  // 一键情报
  intelligence: async (request: IntelligenceRequest): Promise<IntelligenceResponse> => {
    const { data } = await client.post('/api/intelligence', request)
    return data
  },

  // 文章相关
  getArticles: async (params?: {
    industry?: string
    start_time?: string
    end_time?: string
    tags?: string[]
    limit?: number
    offset?: number
    archived?: boolean
  }): Promise<{ articles: Article[]; total: number }> => {
    const { data } = await client.get('/api/articles', { params })
    return data
  },

  getArticle: async (id: string): Promise<Article> => {
    const { data } = await client.get(`/api/articles/${id}`)
    return data
  },

  searchArticles: async (query: string, limit?: number): Promise<{ articles: Article[] }> => {
    const { data } = await client.get(`/api/articles/search/${query}`, {
      params: { limit },
    })
    return data
  },

  archiveArticle: async (id: string): Promise<void> => {
    await client.post(`/api/articles/${id}/archive`)
  },

  exportArticles: async (articleIds: string[]): Promise<any> => {
    const { data } = await client.post('/api/articles/export', {
      article_ids: articleIds,
    })
    return data
  },

  // 配置相关
  getSources: async (params?: {
    industry?: string
    enabled_only?: boolean
  }): Promise<Source[]> => {
    const { data } = await client.get('/api/config/sources', { params })
    return data
  },

  createSource: async (source: Source): Promise<Source> => {
    const { data } = await client.post('/api/config/sources', source)
    return data
  },

  addSource: async (source: any): Promise<Source> => {
    const { data } = await client.post('/api/config/sources', source)
    return data
  },

  updateSource: async (id: string, source: Source): Promise<Source> => {
    const { data } = await client.put(`/api/config/sources/${id}`, source)
    return data
  },

  deleteSource: async (id: string): Promise<void> => {
    await client.delete(`/api/config/sources/${id}`)
  },

  getLLMBackends: async (): Promise<any> => {
    const { data} = await client.get('/api/config/llm-backends')
    return data
  },

  // API Key 管理
  getAPIKeys: async (): Promise<any> => {
    const { data } = await client.get('/api/config/api-keys')
    return data
  },

  setAPIKey: async (backend: string, apiKey: string): Promise<any> => {
    const { data } = await client.post('/api/config/api-keys', {
      backend,
      api_key: apiKey
    })
    return data
  },

  deleteAPIKey: async (backend: string): Promise<any> => {
    const { data } = await client.delete(`/api/config/api-keys/${backend}`)
    return data
  },

  // 分析结果相关（需要在后端添加对应路由）
  getAnalysis: async (id: string): Promise<Analysis> => {
    const { data } = await client.get(`/api/analyses/${id}`)
    return data
  },

  getAnalysesList: async (): Promise<Analysis[]> => {
    const { data } = await client.get('/api/analyses')
    return data
  },

  // 自定义分类相关
  getCustomCategories: async (params?: {
    enabled_only?: boolean
  }): Promise<CustomCategory[]> => {
    const { data } = await client.get('/api/custom-categories', { params })
    return data
  },

  getCustomCategory: async (id: string): Promise<CustomCategory> => {
    const { data } = await client.get(`/api/custom-categories/${id}`)
    return data
  },

  createCustomCategory: async (request: CreateCustomCategoryRequest): Promise<CustomCategory> => {
    const { data } = await client.post('/api/custom-categories', request)
    return data
  },

  updateCustomCategory: async (id: string, request: UpdateCustomCategoryRequest): Promise<CustomCategory> => {
    const { data } = await client.put(`/api/custom-categories/${id}`, request)
    return data
  },

  deleteCustomCategory: async (id: string): Promise<void> => {
    await client.delete(`/api/custom-categories/${id}`)
  },

  getCustomCategorySources: async (categoryId: string): Promise<Source[]> => {
    const { data } = await client.get(`/api/custom-categories/${categoryId}/sources`)
    return data
  },

  addSourceToCustomCategory: async (categoryId: string, sourceId: string): Promise<void> => {
    await client.post(`/api/custom-categories/${categoryId}/sources/${sourceId}`)
  },

  removeSourceFromCustomCategory: async (categoryId: string, sourceId: string): Promise<void> => {
    await client.delete(`/api/custom-categories/${categoryId}/sources/${sourceId}`)
  },

  // 代理配置
  getProxyConfig: async (): Promise<any> => {
    const { data } = await client.get('/api/config/proxy')
    return data
  },

  setProxyConfig: async (config: {
    enabled: boolean
    http_proxy: string
    https_proxy: string
    socks5_proxy: string
  }): Promise<any> => {
    const { data } = await client.post('/api/config/proxy', config)
    return data
  },

  testProxyConfig: async (config: {
    enabled: boolean
    http_proxy: string
    https_proxy: string
    socks5_proxy: string
  }): Promise<any> => {
    const { data } = await client.post('/api/config/proxy/test', config)
    return data
  },

  deleteProxyConfig: async (): Promise<any> => {
    const { data } = await client.delete('/api/config/proxy')
    return data
  },

  // 导出相关
  exportAnalysisPDF: async (analysisId: string): Promise<Blob> => {
    const { data } = await client.get(`/api/export/analysis/${analysisId}/pdf`, {
      responseType: 'blob',
    })
    return data
  },

  // 趋势洞察相关
  createTrendInsight: async (params: {
    analysis_ids: string[]
    llm_backend: string
    llm_model?: string
  }): Promise<any> => {
    const { data } = await client.post('/api/trend-insight', params)
    return data
  },

  getTrendInsights: async (industry?: string): Promise<any[]> => {
    const { data } = await client.get('/api/trend-insights', { 
      params: industry ? { industry } : undefined 
    })
    return data
  },

  getTrendInsight: async (id: string): Promise<any> => {
    const { data } = await client.get(`/api/trend-insights/${id}`)
    return data
  },
}
