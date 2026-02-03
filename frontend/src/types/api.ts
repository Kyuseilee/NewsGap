/**
 * API 类型定义
 */

export interface Article {
  id: string
  title: string
  url: string
  source_id?: string
  source_name?: string
  content: string
  summary?: string
  industry: string
  tags: string[]
  published_at: string
  fetched_at: string
  author?: string
  language: string
  word_count?: number
  archived: boolean
  archived_at?: string
  metadata?: Record<string, any>
}

export interface Source {
  id?: string
  name: string
  url: string
  source_type: 'rss' | 'web' | 'api'
  priority?: string
  industry: string
  enabled: boolean
  fetch_interval_hours: number
  last_fetched_at?: string
  last_error?: string
  error_count?: number
  created_at?: string
  metadata?: Record<string, any>
}

export interface Trend {
  title: string
  description: string
  confidence: number
  supporting_article_ids: string[]
  keywords: string[]
}

export interface Signal {
  title: string
  description: string
  importance: number
  source_article_ids: string[]
  category?: string
}

export interface InformationGap {
  title: string
  description: string
  gap_type: string
  related_article_ids: string[]
  actionable_insight?: string
}

export interface Analysis {
  id?: string
  analysis_type: string
  article_ids: string[]
  executive_brief: string
  markdown_report?: string
  trends: Trend[]
  signals: Signal[]
  information_gaps: InformationGap[]
  llm_backend: string
  llm_model?: string
  token_usage?: number
  estimated_cost?: number
  created_at?: string
  processing_time_seconds?: number
  user_rating?: number
  user_notes?: string
}

export interface FetchRequest {
  industry: string
  hours: number
  source_ids?: string[]
}

export interface FetchResponse {
  article_ids: string[]
  count: number
  sources_used: string[]
  fetch_time_seconds: number
}

export interface AnalyzeRequest {
  article_ids: string[]
  analysis_type: string
  llm_backend: string
  llm_model?: string
  custom_prompt?: string
}

export interface AnalyzeResponse {
  analysis_id: string
  analysis: Analysis
}

export interface IntelligenceRequest {
  industry?: string
  custom_category_id?: string
  hours: number
  llm_backend: string
  llm_model?: string
  source_ids?: string[]
}

export interface IntelligenceResponse {
  article_ids: string[]
  article_count: number
  analysis_id: string
  analysis: Analysis
  total_time_seconds: number
}

export interface CustomCategory {
  id?: string
  name: string
  description?: string
  custom_prompt: string
  source_ids: string[]
  enabled: boolean
  created_at?: string
  updated_at?: string
  metadata?: Record<string, any>
}

export interface CreateCustomCategoryRequest {
  name: string
  description?: string
  custom_prompt: string
  source_ids?: string[]
}

export interface UpdateCustomCategoryRequest {
  name?: string
  description?: string
  custom_prompt?: string
  source_ids?: string[]
  enabled?: boolean
}
