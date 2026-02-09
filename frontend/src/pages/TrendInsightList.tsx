import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { LineChart, Clock, Filter, FileText, Sparkles, ArrowLeft, Calendar } from 'lucide-react'
import { api } from '@/services/api'

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

export default function TrendInsightList() {
  const navigate = useNavigate()
  const [selectedIndustry, setSelectedIndustry] = useState<string>('all')

  const { data: insights, isLoading } = useQuery({
    queryKey: ['trend-insights', selectedIndustry],
    queryFn: () => api.getTrendInsights(selectedIndustry !== 'all' ? selectedIndustry : undefined),
  })

  // 获取所有出现过的行业
  const availableIndustries = useMemo(() => {
    if (!insights) return []
    const industries = new Set(insights.map((i: any) => i.industry).filter(Boolean))
    return Array.from(industries).sort()
  }, [insights])

  if (isLoading) {
    return <div className="p-8 text-center">加载中...</div>
  }

  return (
    <div className="p-8">
      {/* 标题区域 */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <LineChart size={32} className="text-purple-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">趋势洞察历史</h1>
              <p className="text-gray-600">查看所有趋势洞察报告（共 {insights?.length || 0} 条）</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/trend-insight')}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            <ArrowLeft size={18} />
            新建洞察
          </button>
        </div>

        {/* 筛选栏 */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-4">
            <Filter className="text-gray-400" size={20} />
            <select
              value={selectedIndustry}
              onChange={(e) => setSelectedIndustry(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            >
              <option value="all">全部分类</option>
              {availableIndustries.map((industry: string) => (
                <option key={industry} value={industry}>
                  {INDUSTRY_LABELS[industry] || industry}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 列表 */}
      {(!insights || insights.length === 0) ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <LineChart className="mx-auto mb-4 text-gray-400" size={48} />
          <p className="text-gray-600 mb-2">还没有趋势洞察报告</p>
          <p className="text-sm text-gray-500 mb-4">
            选择多个分析报告来生成趋势洞察
          </p>
          <button
            onClick={() => navigate('/trend-insight')}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            创建趋势洞察
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {insights.map((insight: any) => (
            <div
              key={insight.id}
              onClick={() => navigate(`/trend-insight/${insight.id}`)}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:border-purple-500 hover:shadow-md cursor-pointer transition-all"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {INDUSTRY_LABELS[insight.industry] || '未分类'} 趋势洞察
                  </h3>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span className="flex items-center gap-1">
                      <Clock size={16} />
                      {new Date(insight.created_at).toLocaleString('zh-CN')}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar size={16} />
                      {insight.date_range_start && insight.date_range_end ? (
                        `${new Date(insight.date_range_start).toLocaleDateString('zh-CN')} - ${new Date(insight.date_range_end).toLocaleDateString('zh-CN')}`
                      ) : '未知时间范围'}
                    </span>
                    <span className="flex items-center gap-1">
                      <FileText size={16} />
                      {insight.source_analysis_ids?.length || 0} 份报告
                    </span>
                    <span className="flex items-center gap-1">
                      <Sparkles size={16} />
                      {insight.llm_model || insight.llm_backend}
                    </span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded text-sm">
                    {INDUSTRY_LABELS[insight.industry] || '未分类'}
                  </span>
                </div>
              </div>

              {insight.executive_summary && (
                <div className="text-sm text-gray-700 line-clamp-2 bg-gray-50 p-3 rounded">
                  {insight.executive_summary.substring(0, 200)}...
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
