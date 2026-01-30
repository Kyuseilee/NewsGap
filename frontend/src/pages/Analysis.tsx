import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Clock, DollarSign, Zap, Info, ArrowLeft, Copy, Check } from 'lucide-react'
import { api } from '@/services/api'
import AnalysisMarkdown from '@/components/AnalysisMarkdown'
import type { Article } from '@/types/api'

export default function AnalysisPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [copied, setCopied] = useState(false)

  const { data: analysis, isLoading, error } = useQuery({
    queryKey: ['analysis', id],
    queryFn: () => id ? api.getAnalysis(id) : Promise.reject('No ID'),
    enabled: !!id,
  })

  // 获取分析涉及的文章
  const { data: articlesData } = useQuery({
    queryKey: ['analysis-articles', analysis?.article_ids],
    queryFn: async (): Promise<Article[]> => {
      if (!analysis?.article_ids || analysis.article_ids.length === 0) {
        return []
      }
      // 批量获取文章
      const articles = await Promise.all(
        analysis.article_ids.map(id => 
          api.getArticle(id).catch(() => null)  // 如果某个文章获取失败，返回null
        )
      )
      return articles.filter((a): a is Article => a !== null)  // 类型守卫过滤null
    },
    enabled: !!analysis?.article_ids && analysis.article_ids.length > 0,
  })

  const handleCopy = () => {
    if (analysis?.markdown_report) {
      navigator.clipboard.writeText(analysis.markdown_report)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">加载分析结果中...</p>
        </div>
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <div className="text-red-600 text-5xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">分析结果未找到</h1>
            <p className="text-gray-600 mb-6">
              {error ? String(error) : '无法加载分析结果'}
            </p>
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              返回首页
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* 顶部工具栏 */}
        <div className="mb-6 flex items-center justify-between bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft size={20} />
            返回首页
          </button>

          <div className="flex items-center gap-6 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <Zap size={16} className="text-blue-600" />
              <span>{analysis.llm_backend.toUpperCase()}</span>
              {analysis.llm_model && (
                <>
                  <span className="text-gray-400">·</span>
                  <span className="text-gray-500">{analysis.llm_model}</span>
                </>
              )}
            </div>
            {analysis.processing_time_seconds && (
              <div className="flex items-center gap-2">
                <Clock size={16} className="text-green-600" />
                <span>{analysis.processing_time_seconds.toFixed(1)}s</span>
              </div>
            )}
            {analysis.estimated_cost !== undefined && (
              <div className="flex items-center gap-2">
                <DollarSign size={16} className="text-yellow-600" />
                <span>${analysis.estimated_cost.toFixed(4)}</span>
              </div>
            )}
            {analysis.token_usage && (
              <div className="flex items-center gap-2">
                <Info size={16} className="text-purple-600" />
                <span>{analysis.token_usage.toLocaleString()} tokens</span>
              </div>
            )}
          </div>

          <button
            onClick={handleCopy}
            disabled={!analysis.markdown_report}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {copied ? (
              <>
                <Check size={18} />
                已复制
              </>
            ) : (
              <>
                <Copy size={18} />
                复制报告
              </>
            )}
          </button>
        </div>

        {/* 报告内容 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 md:p-12">
          {analysis.markdown_report ? (
            <AnalysisMarkdown 
              content={analysis.markdown_report}
              articles={articlesData || []}
            />
          ) : (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">📊 执行摘要</h2>
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {analysis.executive_brief}
                </p>
              </div>

              <div className="mt-8 p-6 bg-yellow-50 border border-yellow-200 rounded-lg text-center">
                <p className="text-yellow-800">完整的 Markdown 报告生成中...</p>
                <p className="text-sm text-yellow-700 mt-2">
                  该分析可能使用了旧版本，请重新生成分析获取完整报告
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
