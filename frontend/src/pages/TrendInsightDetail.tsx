import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { 
  Clock, DollarSign, Zap, Info, ArrowLeft, Copy, Check, 
  Calendar, FileText, LineChart 
} from 'lucide-react'
import { api } from '@/services/api'
import AnalysisMarkdown from '@/components/AnalysisMarkdown'

// 行业分类中文映射
const INDUSTRY_LABELS: Record<string, string> = {
  daily_info_gap: '综合信息差',
  socialmedia: '社交媒体',
  news: '新闻资讯',
  tech: '科技互联网',
  developer: '开发者',
  finance: '财经金融',
  entertainment: '娱乐影视',
  gaming: '游戏电竞',
  anime: '动漫二次元',
  shopping: '电商购物',
  education: '学习教育',
  lifestyle: '生活方式',
  custom: '自定义',
  other: '其他'
}

export default function TrendInsightDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [copied, setCopied] = useState(false)

  const { data: insight, isLoading, error } = useQuery({
    queryKey: ['trend-insight', id],
    queryFn: () => id ? api.getTrendInsight(id) : Promise.reject('No ID'),
    enabled: !!id,
  })

  const handleCopy = () => {
    if (insight?.markdown_report) {
      navigator.clipboard.writeText(insight.markdown_report)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">加载趋势洞察中...</p>
        </div>
      </div>
    )
  }

  if (error || !insight) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <div className="text-red-600 text-5xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">趋势洞察未找到</h1>
            <p className="text-gray-600 mb-6">
              {error ? String(error) : '无法加载趋势洞察'}
            </p>
            <button
              onClick={() => navigate('/trend-insight')}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              返回趋势洞察
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
            onClick={() => navigate('/trend-insight/history')}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft size={20} />
            返回列表
          </button>

          <div className="flex items-center gap-6 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <LineChart size={16} className="text-purple-600" />
              <span className="font-medium text-purple-700">
                {INDUSTRY_LABELS[insight.industry] || '未分类'} 趋势洞察
              </span>
            </div>
            {insight.date_range_start && insight.date_range_end && (
              <div className="flex items-center gap-2">
                <Calendar size={16} className="text-blue-600" />
                <span>
                  {new Date(insight.date_range_start).toLocaleDateString('zh-CN')} - 
                  {new Date(insight.date_range_end).toLocaleDateString('zh-CN')}
                </span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <FileText size={16} className="text-gray-600" />
              <span>{insight.source_analysis_ids?.length || 0} 份报告</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap size={16} className="text-blue-600" />
              <span>{insight.llm_backend?.toUpperCase()}</span>
              {insight.llm_model && (
                <>
                  <span className="text-gray-400">·</span>
                  <span className="text-gray-500">{insight.llm_model}</span>
                </>
              )}
            </div>
            {insight.processing_time_seconds && (
              <div className="flex items-center gap-2">
                <Clock size={16} className="text-green-600" />
                <span>{insight.processing_time_seconds.toFixed(1)}s</span>
              </div>
            )}
            {insight.estimated_cost !== undefined && insight.estimated_cost !== null && (
              <div className="flex items-center gap-2">
                <DollarSign size={16} className="text-yellow-600" />
                <span>${insight.estimated_cost.toFixed(4)}</span>
              </div>
            )}
            {insight.token_usage && (
              <div className="flex items-center gap-2">
                <Info size={16} className="text-purple-600" />
                <span>{insight.token_usage.toLocaleString()} tokens</span>
              </div>
            )}
          </div>

          <button
            onClick={handleCopy}
            disabled={!insight.markdown_report}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
          {insight.markdown_report ? (
            <AnalysisMarkdown 
              content={insight.markdown_report}
              articles={[]}  // 趋势洞察不需要文章引用
            />
          ) : (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">📊 执行摘要</h2>
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {insight.executive_summary}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
