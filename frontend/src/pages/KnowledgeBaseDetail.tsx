import React, { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import apiClient from '../services/api'

interface KnowledgeBase {
  id: string
  name: string
  description?: string
  type: string
  created_at: string
}

interface TextChunk {
  id: string
  content: string
  chunk_index: number
  source_file?: string
  created_at: string
}

interface ImageVector {
  id: string
  filename: string
  file_path: string
  description?: string
  created_at: string
}

const KnowledgeBaseDetail: React.FC = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [kb, setKb] = useState<KnowledgeBase | null>(null)
  const [chunks, setChunks] = useState<TextChunk[]>([])
  const [images, setImages] = useState<ImageVector[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showUpload, setShowUpload] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadType, setUploadType] = useState<'doc' | 'image'>('doc')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const fetchDetail = async () => {
    setLoading(true)
    try {
      const res = await apiClient.get(`/kb/${id}`)
      setKb(res.data)
      // 获取分块和图片
      const chunkRes = await apiClient.get(`/kb/${id}/chunks`)
      setChunks(chunkRes.data)
      const imgRes = await apiClient.get(`/kb/${id}/images`)
      setImages(imgRes.data)
    } catch (e: any) {
      setError(e.message || '获取详情失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDetail()
    // eslint-disable-next-line
  }, [id])

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!fileInputRef.current?.files?.length) return
    setUploading(true)
    setError('')
    const file = fileInputRef.current.files[0]
    const formData = new FormData()
    formData.append('file', file)
    try {
      if (uploadType === 'doc') {
        await apiClient.post(`/kb/${id}/upload-doc`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
      } else {
        await apiClient.post(`/kb/${id}/upload-image`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
      }
      setShowUpload(false)
      fetchDetail()
    } catch (e: any) {
      setError(e.message || '上传失败')
    } finally {
      setUploading(false)
    }
  }

  if (loading) return <div className="text-center py-12 text-lg text-gray-500">加载中...</div>
  if (error) return <div className="text-center py-12 text-red-500">{error}</div>
  if (!kb) return <div className="text-center py-12 text-gray-400">知识库不存在</div>

  return (
    <div className="max-w-5xl mx-auto py-8">
      <div className="flex items-center mb-6">
        <button className="btn-secondary mr-4" onClick={() => navigate(-1)}>← 返回</button>
        <h1 className="text-2xl font-bold text-primary-700">{kb.name}</h1>
      </div>
      <div className="mb-4 text-gray-600">{kb.description}</div>
      <div className="mb-6 flex flex-wrap gap-2 text-xs text-gray-400">
        <span>类型：{kb.type}</span>
        <span>创建于 {new Date(kb.created_at).toLocaleString()}</span>
        <button className="btn-primary ml-auto" onClick={() => { setShowUpload(true); setUploadType('doc') }}>上传文档</button>
        <button className="btn-secondary" onClick={() => { setShowUpload(true); setUploadType('image') }}>上传图片</button>
      </div>
      {/* 上传弹窗 */}
      {showUpload && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
          <form className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md relative animate-fadeIn" onSubmit={handleUpload}>
            <button type="button" className="absolute right-4 top-4 text-gray-400 hover:text-gray-600" onClick={() => setShowUpload(false)}>✕</button>
            <h2 className="text-lg font-bold mb-4">{uploadType === 'doc' ? '上传文档' : '上传图片'}</h2>
            <input ref={fileInputRef} type="file" accept={uploadType === 'doc' ? '.pdf,.txt,.md,.doc,.docx' : 'image/*'} className="mb-4" required />
            <div className="flex space-x-2">
              <button className="btn-primary" type="submit" disabled={uploading}>{uploading ? '上传中...' : '上传'}</button>
              <button className="btn-secondary" type="button" onClick={() => setShowUpload(false)}>取消</button>
            </div>
            {error && <div className="text-red-500 mt-2">{error}</div>}
          </form>
        </div>
      )}
      {/* 文档分块展示 */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-2">文档分块</h2>
        {chunks.length === 0 ? (
          <div className="text-gray-400">暂无文档分块</div>
        ) : (
          <div className="space-y-4">
            {chunks.map(chunk => (
              <div key={chunk.id} className="bg-gray-50 border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition">
                <div className="text-xs text-gray-400 mb-1">分块 #{chunk.chunk_index} {chunk.source_file && <span>({chunk.source_file})</span>}</div>
                <div className="whitespace-pre-line text-gray-800 text-sm leading-relaxed">{chunk.content}</div>
                <div className="text-right text-xs text-gray-300 mt-2">{new Date(chunk.created_at).toLocaleString()}</div>
              </div>
            ))}
          </div>
        )}
      </div>
      {/* 图片展示 */}
      <div>
        <h2 className="text-lg font-semibold mb-2">图片</h2>
        {images.length === 0 ? (
          <div className="text-gray-400">暂无图片</div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {images.map(img => (
              <div key={img.id} className="bg-white border border-gray-200 rounded-lg p-2 shadow-sm flex flex-col items-center">
                <img src={img.file_path} alt={img.filename} className="w-full h-32 object-contain mb-2 rounded" />
                <div className="text-xs text-gray-500 truncate w-full">{img.filename}</div>
                <div className="text-xs text-gray-300">{new Date(img.created_at).toLocaleString()}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default KnowledgeBaseDetail 