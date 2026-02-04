import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Clock, TrendingUp, FileText, Sparkles, Search, Filter } from 'lucide-react'
import { api } from '@/services/api'

// 行业分类中文映射
const INDUSTRY_LABELS: Record<string, string> = {
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

export default function AnalysisList() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedIndustry, setSelectedIndustry] = useState<string>('all')

  const { data: analyses, isLoading } = useQuery({
    queryKey: ['analyses-list'],
    queryFn: async () => {
      const data = await api.getAnalysesList()
      return data
    },
  })

  // 筛选和搜索
  const filteredAnalyses = useMemo(() => {
    if (!analyses) return []
    
    let filtered = analyses
    
    // 按行业筛选
    if (selectedIndustry !== 'all') {
      filtered = filtered.filter((a: any) => a.industry === selectedIndustry)
    }
    
    // 按搜索关键词过滤
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter((a: any) => 
        a.executive_brief?.toLowerCase().includes(query) ||
        a.markdown_report?.toLowerCase().includes(query)
      )
    }
    
    return filtered
  }, [analyses, selectedIndustry, searchQuery])

  // 获取所有出现过的行业（用于筛选器）
  const availableIndustries = useMemo(() => {
    if (!analyses) return []
    const industries = new Set(analyses.map((a: any) => a.industry).filter(Boolean))
    return Array.from(industries).sort()
  }, [analyses])

  // 生成标题：日期-分类-摘要
  const generateTitle = (analysis: any) => {
    const date = new Date(analysis.created_at).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }).replace(/\//g, '-')
    const industry = INDUSTRY_LABELS[analysis.industry] || '未分类'
    const brief = analysis.executive_brief ? analysis.executive_brief.substring(0, 30) + '...' : '情报分析报告'
    return `${date} · ${industry} · ${brief}`
  }

  if (isLoading) {
    return <div className="p-8 text-center">加载中...</div>
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">分析历史</h1>
            <p className="text-gray-600">查看所有情报分析报告（共 {analyses?.length || 0} 条，筛选后 {filteredAnalyses.length} 条）</p>
          </div>
        </div>

        {/* 搜索和筛选栏 */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex flex-col md:flex-row gap-4">
            {/* 搜索框 */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="搜索分析内容..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* 行业筛选 */}
            <div className="flex items-center gap-2 min-w-[200px]">
              <Filter className="text-gray-400" size={20} />
              <select
                value={selectedIndustry}
                onChange={(e) => setSelectedIndustry(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
      </div>

      {(!analyses || analyses.length === 0) ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <TrendingUp className="mx-auto mb-4 text-gray-400" size={48} />
          <p className="text-gray-600 mb-2">还没有分析报告</p>
          <p className="text-sm text-gray-500">
            前往首页创建第一个情报分析
          </p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            开始分析
          </button>
        </div>
      ) : filteredAnalyses.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <Search className="mx-auto mb-4 text-gray-400" size={48} />
          <p className="text-gray-600 mb-2">没有找到匹配的分析报告</p>
          <p className="text-sm text-gray-500">尝试调整搜索条件或筛选器</p>
          <button
            onClick={() => {
              setSearchQuery('')
              setSelectedIndustry('all')
            }}
            className="mt-4 px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            清除筛选
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredAnalyses.map((analysis: any) => (
            <div
              key={analysis.id}
              onClick={() => navigate(`/analysis/${analysis.id}`)}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:border-blue-500 hover:shadow-md cursor-pointer transition-all"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {generateTitle(analysis)}
                  </h3>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span className="flex items-center gap-1">
                      <Clock size={16} />
                      {new Date(analysis.created_at).toLocaleString('zh-CN')}
                    </span>
                    <span className="flex items-center gap-1">
                      <FileText size={16} />
                      {analysis.article_ids?.length || 0} 篇文章
                    </span>
                    <span className="flex items-center gap-1">
                      <Sparkles size={16} />
                      {analysis.llm_model}
                    </span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <span className="px-3 py-1 bg-green-100 text-green-700 rounded text-sm">
                    {INDUSTRY_LABELS[analysis.industry] || '未分类'}
                  </span>
                  <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                    {analysis.analysis_type}
                  </span>
                </div>
              </div>

              {analysis.markdown_report && (
                <div className="text-sm text-gray-700 line-clamp-2 bg-gray-50 p-3 rounded">
                  {analysis.markdown_report.substring(0, 150)}...
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
