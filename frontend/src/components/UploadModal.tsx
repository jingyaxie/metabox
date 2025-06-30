import React, { useState, useRef } from 'react'
import apiClient from '../services/api'

interface UploadModalProps {
  isOpen: boolean
  onClose: () => void
  kbId: string
  onSuccess: () => void
  type: 'document' | 'image'
}

const UploadModal: React.FC<UploadModalProps> = ({
  isOpen,
  onClose,
  kbId,
  onSuccess,
  type
}) => {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0])
    }
  }

  const handleFileUpload = async (file: File) => {
    setUploading(true)
    setUploadProgress(0)
    setError('')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const endpoint = type === 'document' ? 'upload-doc' : 'upload-image'
      
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      const response = await apiClient.post(`/kb/${kbId}/${endpoint}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      setTimeout(() => {
        onSuccess()
        onClose()
        setUploading(false)
        setUploadProgress(0)
      }, 500)

    } catch (error: any) {
      setError(error.response?.data?.message || '上传失败，请重试')
      setUploading(false)
      setUploadProgress(0)
    }
  }

  const getAcceptedTypes = () => {
    if (type === 'document') {
      return '.txt,.pdf,.doc,.docx,.md'
    }
    return '.jpg,.jpeg,.png,.gif,.webp'
  }

  const getMaxSize = () => {
    return type === 'document' ? '100MB' : '50MB'
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">
              上传{type === 'document' ? '文档' : '图片'}
            </h3>
            <button
              onClick={onClose}
              disabled={uploading}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="text-red-600 text-sm">{error}</div>
            </div>
          )}

          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="text-4xl mb-4">
              {type === 'document' ? '📄' : '🖼️'}
            </div>
            <div className="text-lg font-medium mb-2">
              拖拽文件到此处或点击选择
            </div>
            <div className="text-sm text-gray-500 mb-4">
              支持 {getAcceptedTypes()} 格式，最大 {getMaxSize()}
            </div>
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="btn-primary"
            >
              选择文件
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept={getAcceptedTypes()}
              onChange={handleFileSelect}
              className="hidden"
              disabled={uploading}
            />
          </div>

          {uploading && (
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                <span>上传中...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}

          <div className="flex justify-end space-x-3 mt-6">
            <button
              onClick={onClose}
              disabled={uploading}
              className="btn-secondary"
            >
              取消
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default UploadModal 