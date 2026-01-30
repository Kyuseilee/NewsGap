import { useState, useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Play, Zap, Loader2 } from 'lucide-react'
import { api } from '@/services/api'
import type { IntelligenceRequest, Source } from '@/types/api'

export default function HomePage() {
  // 路由导航和query管理
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  // 选择的行业分类（基于RSSHub分类）
  const [industry, setIndustry] = useState('tech')
  const [hours, setHours] = useState(24)
  const [llmBackend, setLlmBackend] = useState('gemini')
  const [llmModel, setLlmModel] = useState<string>('')
  const [selectedSources, setSelectedSources] = useState<string[]>([])

  // 获取LLM后端列表
  const { data: backends } = useQuery({
    queryKey: ['llm-backends'],
    queryFn: () => api.getLLMBackends(),
  })

  // 获取信息源列表
  const { data: sources } = useQuery({
    queryKey: ['sources', industry],
    queryFn: () => api.getSources({ industry, enabled_only: false }),
  })

  // 当前选中后端的模型列表
  const currentBackendModels = useMemo(() => {
    if (!backends?.backends) return []
    const backend = backends.backends.find((b: any) => b.id === llmBackend)
    return backend?.models || []
  }, [backends, llmBackend])

  // 当后端改变时，自动选择第一个模型
  useMemo(() => {
    if (currentBackendModels.length > 0 && !llmModel) {
      setLlmModel(currentBackendModels[0].id)
    }
  }, [currentBackendModels, llmModel])

  const fetchMutation = useMutation({
    mutationFn: (data: { industry: string; hours: number; source_ids?: string[] }) =>
      api.fetch(data),
    onSuccess: (data) => {
      alert(`成功爬取 ${data.count} 篇文章！`)
      // 刷新文章列表缓存，使Articles页面显示最新数据
      // 使用通配符匹配所有articles查询
      queryClient.invalidateQueries({ queryKey: ['articles'], refetchType: 'all' })
    },
  })

  const intelligenceMutation = useMutation({
    mutationFn: (data: IntelligenceRequest) => api.intelligence(data),
    onSuccess: (data) => {
      alert(`一键情报完成！爬取 ${data.article_count} 篇文章，已生成分析报告。`)
      // 刷新文章列表缓存
      queryClient.invalidateQueries({ queryKey: ['articles'], refetchType: 'all' })
      // 自动跳转到分析报告详情页面
      if (data.analysis_id) {
        navigate(`/analysis/${data.analysis_id}`)
      }
    },
  })

  const handleFetchOnly = () => {
    fetchMutation.mutate({ 
      industry, 
      hours,
      source_ids: selectedSources.length > 0 ? selectedSources : undefined
    })
  }

  const handleIntelligence = () => {
    intelligenceMutation.mutate({ 
      industry, 
      hours, 
      llm_backend: llmBackend,
      llm_model: llmModel || undefined,
      source_ids: selectedSources.length > 0 ? selectedSources : undefined
    })
  }

  const handleSourceToggle = (sourceId: string) => {
    setSelectedSources(prev => 
      prev.includes(sourceId) 
        ? prev.filter(id => id !== sourceId)
        : [...prev, sourceId]
    )
  }

  const isLoading = fetchMutation.isPending || intelligenceMutation.isPending

  return (
    <div className="max-w-6xl mx-auto py-12 px-6">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          NewsGap 信息差情报工具
        </h1>
        <p className="text-lg text-gray-600">
          自动收集、归档和分析行业信息，快速把握关键趋势
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧：配置面板 */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">配置参数</h2>
          
          <div className="space-y-6">
            {/* 行业分类选择（基于RSSHub） */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                信息源分类
              </label>
              <select
                value={industry}
                onChange={(e) => {
                  setIndustry(e.target.value)
                  setSelectedSources([]) // 重置选中的源
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="social">社交媒体（微博、知乎、即刻等）</option>
                <option value="news">新闻资讯（传统媒体）</option>
                <option value="tech">科技互联网（36氪、少数派、IT之家）</option>
                <option value="developer">开发者（GitHub、Hacker News、掘金）</option>
                <option value="finance">财经金融（财联社、金十数据、东方财富）</option>
                <option value="crypto">加密货币（金色财经、律动、TokenInsight）</option>
                <option value="entertainment">娱乐影视（豆瓣电影、B站）</option>
                <option value="gaming">游戏电竞（Steam、TapTap）</option>
                <option value="anime">动漫二次元（Bangumi、ACG资讯）</option>
                <option value="shopping">电商购物（淘宝、京东、小红书）</option>
                <option value="education">学习教育（MOOC、知识付费）</option>
                <option value="lifestyle">生活方式（美食、旅游、健身）</option>
                <option value="other">其他</option>
              </select>
            </div>

            {/* 时间范围 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                时间范围（小时）
              </label>
              <input
                type="number"
                value={hours}
                onChange={(e) => setHours(parseInt(e.target.value))}
                min="1"
                max="168"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* LLM 后端选择 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                LLM 后端
              </label>
              <select
                value={llmBackend}
                onChange={(e) => {
                  setLlmBackend(e.target.value)
                  setLlmModel('') // 重置模型选择
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {backends?.backends?.map((backend: any) => (
                  <option key={backend.id} value={backend.id}>
                    {backend.name} {backend.cost > 0 ? `(约 $${backend.cost}/1k tokens)` : '(免费)'}
                  </option>
                ))}
              </select>
            </div>

            {/* LLM 模型选择 */}
            {currentBackendModels.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  选择模型
                </label>
                <select
                  value={llmModel}
                  onChange={(e) => setLlmModel(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {currentBackendModels.map((model: any) => (
                    <option key={model.id} value={model.id}>
                      {model.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* 操作按钮 */}
            <div className="flex gap-4 pt-4">
              <button
                onClick={handleFetchOnly}
                disabled={isLoading}
                className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {fetchMutation.isPending ? (
                  <>
                    <Loader2 size={20} className="animate-spin" />
                    爬取中...
                  </>
                ) : (
                  <>
                    <Play size={20} />
                    仅爬取
                  </>
                )}
              </button>

              <button
                onClick={handleIntelligence}
                disabled={isLoading}
                className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {intelligenceMutation.isPending ? (
                  <>
                    <Loader2 size={20} className="animate-spin" />
                    处理中...
                  </>
                ) : (
                  <>
                    <Zap size={20} />
                    一键情报
                  </>
                )}
              </button>
            </div>
          </div>

          {/* 结果显示 */}
          {intelligenceMutation.isSuccess && intelligenceMutation.data && (
            <div className="mt-8 p-6 bg-green-50 border border-green-200 rounded-lg">
              <h3 className="text-lg font-semibold text-green-900 mb-2">
                分析完成
              </h3>
              <p className="text-green-700 mb-4">
                {intelligenceMutation.data.analysis.executive_brief}
              </p>
              <div className="text-sm text-green-600">
                <p>文章数量: {intelligenceMutation.data.article_count}</p>
                <p>处理时间: {intelligenceMutation.data.total_time_seconds.toFixed(2)}秒</p>
              </div>
            </div>
          )}
        </div>

        {/* 右侧：信息源选择面板 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            选择信息源
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            {sources?.length || 0} 个可用源，
            {selectedSources.length > 0 ? `已选 ${selectedSources.length} 个` : '全部使用'}
          </p>
          
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {sources && sources.length > 0 ? (
              sources.map((source: Source) => (
                <label
                  key={source.id}
                  className={`flex items-start gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedSources.includes(source.id!)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedSources.includes(source.id!)}
                    onChange={() => handleSourceToggle(source.id!)}
                    className="mt-1 w-4 h-4"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-900 text-sm truncate">
                      {source.name}
                    </div>
                    <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded ${
                        source.enabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                      }`}>
                        {source.enabled ? '启用' : '禁用'}
                      </span>
                      <span className="uppercase">{source.source_type}</span>
                    </div>
                  </div>
                </label>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p className="mb-2">该分类下暂无信息源</p>
                <p className="text-sm">请前往设置页面添加</p>
              </div>
            )}
          </div>
          
          {selectedSources.length > 0 && (
            <button
              onClick={() => setSelectedSources([])}
              className="mt-4 w-full py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              清除选择
            </button>
          )}
        </div>
      </div>

      {/* 功能说明 */}
      <div className="mt-12 grid grid-cols-2 gap-6">
        <InfoCard
          title="分步执行"
          description="先爬取文章，查看列表，选择性分析"
        />
        <InfoCard
          title="一键情报"
          description="自动爬取并分析，快速获取情报摘要"
        />
      </div>
    </div>
  )
}

function InfoCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="p-6 bg-white rounded-lg border border-gray-200">
      <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  )
}
