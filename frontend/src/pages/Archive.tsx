import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Folder, FileText, Zap, Calendar } from 'lucide-react'
import { api } from '@/services/api'

export default function ArchivePage() {
  const navigate = useNavigate()
  const [selectedIndustry, setSelectedIndustry] = useState<string>('all')
  const [llmBackend, setLlmBackend] = useState('gemini')
  const [llmModel, setLlmModel] = useState('gemini-2.5-flash')

  // 获取已归档的文章
  const { data: archivedArticles, isLoading } = useQuery({
    queryKey: ['archived-articles', selectedIndustry],
    queryFn: () =>
      api.getArticles({
        archived: true,
        industry: selectedIndustry === 'all' ? undefined : selectedIndustry,
        limit: 200,
      }),
  })

  const { data: backends } = useQuery({
    queryKey: ['llm-backends'],
    queryFn: () => api.getLLMBackends(),
  })

  const analyzeMutation = useMutation({
    mutationFn: ({ articleIds, backend, model }: { articleIds: string[]; backend: string; model?: string }) =>
      api.analyze({
        article_ids: articleIds,
        analysis_type: 'comprehensive',
        llm_backend: backend,
        llm_model: model,
        custom_prompt: `请对以下已归档的文章进行深度情报分析。这些文章来自${selectedIndustry === 'all' ? '多个行业' : `${selectedIndustry}行业`}，请：

1. 识别核心趋势和模式
2. 提取关键信号和重要事件
3. 分析信息差和潜在机会
4. 提供可执行的洞察建议

重点关注：
- 时间线上的变化和演进
- 不同信息源之间的关联
- 隐藏的市场信号或技术趋势
- 对未来的预测和建议

请生成一份专业、完整的行业情报分析报告。`,
      }),
    onSuccess: (data) => {
      if (data.analysis && data.analysis.id) {
        navigate(`/analysis/${data.analysis.id}`)
      }
    },
    onError: (error: any) => {
      alert(`分析失败：${error.response?.data?.detail || error.message}`)
    },
  })

  const handleAnalyzeCategory = () => {
    const articleIds = archivedArticles?.articles.map((a: any) => a.id).filter(Boolean) || []
    
    if (articleIds.length === 0) {
      alert('该分类下没有归档文章')
      return
    }

    if (articleIds.length > 50) {
      if (!confirm(`该分类有 ${articleIds.length} 篇文章，分析可能需要较长时间和更多费用。是否继续？`)) {
        return
      }
    }

    analyzeMutation.mutate({ articleIds, backend: llmBackend, model: llmModel })
  }

  // 按行业分组统计
  const stats = archivedArticles?.articles.reduce((acc: any, article: any) => {
    const industry = article.industry || 'other'
    if (!acc[industry]) {
      acc[industry] = { count: 0, latest: article.published_at }
    }
    acc[industry].count++
    if (new Date(article.published_at) > new Date(acc[industry].latest)) {
      acc[industry].latest = article.published_at
    }
    return acc
  }, {}) || {}

  const selectedBackend = backends?.backends?.find((b: any) => b.id === llmBackend)
  const availableModels = selectedBackend?.models || []

  const industryNames: Record<string, string> = {
    ai: 'AI / 人工智能',
    tech: '科技',
    finance: '金融',
    healthcare: '医疗',
    energy: '能源',
    education: '教育',
    other: '其他',
  }

  if (isLoading) {
    return <div className="p-8 text-center">加载中...</div>
  }

  const currentArticles = archivedArticles?.articles || []
  const totalCount = archivedArticles?.total || 0

  return (
    <div className="p-4 md:p-8">
      <div className="mb-6 md:mb-8">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2 md:mb-4">归档管理</h1>
        <p className="text-sm md:text-base text-gray-600">
          已归档 {totalCount} 篇文章,按行业分类管理和分析
        </p>
      </div>

      {/* 分析工具栏 */}
      <div className="mb-6 bg-white rounded-lg border border-gray-200 p-4 md:p-6">
        <h2 className="text-base md:text-lg font-semibold text-gray-900 mb-4">📊 归档分析</h2>
        
        <div className="flex flex-col gap-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">选择分类</label>
              <select
                value={selectedIndustry}
                onChange={(e) => setSelectedIndustry(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">全部分类 ({totalCount})</option>
                {Object.entries(stats).map(([industry, stat]: [string, any]) => (
                  <option key={industry} value={industry}>
                    {industryNames[industry] || industry} ({stat.count})
                  </option>
                ))}
              </select>
            </div>

            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">LLM后端</label>
              <select
                value={llmBackend}
                onChange={(e) => {
                  setLlmBackend(e.target.value)
                  const backend = backends?.backends?.find((b: any) => b.id === e.target.value)
                  if (backend?.models?.[0]) {
                    setLlmModel(backend.models[0].id)
                  }
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                {backends?.backends?.map((backend: any) => (
                  <option key={backend.id} value={backend.id}>
                    {backend.name}
                  </option>
                ))}
              </select>
            </div>

            {availableModels.length > 0 && (
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">模型</label>
                <select
                  value={llmModel}
                  onChange={(e) => setLlmModel(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  {availableModels.map((model: any) => (
                    <option key={model.id} value={model.id}>
                      {model.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <button
            onClick={handleAnalyzeCategory}
            disabled={currentArticles.length === 0 || analyzeMutation.isPending}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Zap size={18} />
            {analyzeMutation.isPending ? '分析中...' : '分析当前分类'}
          </button>
        </div>

        {currentArticles.length > 0 && (
          <div className="mt-4 text-sm text-gray-600">
            💡 将对当前分类的 {currentArticles.length} 篇归档文章进行深度情报分析
          </div>
        )}
      </div>

      {/* 分类统计卡片 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6 md:mb-8">
        {Object.entries(stats).map(([industry, stat]: [string, any]) => (
          <div
            key={industry}
            onClick={() => setSelectedIndustry(industry)}
            className={`cursor-pointer bg-white rounded-lg border p-4 md:p-6 transition-all hover:shadow-md ${
              selectedIndustry === industry
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200'
            }`}
          >
            <div className="flex items-center gap-3 mb-3">
              <Folder className="text-blue-600 flex-shrink-0" size={24} />
              <h3 className="text-base md:text-lg font-semibold text-gray-900">
                {industryNames[industry] || industry}
              </h3>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2 text-gray-600">
                <FileText size={16} />
                <span>{stat.count} 篇文章</span>
              </div>
              <div className="flex items-center gap-2 text-gray-600">
                <Calendar size={16} />
                <span className="truncate">最新：{new Date(stat.latest).toLocaleDateString('zh-CN')}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 当前分类文章列表 */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 md:p-6">
        <h2 className="text-base md:text-lg font-semibold text-gray-900 mb-4">
          {selectedIndustry === 'all' ? '全部文章' : `${industryNames[selectedIndustry]} - 文章列表`}
          <span className="ml-2 text-sm text-gray-600">({currentArticles.length} 篇)</span>
        </h2>

        {currentArticles.length === 0 ? (
          <div className="text-center py-12 text-gray-500 text-sm md:text-base">
            该分类下还没有归档文章
          </div>
        ) : (
          <div className="space-y-3">
            {currentArticles.slice(0, 20).map((article: any) => (
              <div
                key={article.id}
                className="border-l-4 border-blue-500 pl-3 md:pl-4 py-2 hover:bg-gray-50 transition-colors"
              >
                <h4 className="font-medium text-gray-900 mb-1 text-sm md:text-base">{article.title}</h4>
                <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3 text-xs md:text-sm text-gray-600">
                  <span className="truncate">{article.source_name}</span>
                  <span className="hidden sm:inline">·</span>
                  <span>{new Date(article.published_at).toLocaleDateString('zh-CN')}</span>
                </div>
              </div>
            ))}
            {currentArticles.length > 20 && (
              <div className="text-center text-sm text-gray-500 pt-4">
                还有 {currentArticles.length - 20} 篇文章未显示
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
