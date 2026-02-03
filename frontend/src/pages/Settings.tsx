import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Key, Eye, EyeOff, Check, X, Edit, Trash2, Globe } from 'lucide-react'
import { api } from '@/services/api'
import SourceManager from '@/components/SourceManager'
import { CustomCategoryManager } from '@/components/CustomCategoryManager'

export default function SettingsPage() {
  const { data: sources, isLoading } = useQuery({
    queryKey: ['sources'],
    queryFn: () => api.getSources({ enabled_only: false }),
  })

  if (isLoading) {
    return <div className="p-8 text-center">加载中...</div>
  }

  return (
    <div className="p-4 md:p-8">
      <div className="mb-6 md:mb-8">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">设置</h1>
      </div>

      {/* 代理配置 */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">网络代理配置</h2>
        <ProxyConfigManager />
      </section>

      {/* API Key 管理 */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">LLM API Key 配置</h2>
        <APIKeyManager />
      </section>

      {/* 自定义分类管理 */}
      <section className="mb-12">
        <CustomCategoryManager />
      </section>

      {/* 信息源管理 */}
      <section className="mb-12">
        <SourceManager sources={sources || []} />
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

function ProxyConfigManager() {
  const [isEditing, setIsEditing] = useState(false)
  const [config, setConfig] = useState({
    enabled: false,
    host: '',
    port: 0,
    protocol: 'http',
  })
  const queryClient = useQueryClient()

  const { data: proxyConfig } = useQuery({
    queryKey: ['proxy-config'],
    queryFn: () => api.getProxyConfig(),
  })

  const setProxyMutation = useMutation({
    mutationFn: (config: any) => api.setProxyConfig(config),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['proxy-config'] })
      setIsEditing(false)
      alert(data.message || '代理配置已保存')
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || '代理配置保存失败')
    },
  })

  const deleteProxyMutation = useMutation({
    mutationFn: () => api.deleteProxyConfig(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['proxy-config'] })
      alert(data.message || '代理配置已禁用')
    },
  })

  const handleEdit = () => {
    setConfig({
      enabled: proxyConfig?.enabled || false,
      host: proxyConfig?.host || '',
      port: proxyConfig?.port || 0,
      protocol: proxyConfig?.protocol || 'http',
    })
    setIsEditing(true)
  }

  const handleSave = () => {
    if (config.enabled && (!config.host || config.port <= 0)) {
      alert('请输入有效的代理地址和端口')
      return
    }
    setProxyMutation.mutate(config)
  }

  const handleCancel = () => {
    setIsEditing(false)
    setConfig({
      enabled: false,
      host: '',
      port: 0,
      protocol: 'http',
    })
  }

  const handleDisable = () => {
    if (confirm('确定要禁用代理配置吗？')) {
      deleteProxyMutation.mutate()
    }
  }

  const isConfigured = proxyConfig?.enabled && proxyConfig?.host

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <Globe size={24} className="text-gray-400" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">HTTP/SOCKS5 代理</h3>
            <p className="text-sm text-gray-600 mt-1">
              配置网络代理以访问RSS源和AI API（适用于受限网络环境）
            </p>
          </div>
          {isConfigured && !isEditing && (
            <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">
              已启用
            </span>
          )}
        </div>
      </div>

      {isEditing ? (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="proxy-enabled"
              checked={config.enabled}
              onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
              className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
            <label htmlFor="proxy-enabled" className="text-sm font-medium text-gray-700">
              启用代理
            </label>
          </div>

          {config.enabled && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  代理协议
                </label>
                <select
                  value={config.protocol}
                  onChange={(e) => setConfig({ ...config, protocol: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="http">HTTP</option>
                  <option value="socks5">SOCKS5</option>
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    代理地址
                  </label>
                  <input
                    type="text"
                    value={config.host}
                    onChange={(e) => setConfig({ ...config, host: e.target.value })}
                    placeholder="例如: 127.0.0.1 或 proxy.example.com"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    端口
                  </label>
                  <input
                    type="number"
                    value={config.port || ''}
                    onChange={(e) => setConfig({ ...config, port: parseInt(e.target.value) || 0 })}
                    placeholder="例如: 7890"
                    min="1"
                    max="65535"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </>
          )}

          <div className="flex gap-2 pt-2">
            <button
              onClick={handleSave}
              disabled={setProxyMutation.isPending}
              className="flex items-center gap-1 px-4 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50"
            >
              <Check size={16} />
              保存
            </button>
            <button
              onClick={handleCancel}
              className="flex items-center gap-1 px-4 py-2 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
            >
              <X size={16} />
              取消
            </button>
          </div>
        </div>
      ) : (
        <div>
          {isConfigured ? (
            <div className="space-y-3">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 md:gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">协议:</span>
                    <span className="ml-2 font-medium text-gray-900 uppercase">
                      {proxyConfig.protocol}
                    </span>
                  </div>
                  <div className="truncate">
                    <span className="text-gray-500">地址:</span>
                    <span className="ml-2 font-medium text-gray-900">{proxyConfig.host}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">端口:</span>
                    <span className="ml-2 font-medium text-gray-900">{proxyConfig.port}</span>
                  </div>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-2">
                <button
                  onClick={handleEdit}
                  className="flex items-center justify-center gap-1 px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                >
                  <Edit size={16} />
                  修改
                </button>
                <button
                  onClick={handleDisable}
                  className="flex items-center justify-center gap-1 px-4 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                >
                  <Trash2 size={16} />
                  禁用
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-gray-500 mb-4">未配置代理</p>
              <button
                onClick={handleEdit}
                className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
              >
                配置代理
              </button>
            </div>
          )}
        </div>
      )}

      <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>提示</strong>：配置代理后，所有RSS拉取和AI API调用都将通过代理服务器。
          支持HTTP和SOCKS5协议。常见代理工具：Clash (7890端口)、V2Ray等。
        </p>
      </div>
    </div>
  )
}

