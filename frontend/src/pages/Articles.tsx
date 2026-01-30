import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Archive, Zap, ExternalLink, Check, Filter, RefreshCw } from 'lucide-react'
import { api } from '@/services/api'
import type { Article } from '@/types/api'

export default function ArticlesPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedArticles, setSelectedArticles] = useState<string[]>([])
  const [llmBackend, setLlmBackend] = useState('gemini')
  const [llmModel, setLlmModel] = useState('gemini-2.5-flash')
  
  // 筛选状态
  const [filterIndustry, setFilterIndustry] = useState<string>('all')
  const [filterArchived, setFilterArchived] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')

  const { data: articlesData, isLoading, refetch } = useQuery({
    queryKey: ['articles', 1000],  // 添加limit到缓存键
    queryFn: () => api.getArticles({ limit: 1000, archived: undefined }),  // 增加到1000
  })

  const { data: backends } = useQuery({
    queryKey: ['llm-backends'],
    queryFn: () => api.getLLMBackends(),
  })

  // 筛选后的文章
  const filteredArticles = useMemo(() => {
    if (!articlesData?.articles) return []
    
    let filtered = articlesData.articles
    
    // 按行业筛选
    if (filterIndustry !== 'all') {
      filtered = filtered.filter(a => a.industry === filterIndustry)
    }
    
    // 按归档状态筛选
    if (filterArchived === 'archived') {
      filtered = filtered.filter(a => a.archived)
    } else if (filterArchived === 'not-archived') {
      filtered = filtered.filter(a => !a.archived)
    }
    
    // 搜索筛选
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(a => 
        a.title.toLowerCase().includes(query) || 
        a.content.toLowerCase().includes(query) ||
        a.source_name?.toLowerCase().includes(query)
      )
    }
    
    // 按发布时间倒序排序
    return filtered.sort((a, b) => 
      new Date(b.published_at).getTime() - new Date(a.published_at).getTime()
    )
  }, [articlesData, filterIndustry, filterArchived, searchQuery])

  // 获取所有行业类别
  const industries = useMemo(() => {
    if (!articlesData?.articles) return []
    const uniqueIndustries = new Set(articlesData.articles.map(a => a.industry))
    return Array.from(uniqueIndustries).sort()
  }, [articlesData])

  // 统计信息
  const stats = useMemo(() => {
    const all = articlesData?.articles || []
    return {
      total: all.length,
      archived: all.filter(a => a.archived).length,
      notArchived: all.filter(a => !a.archived).length,
      filtered: filteredArticles.length
    }
  }, [articlesData, filteredArticles])

  const archiveMutation = useMutation({
    mutationFn: (articleIds: string[]) => api.exportArticles(articleIds),
    onSuccess: (data) => {
      alert(`成功归档 ${selectedArticles.length} 篇文章！\n路径：${data.output_path}`)
      setSelectedArticles([])
      queryClient.invalidateQueries({ queryKey: ['articles'] })
    },
    onError: (error: any) => {
      alert(`归档失败：${error.response?.data?.detail || error.message}`)
    },
  })

  const analyzeMutation = useMutation({
    mutationFn: ({ articleIds, backend, model }: { articleIds: string[]; backend: string; model?: string }) =>
      api.analyze({
        article_ids: articleIds,
        analysis_type: 'comprehensive',
        llm_backend: backend,
        llm_model: model,
      }),
    onSuccess: (data) => {
      if (data.analysis && data.analysis.id) {
        // 自动跳转到分析结果页面
        navigate(`/analysis/${data.analysis.id}`)
        // 清空选择
        setSelectedArticles([])
      } else {
        alert('分析完成，但无法获取结果ID')
      }
    },
    onError: (error: any) => {
      alert(`分析失败：${error.response?.data?.detail || error.message}`)
    },
  })

  const handleToggleArticle = (articleId: string) => {
    setSelectedArticles((prev) =>
      prev.includes(articleId)
        ? prev.filter((id) => id !== articleId)
        : [...prev, articleId]
    )
  }

  const handleToggleAll = () => {
    if (selectedArticles.length === filteredArticles.length) {
      setSelectedArticles([])
    } else {
      setSelectedArticles(filteredArticles.map((a: Article) => a.id!) || [])
    }
  }

  const handleArchive = () => {
    if (selectedArticles.length === 0) {
      alert('请先选择要归档的文章')
      return
    }
    if (confirm(`确定要归档 ${selectedArticles.length} 篇文章吗？`)) {
      archiveMutation.mutate(selectedArticles)
    }
  }

  const handleAnalyze = () => {
    if (selectedArticles.length === 0) {
      alert('请先选择要分析的文章')
      return
    }
    analyzeMutation.mutate({ articleIds: selectedArticles, backend: llmBackend, model: llmModel })
  }

  const selectedBackend = backends?.backends?.find((b: any) => b.id === llmBackend)
  const availableModels = selectedBackend?.models || []

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* 头部 */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-gray-900">文章列表</h1>
          <button
            onClick={() => refetch()}
            className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <RefreshCw size={16} />
            刷新
          </button>
        </div>
        
        {/* 统计卡片 */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-600 mb-1">总文章数</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-600 mb-1">未归档</div>
            <div className="text-2xl font-bold text-blue-600">{stats.notArchived}</div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-600 mb-1">已归档</div>
            <div className="text-2xl font-bold text-green-600">{stats.archived}</div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-600 mb-1">当前显示</div>
            <div className="text-2xl font-bold text-purple-600">{stats.filtered}</div>
          </div>
        </div>
        
        {selectedArticles.length > 0 && (
          <div className="mt-4 text-blue-600 font-medium">
            已选择 {selectedArticles.length} 篇文章
          </div>
        )}
      </div>

      {/* 筛选栏 */}
      <div className="mb-6 bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter size={18} className="text-gray-500" />
          <h3 className="font-semibold text-gray-900">筛选条件</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* 搜索 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              搜索
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索标题、内容或来源..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          {/* 行业筛选 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              行业分类
            </label>
            <select
              value={filterIndustry}
              onChange={(e) => setFilterIndustry(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">全部行业</option>
              {industries.map(industry => (
                <option key={industry} value={industry}>{industry}</option>
              ))}
            </select>
          </div>
          
          {/* 归档状态筛选 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              归档状态
            </label>
            <select
              value={filterArchived}
              onChange={(e) => setFilterArchived(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">全部</option>
              <option value="not-archived">未归档</option>
              <option value="archived">已归档</option>
            </select>
          </div>
        </div>
        
        {(filterIndustry !== 'all' || filterArchived !== 'all' || searchQuery) && (
          <button
            onClick={() => {
              setFilterIndustry('all')
              setFilterArchived('all')
              setSearchQuery('')
            }}
            className="mt-4 text-sm text-blue-600 hover:text-blue-700"
          >
            清除所有筛选
          </button>
        )}
      </div>

      {/* 批量操作工具栏 */}
      {filteredArticles.length > 0 && (
        <div className="mb-6 bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-4 flex-wrap">
            <button
              onClick={handleToggleAll}
              className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              {selectedArticles.length === filteredArticles.length ? '取消全选' : '全选当前页'}
            </button>

            <div className="flex-1 flex items-center gap-3">
              <select
                value={llmBackend}
                onChange={(e) => {
                  setLlmBackend(e.target.value)
                  const backend = backends?.backends?.find((b: any) => b.id === e.target.value)
                  if (backend?.models?.[0]) {
                    setLlmModel(backend.models[0].id)
                  }
                }}
                className="px-3 py-2 text-sm border border-gray-300 rounded-lg"
              >
                {backends?.backends?.map((backend: any) => (
                  <option key={backend.id} value={backend.id}>
                    {backend.name}
                  </option>
                ))}
              </select>

              {availableModels.length > 0 && (
                <select
                  value={llmModel}
                  onChange={(e) => setLlmModel(e.target.value)}
                  className="px-3 py-2 text-sm border border-gray-300 rounded-lg"
                >
                  {availableModels.map((model: any) => (
                    <option key={model.id} value={model.id}>
                      {model.name}
                    </option>
                  ))}
                </select>
              )}
            </div>

            <button
              onClick={handleAnalyze}
              disabled={selectedArticles.length === 0 || analyzeMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {analyzeMutation.isPending ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  正在分析 {selectedArticles.length} 篇文章...
                </>
              ) : (
                <>
                  <Zap size={18} />
                  分析选中文章 ({selectedArticles.length})
                </>
              )}
            </button>

            <button
              onClick={handleArchive}
              disabled={selectedArticles.length === 0 || archiveMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Archive size={18} />
              {archiveMutation.isPending ? '归档中...' : '归档选中文章'}
            </button>
          </div>
        </div>
      )}

      {/* 文章列表 */}
      <div className="space-y-4">
        {filteredArticles.length === 0 ? (
          <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
            {articlesData?.articles.length === 0 ? (
              <>
                <p className="text-gray-600">还没有文章</p>
                <p className="text-sm text-gray-500 mt-2">
                  前往首页爬取文章
                </p>
              </>
            ) : (
              <>
                <p className="text-gray-600">没有符合条件的文章</p>
                <p className="text-sm text-gray-500 mt-2">
                  尝试调整筛选条件
                </p>
              </>
            )}
          </div>
        ) : (
          filteredArticles.map((article: Article) => (
            <div
              key={article.id}
              className={`bg-white rounded-lg border p-6 transition-all ${
                selectedArticles.includes(article.id!)
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start gap-4">
                <input
                  type="checkbox"
                  checked={selectedArticles.includes(article.id!)}
                  onChange={() => handleToggleArticle(article.id!)}
                  className="mt-1 w-5 h-5 text-blue-600 rounded"
                />

                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-semibold text-gray-900 flex-1">
                      {article.title}
                    </h3>
                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-4 text-blue-600 hover:text-blue-700"
                    >
                      <ExternalLink size={18} />
                    </a>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-3 flex-wrap">
                    <span>来源：{article.source_name}</span>
                    <span>·</span>
                    <span>{new Date(article.published_at).toLocaleString('zh-CN')}</span>
                    <span>·</span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                      {article.industry}
                    </span>
                    {article.archived && (
                      <>
                        <span>·</span>
                        <span className="flex items-center gap-1 text-green-600">
                          <Check size={14} />
                          已归档
                        </span>
                      </>
                    )}
                  </div>

                  <p className="text-gray-700 text-sm leading-relaxed line-clamp-3">
                    {article.content.substring(0, 300)}...
                  </p>

                  {article.tags && article.tags.length > 0 && (
                    <div className="mt-3 flex gap-2 flex-wrap">
                      {article.tags.map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
