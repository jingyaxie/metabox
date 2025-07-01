import React, { useState } from 'react'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { 
  Trash2, 
  Download, 
  Settings,
  Edit3,
  Check,
  X
} from 'lucide-react'
import { cn } from '../../utils/cn'
import type { Session } from '../../types/chat'

interface ChatHeaderProps {
  session: Session | null
  onClearSession?: () => void
  onExportSession?: (format: 'txt' | 'md' | 'json') => void
  onRenameSession?: (title: string) => void
  onOpenSettings?: () => void
  className?: string
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  session,
  onClearSession,
  onExportSession,
  onRenameSession,
  onOpenSettings,
  className
}) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editTitle, setEditTitle] = useState('')

  const handleStartEdit = () => {
    if (session) {
      setEditTitle(session.title)
      setIsEditing(true)
    }
  }

  const handleSaveEdit = () => {
    if (editTitle.trim() && onRenameSession) {
      onRenameSession(editTitle.trim())
    }
    setIsEditing(false)
  }

  const handleCancelEdit = () => {
    setIsEditing(false)
    setEditTitle('')
  }

  const handleClearSession = () => {
    if (onClearSession && confirm('确定要清空当前会话吗？此操作不可撤销。')) {
      onClearSession()
    }
  }

  if (!session) {
    return (
      <div className={cn('bg-white border-b border-gray-200 px-4 py-3', className)}>
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-semibold text-gray-900">新对话</h1>
          <div className="flex items-center gap-2">
            {onOpenSettings && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onOpenSettings}
                className="h-8 w-8"
              >
                <Settings className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={cn('bg-white border-b border-gray-200 px-4 py-3', className)}>
      <div className="flex items-center justify-between">
        {/* 会话标题 */}
        <div className="flex items-center gap-3">
          {isEditing ? (
            <div className="flex items-center gap-2">
              <Input
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleSaveEdit()
                  } else if (e.key === 'Escape') {
                    handleCancelEdit()
                  }
                }}
                className="w-64"
                autoFocus
              />
              <Button
                variant="ghost"
                size="icon"
                onClick={handleSaveEdit}
                className="h-6 w-6"
              >
                <Check className="h-3 w-3" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleCancelEdit}
                className="h-6 w-6"
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-semibold text-gray-900">
                {session.title}
              </h1>
              {onRenameSession && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleStartEdit}
                  className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Edit3 className="h-3 w-3" />
                </Button>
              )}
            </div>
          )}
        </div>

        {/* 操作按钮 */}
        <div className="flex items-center gap-2">
          {/* 清空会话 */}
          {onClearSession && (
            <Button
              variant="ghost"
              size="icon"
              onClick={handleClearSession}
              className="h-8 w-8"
              title="清空会话"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}

          {/* 导出会话 */}
          {onExportSession && (
            <div className="relative group">
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                title="导出会话"
              >
                <Download className="h-4 w-4" />
              </Button>
              <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                <div className="py-1">
                  <button
                    onClick={() => onExportSession('txt')}
                    className="block w-full px-3 py-1 text-sm text-left hover:bg-gray-100"
                  >
                    导出为 TXT
                  </button>
                  <button
                    onClick={() => onExportSession('md')}
                    className="block w-full px-3 py-1 text-sm text-left hover:bg-gray-100"
                  >
                    导出为 MD
                  </button>
                  <button
                    onClick={() => onExportSession('json')}
                    className="block w-full px-3 py-1 text-sm text-left hover:bg-gray-100"
                  >
                    导出为 JSON
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* 设置 */}
          {onOpenSettings && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onOpenSettings}
              className="h-8 w-8"
              title="设置"
            >
              <Settings className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* 会话信息 */}
      <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
        <span>创建于 {new Date(session.created_at).toLocaleString()}</span>
        <span>更新于 {new Date(session.updated_at).toLocaleString()}</span>
        {session.kb_ids && session.kb_ids.length > 0 && (
          <span>知识库: {session.kb_ids.length} 个</span>
        )}
        {session.model_id && (
          <span>模型: {session.model_id}</span>
        )}
      </div>
    </div>
  )
} 