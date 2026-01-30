import { useState, useMemo } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, Edit, ChevronDown, ChevronRight } from 'lucide-react'
import { api } from '@/services/api'
import type { Source } from '@/types/api'

// 行业分类映射
const INDUSTRY_CATEGORIES = {
  social: '社交媒体',
  news: '新闻资讯',
  tech: '科技互联网',
  developer: '开发者',
  finance: '财经金融',
  crypto: '加密货币',
  entertainment: '娱乐影视',
  gaming: '游戏电竞',
  anime: '动漫二次元',
  shopping: '电商购物',
  education: '学习教育',
  lifestyle: '生活方式',
  other: '其他',
} as const

interface SourceEditorProps {
  source?: Source
  onClose: () => void
}

function SourceEditor({ source, onClose }: SourceEditorProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    name: source?.name || '',
    url: source?.url || '',
    source_type: source?.source_type || 'rss',
    industry: source?.industry || 'social',
    enabled: source?.enabled ?? true,
  })

  const saveMutation = useMutation({
    mutationFn: (data: any) => {
      if (source?.id) {
        return api.updateSource(source.id, data)
      }
      return api.addSource(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
      alert(source ? '信息源已更新' : '信息源已添加')
      onClose()
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || '保存失败')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.name || !formData.url) {
      alert('请填写必填项')
      return
    }
    saveMutation.mutate(formData)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          {source ? '编辑信息源' : '添加信息源'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              名称 *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              URL *
            </label>
            <input
              type="url"
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              placeholder="https://example.com/feed"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                类型
              </label>
              <select
                value={formData.source_type}
                onChange={(e) => setFormData({ ...formData, source_type: e.target.value as 'rss' | 'web' | 'api' })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="rss">RSS</option>
                <option value="webpage">网页</option>
                <option value="api">API</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                行业
              </label>
              <select
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="social">社交媒体</option>
                <option value="news">新闻资讯</option>
                <option value="tech">科技互联网</option>
                <option value="developer">开发者</option>
                <option value="finance">财经金融</option>
                <option value="crypto">加密货币</option>
                <option value="entertainment">娱乐影视</option>
                <option value="gaming">游戏电竞</option>
                <option value="anime">动漫二次元</option>
                <option value="shopping">电商购物</option>
                <option value="education">学习教育</option>
                <option value="lifestyle">生活方式</option>
                <option value="other">其他</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="enabled"
              checked={formData.enabled}
              onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
              className="w-4 h-4"
            />
            <label htmlFor="enabled" className="text-sm text-gray-700">
              启用此信息源
            </label>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={saveMutation.isPending}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {saveMutation.isPending ? '保存中...' : '保存'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              取消
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface SourceItemProps {
  source: Source
  onEdit: () => void
  onDelete: () => void
}

function SourceItem({ source, onEdit, onDelete }: SourceItemProps) {
  return (
    <div className="bg-white p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
      <div className="flex-1">
        <div className="flex items-center gap-3 mb-2">
          <h3 className="font-semibold text-gray-900">{source.name}</h3>
          <span
            className={`px-2 py-1 text-xs rounded ${
              source.enabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
            }`}
          >
            {source.enabled ? '启用' : '禁用'}
          </span>
          <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded uppercase">
            {source.source_type}
          </span>
        </div>
        <p className="text-sm text-gray-600 break-all">{source.url}</p>
        {source.last_fetched_at && (
          <p className="text-xs text-gray-500 mt-1">
            最后爬取：{new Date(source.last_fetched_at).toLocaleString('zh-CN')}
          </p>
        )}
      </div>

      <div className="flex items-center gap-2 ml-4">
        <button
          onClick={onEdit}
          className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          title="编辑"
        >
          <Edit size={18} />
        </button>
        <button
          onClick={onDelete}
          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          title="删除"
        >
          <Trash2 size={18} />
        </button>
      </div>
    </div>
  )
}

interface SourceManagerProps {
  sources: Source[]
}

export default function SourceManager({ sources }: SourceManagerProps) {
  const queryClient = useQueryClient()
  const [editingSource, setEditingSource] = useState<Source | null>(null)
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(Object.keys(INDUSTRY_CATEGORIES)))

  // 按行业分组
  const sourcesByIndustry = useMemo(() => {
    const grouped: Record<string, Source[]> = {}
    Object.keys(INDUSTRY_CATEGORIES).forEach(key => {
      grouped[key] = []
    })
    
    sources.forEach(source => {
      const industry = source.industry || 'other'
      if (!grouped[industry]) {
        grouped[industry] = []
      }
      grouped[industry].push(source)
    })
    
    return grouped
  }, [sources])

  // 统计信息
  const stats = useMemo(() => {
    return {
      total: sources.length,
      enabled: sources.filter(s => s.enabled).length,
      disabled: sources.filter(s => !s.enabled).length,
    }
  }, [sources])

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories)
    if (newExpanded.has(category)) {
      newExpanded.delete(category)
    } else {
      newExpanded.add(category)
    }
    setExpandedCategories(newExpanded)
  }

  const deleteMutation = useMutation({
    mutationFn: (sourceId: string) => api.deleteSource(sourceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
      alert('信息源已删除')
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || '删除失败')
    },
  })

  const handleDelete = (source: Source) => {
    if (confirm(`确定要删除信息源"${source.name}"吗？`)) {
      deleteMutation.mutate(source.id!)
    }
  }

  return (
    <>
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">信息源管理</h2>
          <button
            onClick={() => setShowAddDialog(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={20} />
            添加信息源
          </button>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-600 mb-1">总数</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-600 mb-1">已启用</div>
            <div className="text-2xl font-bold text-green-600">{stats.enabled}</div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-600 mb-1">已禁用</div>
            <div className="text-2xl font-bold text-gray-600">{stats.disabled}</div>
          </div>
        </div>
      </div>

      {/* 按分类显示信息源 */}
      <div className="space-y-4">
        {Object.entries(INDUSTRY_CATEGORIES).map(([categoryKey, categoryName]) => {
          const categorySources = sourcesByIndustry[categoryKey] || []
          const isExpanded = expandedCategories.has(categoryKey)
          
          if (categorySources.length === 0) return null
          
          return (
            <div key={categoryKey} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              {/* 分类头部 */}
              <button
                onClick={() => toggleCategory(categoryKey)}
                className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                  <h3 className="text-lg font-semibold text-gray-900">{categoryName}</h3>
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 text-sm rounded">
                    {categorySources.length} 个源
                  </span>
                  <span className="text-sm text-gray-600">
                    ({categorySources.filter(s => s.enabled).length} 启用)
                  </span>
                </div>
              </button>

              {/* 分类内容 */}
              {isExpanded && (
                <div className="border-t border-gray-200 divide-y divide-gray-200">
                  {categorySources.map((source) => (
                    <SourceItem
                      key={source.id}
                      source={source}
                      onEdit={() => setEditingSource(source)}
                      onDelete={() => handleDelete(source)}
                    />
                  ))}
                </div>
              )}
            </div>
          )
        })}

        {sources.length === 0 && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
            <p className="text-gray-600">还没有信息源</p>
            <button
              onClick={() => setShowAddDialog(true)}
              className="mt-4 text-blue-600 hover:text-blue-700"
            >
              添加第一个信息源
            </button>
          </div>
        )}
      </div>

      {(showAddDialog || editingSource) && (
        <SourceEditor
          source={editingSource || undefined}
          onClose={() => {
            setShowAddDialog(false)
            setEditingSource(null)
          }}
        />
      )}
    </>
  )
}
