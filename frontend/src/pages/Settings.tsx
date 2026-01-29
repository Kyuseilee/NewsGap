import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, Edit } from 'lucide-react'
import { api } from '@/services/api'
import type { Source } from '@/types/api'

export default function SettingsPage() {
  const [showAddSource, setShowAddSource] = useState(false)
  const queryClient = useQueryClient()

  const { data: sources, isLoading } = useQuery({
    queryKey: ['sources'],
    queryFn: () => api.getSources({ enabled_only: false }),
  })

  if (isLoading) {
    return <div className="p-8 text-center">加载中...</div>
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">设置</h1>
      </div>

      {/* 信息源管理 */}
      <section className="mb-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">信息源管理</h2>
          <button
            onClick={() => setShowAddSource(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus size={20} />
            添加信息源
          </button>
        </div>

        <div className="space-y-3">
          {sources?.map((source: Source) => (
            <SourceItem key={source.id} source={source} />
          ))}
        </div>
      </section>

      {/* LLM 配置 */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">LLM 配置</h2>
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <p className="text-gray-600 text-sm">
            LLM API 密钥需要通过环境变量配置：
          </p>
          <ul className="mt-4 space-y-2 text-sm text-gray-600">
            <li><code className="bg-gray-100 px-2 py-1 rounded">OPENAI_API_KEY</code></li>
            <li><code className="bg-gray-100 px-2 py-1 rounded">DEEPSEEK_API_KEY</code></li>
            <li><code className="bg-gray-100 px-2 py-1 rounded">GEMINI_API_KEY</code></li>
          </ul>
        </div>
      </section>

      {/* 归档路径 */}
      <section>
        <h2 className="text-xl font-semibold text-gray-900 mb-6">归档设置</h2>
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            归档路径
          </label>
          <input
            type="text"
            defaultValue="./archives"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            readOnly
          />
          <p className="mt-2 text-sm text-gray-500">
            文章将导出为 Markdown 格式保存在此目录
          </p>
        </div>
      </section>
    </div>
  )
}

function SourceItem({ source }: { source: Source }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 flex items-center justify-between">
      <div className="flex-1">
        <div className="flex items-center gap-3">
          <h3 className="font-semibold text-gray-900">{source.name}</h3>
          <span className={`px-2 py-1 text-xs rounded ${
            source.enabled
              ? 'bg-green-100 text-green-700'
              : 'bg-gray-100 text-gray-600'
          }`}>
            {source.enabled ? '启用' : '禁用'}
          </span>
          <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
            {source.source_type.toUpperCase()}
          </span>
          <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
            {source.industry}
          </span>
        </div>
        <p className="text-sm text-gray-600 mt-1">{source.url}</p>
      </div>

      <div className="flex items-center gap-2">
        <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
          <Edit size={18} />
        </button>
        <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg">
          <Trash2 size={18} />
        </button>
      </div>
    </div>
  )
}
