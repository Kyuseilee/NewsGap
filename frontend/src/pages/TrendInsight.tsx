import { useState, useMemo } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { 
  LineChart, Calendar, Filter, CheckSquare, Square, 
  Sparkles, Clock, ArrowRight, AlertCircle, History
} from 'lucide-react'
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

// LLM 后端配置
const LLM_BACKENDS = [
  { id: 'deepseek', name: 'DeepSeek', models: ['deepseek-chat', 'deepseek-reasoner'] },
  { id: 'gemini', name: 'Gemini', models: ['gemini-2.5-flash', 'gemini-2.5-pro'] },
  { id: 'openai', name: 'OpenAI', models: ['gpt-4o-mini', 'gpt-4o'] },
]

export default function TrendInsightPage() {
  const navigate = useNavigate()
  
  // 状态
  const [selectedIndustry, setSelectedIndustry] = useState<string>('all')
  const [dateRange, setDateRange] = useState<'7d' | '30d' | 'custom'>('7d')
  const [customStartDate, setCustomStartDate] = useState<string>('')
  const [customEndDate, setCustomEndDate] = useState<string>('')
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [llmBackend, setLlmBackend] = useState<string>('deepseek')
  const [llmModel, setLlmModel] = useState<string>('deepseek-chat')

  // 获取分析报告列表
  const { data: analyses, isLoading } = useQuery({
    queryKey: ['analyses-list'],
    queryFn: () => api.getAnalysesList(),
  })

  // 过滤报告
  const filteredAnalyses = useMemo(() => {
    if (!analyses) return []
    
    let filtered = [...analyses]
    
    // 按行业筛选
    if (selectedIndustry !== 'all') {
      filtered = filtered.filter((a: any) => a.industry === selectedIndustry)
    }
    
    // 按日期范围筛选
    const now = new Date()
    let startDate: Date | null = null
    let endDate: Date | null = null
    
    if (dateRange === '7d') {
      startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    } else if (dateRange === '30d') {
      startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
    } else if (dateRange === 'custom' && customStartDate) {
      startDate = new Date(customStartDate)
      if (customEndDate) {
        endDate = new Date(customEndDate)
        endDate.setHours(23, 59, 59, 999)
      }
    }
    
    if (startDate) {
      filtered = filtered.filter((a: any) => new Date(a.created_at) >= startDate!)
    }
    if (endDate) {
      filtered = filtered.filter((a: any) => new Date(a.created_at) <= endDate!)
    }
    
    // 按时间排序（新的在前）
    filtered.sort((a: any, b: any) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
    
    return filtered
  }, [analyses, selectedIndustry, dateRange, customStartDate, customEndDate])

  // 获取所有可用的行业
  const availableIndustries = useMemo(() => {
    if (!analyses) return []
    const industries = new Set(analyses.map((a: any) => a.industry).filter(Boolean))
    return Array.from(industries).sort()
  }, [analyses])

  // 创建趋势洞察
  const createMutation = useMutation({
    mutationFn: (params: { analysis_ids: string[]; llm_backend: string; llm_model?: string }) =>
      api.createTrendInsight(params),
    onSuccess: (data) => {
      navigate(`/trend-insight/${data.id}`)
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || '趋势洞察生成失败')
    }
  })

  // 切换选择
  const toggleSelect = (id: string) => {
    const newSelected = new Set(selectedIds)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedIds(newSelected)
  }

  // 全选/取消全选
  const toggleSelectAll = () => {
    if (selectedIds.size === filteredAnalyses.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(filteredAnalyses.map((a: any) => a.id)))
    }
  }

  // 计算已选报告的时间跨度
  const selectedTimeSpan = useMemo(() => {
    if (selectedIds.size === 0) return null
    
    const selectedAnalyses = filteredAnalyses.filter((a: any) => selectedIds.has(a.id))
    if (selectedAnalyses.length === 0) return null
    
    const dates = selectedAnalyses.map((a: any) => new Date(a.created_at).getTime())
    const minDate = new Date(Math.min(...dates))
    const maxDate = new Date(Math.max(...dates))
    const daysDiff = Math.ceil((maxDate.getTime() - minDate.getTime()) / (1000 * 60 * 60 * 24))
    
    return {
      start: minDate.toLocaleDateString('zh-CN'),
      end: maxDate.toLocaleDateString('zh-CN'),
      days: daysDiff + 1
    }
  }, [selectedIds, filteredAnalyses])

  // 提交分析
  const handleSubmit = () => {
    if (selectedIds.size < 2) {
      alert('请至少选择2个分析报告')
      return
    }
    
    createMutation.mutate({
      analysis_ids: Array.from(selectedIds),
      llm_backend: llmBackend,
      llm_model: llmModel
    })
  }

  // 切换 LLM 后端时更新模型
  const handleBackendChange = (backend: string) => {
    setLlmBackend(backend)
    const backendConfig = LLM_BACKENDS.find(b => b.id === backend)
    if (backendConfig && backendConfig.models.length > 0) {
      setLlmModel(backendConfig.models[0])
    }
  }

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
              <h1 className="text-3xl font-bold text-gray-900">趋势洞察</h1>
              <p className="text-gray-600">从多个分析报告中识别趋势、规律和拐点</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/trend-insight/history')}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <History size={18} />
            历史记录
          </button>
        </div>
      </div>

      {/* 筛选区域 */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">选择分析报告</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* 日期范围快捷选择 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Calendar size={16} className="inline mr-1" />
              时间范围
            </label>
            <div className="flex gap-2">
              <button
                onClick={() => setDateRange('7d')}
                className={`flex-1 px-3 py-2 text-sm rounded-lg border ${
                  dateRange === '7d' 
                    ? 'bg-purple-100 border-purple-500 text-purple-700' 
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                最近7天
              </button>
              <button
                onClick={() => setDateRange('30d')}
                className={`flex-1 px-3 py-2 text-sm rounded-lg border ${
                  dateRange === '30d' 
                    ? 'bg-purple-100 border-purple-500 text-purple-700' 
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                最近30天
              </button>
              <button
                onClick={() => setDateRange('custom')}
                className={`flex-1 px-3 py-2 text-sm rounded-lg border ${
                  dateRange === 'custom' 
                    ? 'bg-purple-100 border-purple-500 text-purple-700' 
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                自定义
              </button>
            </div>
          </div>

          {/* 自定义日期 */}
          {dateRange === 'custom' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">开始日期</label>
                <input
                  type="date"
                  value={customStartDate}
                  onChange={(e) => setCustomStartDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">结束日期</label>
                <input
                  type="date"
                  value={customEndDate}
                  onChange={(e) => setCustomEndDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </>
          )}

          {/* 行业筛选 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Filter size={16} className="inline mr-1" />
              行业分类
            </label>
            <select
              value={selectedIndustry}
              onChange={(e) => setSelectedIndustry(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
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

        {/* 全选按钮 */}
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={toggleSelectAll}
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
          >
            {selectedIds.size === filteredAnalyses.length && filteredAnalyses.length > 0 ? (
              <CheckSquare size={18} className="text-purple-600" />
            ) : (
              <Square size={18} />
            )}
            {selectedIds.size === filteredAnalyses.length && filteredAnalyses.length > 0 
              ? '取消全选' 
              : `全选 (${filteredAnalyses.length})`}
          </button>
          
          <span className="text-sm text-gray-500">
            已选择 {selectedIds.size} 个报告
          </span>
        </div>

        {/* 报告列表 */}
        <div className="max-h-96 overflow-y-auto border border-gray-200 rounded-lg">
          {filteredAnalyses.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <AlertCircle className="mx-auto mb-2" size={32} />
              <p>没有找到符合条件的分析报告</p>
              <p className="text-sm mt-1">请调整筛选条件或先生成一些分析报告</p>
            </div>
          ) : (
            filteredAnalyses.map((analysis: any) => (
              <div
                key={analysis.id}
                onClick={() => toggleSelect(analysis.id)}
                className={`flex items-start gap-4 p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                  selectedIds.has(analysis.id) ? 'bg-purple-50' : ''
                }`}
              >
                <div className="pt-1">
                  {selectedIds.has(analysis.id) ? (
                    <CheckSquare size={20} className="text-purple-600" />
                  ) : (
                    <Square size={20} className="text-gray-400" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-gray-900">
                      {new Date(analysis.created_at).toLocaleDateString('zh-CN')}
                    </span>
                    <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded">
                      {INDUSTRY_LABELS[analysis.industry] || '未分类'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 truncate">
                    {analysis.executive_brief?.substring(0, 100) || '暂无摘要'}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* LLM 配置和提交区域 */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row items-start md:items-end gap-6">
          {/* 已选统计 */}
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">分析配置</h3>
            {selectedTimeSpan ? (
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span className="flex items-center gap-1">
                  <CheckSquare size={16} className="text-purple-600" />
                  已选 {selectedIds.size} 篇报告
                </span>
                <span className="flex items-center gap-1">
                  <Clock size={16} />
                  时间跨度: {selectedTimeSpan.days} 天
                </span>
                <span className="text-gray-400">
                  ({selectedTimeSpan.start} - {selectedTimeSpan.end})
                </span>
              </div>
            ) : (
              <p className="text-sm text-gray-500">请至少选择2个分析报告进行趋势洞察</p>
            )}
          </div>

          {/* LLM 选择 */}
          <div className="flex items-end gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">LLM 后端</label>
              <select
                value={llmBackend}
                onChange={(e) => handleBackendChange(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                {LLM_BACKENDS.map(backend => (
                  <option key={backend.id} value={backend.id}>{backend.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">模型</label>
              <select
                value={llmModel}
                onChange={(e) => setLlmModel(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                {LLM_BACKENDS.find(b => b.id === llmBackend)?.models.map(model => (
                  <option key={model} value={model}>{model}</option>
                ))}
              </select>
            </div>
            
            {/* 提交按钮 */}
            <button
              onClick={handleSubmit}
              disabled={selectedIds.size < 2 || createMutation.isPending}
              className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {createMutation.isPending ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                  分析中...
                </>
              ) : (
                <>
                  <Sparkles size={18} />
                  生成趋势洞察
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
