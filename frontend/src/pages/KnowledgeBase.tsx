import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Alert, AlertDescription } from '../components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { Brain, Database, Image, FileText, Settings } from 'lucide-react'
import apiClient from '../services/api'

interface KnowledgeBase {
  id: string
  name: string
  description: string
  type: string
  created_at: string
  text_model_info?: any
  image_model_info?: any
  embedding_model_info?: any
  image_embedding_model_info?: any
}

interface Model {
  id: string
  name: string
  model_name: string
  provider: string
  provider_type: string
  model_type: string
  max_tokens?: number
  temperature?: string
  is_default: boolean
  description: string
}

const KnowledgeBase: React.FC = () => {
  const [kbs, setKbs] = useState<KnowledgeBase[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [models, setModels] = useState<{
    chat: Model[]
    embedding: Model[]
    image: Model[]
  }>({ chat: [], embedding: [], image: [] })
  const [form, setForm] = useState({
    name: '',
    description: '',
    type: 'text',
    text_model_id: '',
    image_model_id: '',
    embedding_model_id: '',
    image_embedding_model_id: ''
  })
  const navigate = useNavigate()

  const fetchKbs = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/kb/')
      setKbs(response.data)
    } catch (e: any) {
      setError('获取知识库失败')
    } finally {
      setLoading(false)
    }
  }

  const fetchModels = async () => {
    try {
      const response = await apiClient.get('/kb/models')
      setModels(response.data)
    } catch (e: any) {
      console.error('获取模型列表失败:', e)
    }
  }

  useEffect(() => {
    fetchKbs()
    fetchModels()
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await apiClient.post('/kb/', {
        name: form.name,
        description: form.description,
        kb_type: form.type,
        text_model_id: form.text_model_id || null,
        image_model_id: form.image_model_id || null,
        embedding_model_id: form.embedding_model_id || null,
        image_embedding_model_id: form.image_embedding_model_id || null
      })
      
      setKbs(prev => [...prev, response.data])
      setShowCreate(false)
      setForm({
        name: '',
        description: '',
        type: 'text',
        text_model_id: '',
        image_model_id: '',
        embedding_model_id: '',
        image_embedding_model_id: ''
      })
    } catch (e: any) {
      setError('创建失败')
    }
  }

  const handleDelete = async (id: string) => {
    if (!window.confirm('确定要删除该知识库吗？')) return
    try {
      await apiClient.delete(`/kb/${id}`)
      setKbs(prev => prev.filter(kb => kb.id !== id))
    } catch (e: any) {
      setError('删除失败')
    }
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">知识库管理</h1>
        <Button 
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2"
        >
          <Database className="w-4 h-4" />
          新建知识库
        </Button>
      </div>
      
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {showCreate && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5" />
              创建知识库
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">名称</Label>
                  <Input
                    id="name"
                    required
                    value={form.name}
                    onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                    placeholder="请输入知识库名称"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="type">类型</Label>
                  <Select value={form.type} onValueChange={value => setForm(f => ({ ...f, type: value }))}>
                    <SelectTrigger>
                      <SelectValue>请选择</SelectValue>
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="text">文本</SelectItem>
                      <SelectItem value="image">图片</SelectItem>
                      <SelectItem value="mixed">混合</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">描述</Label>
                <Input
                  id="description"
                  value={form.description}
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                  placeholder="请输入知识库描述"
                />
              </div>

              <Tabs defaultValue="text" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="text" className="flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    文本模型
                  </TabsTrigger>
                  <TabsTrigger value="image" className="flex items-center gap-2">
                    <Image className="w-4 h-4" />
                    图片模型
                  </TabsTrigger>
                  <TabsTrigger value="embedding" className="flex items-center gap-2">
                    <Brain className="w-4 h-4" />
                    嵌入模型
                  </TabsTrigger>
                  <TabsTrigger value="image-embedding" className="flex items-center gap-2">
                    <Image className="w-4 h-4" />
                    图片嵌入
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="text" className="space-y-4">
                  <div className="space-y-2">
                    <Label>文本理解模型</Label>
                    <Select 
                      value={form.text_model_id} 
                      onValueChange={value => setForm(f => ({ ...f, text_model_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue>请选择</SelectValue>
                      </SelectTrigger>
                      <SelectContent>
                        {models.chat.map(model => (
                          <SelectItem key={model.id} value={model.id}>
                            {model.provider} - {model.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </TabsContent>

                <TabsContent value="image" className="space-y-4">
                  <div className="space-y-2">
                    <Label>图片理解模型</Label>
                    <Select 
                      value={form.image_model_id} 
                      onValueChange={value => setForm(f => ({ ...f, image_model_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue>请选择</SelectValue>
                      </SelectTrigger>
                      <SelectContent>
                        {models.image.map(model => (
                          <SelectItem key={model.id} value={model.id}>
                            {model.provider} - {model.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </TabsContent>

                <TabsContent value="embedding" className="space-y-4">
                  <div className="space-y-2">
                    <Label>文本嵌入模型</Label>
                    <Select 
                      value={form.embedding_model_id} 
                      onValueChange={value => setForm(f => ({ ...f, embedding_model_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue>请选择</SelectValue>
                      </SelectTrigger>
                      <SelectContent>
                        {models.embedding.map(model => (
                          <SelectItem key={model.id} value={model.id}>
                            {model.provider} - {model.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </TabsContent>

                <TabsContent value="image-embedding" className="space-y-4">
                  <div className="space-y-2">
                    <Label>图片嵌入模型</Label>
                    <Select 
                      value={form.image_embedding_model_id} 
                      onValueChange={value => setForm(f => ({ ...f, image_embedding_model_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue>请选择</SelectValue>
                      </SelectTrigger>
                      <SelectContent>
                        {models.image.map(model => (
                          <SelectItem key={model.id} value={model.id}>
                            {model.provider} - {model.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </TabsContent>
              </Tabs>

              <div className="flex space-x-2">
                <Button type="submit">
                  创建
                </Button>
                <Button 
                  type="button" 
                  variant="outline"
                  onClick={() => setShowCreate(false)}
                >
                  取消
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}
      
      {loading ? (
        <div className="text-center py-8">
          <div className="text-gray-500">加载中...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {kbs.map(kb => (
            <Card 
              key={kb.id} 
              className="cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => navigate(`/kb/${kb.id}`)}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{kb.name}</CardTitle>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(kb.id)
                    }}
                    className="text-red-500 hover:text-red-700"
                  >
                    删除
                  </Button>
                </div>
                <p className="text-sm text-gray-600">{kb.description}</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm text-gray-500">
                  <div>类型：{kb.type}</div>
                  {kb.text_model_info && (
                    <div>文本模型：{kb.text_model_info.provider} - {kb.text_model_info.name}</div>
                  )}
                  {kb.embedding_model_info && (
                    <div>嵌入模型：{kb.embedding_model_info.provider} - {kb.embedding_model_info.name}</div>
                  )}
                  <div className="text-xs text-gray-400">
                    创建于 {new Date(kb.created_at).toLocaleString()}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

export default KnowledgeBase 