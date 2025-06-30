import React, { useState, useEffect } from 'react'
import { Card, Button, Input, Select, Slider, Switch, Tabs, message, Spin, Progress } from 'antd'
import { 
  SettingOutlined, 
  EyeOutlined, 
  SaveOutlined, 
  ReloadOutlined,
  ExperimentOutlined,
  BarChartOutlined,
  FileTextOutlined,
  RocketOutlined
} from '@ant-design/icons'
import { api } from '../services/api'

const { Option } = Select
const { TabPane } = Tabs
const { TextArea } = Input

interface SmartConfigPanelProps {
  content: string
  onConfigChange: (config: any) => void
  onApply: (config: any) => void
}

interface ConfigPreview {
  chunks: any[]
  performance: any
  suggestions: any[]
  hierarchy: any
  statistics: any
  quality_score: number
  preview_time: number
}

interface ConfigTemplate {
  id: string
  name: string
  description: string
  config: any
  created_at: string
}

const SmartConfigPanel: React.FC<SmartConfigPanelProps> = ({
  content,
  onConfigChange,
  onApply
}) => {
  const [loading, setLoading] = useState(false)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [config, setConfig] = useState({
    chunk_size: 512,
    chunk_overlap: 50,
    embedding_model: 'bge-m3',
    similarity_threshold: 0.7,
    max_tokens: 2000,
    use_hybrid: true,
    use_markdown: true
  })
  
  const [preview, setPreview] = useState<ConfigPreview | null>(null)
  const [templates, setTemplates] = useState<ConfigTemplate[]>([])
  const [activeTab, setActiveTab] = useState('config')

  // 获取智能配置推荐
  const getSmartConfig = async () => {
    if (!content.trim()) {
      message.warning('请先输入文档内容')
      return
    }

    setLoading(true)
    try {
      const response = await api.post('/kb/smart-config', {
        content: content,
        advanced_config: config
      })

      if (response.data.success) {
        const smartConfig = response.data.data
        setConfig(smartConfig.recommendations.recommended_config)
        setPreview(smartConfig.advanced_preview)
        onConfigChange(smartConfig.recommendations.recommended_config)
        message.success('智能配置生成成功')
      }
    } catch (error) {
      console.error('获取智能配置失败:', error)
      message.error('获取智能配置失败')
    } finally {
      setLoading(false)
    }
  }

  // 获取配置预览
  const getConfigPreview = async () => {
    if (!content.trim()) {
      message.warning('请先输入文档内容')
      return
    }

    setPreviewLoading(true)
    try {
      const response = await api.post('/kb/smart-config/preview', {
        content: content,
        config: config
      })

      if (response.data.success) {
        setPreview(response.data.data)
        message.success('配置预览生成成功')
      }
    } catch (error) {
      console.error('获取配置预览失败:', error)
      message.error('获取配置预览失败')
    } finally {
      setPreviewLoading(false)
    }
  }

  // 获取模板列表
  const getTemplates = async () => {
    try {
      const response = await api.get('/kb/smart-config/templates')
      if (response.data.success) {
        setTemplates(response.data.data)
      }
    } catch (error) {
      console.error('获取模板列表失败:', error)
    }
  }

  // 应用模板
  const applyTemplate = async (templateId: string) => {
    if (!content.trim()) {
      message.warning('请先输入文档内容')
      return
    }

    setLoading(true)
    try {
      const response = await api.post(`/kb/smart-config/templates/${templateId}/apply`, {
        content: content
      })

      if (response.data.success) {
        const smartConfig = response.data.data
        setConfig(smartConfig.recommendations.recommended_config)
        setPreview(smartConfig.advanced_preview)
        onConfigChange(smartConfig.recommendations.recommended_config)
        message.success('模板应用成功')
      }
    } catch (error) {
      console.error('应用模板失败:', error)
      message.error('应用模板失败')
    } finally {
      setLoading(false)
    }
  }

  // 保存为模板
  const saveAsTemplate = async () => {
    const templateName = prompt('请输入模板名称:')
    if (!templateName) return

    try {
      const response = await api.post('/kb/smart-config/templates', {
        name: templateName,
        description: '用户自定义配置模板',
        config: config
      })

      if (response.data.success) {
        message.success('模板保存成功')
        getTemplates()
      }
    } catch (error) {
      console.error('保存模板失败:', error)
      message.error('保存模板失败')
    }
  }

  // 应用配置
  const handleApply = () => {
    onApply(config)
    message.success('配置已应用')
  }

  useEffect(() => {
    getTemplates()
  }, [])

  const renderConfigTab = () => (
    <div className="space-y-4">
      <Card title="基础配置" size="small">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">分块大小</label>
            <Slider
              min={128}
              max={2048}
              step={64}
              value={config.chunk_size}
              onChange={(value) => setConfig({ ...config, chunk_size: value })}
              marks={{
                128: '128',
                512: '512',
                1024: '1024',
                2048: '2048'
              }}
            />
            <div className="text-xs text-gray-500 mt-1">
              当前值: {config.chunk_size} 字符
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">重叠大小</label>
            <Slider
              min={0}
              max={200}
              step={10}
              value={config.chunk_overlap}
              onChange={(value) => setConfig({ ...config, chunk_overlap: value })}
              marks={{
                0: '0',
                50: '50',
                100: '100',
                200: '200'
              }}
            />
            <div className="text-xs text-gray-500 mt-1">
              当前值: {config.chunk_overlap} 字符
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Embedding模型</label>
            <Select
              value={config.embedding_model}
              onChange={(value) => setConfig({ ...config, embedding_model: value })}
              className="w-full"
            >
              <Option value="bge-m3">BGE-M3 (本地)</Option>
              <Option value="text-embedding-3-small">OpenAI 3-Small</Option>
              <Option value="text-embedding-3-large">OpenAI 3-Large</Option>
              <Option value="gte-large">GTE-Large (本地)</Option>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">相似度阈值</label>
            <Slider
              min={0.1}
              max={1.0}
              step={0.05}
              value={config.similarity_threshold}
              onChange={(value) => setConfig({ ...config, similarity_threshold: value })}
              marks={{
                0.1: '0.1',
                0.5: '0.5',
                0.7: '0.7',
                1.0: '1.0'
              }}
            />
            <div className="text-xs text-gray-500 mt-1">
              当前值: {config.similarity_threshold}
            </div>
          </div>
        </div>
      </Card>

      <Card title="高级选项" size="small">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm">启用混合分块</span>
            <Switch
              checked={config.use_hybrid}
              onChange={(checked) => setConfig({ ...config, use_hybrid: checked })}
            />
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm">启用Markdown结构</span>
            <Switch
              checked={config.use_markdown}
              onChange={(checked) => setConfig({ ...config, use_markdown: checked })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">最大Token数</label>
            <Input
              type="number"
              value={config.max_tokens}
              onChange={(e) => setConfig({ ...config, max_tokens: parseInt(e.target.value) })}
              min={1000}
              max={8000}
              step={500}
            />
          </div>
        </div>
      </Card>

      <div className="flex space-x-2">
        <Button
          type="primary"
          icon={<ExperimentOutlined />}
          onClick={getSmartConfig}
          loading={loading}
          className="flex-1"
        >
          智能推荐
        </Button>
        <Button
          icon={<EyeOutlined />}
          onClick={getConfigPreview}
          loading={previewLoading}
          className="flex-1"
        >
          预览效果
        </Button>
        <Button
          icon={<SaveOutlined />}
          onClick={saveAsTemplate}
          className="flex-1"
        >
          保存模板
        </Button>
      </div>
    </div>
  )

  const renderPreviewTab = () => (
    <div className="space-y-4">
      {preview ? (
        <>
          <Card title="性能预估" size="small">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-500">总分块数</div>
                <div className="text-lg font-semibold">{preview.performance.total_chunks}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">总Token数</div>
                <div className="text-lg font-semibold">{preview.performance.total_tokens}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">预估成本</div>
                <div className="text-lg font-semibold">${preview.performance.embedding_cost.toFixed(4)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">处理时间</div>
                <div className="text-lg font-semibold">{preview.performance.processing_time_estimate.toFixed(1)}s</div>
              </div>
            </div>
          </Card>

          <Card title="质量评分" size="small">
            <div className="flex items-center space-x-4">
              <Progress
                type="circle"
                percent={Math.round(preview.quality_score * 100)}
                format={(percent) => `${percent}%`}
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
              />
              <div>
                <div className="text-sm text-gray-500">配置质量</div>
                <div className="text-lg font-semibold">
                  {preview.quality_score >= 0.8 ? '优秀' : 
                   preview.quality_score >= 0.6 ? '良好' : 
                   preview.quality_score >= 0.4 ? '一般' : '需要优化'}
                </div>
              </div>
            </div>
          </Card>

          <Card title="优化建议" size="small">
            {preview.suggestions.length > 0 ? (
              <div className="space-y-2">
                {preview.suggestions.map((suggestion, index) => (
                  <div key={index} className="p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className={`px-2 py-1 text-xs rounded ${
                        suggestion.impact === 'high' ? 'bg-red-100 text-red-800' :
                        suggestion.impact === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {suggestion.impact === 'high' ? '高' : 
                         suggestion.impact === 'medium' ? '中' : '低'}
                      </span>
                      <span className="font-medium">{suggestion.description}</span>
                    </div>
                    <div className="text-sm text-gray-600">{suggestion.reasoning}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-4">
                当前配置良好，无需优化
              </div>
            )}
          </Card>

          <Card title="分块统计" size="small">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-500">平均分块大小</div>
                <div className="text-lg font-semibold">{Math.round(preview.statistics.avg_size)} 字符</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">平均Token数</div>
                <div className="text-lg font-semibold">{Math.round(preview.statistics.avg_tokens)}</div>
              </div>
            </div>
          </Card>
        </>
      ) : (
        <div className="text-center py-8">
          <EyeOutlined className="text-4xl text-gray-300 mb-4" />
          <div className="text-gray-500">点击"预览效果"查看配置预览</div>
        </div>
      )}
    </div>
  )

  const renderTemplatesTab = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">配置模板</h3>
        <Button
          icon={<ReloadOutlined />}
          onClick={getTemplates}
          size="small"
        >
          刷新
        </Button>
      </div>

      {templates.length > 0 ? (
        <div className="space-y-2">
          {templates.map((template) => (
            <Card key={template.id} size="small" className="cursor-pointer hover:shadow-md">
              <div className="flex justify-between items-center">
                <div>
                  <div className="font-medium">{template.name}</div>
                  <div className="text-sm text-gray-500">{template.description}</div>
                  <div className="text-xs text-gray-400">
                    创建时间: {new Date(template.created_at).toLocaleDateString()}
                  </div>
                </div>
                <Button
                  type="primary"
                  size="small"
                  onClick={() => applyTemplate(template.id)}
                  loading={loading}
                >
                  应用
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <FileTextOutlined className="text-4xl text-gray-300 mb-4" />
          <div className="text-gray-500">暂无配置模板</div>
        </div>
      )}
    </div>
  )

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="p-4 border-b">
        <div className="flex items-center space-x-2">
          <SettingOutlined className="text-blue-500" />
          <h2 className="text-lg font-semibold">智能配置</h2>
        </div>
      </div>

      <div className="p-4">
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="配置参数" key="config">
            {renderConfigTab()}
          </TabPane>
          <TabPane tab="预览效果" key="preview">
            {renderPreviewTab()}
          </TabPane>
          <TabPane tab="配置模板" key="templates">
            {renderTemplatesTab()}
          </TabPane>
        </Tabs>

        <div className="mt-6 pt-4 border-t">
          <Button
            type="primary"
            size="large"
            icon={<RocketOutlined />}
            onClick={handleApply}
            className="w-full"
            loading={loading}
          >
            应用配置
          </Button>
        </div>
      </div>
    </div>
  )
}

export default SmartConfigPanel 