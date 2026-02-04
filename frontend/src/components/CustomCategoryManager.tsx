/**
 * 自定义分类管理组件
 */

import { useState, useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import type { CustomCategory, Source } from '@/types/api'
import { Plus, Edit2, Trash2, ChevronDown, ChevronRight, Save, X, Search } from 'lucide-react'

export function CustomCategoryManager() {
  const queryClient = useQueryClient()
  const [isEditorOpen, setIsEditorOpen] = useState(false)
  const [editingCategory, setEditingCategory] = useState<CustomCategory | null>(null)
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set())

  // 获取自定义分类列表
  const { data: categories = [], isLoading } = useQuery({
    queryKey: ['customCategories'],
    queryFn: () => api.getCustomCategories(),
  })

  // 获取所有信息源
  const { data: allSources = [] } = useQuery({
    queryKey: ['sources'],
    queryFn: () => api.getSources(),
  })

  // 删除分类
  const deleteMutation = useMutation({
    mutationFn: api.deleteCustomCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customCategories'] })
    },
  })

  const handleAddCategory = () => {
    setEditingCategory(null)
    setIsEditorOpen(true)
  }

  const handleEditCategory = (category: CustomCategory) => {
    setEditingCategory(category)
    setIsEditorOpen(true)
  }

  const handleDeleteCategory = async (id: string) => {
    if (confirm('确定要删除这个自定义分类吗？')) {
      await deleteMutation.mutateAsync(id)
    }
  }

  const toggleExpand = (id: string) => {
    const newExpanded = new Set(expandedCategories)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedCategories(newExpanded)
  }

  const enabledCount = useMemo(() => categories.filter(c => c.enabled).length, [categories])
  const disabledCount = useMemo(() => categories.filter(c => !c.enabled).length, [categories])

  if (isLoading) {
    return <div className="text-gray-600">加载中...</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">自定义分类管理</h3>
          <p className="text-sm text-gray-600 mt-1">
            共 {categories.length} 个分类，{enabledCount} 个启用，{disabledCount} 个禁用
          </p>
        </div>
        <button
          onClick={handleAddCategory}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          添加分类
        </button>
      </div>

      {categories.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          暂无自定义分类，点击"添加分类"创建第一个分类
        </div>
      ) : (
        <div className="space-y-3">
          {categories.map(category => (
            <CategoryItem
              key={category.id}
              category={category}
              allSources={allSources}
              isExpanded={expandedCategories.has(category.id!)}
              onToggleExpand={() => toggleExpand(category.id!)}
              onEdit={() => handleEditCategory(category)}
              onDelete={() => handleDeleteCategory(category.id!)}
            />
          ))}
        </div>
      )}

      {isEditorOpen && (
        <CategoryEditor
          category={editingCategory}
          allSources={allSources}
          onClose={() => setIsEditorOpen(false)}
          onSuccess={() => {
            setIsEditorOpen(false)
            queryClient.invalidateQueries({ queryKey: ['customCategories'] })
          }}
        />
      )}
    </div>
  )
}

interface CategoryItemProps {
  category: CustomCategory
  allSources: Source[]
  isExpanded: boolean
  onToggleExpand: () => void
  onEdit: () => void
  onDelete: () => void
}

