import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Clock, TrendingUp, FileText, Sparkles } from 'lucide-react'
import { api } from '@/services/api'

export default function AnalysisList() {
  const navigate = useNavigate()

  const { data: analyses, isLoading } = useQuery({
    queryKey: ['analyses-list'],
    queryFn: async () => {
      const data = await api.getAnalysesList()
      return data
    },
  })

  if (isLoading) {
    return <div className="p-8 text-center">加载中...</div>
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">分析历史</h1>
        <p className="text-gray-600">查看所有情报分析报告</p>
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
      ) : (
        <div className="space-y-4">
          {analyses.map((analysis: any) => (
            <div
              key={analysis.id}
              onClick={() => navigate(`/analysis/${analysis.id}`)}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:border-blue-500 hover:shadow-md cursor-pointer transition-all"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {analysis.executive_brief ? analysis.executive_brief.substring(0, 80) + '...' : '情报分析报告'}
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
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                  {analysis.analysis_type}
                </span>
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
