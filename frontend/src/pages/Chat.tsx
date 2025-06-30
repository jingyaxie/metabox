import React, { useState, useEffect, useRef } from 'react'
import apiClient from '../services/api'

interface ChatSession {
  id: string
  title: string
  created_at: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

const Chat: React.FC = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const fetchSessions = async () => {
    try {
      const res = await apiClient.get('/chat/sessions')
      setSessions(res.data)
    } catch (error) {
      console.error('获取会话失败:', error)
    }
  }

  const createSession = async () => {
    try {
      const res = await apiClient.post('/chat/sessions')
      setCurrentSession(res.data)
      setMessages([])
      fetchSessions()
    } catch (error) {
      console.error('创建会话失败:', error)
    }
  }

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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    fetchSessions()
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
          <button 
            className="btn-primary w-full"
            onClick={createSession}
          >
            新建对话
          </button>
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
              <div className="font-medium text-sm truncate">{session.title}</div>
              <div className="text-xs text-gray-500">
                {new Date(session.created_at).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 聊天区域 */}
      <div className="flex-1 flex flex-col">
        {currentSession ? (
          <>
            <div className="bg-white border-b border-gray-200 p-4">
              <h3 className="text-lg font-semibold">{currentSession.title}</h3>
            </div>

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

            <div className="bg-white border-t border-gray-200 p-4">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
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
    </div>
  )
}

export default Chat 