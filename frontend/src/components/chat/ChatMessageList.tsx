import React, { useRef, useEffect } from 'react'
import { Message } from '../../types/chat'
import { ChatMessage } from './ChatMessage'
import { ScrollArea } from '../ui/scroll-area'
import { cn } from '../../utils/cn'

interface ChatMessageListProps {
  messages: Message[]
  streamingMessageId?: string | null
  streamingContent?: string
  onCopy?: (content: string) => void
  onRegenerate?: (messageId: string) => void
  onFeedback?: (messageId: string, type: 'like' | 'dislike') => void
  className?: string
}

export const ChatMessageList: React.FC<ChatMessageListProps> = ({
  messages,
  streamingMessageId,
  streamingContent = '',
  onCopy,
  onRegenerate,
  onFeedback,
  className
}) => {
  const scrollRef = useRef<HTMLDivElement>(null)

  // 自动滚动到底部
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, streamingContent])

  // 如果没有消息，显示空状态
  if (messages.length === 0) {
    return (
      <div className={cn('flex-1 flex items-center justify-center', className)}>
        <div className="text-center text-gray-500">
          <div className="text-4xl mb-4">💬</div>
          <div className="text-lg mb-2">开始新的对话</div>
          <div className="text-sm">输入消息开始与 AI 助手聊天</div>
        </div>
      </div>
    )
  }

  return (
    <ScrollArea className={cn('flex-1', className)} ref={scrollRef}>
      <div className="space-y-0">
        {messages.map((message) => {
          // 如果是流式响应的消息，显示流式内容
          const isStreaming = message.id === streamingMessageId
          const displayContent = isStreaming ? streamingContent : message.content
          
          return (
            <ChatMessage
              key={message.id}
              message={{
                ...message,
                content: displayContent
              }}
              isStreaming={isStreaming}
              onCopy={onCopy ? () => onCopy(message.content) : undefined}
              onRegenerate={onRegenerate ? () => onRegenerate(message.id) : undefined}
              onFeedback={onFeedback ? (type) => onFeedback(message.id, type) : undefined}
            />
          )
        })}
        
        {/* 流式响应的占位符 */}
        {streamingMessageId && !messages.find(m => m.id === streamingMessageId) && (
          <ChatMessage
            message={{
              id: streamingMessageId,
              role: 'assistant',
              content: streamingContent,
              created_at: new Date().toISOString(),
              session_id: ''
            }}
            isStreaming={true}
            onCopy={onCopy ? () => onCopy(streamingContent) : undefined}
          />
        )}
      </div>
    </ScrollArea>
  )
} 