function APIKeyManager() {
  const [editingBackend, setEditingBackend] = useState<string | null>(null)
  const [apiKeyValues, setApiKeyValues] = useState<Record<string, string>>({})
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({})
  const queryClient = useQueryClient()

  const { data: apiKeys } = useQuery({
    queryKey: ['api-keys'],
    queryFn: () => api.getAPIKeys(),
  })

  const { data: backends } = useQuery({
    queryKey: ['llm-backends'],
    queryFn: () => api.getLLMBackends(),
  })

  const setKeyMutation = useMutation({
    mutationFn: ({ backend, apiKey }: { backend: string; apiKey: string }) =>
      api.setAPIKey(backend, apiKey),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      setEditingBackend(null)
      setApiKeyValues({})
      alert(data.message || 'API Key 保存成功')
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || 'API Key 保存失败')
    },
  })

  const deleteKeyMutation = useMutation({
    mutationFn: (backend: string) => api.deleteAPIKey(backend),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      alert(data.message || 'API Key 已删除')
    },
  })

  const handleSave = (backend: string) => {
    const apiKey = apiKeyValues[backend]
    if (!apiKey || apiKey.length < 10) {
      alert('请输入有效的 API Key')
      return
    }
    setKeyMutation.mutate({ backend, apiKey })
  }

  const handleCancel = (backend: string) => {
    setEditingBackend(null)
    setApiKeyValues({ ...apiKeyValues, [backend]: '' })
  }

  const toggleShowKey = (backend: string) => {
    setShowKeys({ ...showKeys, [backend]: !showKeys[backend] })
  }

  const needsKeyBackends = backends?.backends?.filter((b: any) => b.requires_api_key) || []

  return (
    <div className="space-y-4">
      {needsKeyBackends.map((backend: any) => {
        const keyInfo = apiKeys?.api_keys?.find((k: any) => k.backend === backend.id)
        const isEditing = editingBackend === backend.id
        const hasKey = keyInfo?.has_key

        return (
          <div key={backend.id} className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <Key size={20} className="text-gray-400" />
                  <h3 className="text-lg font-semibold text-gray-900">{backend.name}</h3>
                  {hasKey && !isEditing && (
                    <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">
                      已配置
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-3">{backend.description}</p>

                {isEditing ? (
                  <div className="space-y-3">
                    <div className="relative">
                      <input
                        type={showKeys[backend.id] ? 'text' : 'password'}
                        value={apiKeyValues[backend.id] || ''}
                        onChange={(e) =>
                          setApiKeyValues({ ...apiKeyValues, [backend.id]: e.target.value })
                        }
                        placeholder={`输入 ${backend.name} API Key`}
                        className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <button
                        onClick={() => toggleShowKey(backend.id)}
                        className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600"
                      >
                        {showKeys[backend.id] ? <EyeOff size={18} /> : <Eye size={18} />}
                      </button>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleSave(backend.id)}
                        disabled={setKeyMutation.isPending}
                        className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50"
                      >
                        <Check size={16} />
                        保存
                      </button>
                      <button
                        onClick={() => handleCancel(backend.id)}
                        className="flex items-center gap-1 px-3 py-1.5 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
                      >
                        <X size={16} />
                        取消
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-4">
                    {hasKey && (
                      <code className="text-sm text-gray-600 bg-gray-50 px-3 py-1 rounded">
                        {keyInfo.masked_key}
                      </code>
                    )}
                    <button
                      onClick={() => {
                        setEditingBackend(backend.id)
                        setApiKeyValues({ ...apiKeyValues, [backend.id]: '' })
                      }}
                      className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                    >
                      <Edit size={16} />
                      {hasKey ? '修改' : '配置'}
                    </button>
                    {hasKey && (
                      <button
                        onClick={() => {
                          if (confirm(`确定要删除 ${backend.name} 的 API Key 吗？`)) {
                            deleteKeyMutation.mutate(backend.id)
                          }
                        }}
                        className="flex items-center gap-1 px-3 py-1.5 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                      >
                        <Trash2 size={16} />
                        删除
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )
      })}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>提示</strong>：API Key 将加密存储在本地数据库中。Ollama 本地模型无需配置 API Key。
        </p>
      </div>
    </div>
  )
}
