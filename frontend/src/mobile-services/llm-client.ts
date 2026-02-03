// 移动端 LLM API 客户端
import { Http, HttpResponse } from '@capacitor-community/http';
import { Preferences } from '@capacitor/preferences';
import type { Article, Analysis, AnalysisRequest, LLMBackend } from './types';

export class MobileLLMClient {
  private apiKeys: Map<string, string> = new Map();

  async initialize(): Promise<void> {
    // 从本地存储加载 API Keys
    await this.loadAPIKeys();
  }

  /**
   * 分析文章生成情报报告
   */
  async analyze(request: AnalysisRequest, articles: Article[]): Promise<Analysis> {
    const backend = request.llm_backend || 'gemini';
    const model = request.llm_model || this.getDefaultModel(backend);
    
    const apiKey = await this.getAPIKey(backend);
    if (!apiKey) {
      throw new Error(`API Key not configured for ${backend}`);
    }

    console.log(`Analyzing ${articles.length} articles with ${backend}/${model}...`);

    let analysisContent: string;

    switch (backend) {
      case 'gemini':
        analysisContent = await this.analyzeWithGemini(articles, model, apiKey, request.custom_prompt);
        break;
      case 'deepseek':
        analysisContent = await this.analyzeWithDeepSeek(articles, model, apiKey, request.custom_prompt);
        break;
      case 'openai':
        analysisContent = await this.analyzeWithOpenAI(articles, model, apiKey, request.custom_prompt);
        break;
      default:
        throw new Error(`Unsupported LLM backend: ${backend}`);
    }

    return {
      id: this.generateId(),
      executive_brief: this.extractBrief(analysisContent),
      markdown_report: analysisContent,
      article_ids: articles.map(a => a.id!),
      created_at: new Date().toISOString(),
      analysis_type: request.analysis_type,
      llm_model: model,
      llm_backend: backend
    };
  }

  /**
   * Gemini API 调用
   */
  private async analyzeWithGemini(
    articles: Article[], 
    model: string, 
    apiKey: string,
    customPrompt?: string
  ): Promise<string> {
    const prompt = this.buildPrompt(articles, customPrompt);
    
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
    
    const response: HttpResponse = await Http.post({
      url,
      headers: {
        'Content-Type': 'application/json'
      },
      data: {
        contents: [{
          parts: [{ text: prompt }]
        }],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 8000,
          topP: 0.95,
          topK: 40
        }
      }
    });

    if (response.status !== 200) {
      throw new Error(`Gemini API error: ${response.status}`);
    }

    const data = response.data;
    if (!data.candidates || data.candidates.length === 0) {
      throw new Error('No response from Gemini');
    }

