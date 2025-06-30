import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import apiClient from '../services/api'

interface KnowledgeBase {
  id: string
  name: string
  description: string
  type: string
  created_at: string
}

interface TextChunk {
  id: string
  content: string
  source_file: string
  chunk_index: number
}

interface ImageVector {
  id: string
  filename: string
  description: string
  created_at: string
}

const KnowledgeBaseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase | null>(null)
  const [chunks, setChunks] = useState<TextChunk[]>([])
  const [images, setImages] = useState<ImageVector[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'chunks' | 'images'>('overview')

  useEffect(() => {
    if (id) {
      fetchKnowledgeBaseDetail()
    }
  }, [id])

  const fetchKnowledgeBaseDetail = async () => {
    try {
      setLoading(true)
      const [kbRes, chunksRes, imagesRes] = await Promise.all([
        apiClient.get(`/kb/${id}`),
        apiClient.get(`/kb/${id}/chunks`),
        apiClient.get(`/kb/${id}/images`)
      ])
      
      setKnowledgeBase(kbRes.data)
      setChunks(chunksRes.data)
      setImages(imagesRes.data)
    } catch (error) {
      console.error('获取知识库详情失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!knowledgeBase) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center text-gray-500">
          <div className="text-2xl mb-2">❌</div>
          <div>知识库不存在或无权访问</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* 头部信息 */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{knowledgeBase.name}</h1>
              <p className="text-gray-600 mt-2">{knowledgeBase.description}</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">创建时间</div>
              <div className="text-sm font-medium">
                {new Date(knowledgeBase.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center">
              <span className="w-2 h-2 bg-primary-600 rounded-full mr-2"></span>
              <span>类型: {knowledgeBase.type}</span>
            </div>
            <div className="flex items-center">
              <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
              <span>文档: {chunks.length} 个分块</span>
            </div>
            <div className="flex items-center">
              <span className="w-2 h-2 bg-blue-600 rounded-full mr-2"></span>
              <span>图片: {images.length} 张</span>
            </div>
          </div>
        </div>

        {/* 标签页 */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {[
                { id: 'overview', name: '概览', icon: '📊' },
                { id: 'chunks', name: '文档分块', icon: '📄' },
                { id: 'images', name: '图片', icon: '🖼️' }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
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
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-blue-50 rounded-lg p-6">
                    <div className="flex items-center">
                      <div className="text-3xl mr-4">📄</div>
                      <div>
                        <div className="text-2xl font-bold text-blue-600">{chunks.length}</div>
                        <div className="text-sm text-blue-600">文档分块</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-green-50 rounded-lg p-6">
                    <div className="flex items-center">
                      <div className="text-3xl mr-4">🖼️</div>
                      <div>
                        <div className="text-2xl font-bold text-green-600">{images.length}</div>
                        <div className="text-sm text-green-600">图片文件</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-purple-50 rounded-lg p-6">
                    <div className="flex items-center">
                      <div className="text-3xl mr-4">📊</div>
                      <div>
                        <div className="text-2xl font-bold text-purple-600">
                          {chunks.length + images.length}
                        </div>
                        <div className="text-sm text-purple-600">总资源数</div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">最近活动</h3>
                  <div className="space-y-3">
                    <div className="flex items-center text-sm text-gray-600">
                      <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
                      <span>知识库创建于 {new Date(knowledgeBase.created_at).toLocaleString()}</span>
                    </div>
                    {chunks.length > 0 && (
                      <div className="flex items-center text-sm text-gray-600">
                        <span className="w-2 h-2 bg-green-600 rounded-full mr-3"></span>
                        <span>已上传 {chunks.length} 个文档分块</span>
                      </div>
                    )}
                    {images.length > 0 && (
                      <div className="flex items-center text-sm text-gray-600">
                        <span className="w-2 h-2 bg-purple-600 rounded-full mr-3"></span>
                        <span>已上传 {images.length} 张图片</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'chunks' && (
              <div className="space-y-4">
                {chunks.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <div className="text-4xl mb-4">📄</div>
                    <div className="text-lg mb-2">暂无文档分块</div>
                    <div className="text-sm">上传文档后将自动分块显示</div>
                  </div>
                ) : (
                  chunks.map((chunk, index) => (
                    <div key={chunk.id} className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="text-sm font-medium text-gray-700">
                          {chunk.source_file} - 分块 {chunk.chunk_index + 1}
                        </div>
                        <div className="text-xs text-gray-500">
                          #{index + 1}
                        </div>
                      </div>
                      <div className="text-sm text-gray-600 leading-relaxed">
                        {chunk.content}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'images' && (
              <div className="space-y-4">
                {images.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <div className="text-4xl mb-4">🖼️</div>
                    <div className="text-lg mb-2">暂无图片</div>
                    <div className="text-sm">上传图片后将在此显示</div>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {images.map(image => (
                      <div key={image.id} className="bg-gray-50 rounded-lg p-4">
                        <div className="aspect-square bg-gray-200 rounded-lg mb-3 flex items-center justify-center">
                          <span className="text-4xl">🖼️</span>
                        </div>
                        <div className="text-sm font-medium text-gray-700 mb-1">
                          {image.filename}
                        </div>
                        {image.description && (
                          <div className="text-xs text-gray-500 mb-2">
                            {image.description}
                          </div>
                        )}
                        <div className="text-xs text-gray-400">
                          {new Date(image.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default KnowledgeBaseDetail 