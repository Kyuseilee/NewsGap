/**
 * API 客户端
 */

import axios from 'axios'
import type {
  Article,
  Source,
  FetchRequest,
  FetchResponse,
  AnalyzeRequest,
  AnalyzeResponse,
  IntelligenceRequest,
  IntelligenceResponse,
  Analysis,
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
  fetch: async (request: FetchRequest): Promise<FetchResponse> => {
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

  exportArticles: async (articleIds: string[], outputDir?: string): Promise<any> => {
    const { data } = await client.post('/api/articles/export', {
      article_ids: articleIds,
      output_dir: outputDir,
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

  // 分析结果相关（需要在后端添加对应路由）
  getAnalysis: async (id: string): Promise<Analysis> => {
    // 这个路由后端还没实现，需要添加
    const { data } = await client.get(`/api/analyses/${id}`)
    return data
  },
}