    return data.candidates[0].content.parts[0].text;
  }

  /**
   * DeepSeek API 调用
   */
  private async analyzeWithDeepSeek(
    articles: Article[], 
    model: string, 
    apiKey: string,
    customPrompt?: string
  ): Promise<string> {
    const prompt = this.buildPrompt(articles, customPrompt);
    
    const response: HttpResponse = await Http.post({
      url: 'https://api.deepseek.com/v1/chat/completions',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      data: {
        model: model,
        messages: [
          {
            role: 'system',
            content: '你是一个专业的信息分析师，擅长从海量信息中识别关键信号。'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 8000
      }
    });

    if (response.status !== 200) {
      throw new Error(`DeepSeek API error: ${response.status}`);
    }

    return response.data.choices[0].message.content;
  }

  /**
   * OpenAI API 调用
   */
  private async analyzeWithOpenAI(
    articles: Article[], 
    model: string, 
    apiKey: string,
    customPrompt?: string
  ): Promise<string> {
    const prompt = this.buildPrompt(articles, customPrompt);
    
    const response: HttpResponse = await Http.post({
      url: 'https://api.openai.com/v1/chat/completions',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      data: {
        model: model,
        messages: [
          {
            role: 'system',
            content: '你是一个专业的信息分析师，擅长从海量信息中识别关键信号。'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 8000
      }
    });

    if (response.status !== 200) {
      throw new Error(`OpenAI API error: ${response.status}`);
    }

    return response.data.choices[0].message.content;
  }

  /**
   * 构建分析 Prompt
   */
  private buildPrompt(articles: Article[], customPrompt?: string): string {
    const articlesText = articles
      .slice(0, 50) // 限制文章数量
      .map((article, index) => {
        const preview = article.content.substring(0, 500);
        return `
[${index + 1}] ${article.title}
来源: ${article.source_name}
时间: ${new Date(article.published_at).toLocaleString('zh-CN')}
内容: ${preview}...
URL: ${article.url}
`;
      })
      .join('\n---\n');

    const basePrompt = customPrompt || this.getDefaultPrompt();

    return `${basePrompt}

# 文章列表 (共 ${articles.length} 篇)

${articlesText}

请基于以上文章生成情报分析报告。`;
  }

  /**
   * 默认分析 Prompt
   */
  private getDefaultPrompt(): string {
    return `你是一个专业的信息分析师。请分析以下文章，生成一份精炼的情报报告。

## 报告要求

1. **执行摘要** (3-5个核心要点)
   - 用一句话概括最重要的信号
   - 只保留真正改变判断的信息

2. **今日主线叙事** (2-3条主线)
   - 识别核心趋势和模式
   - 每条主线包含：标题、证据链、影响分析

3. **关键信号清单**
   - 高置信度信号 (3-5个)
   - 中置信度信号 (2-3个)
   - 低置信度信号 (1-2个)
   - 每个信号注明证据来源

4. **被过滤内容** (简述)
   - 说明哪些信息被排除，为什么不重要

5. **行动提示**
   - 风险规避 (1-2点)
   - 机会布局 (1-2点)
   - 跟踪建议 (1-2点)

## 分析原则

- **信号优先**: 只关注真正改变格局的少数信号
- **证据支撑**: 每个结论都要有明确的证据来源
- **可操作性**: 提供具体、可执行的建议
- **客观中立**: 避免情绪化表述

请用中文、Markdown 格式输出报告。`;
  }

  /**
   * 提取简要摘要
   */
  private extractBrief(content: string): string {
    const lines = content.split('\n').filter(line => line.trim());
    
    // 尝试提取执行摘要部分
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes('执行摘要') || lines[i].includes('核心要点')) {
        const summaryLines = lines.slice(i + 1, i + 4);
        return summaryLines.join(' ').replace(/[#*-]/g, '').trim();
      }
    }

    // 如果没找到，返回前3行
    return lines.slice(0, 3).join(' ').substring(0, 200);
  }

  /**
   * API Key 管理
   */
  async getAPIKey(backend: string): Promise<string | null> {
    // 先从内存缓存获取
    if (this.apiKeys.has(backend)) {
      return this.apiKeys.get(backend) || null;
    }

    // 从本地存储获取
    const { value } = await Preferences.get({ key: `${backend}_api_key` });
    if (value) {
      this.apiKeys.set(backend, value);
    }
    return value;
  }

  async setAPIKey(backend: string, apiKey: string): Promise<void> {
    await Preferences.set({
      key: `${backend}_api_key`,
      value: apiKey
    });
    this.apiKeys.set(backend, apiKey);
  }

  async deleteAPIKey(backend: string): Promise<void> {
    await Preferences.remove({ key: `${backend}_api_key` });
    this.apiKeys.delete(backend);
  }

  private async loadAPIKeys(): Promise<void> {
    const backends = ['gemini', 'deepseek', 'openai'];
    for (const backend of backends) {
      await this.getAPIKey(backend);
    }
  }

  /**
   * 获取支持的 LLM 后端列表
   */
  getLLMBackends(): LLMBackend[] {
    return [
      {
        id: 'gemini',
        name: 'Google Gemini',
        description: '免费额度大，速度快',
        requires_api_key: true,
        cost: 0,
        models: [
          { id: 'gemini-2.0-flash-exp', name: 'Gemini 2.0 Flash (推荐)' },
          { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro' },
          { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash' }
        ]
      },
      {
        id: 'deepseek',
        name: 'DeepSeek',
        description: '性价比高，中文友好',
        requires_api_key: true,
        cost: 0.14,
        models: [
          { id: 'deepseek-chat', name: 'DeepSeek Chat' },
          { id: 'deepseek-coder', name: 'DeepSeek Coder' }
        ]
      },
      {
        id: 'openai',
        name: 'OpenAI',
        description: '质量最佳，成本较高',
        requires_api_key: true,
        cost: 0.15,
        models: [
          { id: 'gpt-4o', name: 'GPT-4o' },
          { id: 'gpt-4o-mini', name: 'GPT-4o Mini' },
          { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' }
        ]
      }
    ];
  }

  /**
   * 获取默认模型
   */
  private getDefaultModel(backend: string): string {
    const backends = this.getLLMBackends();
    const backendConfig = backends.find(b => b.id === backend);
    return backendConfig?.models[0]?.id || 'gemini-2.0-flash-exp';
  }

  /**
   * 生成唯一 ID
   */
  private generateId(): string {
    return `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
