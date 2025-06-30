import React, { useState, useEffect } from 'react'
import apiClient from '../services/api'

interface SmartConfigPanelProps {
  docText: string
}

interface SmartConfig {
  detected_type: string
  confidence: number
  config: {
    splitter: string
    chunk_size: number
    chunk_overlap: number
    embedding_model: string
    use_parent_child: boolean
    [key: string]: any
  }
  errors?: string[]
  valid?: boolean
}

const splitterOptions = [
  { value: 'recursive', label: '递归分割' },
  { value: 'markdown_header', label: 'Markdown标题分割' },
  { value: 'semantic', label: '语义分割' }
]

const SmartConfigPanel: React.FC<SmartConfigPanelProps> = ({ docText }) => {
  const [config, setConfig] = useState<SmartConfig | null>(null)
  const [customConfig, setCustomConfig] = useState<any>({})
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (docText) fetchSmartConfig()
    // eslint-disable-next-line
  }, [docText])

  const fetchSmartConfig = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await apiClient.post('/kb/smart-config', { text: docText })
      setConfig(res.data)
      setCustomConfig({ ...res.data.config })
    } catch (e: any) {
      setError('智能推荐失败')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (key: string, value: any) => {
    setCustomConfig((prev: any) => ({ ...prev, [key]: value }))
  }

  const handleValidate = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await apiClient.post('/kb/smart-config', { text: docText, user_preferences: customConfig })
      setConfig(res.data)
    } catch (e: any) {
      setError('参数验证失败')
    } finally {
      setLoading(false)
    }
  }

  if (!docText) return <div className="text-gray-400">请先上传或粘贴文档内容</div>
  if (loading) return <div className="text-blue-500 animate-pulse">智能分析中...</div>
  if (error) return <div className="text-red-500">{error}</div>
  if (!config) return null

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <span className="text-sm text-gray-500">检测类型：</span>
          <span className="font-bold text-primary-600 mr-2">{config.detected_type}</span>
          <span className="text-xs text-gray-400">置信度 {config.confidence?.toFixed(1)}%</span>
        </div>
        <button
          className="text-xs text-blue-500 hover:underline"
          onClick={() => setShowAdvanced(v => !v)}
        >
          {showAdvanced ? '收起高级' : '高级配置'}
        </button>
      </div>
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">分割方式</label>
            <select
              className="w-full border rounded px-3 py-2"
              value={customConfig.splitter}
              onChange={e => handleChange('splitter', e.target.value)}
              disabled={!showAdvanced}
            >
              {splitterOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Embedding模型</label>
            <input
              className="w-full border rounded px-3 py-2"
              value={customConfig.embedding_model || ''}
              onChange={e => handleChange('embedding_model', e.target.value)}
              disabled={!showAdvanced}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">分块大小</label>
            <input
              type="number"
              className="w-full border rounded px-3 py-2"
              value={customConfig.chunk_size || ''}
              onChange={e => handleChange('chunk_size', Number(e.target.value))}
              disabled={!showAdvanced}
              min={64}
              max={2048}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">重叠大小</label>
            <input
              type="number"
              className="w-full border rounded px-3 py-2"
              value={customConfig.chunk_overlap || ''}
              onChange={e => handleChange('chunk_overlap', Number(e.target.value))}
              disabled={!showAdvanced}
              min={0}
              max={512}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">父子块分割</label>
            <input
              type="checkbox"
              checked={!!customConfig.use_parent_child}
              onChange={e => handleChange('use_parent_child', e.target.checked)}
              disabled={!showAdvanced}
            />
          </div>
        </div>
        {showAdvanced && (
          <div className="bg-gray-50 rounded p-4 mt-2">
            <div className="text-xs text-gray-500 mb-2">高级参数（如分隔符、header层级、语义阈值等）</div>
            {/* 可扩展更多高级参数 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1">分隔符</label>
                <input
                  className="w-full border rounded px-2 py-1"
                  value={customConfig.separators?.join(',') || ''}
                  onChange={e => handleChange('separators', e.target.value.split(','))}
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">header层级</label>
                <input
                  className="w-full border rounded px-2 py-1"
                  value={customConfig.header_levels?.join(',') || ''}
                  onChange={e => handleChange('header_levels', e.target.value.split(',').map(Number))}
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">语义阈值</label>
                <input
                  type="number"
                  className="w-full border rounded px-2 py-1"
                  value={customConfig.semantic_threshold || ''}
                  onChange={e => handleChange('semantic_threshold', Number(e.target.value))}
                  min={0}
                  max={1}
                  step={0.01}
                />
              </div>
            </div>
          </div>
        )}
        <div className="flex items-center space-x-4 mt-4">
          <button
            className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
            onClick={handleValidate}
            disabled={loading}
          >
            验证参数
          </button>
          {config.errors && (
            <span className="text-red-500 text-sm">{config.errors.join('，')}</span>
          )}
          {config.valid && (
            <span className="text-green-600 text-sm">参数有效</span>
          )}
        </div>
      </div>
    </div>
  )
}

export default SmartConfigPanel 