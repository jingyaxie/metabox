import React, { useState, useRef, useCallback } from 'react'
import { Button } from '../ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { 
  Send, 
  Paperclip, 
  Settings,
  X
} from 'lucide-react'
import { cn } from '../../utils/cn'
import type { KnowledgeBase, Model, SendOptions } from '../../types/chat'

interface ChatInputBarProps {
  onSend: (message: string, options?: Partial<SendOptions>) => void
  onFileUpload?: (files: File[]) => void
  knowledgeBases: KnowledgeBase[]
  models: Model[]
  selectedKnowledgeBase: string
  selectedModel: string
  onKnowledgeBaseChange: (kbId: string) => void
  onModelChange: (modelId: string) => void
  loading?: boolean
  className?: string
}

export const ChatInputBar: React.FC<ChatInputBarProps> = ({
  onSend,
  onFileUpload,
  knowledgeBases,
  models,
  selectedKnowledgeBase,
  selectedModel,
  onKnowledgeBaseChange,
  onModelChange,
  loading = false,
  className
}) => {
  const [message, setMessage] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)
  const [attachedFiles, setAttachedFiles] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // 处理发送消息
  const handleSend = useCallback(() => {
    if (!message.trim() || loading) return

    const options: Partial<SendOptions> = {
      knowledge_base_ids: selectedKnowledgeBase ? [selectedKnowledgeBase] : [],
      model_id: selectedModel,
      files: attachedFiles.length > 0 ? attachedFiles : undefined
    }

    onSend(message.trim(), options)
    setMessage('')
    setAttachedFiles([])
    setIsExpanded(false)
  }, [message, loading, selectedKnowledgeBase, selectedModel, attachedFiles, onSend])

  // 处理键盘事件
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }, [handleSend])

  // 处理文件上传
  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (files.length > 0) {
      setAttachedFiles(prev => [...prev, ...files])
      if (onFileUpload) {
        onFileUpload(files)
      }
    }
    // 重置 input 值，允许重复选择同一文件
    e.target.value = ''
  }, [onFileUpload])

  // 移除附件
  const removeFile = useCallback((index: number) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index))
  }, [])

  // 格式化文件大小
  const formatFileSize = useCallback((bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }, [])

  return (
    <div className={cn('border-t border-gray-200 bg-white', className)}>
      {/* 附件列表 */}
      {attachedFiles.length > 0 && (
        <div className="px-4 py-2 border-b border-gray-100">
          <div className="flex flex-wrap gap-2">
            {attachedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center gap-2 bg-gray-100 rounded-lg px-3 py-1 text-sm"
              >
                <Paperclip className="h-3 w-3 text-gray-500" />
                <span className="text-gray-700">{file.name}</span>
                <span className="text-gray-500">({formatFileSize(file.size)})</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeFile(index)}
                  className="h-4 w-4 p-0 hover:bg-gray-200"
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 输入区域 */}
      <div className="p-4">
        <div className="flex items-end gap-3">
          {/* 知识库选择 */}
          <div className="flex-shrink-0">
            <Select value={selectedKnowledgeBase} onValueChange={onKnowledgeBaseChange}>
              <SelectTrigger>
                <SelectValue>选择知识库</SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">全部知识库</SelectItem>
                {knowledgeBases.map(kb => (
                  <SelectItem key={kb.id} value={kb.id}>
                    {kb.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 模型选择 */}
          <div className="flex-shrink-0">
            <Select value={selectedModel} onValueChange={onModelChange}>
              <SelectTrigger>
                <SelectValue>选择模型</SelectValue>
              </SelectTrigger>
              <SelectContent>
                {models.map(model => (
                  <SelectItem key={model.id} value={model.id}>
                    {model.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 输入框 */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入消息... (Shift + Enter 换行)"
              className="min-h-[44px] max-h-32 resize-none pr-12 w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={loading}
              onFocus={() => setIsExpanded(true)}
            />
            
            {/* 文件上传按钮 */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => fileInputRef.current?.click()}
              className="absolute right-2 bottom-2 h-8 w-8"
              disabled={loading}
            >
              <Paperclip className="h-4 w-4" />
            </Button>
          </div>

          {/* 发送按钮 */}
          <Button
            onClick={handleSend}
            disabled={!message.trim() || loading}
            className="flex-shrink-0"
            size="lg"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* 高级设置 */}
        {isExpanded && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>已选择 {selectedKnowledgeBase ? '1' : '0'} 个知识库</span>
                <span>模型: {models.find(m => m.id === selectedModel)?.name}</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(false)}
              >
                <Settings className="h-4 w-4 mr-1" />
                设置
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* 隐藏的文件输入 */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        onChange={handleFileSelect}
        className="hidden"
        accept=".txt,.md,.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif"
      />
    </div>
  )
} 