function CategoryItem({
  category,
  allSources,
  isExpanded,
  onToggleExpand,
  onEdit,
  onDelete,
}: CategoryItemProps) {
  const categorySources = useMemo(
    () => allSources.filter(s => category.source_ids.includes(s.id!)),
    [allSources, category.source_ids]
  )

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <button
                onClick={onToggleExpand}
                className="text-gray-500 hover:text-gray-700 transition-colors"
              >
                {isExpanded ? (
                  <ChevronDown className="w-5 h-5" />
                ) : (
                  <ChevronRight className="w-5 h-5" />
                )}
              </button>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-gray-900">{category.name}</h4>
                  <span
                    className={`px-2 py-0.5 text-xs rounded-full ${
                      category.enabled
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {category.enabled ? '启用' : '禁用'}
                  </span>
                </div>
                {category.description && (
                  <p className="text-sm text-gray-600 mt-1">{category.description}</p>
                )}
                <p className="text-sm text-gray-500 mt-1">
                  关联 {categorySources.length} 个信息源
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onEdit}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="编辑"
            >
              <Edit2 className="w-4 h-4" />
            </button>
            <button
              onClick={onDelete}
              className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="删除"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {isExpanded && (
          <div className="mt-4 pl-8 space-y-3">
            <div>
              <h5 className="text-sm font-medium text-gray-700 mb-2">自定义 Prompt</h5>
              <div className="bg-gray-50 p-3 rounded-lg text-sm text-gray-700 whitespace-pre-wrap">
                {category.custom_prompt}
              </div>
            </div>

            {categorySources.length > 0 && (
              <div>
                <h5 className="text-sm font-medium text-gray-700 mb-2">关联的信息源</h5>
                <div className="space-y-2">
                  {categorySources.map(source => (
                    <div
                      key={source.id}
                      className="flex items-center justify-between bg-gray-50 p-2 rounded-lg"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-gray-900">{source.name}</span>
                          <span
                            className={`px-2 py-0.5 text-xs rounded-full ${
                              source.enabled
                                ? 'bg-green-100 text-green-700'
                                : 'bg-gray-100 text-gray-600'
                            }`}
                          >
                            {source.enabled ? '启用' : '禁用'}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">{source.url}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

interface CategoryEditorProps {
  category: CustomCategory | null
  allSources: Source[]
  onClose: () => void
  onSuccess: () => void
}

function CategoryEditor({ category, allSources, onClose, onSuccess }: CategoryEditorProps) {
  const [formData, setFormData] = useState({
    name: category?.name || '',
    description: category?.description || '',
    custom_prompt: category?.custom_prompt || '',
    source_ids: category?.source_ids || [],
    enabled: category?.enabled ?? true,
  })

  // 搜索和筛选状态
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedIndustry, setSelectedIndustry] = useState<string>('all')
  const [showEnabledOnly, setShowEnabledOnly] = useState(false)

  const createMutation = useMutation({
    mutationFn: api.createCustomCategory,
    onSuccess,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => api.updateCustomCategory(id, data),
    onSuccess,
  })

  // 过滤后的信息源列表
  const filteredSources = useMemo(() => {
    let filtered = allSources

    // 按启用状态筛选
    if (showEnabledOnly) {
      filtered = filtered.filter(s => s.enabled)
    }

    // 按行业筛选
    if (selectedIndustry !== 'all') {
      filtered = filtered.filter(s => s.industry === selectedIndustry)
    }

    // 模糊搜索（搜索名称和URL）
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        s =>
          s.name.toLowerCase().includes(query) ||
          s.url.toLowerCase().includes(query)
      )
    }

    return filtered
  }, [allSources, searchQuery, selectedIndustry, showEnabledOnly])

  // 获取所有行业分类
  const industries = useMemo(() => {
    const uniqueIndustries = new Set(allSources.map(s => s.industry))
    return Array.from(uniqueIndustries).sort()
  }, [allSources])

  // 行业分类中文映射
  const industryLabels: Record<string, string> = {
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
    other: '其他',
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (formData.name.trim().length === 0) {
      alert('请输入分类名称')
      return
    }

    if (formData.custom_prompt.trim().length < 10) {
      alert('自定义 Prompt 至少需要 10 个字符')
      return
    }

    try {
      if (category?.id) {
        await updateMutation.mutateAsync({ id: category.id, data: formData })
      } else {
        await createMutation.mutateAsync(formData)
      }
    } catch (error) {
      alert('操作失败，请重试')
    }
  }

  const toggleSource = (sourceId: string) => {
    const newSourceIds = formData.source_ids.includes(sourceId)
      ? formData.source_ids.filter(id => id !== sourceId)
      : [...formData.source_ids, sourceId]
    setFormData({ ...formData, source_ids: newSourceIds })
  }

  const selectAllFiltered = () => {
    const newSourceIds = new Set(formData.source_ids)
    filteredSources.forEach(source => {
      if (source.id) newSourceIds.add(source.id)
    })
    setFormData({ ...formData, source_ids: Array.from(newSourceIds) })
  }

  const deselectAllFiltered = () => {
    const filteredIds = new Set(filteredSources.map(s => s.id))
    const newSourceIds = formData.source_ids.filter(id => !filteredIds.has(id))
    setFormData({ ...formData, source_ids: newSourceIds })
  }

  const isSubmitting = createMutation.isPending || updateMutation.isPending

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 flex justify-between items-center sticky top-0 bg-white">
          <h3 className="text-xl font-semibold text-gray-900">
            {category ? '编辑分类' : '添加分类'}
          </h3>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              分类名称 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={e => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="例如：加密货币深度分析"
              maxLength={100}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">分类描述</label>
            <input
              type="text"
              value={formData.description}
              onChange={e => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="简要描述这个分类的用途"
              maxLength={500}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              自定义 Prompt <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.custom_prompt}
              onChange={e => setFormData({ ...formData, custom_prompt: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              placeholder="请输入分析时使用的自定义 Prompt，例如：&#10;请从以下角度分析：&#10;1. 技术创新与突破&#10;2. 市场趋势与价格走势&#10;3. 监管政策影响&#10;4. 投资机会与风险"
              rows={8}
              required
              minLength={10}
            />
            <p className="text-xs text-gray-500 mt-1">
              最少 10 个字符，这将用于指导 AI 分析的重点方向
            </p>
          </div>

          <div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.enabled}
                onChange={e => setFormData({ ...formData, enabled: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">启用此分类</span>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              关联信息源（已选 {formData.source_ids.length} 个）
            </label>

            {/* 搜索和筛选工具栏 */}
            <div className="space-y-3 mb-3">
              {/* 搜索框 */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  placeholder="搜索信息源名称或URL..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
              </div>

              {/* 筛选器 */}
              <div className="flex gap-2 items-center flex-wrap">
                <select
                  value={selectedIndustry}
                  onChange={e => setSelectedIndustry(e.target.value)}
                  className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">所有行业</option>
                  {industries.map(industry => (
                    <option key={industry} value={industry}>
                      {industryLabels[industry] || industry}
                    </option>
                  ))}
                </select>

                <label className="flex items-center gap-1.5 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={showEnabledOnly}
                    onChange={e => setShowEnabledOnly(e.target.checked)}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  仅显示启用的
                </label>

                <div className="flex-1"></div>

                {/* 批量操作 */}
                {filteredSources.length > 0 && (
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={selectAllFiltered}
                      className="px-3 py-1.5 text-xs text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                    >
                      全选当前
                    </button>
                    <button
                      type="button"
                      onClick={deselectAllFiltered}
                      className="px-3 py-1.5 text-xs text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                    >
                      取消当前
                    </button>
                  </div>
                )}
              </div>

              {/* 结果统计 */}
              <div className="text-xs text-gray-500">
                显示 {filteredSources.length} / {allSources.length} 个信息源
                {searchQuery && ` · 搜索: "${searchQuery}"`}
                {selectedIndustry !== 'all' && ` · ${industryLabels[selectedIndustry] || selectedIndustry}`}
                {showEnabledOnly && ' · 仅启用'}
              </div>
            </div>

            {/* 信息源列表 */}
            <div className="border border-gray-300 rounded-lg max-h-64 overflow-y-auto">
              {allSources.length === 0 ? (
                <div className="p-4 text-center text-gray-500">暂无可用信息源</div>
              ) : filteredSources.length === 0 ? (
                <div className="p-4 text-center text-gray-500">
                  <p className="mb-1">未找到匹配的信息源</p>
                  <button
                    type="button"
                    onClick={() => {
                      setSearchQuery('')
                      setSelectedIndustry('all')
                      setShowEnabledOnly(false)
                    }}
                    className="text-blue-600 text-sm hover:underline"
                  >
                    清除筛选条件
                  </button>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {filteredSources.map(source => (
                    <label
                      key={source.id}
                      className="flex items-start gap-3 p-3 hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={formData.source_ids.includes(source.id!)}
                        onChange={() => toggleSource(source.id!)}
                        className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-gray-900">{source.name}</span>
                          <span
                            className={`px-2 py-0.5 text-xs rounded-full ${
                              source.enabled
                                ? 'bg-green-100 text-green-700'
                                : 'bg-gray-100 text-gray-600'
                            }`}
                          >
                            {source.enabled ? '启用' : '禁用'}
                          </span>
                          <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded-full">
                            {industryLabels[source.industry] || source.industry}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5 truncate">{source.url}</p>
                      </div>
                    </label>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              disabled={isSubmitting}
            >
              取消
            </button>
            <button
              type="submit"
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isSubmitting}
            >
              <Save className="w-4 h-4" />
              {isSubmitting ? '保存中...' : '保存'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
