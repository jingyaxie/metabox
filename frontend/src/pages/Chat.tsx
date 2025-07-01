import React, { useEffect } from 'react'
import { useChatStore } from '../stores/chatStore'
import { ChatSidebar } from '../components/chat/ChatSidebar'
import { ChatHeader } from '../components/chat/ChatHeader'
import { ChatMessageList } from '../components/chat/ChatMessageList'
import { ChatInputBar } from '../components/chat/ChatInputBar'
import { cn } from '../utils/cn'

const Chat: React.FC = () => {
  const {
    // 状态
    sessions,
    currentSessionId,
    messages,
    streamingMessageId,
    streamingContent,
    selectedKnowledgeBase,
    selectedModel,
    loading,
    sidebarCollapsed,
    availableKnowledgeBases,
    availableModels,
    
    // 操作
    createSession,
    sendMessage,
    regenerateMessage,
    copyMessage,
    feedbackMessage,
    clearCurrentSession,
    exportSession,
    renameSession,
    selectKnowledgeBase,
    selectModel,
    loadSessions,
    loadMessages,
    loadKnowledgeBases,
    loadModels
  } = useChatStore()

  // 获取当前会话
  const currentSession = sessions.find(s => s.id === currentSessionId) || null
  const currentMessages = currentSessionId ? (messages[currentSessionId] || []) : []

  // 初始化数据
  useEffect(() => {
    loadSessions()
    loadKnowledgeBases()
    loadModels()
  }, [loadSessions, loadKnowledgeBases, loadModels])

  // 加载当前会话的消息
  useEffect(() => {
    if (currentSessionId) {
      loadMessages(currentSessionId)
    }
  }, [currentSessionId, loadMessages])

  // 处理发送消息
  const handleSend = async (content: string, options?: any) => {
    if (!currentSessionId) {
      // 如果没有当前会话，先创建一个
      await createSession()
      // 等待会话创建完成后再发送消息
      setTimeout(() => {
        sendMessage(content, options)
      }, 100)
    } else {
      sendMessage(content, options)
    }
  }

  // 处理重新生成消息
  const handleRegenerate = (messageId: string) => {
    regenerateMessage(messageId)
  }

  // 处理复制消息
  const handleCopy = (content: string) => {
    copyMessage(content)
  }

  // 处理消息反馈
  const handleFeedback = (messageId: string, type: 'like' | 'dislike') => {
    feedbackMessage(messageId, type)
  }

  // 处理清空会话
  const handleClearSession = () => {
    if (currentSessionId) {
      clearCurrentSession()
    }
  }

  // 处理导出会话
  const handleExportSession = (format: 'txt' | 'md' | 'json') => {
    if (currentSessionId) {
      exportSession(currentSessionId, format)
    }
  }

  // 处理重命名会话
  const handleRenameSession = (title: string) => {
    if (currentSessionId) {
      renameSession(currentSessionId, title)
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 左侧边栏 */}
      <ChatSidebar />

      {/* 主聊天区域 */}
      <div className={cn(
        'flex-1 flex flex-col transition-all duration-300',
        sidebarCollapsed ? 'ml-16' : 'ml-0'
      )}>
        {/* 聊天头部 */}
        <ChatHeader
          session={currentSession}
          onClearSession={handleClearSession}
          onExportSession={handleExportSession}
          onRenameSession={handleRenameSession}
        />

        {/* 消息列表 */}
        <ChatMessageList
          messages={currentMessages}
          streamingMessageId={streamingMessageId}
          streamingContent={streamingContent}
          onCopy={handleCopy}
          onRegenerate={handleRegenerate}
          onFeedback={handleFeedback}
        />

        {/* 输入区域 */}
        <ChatInputBar
          onSend={handleSend}
          knowledgeBases={availableKnowledgeBases}
          models={availableModels}
          selectedKnowledgeBase={selectedKnowledgeBase}
          selectedModel={selectedModel}
          onKnowledgeBaseChange={selectKnowledgeBase}
          onModelChange={selectModel}
          loading={loading}
        />
      </div>
    </div>
  )
}

export default Chat 