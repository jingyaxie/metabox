import React, { useEffect, useState } from 'react'
import apiClient from '../services/api'

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

  const fetchKbs = async () => {
    setLoading(true)
    try {
      const res = await apiClient.get('/kb/')
      setKbs(res.data)
    } catch (e: any) {
      setError(e.message || '获取知识库失败')
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
      await apiClient.post('/kb/', null, { params: form })
      setShowCreate(false)
      setForm({ name: '', description: '', type: 'text' })
      fetchKbs()
    } catch (e: any) {
      setError(e.message || '创建失败')
    }
  }

  const handleDelete = async (id: string) => {
    if (!window.confirm('确定要删除该知识库吗？')) return
    try {
      await apiClient.delete(`/kb/${id}`)
      fetchKbs()
    } catch (e: any) {
      setError(e.message || '删除失败')
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">知识库管理</h1>
        <button className="btn-primary" onClick={() => setShowCreate(true)}>新建知识库</button>
      </div>
      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 mb-4 rounded">{error}</div>}
      {showCreate && (
        <form className="card mb-6" onSubmit={handleCreate}>
          <div className="mb-4">
            <label className="block mb-1">名称</label>
            <input className="input-field" required value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
          </div>
          <div className="mb-4">
            <label className="block mb-1">描述</label>
            <input className="input-field" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          </div>
          <div className="mb-4">
            <label className="block mb-1">类型</label>
            <select className="input-field" value={form.type} onChange={e => setForm(f => ({ ...f, type: e.target.value }))}>
              <option value="text">文本</option>
              <option value="image">图片</option>
              <option value="mixed">混合</option>
            </select>
          </div>
          <div className="flex space-x-2">
            <button className="btn-primary" type="submit">创建</button>
            <button className="btn-secondary" type="button" onClick={() => setShowCreate(false)}>取消</button>
          </div>
        </form>
      )}
      {loading ? (
        <div>加载中...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {kbs.map(kb => (
            <div key={kb.id} className="card relative">
              <div className="absolute right-4 top-4">
                <button className="text-red-500 hover:underline" onClick={() => handleDelete(kb.id)}>删除</button>
              </div>
              <h2 className="text-lg font-bold mb-2">{kb.name}</h2>
              <div className="text-gray-600 mb-2">{kb.description}</div>
              <div className="text-sm text-gray-400">类型：{kb.type}</div>
              <div className="text-xs text-gray-300 mt-2">创建于 {new Date(kb.created_at).toLocaleString()}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default KnowledgeBase 