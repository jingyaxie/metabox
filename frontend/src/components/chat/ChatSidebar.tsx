import React, { useState, useRef, useEffect } from 'react'
import { useChatStore } from '../../stores/chatStore'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { ScrollArea } from '../ui/scroll-area'
import { 
  Plus, 
  Search, 
  MessageSquare, 
  Trash2, 
  Edit3, 
  Download,
  MoreVertical,
  X
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu'
import { cn } from '../../utils/cn'

interface ChatSidebarProps {
  className?: string
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({ className }) => {
  const {
    sessions,
    currentSessionId,
    sidebarCollapsed,
    createSession,
    switchSession,
    deleteSession,
    renameSession,
    exportSession,
    toggleSidebar,
    loadSessions
  } = useChatStore()

  const [searchQuery, setSearchQuery] = useState('')
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null)
  const [editingTitle, setEditingTitle] = useState('')
  const searchInputRef = useRef<HTMLInputElement>(null)

  // 过滤会话
  const filteredSessions = sessions.filter(session =>
    session.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // 处理新建会话
  const handleNewSession = () => {
    createSession()
    setSearchQuery('')
  }

  // 处理会话切换
  const handleSessionSelect = (sessionId: string) => {
    switchSession(sessionId)
    setEditingSessionId(null)
  }

  // 处理会话删除
  const handleSessionDelete = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('确定要删除这个会话吗？此操作不可撤销。')) {
      await deleteSession(sessionId)
    }
  }

  // 处理会话重命名
  const handleSessionRename = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const session = sessions.find(s => s.id === sessionId)
    if (session) {
      setEditingSessionId(sessionId)
      setEditingTitle(session.title)
    }
  }

  // 保存重命名
  const handleSaveRename = async () => {
    if (editingSessionId && editingTitle.trim()) {
      await renameSession(editingSessionId, editingTitle.trim())
      setEditingSessionId(null)
      setEditingTitle('')
    }
  }

  // 取消重命名
  const handleCancelRename = () => {
    setEditingSessionId(null)
    setEditingTitle('')
  }

  // 处理会话导出
  const handleSessionExport = (sessionId: string, format: 'txt' | 'md' | 'json', e: React.MouseEvent) => {
    e.stopPropagation()
    exportSession(sessionId, format)
  }

  // 快捷键处理
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'k':
            e.preventDefault()
            handleNewSession()
            break
          case 'f':
            e.preventDefault()
            searchInputRef.current?.focus()
            break
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  // 加载会话数据
  useEffect(() => {
    loadSessions()
  }, [loadSessions])

  if (sidebarCollapsed) {
    return (
      <div className={cn('w-16 bg-gray-50 border-r border-gray-200 flex flex-col', className)}>
        <div className="p-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleNewSession}
            className="w-8 h-8"
            title="新建对话 (Ctrl+K)"
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
        <div className="flex-1 flex flex-col items-center space-y-2 p-2">
          {filteredSessions.slice(0, 5).map(session => (
            <Button
              key={session.id}
              variant={currentSessionId === session.id ? "default" : "ghost"}
              size="icon"
              onClick={() => handleSessionSelect(session.id)}
              className="w-8 h-8"
              title={session.title}
            >
              <MessageSquare className="h-4 w-4" />
            </Button>
          ))}
        </div>
        <div className="p-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="w-8 h-8"
            title="展开侧边栏"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className={cn('w-80 bg-gray-50 border-r border-gray-200 flex flex-col', className)}>
      {/* 头部 */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">对话</h2>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="h-8 w-8"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        
        {/* 新建按钮 */}
        <Button
          onClick={handleNewSession}
          className="w-full mb-3"
          size="sm"
        >
          <Plus className="h-4 w-4 mr-2" />
          新建对话
        </Button>

        {/* 搜索框 */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="搜索对话..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* 会话列表 */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {filteredSessions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {searchQuery ? '没有找到匹配的对话' : '还没有对话，开始创建吧！'}
            </div>
          ) : (
            filteredSessions.map(session => (
              <div
                key={session.id}
                className={cn(
                  'group relative flex items-center p-3 rounded-lg cursor-pointer transition-colors',
                  currentSessionId === session.id
                    ? 'bg-primary-50 border border-primary-200'
                    : 'hover:bg-gray-100'
                )}
                onClick={() => handleSessionSelect(session.id)}
              >
                {/* 会话图标 */}
                <div className="flex-shrink-0 mr-3">
                  <MessageSquare className={cn(
                    'h-5 w-5',
                    currentSessionId === session.id ? 'text-primary-600' : 'text-gray-400'
                  )} />
                </div>

                {/* 会话内容 */}
                <div className="flex-1 min-w-0">
                  {editingSessionId === session.id ? (
                    <div className="flex items-center space-x-2">
                      <Input
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            handleSaveRename()
                          } else if (e.key === 'Escape') {
                            handleCancelRename()
                          }
                        }}
                        className="h-6 text-sm"
                        autoFocus
                      />
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={handleSaveRename}
                        className="h-6 px-2"
                      >
                        保存
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={handleCancelRename}
                        className="h-6 px-2"
                      >
                        取消
                      </Button>
                    </div>
                  ) : (
                    <>
                      <div className="font-medium text-sm text-gray-900 truncate">
                        {session.title}
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(session.updated_at).toLocaleDateString()}
                      </div>
                    </>
                  )}
                </div>

                {/* 操作按钮 */}
                <div className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                  <DropdownMenu>
                    <DropdownMenuTrigger>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <MoreVertical className="h-3 w-3" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-48">
                      <DropdownMenuItem onClick={(e) => handleSessionRename(session.id, e)}>
                        <Edit3 className="h-4 w-4 mr-2" />
                        重命名
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem onClick={(e) => handleSessionExport(session.id, 'txt', e)}>
                        <Download className="h-4 w-4 mr-2" />
                        导出为 TXT
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={(e) => handleSessionExport(session.id, 'md', e)}>
                        <Download className="h-4 w-4 mr-2" />
                        导出为 MD
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={(e) => handleSessionExport(session.id, 'json', e)}>
                        <Download className="h-4 w-4 mr-2" />
                        导出为 JSON
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem 
                        onClick={(e) => handleSessionDelete(session.id, e)}
                        className="text-red-600 focus:text-red-600"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        删除
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      {/* 底部信息 */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          {filteredSessions.length} 个对话
        </div>
        <div className="text-xs text-gray-400 text-center mt-1">
          Ctrl+K 新建 | Ctrl+F 搜索
        </div>
      </div>
    </div>
  )
} 