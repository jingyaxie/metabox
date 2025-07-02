import React, { useState } from 'react'
import { Message } from '../../types/chat'
import { Button } from '../ui/button'
import { cn } from '../../utils/cn'
import { 
  Copy, 
  RefreshCw, 
  ThumbsUp, 
  ThumbsDown,
  User,
  Bot
} from 'lucide-react'

interface ChatMessageProps {
  message: Message
  isStreaming?: boolean
  onCopy?: (content: string) => void
  onRegenerate?: () => void
  onFeedback?: (type: 'like' | 'dislike') => void
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isStreaming = false,
  onCopy,
  onRegenerate,
  onFeedback
}) => {
  const [showActions, setShowActions] = useState(false)
  const isUser = message.role === 'user'
  const hasFeedback = message.metadata?.feedback

  const handleCopy = () => {
    if (onCopy) {
      onCopy(message.content)
    } else {
      navigator.clipboard.writeText(message.content)
    }
  }

  const handleFeedback = (type: 'like' | 'dislike') => {
    if (onFeedback) {
      onFeedback(type)
    }
  }

  return (
    <div
      className={cn(
        'group relative flex gap-3 px-4 py-6 transition-colors',
        isUser ? 'bg-gray-50' : 'bg-white'
      )}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* 头像 */}
      <div className="flex-shrink-0">
        <div className={cn(
          'w-8 h-8 rounded-full flex items-center justify-center',
          isUser ? 'bg-primary-600' : 'bg-gray-600'
        )}>
          {isUser ? (
            <User className="h-4 w-4 text-white" />
          ) : (
            <Bot className="h-4 w-4 text-white" />
          )}
        </div>
      </div>

      {/* 消息内容 */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm font-medium text-gray-900">
            {isUser ? '你' : 'AI 助手'}
          </span>
          <span className="text-xs text-gray-500">
            {new Date(message.created_at).toLocaleTimeString()}
          </span>
        </div>

        <div className="prose prose-sm max-w-none">
          <div className={cn(
            'whitespace-pre-wrap break-words',
            isStreaming && 'animate-pulse'
          )}>
            {message.content}
            {isStreaming && (
              <span className="inline-block w-2 h-4 bg-gray-400 ml-1 animate-pulse" />
            )}
          </div>
        </div>

        {/* 消息元数据 */}
        {message.metadata && (
          <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
            {message.metadata?.model && (
              <span>模型: {message.metadata.model}</span>
            )}
            {message.metadata?.knowledge_base && (
              <span>知识库: {message.metadata.knowledge_base}</span>
            )}
            {message.metadata?.tokens && (
              <span>Token: {message.metadata.tokens}</span>
            )}
          </div>
        )}

        {/* 操作按钮 */}
        {!isUser && (
          <div className={cn(
            'mt-3 flex items-center gap-2 transition-opacity',
            showActions ? 'opacity-100' : 'opacity-0'
          )}>
            {onCopy && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopy}
                className="h-8 px-2 text-xs"
              >
                <Copy className="h-3 w-3 mr-1" />
                复制
              </Button>
            )}
            
            {onRegenerate && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onRegenerate}
                className="h-8 px-2 text-xs"
              >
                <RefreshCw className="h-3 w-3 mr-1" />
                重新生成
              </Button>
            )}

            {onFeedback && (
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleFeedback('like')}
                  className={cn(
                    'h-8 w-8 p-0',
                    hasFeedback === 'like' && 'text-green-600'
                  )}
                >
                  <ThumbsUp className="h-3 w-3" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleFeedback('dislike')}
                  className={cn(
                    'h-8 w-8 p-0',
                    hasFeedback === 'dislike' && 'text-red-600'
                  )}
                >
                  <ThumbsDown className="h-3 w-3" />
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
} 