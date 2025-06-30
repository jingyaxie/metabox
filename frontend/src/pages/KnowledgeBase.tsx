import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

interface KnowledgeBase {
  id: string
  name: string
  description?: string
  type: string
  created_at: string
}

const KnowledgeBase: React.FC = () => {
  const [kbs, setKbs] = useState<KnowledgeBase[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: '', description: '', type: 'text' })
  const navigate = useNavigate()

  const fetchKbs = async () => {
    setLoading(true)
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 模拟数据
      const mockKbs: KnowledgeBase[] = [
        {
          id: '1',
          name: '技术文档库',
          description: '包含各种技术文档和API说明',
          type: 'text',
          created_at: '2024-01-15T10:30:00Z'
        },
        {
          id: '2',
          name: '产品手册',
          description: '产品使用说明和功能介绍',
          type: 'mixed',
          created_at: '2024-01-20T14:20:00Z'
        }
      ]
      setKbs(mockKbs)
    } catch (e: any) {
      setError('获取知识库失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchKbs()
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      // 模拟创建
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const newKb: KnowledgeBase = {
        id: Date.now().toString(),
        name: form.name,
        description: form.description,
        type: form.type,
        created_at: new Date().toISOString()
      }
      
      setKbs(prev => [...prev, newKb])
      setShowCreate(false)
      setForm({ name: '', description: '', type: 'text' })
    } catch (e: any) {
      setError('创建失败')
    }
  }

  const handleDelete = async (id: string) => {
    if (!window.confirm('确定要删除该知识库吗？')) return
    try {
      // 模拟删除
      await new Promise(resolve => setTimeout(resolve, 300))
      setKbs(prev => prev.filter(kb => kb.id !== id))
    } catch (e: any) {
      setError('删除失败')
    }
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">知识库管理</h1>
        <button 
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          onClick={() => setShowCreate(true)}
        >
          新建知识库
        </button>
      </div>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 mb-4 rounded">
          {error}
        </div>
      )}
      
      {showCreate && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">创建知识库</h2>
          <form onSubmit={handleCreate}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">名称</label>
              <input 
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required 
                value={form.name} 
                onChange={e => setForm(f => ({ ...f, name: e.target.value }))} 
              />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">描述</label>
              <input 
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.description} 
                onChange={e => setForm(f => ({ ...f, description: e.target.value }))} 
              />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">类型</label>
              <select 
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.type} 
                onChange={e => setForm(f => ({ ...f, type: e.target.value }))}
              >
                <option value="text">文本</option>
                <option value="image">图片</option>
                <option value="mixed">混合</option>
              </select>
            </div>
            <div className="flex space-x-2">
              <button 
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                type="submit"
              >
                创建
              </button>
              <button 
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                type="button" 
                onClick={() => setShowCreate(false)}
              >
                取消
              </button>
            </div>
          </form>
        </div>
      )}
      
      {loading ? (
        <div className="text-center py-8">
          <div className="text-gray-500">加载中...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {kbs.map(kb => (
            <div 
              key={kb.id} 
              className="bg-white rounded-lg shadow p-6 relative cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => navigate(`/kb/${kb.id}`)}
            >
              <div className="absolute right-4 top-4">
                <button 
                  className="text-red-500 hover:text-red-700 text-sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDelete(kb.id)
                  }}
                >
                  删除
                </button>
              </div>
              <h2 className="text-lg font-bold mb-2 text-gray-900">{kb.name}</h2>
              <div className="text-gray-600 mb-2">{kb.description}</div>
              <div className="text-sm text-gray-500 mb-2">类型：{kb.type}</div>
              <div className="text-xs text-gray-400">
                创建于 {new Date(kb.created_at).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default KnowledgeBase 