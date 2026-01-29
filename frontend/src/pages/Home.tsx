import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Play, Zap, Loader2 } from 'lucide-react'
import { api } from '@/services/api'
import type { IntelligenceRequest } from '@/types/api'

export default function HomePage() {
  const [industry, setIndustry] = useState('ai')
  const [hours, setHours] = useState(24)
  const [llmBackend, setLlmBackend] = useState('deepseek')

  const { data: backends } = useQuery({
    queryKey: ['llm-backends'],
    queryFn: () => api.getLLMBackends(),
  })

  const fetchMutation = useMutation({
    mutationFn: (data: { industry: string; hours: number }) =>
      api.fetch(data),
    onSuccess: (data) => {
      alert(`成功爬取 ${data.count} 篇文章！`)
    },
  })

  const intelligenceMutation = useMutation({
    mutationFn: (data: IntelligenceRequest) => api.intelligence(data),
    onSuccess: (data) => {
      alert(`一键情报完成！爬取 ${data.article_count} 篇文章，已生成分析报告。`)
    },
  })

  const handleFetchOnly = () => {
    fetchMutation.mutate({ industry, hours })
  }

  const handleIntelligence = () => {
    intelligenceMutation.mutate({ industry, hours, llm_backend: llmBackend })
  }

  const isLoading = fetchMutation.isPending || intelligenceMutation.isPending

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

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <div className="space-y-6">
          {/* 行业选择 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              选择行业
            </label>
            <select
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="ai">AI / 人工智能</option>
              <option value="tech">科技</option>
              <option value="finance">金融</option>
              <option value="healthcare">医疗</option>
              <option value="energy">能源</option>
              <option value="education">教育</option>
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
              onChange={(e) => setLlmBackend(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {backends?.backends?.map((backend: any) => (
                <option key={backend.id} value={backend.id}>
                  {backend.name} {backend.cost > 0 ? `(约 $${backend.cost}/1k tokens)` : '(免费)'}
                </option>
              ))}
            </select>
          </div>

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
