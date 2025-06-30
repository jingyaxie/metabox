import React, { useState, useEffect } from 'react'
import apiClient from '../services/api'
import AgentPanel from '../components/AgentPanel'

interface Plugin {
  name: string
  description: string
  version: string
  author: string
  enabled: boolean
  created_at: string
}

interface PluginDetail {
  name: string
  description: string
  version: string
  author: string
  enabled: boolean
  parameters: Record<string, any>
}

type TabType = 'plugins' | 'agent'

const Plugins: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('plugins')
  const [plugins, setPlugins] = useState<Plugin[]>([])
  const [selectedPlugin, setSelectedPlugin] = useState<PluginDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showDetail, setShowDetail] = useState(false)
  const [executing, setExecuting] = useState<string | null>(null)
  const [executionResult, setExecutionResult] = useState<any>(null)

  // 获取插件列表
  const fetchPlugins = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/plugins/')
      setPlugins(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '获取插件列表失败')
    } finally {
      setLoading(false)
    }
  }

  // 获取插件详情
  const fetchPluginDetail = async (pluginName: string) => {
    try {
      const response = await apiClient.get(`/plugins/${pluginName}`)
      setSelectedPlugin(response.data.data)
      setShowDetail(true)
    } catch (err: any) {
      setError(err.response?.data?.detail || '获取插件详情失败')
    }
  }

  // 启用/禁用插件
  const togglePlugin = async (pluginName: string, enabled: boolean) => {
    try {
      const endpoint = enabled ? 'enable' : 'disable'
      await apiClient.post(`/plugins/${pluginName}/${endpoint}`)
      await fetchPlugins() // 刷新列表
    } catch (err: any) {
      setError(err.response?.data?.detail || '操作失败')
    }
  }

  // 执行插件
  const executePlugin = async (pluginName: string, parameters: Record<string, any> = {}) => {
    try {
      setExecuting(pluginName)
      const response = await apiClient.post(`/plugins/${pluginName}/execute`, {
        plugin_name: pluginName,
        parameters
      })
      setExecutionResult(response.data.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '执行插件失败')
    } finally {
      setExecuting(null)
    }
  }

  useEffect(() => {
    fetchPlugins()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* 头部 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">插件与Agent</h1>
          <p className="text-gray-600 mt-2">管理和配置系统插件，体验智能Agent多步推理</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="text-red-600">{error}</div>
          </div>
        )}

        {/* 标签页 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {[
                { id: 'plugins', name: '插件管理', icon: '🔌' },
                { id: 'agent', name: 'Agent推理', icon: '🤖' }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as TabType)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'plugins' && (
              <div>
                {/* 插件列表 */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {plugins.map(plugin => (
                    <div key={plugin.name} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                      <div className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">{plugin.name}</h3>
                            <p className="text-sm text-gray-600 mb-2">{plugin.description}</p>
                            <div className="flex items-center space-x-4 text-xs text-gray-500">
                              <span>版本: {plugin.version}</span>
                              <span>作者: {plugin.author}</span>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              plugin.enabled 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-gray-100 text-gray-800'
                            }`}>
                              {plugin.enabled ? '已启用' : '已禁用'}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => fetchPluginDetail(plugin.name)}
                              className="px-3 py-1 text-sm text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded"
                            >
                              详情
                            </button>
                            <button
                              onClick={() => executePlugin(plugin.name)}
                              disabled={!plugin.enabled || executing === plugin.name}
                              className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              {executing === plugin.name ? '执行中...' : '执行'}
                            </button>
                          </div>
                          <button
                            onClick={() => togglePlugin(plugin.name, !plugin.enabled)}
                            className={`px-3 py-1 text-sm rounded ${
                              plugin.enabled
                                ? 'text-red-600 hover:text-red-700 hover:bg-red-50'
                                : 'text-green-600 hover:text-green-700 hover:bg-green-50'
                            }`}
                          >
                            {plugin.enabled ? '禁用' : '启用'}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* 插件详情弹窗 */}
                {showDetail && selectedPlugin && (
                  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                      <div className="p-6">
                        <div className="flex items-center justify-between mb-6">
                          <h2 className="text-xl font-semibold">{selectedPlugin.name}</h2>
                          <button
                            onClick={() => setShowDetail(false)}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            ✕
                          </button>
                        </div>

                        <div className="space-y-6">
                          {/* 基本信息 */}
                          <div>
                            <h3 className="text-lg font-medium mb-3">基本信息</h3>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <span className="text-gray-500">描述:</span>
                                <p className="text-gray-900 mt-1">{selectedPlugin.description}</p>
                              </div>
                              <div>
                                <span className="text-gray-500">版本:</span>
                                <p className="text-gray-900 mt-1">{selectedPlugin.version}</p>
                              </div>
                              <div>
                                <span className="text-gray-500">作者:</span>
                                <p className="text-gray-900 mt-1">{selectedPlugin.author}</p>
                              </div>
                              <div>
                                <span className="text-gray-500">状态:</span>
                                <p className="text-gray-900 mt-1">
                                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                    selectedPlugin.enabled 
                                      ? 'bg-green-100 text-green-800' 
                                      : 'bg-gray-100 text-gray-800'
                                  }`}>
                                    {selectedPlugin.enabled ? '已启用' : '已禁用'}
                                  </span>
                                </p>
                              </div>
                            </div>
                          </div>

                          {/* 参数配置 */}
                          {Object.keys(selectedPlugin.parameters).length > 0 && (
                            <div>
                              <h3 className="text-lg font-medium mb-3">参数配置</h3>
                              <div className="bg-gray-50 rounded-lg p-4">
                                <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                                  {JSON.stringify(selectedPlugin.parameters, null, 2)}
                                </pre>
                              </div>
                            </div>
                          )}

                          {/* 执行结果 */}
                          {executionResult && (
                            <div>
                              <h3 className="text-lg font-medium mb-3">执行结果</h3>
                              <div className="bg-gray-50 rounded-lg p-4">
                                <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                                  {JSON.stringify(executionResult, null, 2)}
                                </pre>
                              </div>
                            </div>
                          )}

                          {/* 操作按钮 */}
                          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                            <button
                              onClick={() => setShowDetail(false)}
                              className="px-4 py-2 text-gray-600 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
                            >
                              关闭
                            </button>
                            <button
                              onClick={() => executePlugin(selectedPlugin.name)}
                              disabled={!selectedPlugin.enabled || executing === selectedPlugin.name}
                              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              {executing === selectedPlugin.name ? '执行中...' : '执行插件'}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'agent' && (
              <AgentPanel />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Plugins 