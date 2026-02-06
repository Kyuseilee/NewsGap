import { useState, useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Play, Zap, Loader2, AlertTriangle } from 'lucide-react'
import { api } from '@/services/api'
import type { IntelligenceRequest, CustomCategory } from '@/types/api'

// 文章数量阈值配置
const ARTICLE_COUNT_THRESHOLD = {
  MIN: 5,        // 最小文章数量
  WARNING: 10,   // 警告阈值
  GOOD: 20,      // 良好阈值
}

// 重试配置
const RETRY_CONFIG = {
  MAX_ATTEMPTS: 2,   // 最大重试次数
  DELAY_MS: 3000,    // 重试延迟（毫秒）
}

export default function HomePage() {
  // 路由导航和query管理
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  // 分类模式：'industry' 或 'custom'
  const [categoryMode, setCategoryMode] = useState<'industry' | 'custom'>('industry')
  // 选择的行业分类（基于RSSHub分类）
  const [industry, setIndustry] = useState('daily_info_gap')
  // 选择的自定义分类ID
  const [customCategoryId, setCustomCategoryId] = useState<string>('')
  const [hours, setHours] = useState(24)
  const [llmBackend, setLlmBackend] = useState('gemini')
  const [llmModel, setLlmModel] = useState<string>('')
  
  // 文章获取状态
  const [fetchingStatus, setFetchingStatus] = useState<{
    attempt: number
    articleCount: number
    isRetrying: boolean
  } | null>(null)

  // 获取LLM后端列表
  const { data: backends } = useQuery({
    queryKey: ['llm-backends'],
    queryFn: () => api.getLLMBackends(),
  })

  // 获取自定义分类列表
  const { data: customCategories = [] } = useQuery({
    queryKey: ['customCategories'],
    queryFn: () => api.getCustomCategories({ enabled_only: true }),
  })

  // 获取当前选中的自定义分类
  const currentCustomCategory = useMemo(() => {
    if (categoryMode === 'custom' && customCategoryId) {
      return customCategories.find((c: CustomCategory) => c.id === customCategoryId)
    }
    return null
  }, [categoryMode, customCategoryId, customCategories])

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
    mutationFn: (data: { industry: string; hours: number }) =>
      api.fetch(data),
    onSuccess: (data) => {
      alert(`成功爬取 ${data.count} 篇文章！`)
      // 刷新文章列表缓存，使Articles页面显示最新数据
      queryClient.invalidateQueries({ queryKey: ['articles'], refetchType: 'all' })
    },
    onError: (error: any) => {
      // 处理404和其他错误
      if (error.response?.status === 404) {
        alert('❌ 未能获取到文章\n\n可能原因：\n• 本地 RSSHub 服务未启动\n• 信息源暂时不可用\n• 该分类下没有可用的信息源\n\n请检查 RSSHub 服务状态或稍后重试')
      } else {
        const errorMsg = error.response?.data?.detail || error.message || '未知错误'
        alert(`❌ 爬取失败：${errorMsg}`)
      }
    },
  })

  const intelligenceMutation = useMutation({
    mutationFn: (data: IntelligenceRequest) => api.intelligence(data),
    onSuccess: (data) => {
      alert(`✅ 一键情报完成！\n\n爬取 ${data.article_count} 篇文章，已生成分析报告。`)
      // 刷新文章列表缓存
      queryClient.invalidateQueries({ queryKey: ['articles'], refetchType: 'all' })
      // 自动跳转到分析报告详情页面
      if (data.analysis_id) {
        navigate(`/analysis/${data.analysis_id}`)
      }
    },
    onError: (error: any) => {
      // 只处理分析阶段的错误（文章获取错误已在 handleIntelligence 中处理）
      const errorMsg = error.response?.data?.detail || error.message || '未知错误'
      alert(`❌ 分析失败：${errorMsg}\n\n可能原因：\n• LLM API 调用失败\n• API Key 未配置或无效\n• 网络连接问题`)
    },
  })

  const handleFetchOnly = () => {
    fetchMutation.mutate({ 
      industry, 
      hours,
    })
  }

  // 检查文章数量（带重试）
  const checkAndFetchArticles = async (
    request: { industry?: string; custom_category_id?: string; hours: number },
    attempt: number = 1
  ): Promise<{ count: number; shouldProceed: boolean }> => {
    try {
      // 显示获取状态
      setFetchingStatus({
        attempt,
        articleCount: 0,
        isRetrying: attempt > 1
      })

      // 调用爬取 API
      const fetchRequest: any = { hours: request.hours }
      if (request.industry) {
        fetchRequest.industry = request.industry
      }
      if (request.custom_category_id) {
        fetchRequest.custom_category_id = request.custom_category_id
      }
      
      const result = await api.fetch(fetchRequest)
      const count = result.count

      // 更新文章数量
      setFetchingStatus(prev => prev ? { ...prev, articleCount: count } : null)

      // 如果文章数量足够，直接返回
      if (count >= ARTICLE_COUNT_THRESHOLD.MIN) {
        setFetchingStatus(null)
        return { count, shouldProceed: true }
      }

      // 如果还有重试机会且文章太少
      if (attempt < RETRY_CONFIG.MAX_ATTEMPTS) {
        // 等待一段时间后重试
        await new Promise(resolve => setTimeout(resolve, RETRY_CONFIG.DELAY_MS))
        return checkAndFetchArticles(request, attempt + 1)
      }

      // 重试次数用尽，文章仍然太少
      setFetchingStatus(null)
      return { count, shouldProceed: false }
    } catch (error) {
      setFetchingStatus(null)
      throw error
    }
  }

  // 显示文章数量警告弹窗
  const showArticleCountWarning = (count: number) => {
    const message = count === 0
      ? '❌ 未能获取到任何文章\n\n可能原因：\n• 本地 RSSHub 服务未启动\n• 信息源暂时不可用\n• 该分类下没有可用的信息源\n\n请检查 RSSHub 服务状态或稍后重试'
      : `⚠️ 获取的文章数量较少（${count} 篇）\n\n建议：\n• 扩大时间范围（当前：${hours}小时）\n• 检查信息源配置是否正常\n• 等待一段时间后重试\n\n至少需要 ${ARTICLE_COUNT_THRESHOLD.MIN} 篇文章才能进行有效分析。`
    
    if (window.confirm(message + '\n\n是否要继续？')) {
      // 用户确认继续
      return true
    }
    return false
  }

  const handleIntelligence = async () => {
    const request: IntelligenceRequest = {
      hours,
      llm_backend: llmBackend,
      llm_model: llmModel || undefined,
    }

    if (categoryMode === 'custom' && customCategoryId) {
      request.custom_category_id = customCategoryId
    } else {
      request.industry = industry
    }

    try {
      // 先检查文章数量（带重试）
      const { count, shouldProceed } = await checkAndFetchArticles(request)
      
      if (!shouldProceed) {
        // 文章太少，显示警告
        const userConfirmed = showArticleCountWarning(count)
        if (!userConfirmed) {
          return // 用户取消
        }
      }

      // 文章数量足够（或用户确认继续），发起分析请求
      intelligenceMutation.mutate(request)
    } catch (error: any) {
      // 处理获取文章时的错误
      if (error.response?.status === 404) {
        alert('❌ 未能获取到文章\n\n可能原因：\n• 本地 RSSHub 服务未启动\n• 信息源暂时不可用\n• 该分类下没有可用的信息源\n\n请检查 RSSHub 服务状态或稍后重试')
      } else {
        const errorMsg = error.response?.data?.detail || error.message || '未知错误'
        alert(`❌ 获取文章失败：${errorMsg}`)
      }
    }
  }

  const isLoading = fetchMutation.isPending || intelligenceMutation.isPending || fetchingStatus !== null

  return (
    <div className="max-w-4xl mx-auto py-12 px-6">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          NewsGap 信息差情报工具
        </h1>
        <p className="text-lg text-gray-600">
          自动收集、归档和分析行业信息，快速把握关键趋势
        </p>
      </div>

      {/* 配置面板 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">配置参数</h2>
        
        <div className="space-y-6">
          {/* 分类模式选择 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              分类模式
            </label>
            <div className="flex gap-3">
              <button
                onClick={() => setCategoryMode('industry')}
                className={`flex-1 px-4 py-2 rounded-lg border-2 transition-all ${
                  categoryMode === 'industry'
                    ? 'border-blue-500 bg-blue-50 text-blue-700 font-medium'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                标准行业分类
              </button>
              <button
                onClick={() => {
                  setCategoryMode('custom')
                  if (customCategories.length > 0 && !customCategoryId) {
                    setCustomCategoryId(customCategories[0].id!)
                  }
                }}
                className={`flex-1 px-4 py-2 rounded-lg border-2 transition-all ${
                  categoryMode === 'custom'
                    ? 'border-blue-500 bg-blue-50 text-blue-700 font-medium'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                自定义分类
              </button>
            </div>
          </div>

          {/* 标准行业分类选择 */}
          {categoryMode === 'industry' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                信息源分类
              </label>
              <select
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="daily_info_gap">每日信息差（精选综合信息源）</option>
                <option value="socialmedia">社交媒体（微博、知乎、即刻等）</option>
                <option value="news">新闻资讯（传统媒体）</option>
                <option value="tech">科技互联网（36氪、少数派、IT之家）</option>
                <option value="developer">开发者（GitHub、Hacker News、掘金）</option>
                <option value="finance">财经金融（财联社、金十数据、东方财富）</option>
                <option value="entertainment">娱乐影视（豆瓣电影、B站）</option>
                <option value="gaming">游戏电竞（Steam、TapTap）</option>
                <option value="anime">动漫二次元（Bangumi、ACG资讯）</option>
                <option value="shopping">电商购物（淘宝、京东、小红书）</option>
                <option value="education">学习教育（MOOC、知识付费）</option>
                <option value="lifestyle">生活方式（美食、旅游、健身）</option>
                <option value="other">其他</option>
              </select>
            </div>
          )}

          {/* 自定义分类选择 */}
          {categoryMode === 'custom' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                选择自定义分类
              </label>
              {customCategories.length === 0 ? (
                <div className="p-4 border border-gray-300 rounded-lg bg-gray-50 text-center">
                  <p className="text-gray-600 text-sm mb-2">暂无自定义分类</p>
                  <p className="text-gray-500 text-xs">请前往设置页面创建自定义分类</p>
                </div>
              ) : (
                <>
                  <select
                    value={customCategoryId}
                    onChange={(e) => setCustomCategoryId(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {customCategories.map((category: CustomCategory) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                        {category.description ? ` - ${category.description}` : ''}
                      </option>
                    ))}
                  </select>
                  {currentCustomCategory && (
                    <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-xs font-medium text-blue-900 mb-1">自定义 Prompt:</p>
                      <p className="text-xs text-blue-700 whitespace-pre-wrap">
                        {currentCustomCategory.custom_prompt}
                      </p>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {/* 时间范围 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              时间范围
            </label>
            <div className="flex gap-2">
              {[12, 24, 48, 72, 168].map((h) => (
                <button
                  key={h}
                  onClick={() => setHours(h)}
                  className={`flex-1 px-4 py-2 rounded-lg border transition-all ${
                    hours === h
                      ? 'border-blue-500 bg-blue-50 text-blue-700 font-medium'
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {h < 24 ? `${h}h` : h === 168 ? '1周' : `${h / 24}天`}
                </button>
              ))}
            </div>
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
                  分析中...
                </>
              ) : fetchingStatus ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  {fetchingStatus.isRetrying ? `重试中 (${fetchingStatus.attempt}/${RETRY_CONFIG.MAX_ATTEMPTS})` : '获取文章中...'}
                </>
              ) : (
                <>
                  <Zap size={20} />
                  一键情报
                </>
              )}
            </button>
          </div>

          {/* 文章获取状态提示 */}
          {fetchingStatus && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-start gap-3">
                <AlertTriangle className="text-yellow-600 mt-0.5" size={20} />
                <div className="flex-1">
                  <p className="text-sm font-medium text-yellow-900">
                    {fetchingStatus.isRetrying ? '文章数量较少，正在重新获取...' : '正在获取文章...'}
                  </p>
                  <p className="text-xs text-yellow-700 mt-1">
                    尝试次数: {fetchingStatus.attempt}/{RETRY_CONFIG.MAX_ATTEMPTS}
                    {fetchingStatus.articleCount > 0 && ` · 已获取: ${fetchingStatus.articleCount} 篇`}
                  </p>
                  {fetchingStatus.isRetrying && (
                    <p className="text-xs text-yellow-600 mt-1">
                      等待 {RETRY_CONFIG.DELAY_MS / 1000} 秒后重试...
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}
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

      {/* 功能说明 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <InfoCard
          title="仅爬取"
          description="先收集所有文章，在文章列表页面查看详情，选择性进行分析"
        />
        <InfoCard
          title="一键情报"
          description="自动爬取并使用 AI 分析，直接生成情报报告，快速了解行业动态"
        />
      </div>

      {/* 提示信息 */}
      <div className="mt-8 p-6 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">💡 提示</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• 信息源管理请前往<strong>设置页面</strong>，在那里可以启用/禁用特定信息源</li>
          <li>• 选择合适的时间范围可以获得更准确的情报分析</li>
          <li>• 建议首次使用选择 Gemini（免费且速度快）</li>
        </ul>
      </div>
    </div>
  )
}

function InfoCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="p-6 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
      <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  )
}
