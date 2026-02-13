import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Key, Eye, EyeOff, Check, X, Edit, Trash2, Globe, Wifi, Loader2 } from 'lucide-react'
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
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">设置</h1>
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
    http_proxy: '',
    https_proxy: '',
    socks5_proxy: '',
  })
  const [testResult, setTestResult] = useState<any>(null)
  const [isTesting, setIsTesting] = useState(false)
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
      setTestResult(null)
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
      setTestResult(null)
      alert(data.message || '代理配置已禁用')
    },
  })

  const handleEdit = () => {
    setConfig({
      enabled: proxyConfig?.enabled || false,
      http_proxy: proxyConfig?.http || '',
      https_proxy: proxyConfig?.https || '',
      socks5_proxy: proxyConfig?.socks5 || '',
    })
    setIsEditing(true)
    setTestResult(null)
  }

  const handleSave = () => {
    if (config.enabled && !config.http_proxy && !config.https_proxy && !config.socks5_proxy) {
      alert('请至少配置一个代理地址 (HTTP, HTTPS, 或 SOCKS5)')
      return
    }
    setProxyMutation.mutate(config)
  }

  const handleCancel = () => {
    setIsEditing(false)
    setTestResult(null)
    setConfig({
      enabled: false,
      http_proxy: '',
      https_proxy: '',
      socks5_proxy: '',
    })
  }

  const handleDisable = () => {
    if (confirm('确定要禁用代理配置吗？')) {
      deleteProxyMutation.mutate()
    }
  }

  const handleTest = async (testConfig?: typeof config) => {
    const configToTest = testConfig || config
    if (!configToTest.http_proxy && !configToTest.https_proxy && !configToTest.socks5_proxy) {
      alert('请至少填写一个代理地址后再测试')
      return
    }
    setIsTesting(true)
    setTestResult(null)
    try {
      const result = await api.testProxyConfig({
        enabled: true,
        http_proxy: configToTest.http_proxy,
        https_proxy: configToTest.https_proxy,
        socks5_proxy: configToTest.socks5_proxy,
      })
      setTestResult(result)
    } catch (error: any) {
      setTestResult({
        success: false,
        message: error.response?.data?.detail || '测试请求失败，请检查后端服务',
        results: [],
      })
    } finally {
      setIsTesting(false)
    }
  }

  const isConfigured = proxyConfig?.enabled && (proxyConfig?.http || proxyConfig?.https || proxyConfig?.socks5)

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <Globe size={24} className="text-gray-400" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">网络代理配置</h3>
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
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    HTTP 代理
                  </label>
                  <input
                    type="text"
                    value={config.http_proxy}
                    onChange={(e) => setConfig({ ...config, http_proxy: e.target.value })}
                    placeholder="例如: http://127.0.0.1:7897"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    HTTPS 代理
                  </label>
                  <input
                    type="text"
                    value={config.https_proxy}
                    onChange={(e) => setConfig({ ...config, https_proxy: e.target.value })}
                    placeholder="留空则复用 HTTP 代理"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    SOCKS5 代理
                  </label>
                  <input
                    type="text"
                    value={config.socks5_proxy}
                    onChange={(e) => setConfig({ ...config, socks5_proxy: e.target.value })}
                    placeholder="例如: socks5://127.0.0.1:1080"
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
            {config.enabled && (
              <button
                onClick={() => handleTest()}
                disabled={isTesting}
                className="flex items-center gap-1 px-4 py-2 bg-orange-500 text-white text-sm rounded hover:bg-orange-600 disabled:opacity-50"
              >
                {isTesting ? <Loader2 size={16} className="animate-spin" /> : <Wifi size={16} />}
                {isTesting ? '测试中...' : '测试连接'}
              </button>
            )}
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
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">HTTP 代理:</span>
                    <span className="ml-2 font-medium text-gray-900">
                      {proxyConfig.http ? proxyConfig.http : '未配置'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">HTTPS 代理:</span>
                    <span className="ml-2 font-medium text-gray-900">
                      {proxyConfig.https ? proxyConfig.https : '未配置'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">SOCKS5 代理:</span>
                    <span className="ml-2 font-medium text-gray-900">
                      {proxyConfig.socks5 ? proxyConfig.socks5 : '未配置'}
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleEdit}
                  className="flex items-center gap-1 px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                >
                  <Edit size={16} />
                  修改
                </button>
                <button
                  onClick={() => handleTest({
                    enabled: true,
                    http_proxy: proxyConfig?.http || '',
                    https_proxy: proxyConfig?.https || '',
                    socks5_proxy: proxyConfig?.socks5 || '',
                  })}
                  disabled={isTesting}
                  className="flex items-center gap-1 px-4 py-2 bg-orange-500 text-white text-sm rounded hover:bg-orange-600 disabled:opacity-50"
                >
                  {isTesting ? <Loader2 size={16} className="animate-spin" /> : <Wifi size={16} />}
                  {isTesting ? '测试中...' : '测试连接'}
                </button>
                <button
                  onClick={handleDisable}
                  className="flex items-center gap-1 px-4 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700"
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

      {/* 代理测试结果 */}
      {testResult && (
        <div className={`mt-4 rounded-lg border p-4 ${
          testResult.success
            ? 'bg-green-50 border-green-200'
            : 'bg-red-50 border-red-200'
        }`}>
          <div className="flex items-center gap-2 mb-3">
            <Wifi size={18} className={testResult.success ? 'text-green-600' : 'text-red-600'} />
            <span className={`font-medium text-sm ${
              testResult.success ? 'text-green-800' : 'text-red-800'
            }`}>
              {testResult.message}
            </span>
          </div>
          {testResult.results && testResult.results.length > 0 && (
            <div className="space-y-2">
              {testResult.results.map((r: any, i: number) => (
                <div key={i} className="flex items-center justify-between text-sm bg-white rounded px-3 py-2 border border-gray-100">
                  <div className="flex items-center gap-2">
                    <span className={`inline-block w-2 h-2 rounded-full ${
                      r.success ? 'bg-green-500' : 'bg-red-500'
                    }`} />
                    <span className="font-medium text-gray-800">{r.name}</span>
                    <span className="text-gray-400 text-xs">{r.description}</span>
                  </div>
                  <div className="flex items-center gap-3 text-xs">
                    {r.proxy_ip && (
                      <span className="text-gray-500">
                        出口IP: <span className="font-mono text-gray-700">{r.proxy_ip}</span>
                      </span>
                    )}
                    {r.latency_ms != null && (
                      <span className={`font-mono ${
                        r.latency_ms < 1000 ? 'text-green-600' : r.latency_ms < 3000 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {r.latency_ms}ms
                      </span>
                    )}
                    {r.error && (
                      <span className="text-red-600 max-w-xs truncate" title={r.error}>
                        {r.error}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>提示</strong>：配置代理后，所有RSS拉取和AI API调用都将通过代理服务器。
          Clash 用户通常只需填写 HTTP 代理（如 http://127.0.0.1:7897），HTTPS 会自动复用。
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
