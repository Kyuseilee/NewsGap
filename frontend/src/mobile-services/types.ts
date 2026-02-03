// 移动端服务层类型定义

export interface Article {
  id?: string;
  title: string;
  url: string;
  content: string;
  published_at: string;
  source_name: string;
  industry: string;
  archived?: boolean;
  tags?: string[];
  created_at?: string;
}

export interface ArticleFilters {
  industry?: string;
  archived?: boolean;
  limit?: number;
  offset?: number;
}

export interface Analysis {
  id?: string;
  executive_brief: string;
  markdown_report: string;
  article_ids: string[];
  created_at: string;
  analysis_type: string;
  llm_model: string;
  llm_backend?: string;
}

export interface RSSSource {
  id?: string;
  name: string;
  url: string;
  industry: string;
  enabled: boolean;
  description?: string;
}

export interface CustomCategory {
  id?: string;
  name: string;
  description?: string;
  custom_prompt: string;
  enabled: boolean;
  sources: RSSSource[];
}

export interface LLMBackend {
  id: string;
  name: string;
  description: string;
  requires_api_key: boolean;
  cost: number;
  models: LLMModel[];
}

export interface LLMModel {
  id: string;
  name: string;
}

export interface APIKey {
  backend: string;
  has_key: boolean;
  masked_key?: string;
}

export interface AnalysisRequest {
  articles?: Article[];
  article_ids?: string[];
  analysis_type: string;
  llm_backend: string;
  llm_model?: string;
  custom_prompt?: string;
}

export interface IntelligenceRequest {
  industry?: string;
  custom_category_id?: string;
  hours: number;
  llm_backend: string;
  llm_model?: string;
}

export interface IntelligenceResponse {
  analysis: Analysis;
  article_count: number;
  analysis_id: string;
  total_time_seconds: number;
}

export interface ProxyConfig {
  enabled: boolean;
  protocol: string;
  host: string;
  port: number;
}
