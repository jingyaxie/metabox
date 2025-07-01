import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import { Switch } from './ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'

import apiClient from '../services/api'

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

  // 获取智能配置推荐
  const getSmartConfig = async () => {
    if (!content.trim()) {
      alert('请先输入文档内容')
      return
    }

    setLoading(true)
    try {
      const response = await apiClient.post('/kb/smart-config', {
        content: content,
        advanced_config: config
      })

      if (response.data.success) {
        const smartConfig = response.data.data
        setConfig(smartConfig.recommendations.recommended_config)
        setPreview(smartConfig.advanced_preview)
        onConfigChange(smartConfig.recommendations.recommended_config)
        alert('智能配置生成成功')
      }
    } catch (error) {
      console.error('获取智能配置失败:', error)
      alert('获取智能配置失败')
    } finally {
      setLoading(false)
    }
  }

  // 获取配置预览
  const getConfigPreview = async () => {
    if (!content.trim()) {
      alert('请先输入文档内容')
      return
    }

    setPreviewLoading(true)
    try {
      const response = await apiClient.post('/kb/smart-config/preview', {
        content: content,
        config: config
      })

      if (response.data.success) {
        setPreview(response.data.data)
        alert('配置预览生成成功')
      }
    } catch (error) {
      console.error('获取配置预览失败:', error)
      alert('获取配置预览失败')
    } finally {
      setPreviewLoading(false)
    }
  }

  // 获取模板列表
  const getTemplates = async () => {
    try {
      const response = await apiClient.get('/kb/smart-config/templates')
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
      alert('请先输入文档内容')
      return
    }

    setLoading(true)
    try {
      const response = await apiClient.post(`/kb/smart-config/templates/${templateId}/apply`, {
        content: content
      })

      if (response.data.success) {
        const smartConfig = response.data.data
        setConfig(smartConfig.recommendations.recommended_config)
        setPreview(smartConfig.advanced_preview)
        onConfigChange(smartConfig.recommendations.recommended_config)
        alert('模板应用成功')
      }
    } catch (error) {
      console.error('应用模板失败:', error)
      alert('应用模板失败')
    } finally {
      setLoading(false)
    }
  }

  // 保存为模板
  const saveAsTemplate = async () => {
    const templateName = prompt('请输入模板名称:')
    if (!templateName) return

    try {
      const response = await apiClient.post('/kb/smart-config/templates', {
        name: templateName,
        description: '用户自定义配置模板',
        config: config
      })

      if (response.data.success) {
        alert('模板保存成功')
        getTemplates()
      }
    } catch (error) {
      console.error('保存模板失败:', error)
      alert('保存模板失败')
    }
  }

  // 应用配置
  const handleApply = () => {
    onApply(config)
    alert('配置已应用')
  }

  useEffect(() => {
    getTemplates()
  }, [])

  const renderConfigTab = () => (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>基础配置</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">分块大小</label>
            <Input 
              type="number" 
              min="128" 
              max="2048" 
              step="64"
              value={config.chunk_size}
              onChange={(e) => setConfig({...config, chunk_size: parseInt(e.target.value)})}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">分块重叠</label>
            <Input 
              type="number" 
              min="0" 
              max="200"
              value={config.chunk_overlap}
              onChange={(e) => setConfig({...config, chunk_overlap: parseInt(e.target.value)})}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">嵌入模型</label>
            <Select 
              value={config.embedding_model} 
              onValueChange={(value) => setConfig({...config, embedding_model: value})}
            >
              <SelectTrigger>
                <SelectValue>选择模型</SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="bge-m3">BGE-M3</SelectItem>
                <SelectItem value="text-embedding-3-small">OpenAI Text Embedding 3 Small</SelectItem>
                <SelectItem value="text-embedding-3-large">OpenAI Text Embedding 3 Large</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">相似度阈值</label>
            <Input 
              type="number" 
              min="0" 
              max="1" 
              step="0.1"
              value={config.similarity_threshold}
              onChange={(e) => setConfig({...config, similarity_threshold: parseFloat(e.target.value)})}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">最大Token数</label>
            <Input 
              type="number" 
              min="100" 
              max="8000"
              value={config.max_tokens}
              onChange={(e) => setConfig({...config, max_tokens: parseInt(e.target.value)})}
            />
          </div>

          <div className="flex items-center justify-between">
            <label className="block text-sm font-medium">混合检索</label>
            <Switch
              checked={config.use_hybrid}
              onCheckedChange={(checked) => setConfig({...config, use_hybrid: checked})}
            />
          </div>

          <div className="flex items-center justify-between">
            <label className="block text-sm font-medium">Markdown解析</label>
            <Switch
              checked={config.use_markdown}
              onCheckedChange={(checked) => setConfig({...config, use_markdown: checked})}
            />
          </div>
        </CardContent>
      </Card>

      <div className="flex space-x-2">
        <Button onClick={getSmartConfig} disabled={loading}>
          {loading ? '生成中...' : '生成智能配置'}
        </Button>
        <Button onClick={getConfigPreview} disabled={previewLoading}>
          {previewLoading ? '预览中...' : '配置预览'}
        </Button>
        <Button onClick={handleApply}>
          应用配置
        </Button>
      </div>
    </div>
  )

  const renderPreviewTab = () => (
    <div className="space-y-4">
      {preview ? (
        <>
          <Card>
            <CardHeader>
              <CardTitle>质量评分</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {preview.quality_score.toFixed(1)}/10
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>分块统计</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-600">总分块数</div>
                  <div className="text-lg font-semibold">{preview.chunks.length}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">平均长度</div>
                  <div className="text-lg font-semibold">
                    {Math.round(preview.statistics.avg_chunk_length || 0)} 字符
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>性能指标</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>处理时间</span>
                  <span>{preview.preview_time}ms</span>
                </div>
                <div className="flex justify-between">
                  <span>内存使用</span>
                  <span>{preview.performance?.memory_usage || 'N/A'}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>优化建议</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {preview.suggestions?.map((suggestion, index) => (
                  <li key={index} className="text-sm text-gray-700">
                    • {suggestion}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </>
      ) : (
        <Card>
          <CardContent>
            <div className="text-center text-gray-500 py-8">
              点击"配置预览"生成预览信息
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )

  const renderTemplatesTab = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">配置模板</h3>
        <Button onClick={saveAsTemplate}>
          保存为模板
        </Button>
      </div>

      <div className="grid gap-4">
        {templates.map((template) => (
          <Card key={template.id}>
            <CardHeader>
              <CardTitle className="text-base">{template.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-3">{template.description}</p>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">
                  {new Date(template.created_at).toLocaleDateString()}
                </span>
                <Button 
                  onClick={() => applyTemplate(template.id)}
                  disabled={loading}
                >
                  应用
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">智能配置</h2>
      </div>

      <Tabs defaultValue="config">
        <TabsList>
          <TabsTrigger value="config">配置</TabsTrigger>
          <TabsTrigger value="preview">预览</TabsTrigger>
          <TabsTrigger value="templates">模板</TabsTrigger>
        </TabsList>

        <TabsContent value="config">
          {renderConfigTab()}
        </TabsContent>

        <TabsContent value="preview">
          {renderPreviewTab()}
        </TabsContent>

        <TabsContent value="templates">
          {renderTemplatesTab()}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default SmartConfigPanel 