import React, { useState, useEffect, useRef } from 'react'
import apiClient from '../services/api'

interface ChatSession {
  id: string
  title: string
  created_at: string
  updated_at: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

interface KnowledgeBase {
  id: string
  name: string
  description: string
}

const Chat: React.FC = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [selectedKbs, setSelectedKbs] = useState<string[]>([])
  const [availableKbs, setAvailableKbs] = useState<KnowledgeBase[]>([])
  const [showKbSelector, setShowKbSelector] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 获取会话列表
  const fetchSessions = async () => {
    try {
      const res = await apiClient.get('/chat/sessions')
      setSessions(res.data)
    } catch (error) {
      console.error('获取会话失败:', error)
    }
  }

  // 获取知识库列表
  const fetchKnowledgeBases = async () => {
    try {
      const res = await apiClient.get('/kb/')
      setAvailableKbs(res.data)
    } catch (error) {
      console.error('获取知识库失败:', error)
    }
  }

  // 创建新会话
  const createSession = async () => {
    try {
      const res = await apiClient.post('/chat/sessions', null, {
        params: { title: '新对话', kb_ids: selectedKbs }
      })
      setCurrentSession(res.data)
      setMessages([])
      fetchSessions()
    } catch (error) {
      console.error('创建会话失败:', error)
    }
  }

  // 删除会话
  const deleteSession = async (sessionId: string) => {
    try {
      await apiClient.delete(`/chat/sessions/${sessionId}`)
      if (currentSession?.id === sessionId) {
        setCurrentSession(null)
        setMessages([])
      }
      fetchSessions()
    } catch (error) {
      console.error('删除会话失败:', error)
    }
  }

  // 发送消息
  const sendMessage = async () => {
    if (!inputMessage.trim() || !currentSession) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      created_at: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setLoading(true)

    try {
      const res = await apiClient.post('/chat/', {
        message: inputMessage,
        kb_ids: selectedKbs,
        session_id: currentSession.id
      })
      
      const assistantMessage: Message = {
        id: res.data.message_id,
        role: 'assistant',
        content: res.data.answer,
        created_at: new Date().toISOString()
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('发送消息失败:', error)
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: '抱歉，发送消息失败，请重试。',
        created_at: new Date().toISOString()
      }])
    } finally {
      setLoading(false)
    }
  }

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    fetchSessions()
    fetchKnowledgeBases()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 侧边栏 */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold mb-4">聊天会话</h2>
          <div className="space-y-2">
            <button 
              className="btn-primary w-full"
              onClick={createSession}
            >
              新建对话
            </button>
            <button 
              className="btn-secondary w-full"
              onClick={() => setShowKbSelector(true)}
            >
              选择知识库 ({selectedKbs.length})
            </button>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {sessions.map(session => (
            <div
              key={session.id}
              className={`p-4 cursor-pointer hover:bg-gray-50 border-l-4 ${
                currentSession?.id === session.id ? 'border-primary-500 bg-primary-50' : 'border-transparent'
              }`}
              onClick={() => setCurrentSession(session)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm truncate">{session.title}</div>
                  <div className="text-xs text-gray-500">
                    {new Date(session.updated_at).toLocaleString()}
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteSession(session.id)
                  }}
                  className="text-gray-400 hover:text-red-500 ml-2"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 聊天区域 */}
      <div className="flex-1 flex flex-col">
        {currentSession ? (
          <>
            {/* 聊天头部 */}
            <div className="bg-white border-b border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">{currentSession.title}</h3>
                <div className="text-sm text-gray-500">
                  已选择 {selectedKbs.length} 个知识库
                </div>
              </div>
            </div>

            {/* 消息列表 */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map(message => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-3xl rounded-lg px-4 py-2 ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-white border border-gray-200'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    <div className={`text-xs mt-1 ${
                      message.role === 'user' ? 'text-primary-100' : 'text-gray-400'
                    }`}>
                      {new Date(message.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white border border-gray-200 rounded-lg px-4 py-2">
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                      <span className="text-gray-500">正在思考...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* 输入区域 */}
            <div className="bg-white border-t border-gray-200 p-4">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                  placeholder="输入消息..."
                  className="flex-1 input-field"
                  disabled={loading}
                />
                <button
                  onClick={sendMessage}
                  disabled={!inputMessage.trim() || loading}
                  className="btn-primary px-6"
                >
                  发送
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <div className="text-4xl mb-4">💬</div>
              <div className="text-lg mb-2">选择或创建一个对话</div>
              <div className="text-sm">开始与 AI 助手聊天</div>
            </div>
          </div>
        )}
      </div>

      {/* 知识库选择模态框 */}
      {showKbSelector && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">选择知识库</h3>
                <button
                  onClick={() => setShowKbSelector(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-2 max-h-64 overflow-y-auto">
                {availableKbs.map(kb => (
                  <label key={kb.id} className="flex items-center p-3 hover:bg-gray-50 rounded-lg cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedKbs.includes(kb.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedKbs(prev => [...prev, kb.id])
                        } else {
                          setSelectedKbs(prev => prev.filter(id => id !== kb.id))
                        }
                      }}
                      className="mr-3"
                    />
                    <div>
                      <div className="font-medium text-sm">{kb.name}</div>
                      <div className="text-xs text-gray-500">{kb.description}</div>
                    </div>
                  </label>
                ))}
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowKbSelector(false)}
                  className="btn-secondary"
                >
                  确定
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Chat 