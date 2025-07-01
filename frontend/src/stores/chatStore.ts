import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import apiClient from '../services/api'
import type { 
  ChatStore, 
  Message, 
  Model, 
  ChatSettings, 
  SendOptions,
  StreamChunk 
} from '../types/chat'

// 默认聊天设置
const defaultSettings: ChatSettings = {
  temperature: 0.7,
  max_tokens: 2000,
  top_p: 1.0,
  frequency_penalty: 0.0,
  presence_penalty: 0.0,
  system_prompt: '你是一个有用的AI助手，能够基于知识库内容回答问题。'
}

// 默认模型
const defaultModels: Model[] = [
  {
    id: 'gpt-3.5-turbo',
    name: 'GPT-3.5 Turbo',
    provider: 'OpenAI',
    description: '快速、高效的对话模型',
    max_tokens: 4096,
    temperature: 0.7
  },
  {
    id: 'gpt-4',
    name: 'GPT-4',
    provider: 'OpenAI',
    description: '更强大的推理能力',
    max_tokens: 8192,
    temperature: 0.7
  },
  {
    id: 'claude-3-sonnet',
    name: 'Claude 3 Sonnet',
    provider: 'Anthropic',
    description: '平衡性能和速度',
    max_tokens: 4096,
    temperature: 0.7
  }
]

export const useChatStore = create<ChatStore>()(
  devtools(
    persist(
      (set, get) => ({
        // 初始状态
        sessions: [],
        currentSessionId: null,
        messages: {},
        streamingMessageId: null,
        streamingContent: '',
        selectedKnowledgeBase: '',
        selectedModel: 'gpt-3.5-turbo',
        chatSettings: defaultSettings,
        loading: false,
        sidebarCollapsed: false,
        showSettings: false,
        availableKnowledgeBases: [],
        availableModels: defaultModels,

        // 会话管理
        createSession: async (title = '新对话') => {
          try {
            set({ loading: true })
            const { selectedKnowledgeBase, selectedModel } = get()
            
            const response = await apiClient.post('/chat/sessions', {
              title,
              kb_ids: selectedKnowledgeBase ? [selectedKnowledgeBase] : [],
              model_id: selectedModel
            })
            
            const newSession = response.data
            set(state => ({
              sessions: [newSession, ...state.sessions],
              currentSessionId: newSession.id,
              messages: {
                ...state.messages,
                [newSession.id]: []
              }
            }))
          } catch (error) {
            console.error('创建会话失败:', error)
          } finally {
            set({ loading: false })
          }
        },

        switchSession: (sessionId: string) => {
          set({ currentSessionId: sessionId })
        },

        deleteSession: async (sessionId: string) => {
          try {
            await apiClient.delete(`/chat/sessions/${sessionId}`)
            set(state => {
              const newSessions = state.sessions.filter(s => s.id !== sessionId)
              const newMessages = { ...state.messages }
              delete newMessages[sessionId]
              
              let newCurrentSessionId = state.currentSessionId
              if (state.currentSessionId === sessionId) {
                newCurrentSessionId = newSessions.length > 0 ? newSessions[0].id : null
              }
              
              return {
                sessions: newSessions,
                currentSessionId: newCurrentSessionId,
                messages: newMessages
              }
            })
          } catch (error) {
            console.error('删除会话失败:', error)
          }
        },

        renameSession: async (sessionId: string, title: string) => {
          try {
            await apiClient.put(`/chat/sessions/${sessionId}`, { title })
            set(state => ({
              sessions: state.sessions.map(s => 
                s.id === sessionId ? { ...s, title } : s
              )
            }))
          } catch (error) {
            console.error('重命名会话失败:', error)
          }
        },

        exportSession: (sessionId: string, format: 'txt' | 'md' | 'json') => {
          const { messages } = get()
          const sessionMessages = messages[sessionId] || []
          
          let content = ''
          switch (format) {
            case 'txt':
              content = sessionMessages.map(m => 
                `${m.role === 'user' ? '用户' : 'AI'}: ${m.content}`
              ).join('\n\n')
              break
            case 'md':
              content = sessionMessages.map(m => 
                `### ${m.role === 'user' ? '用户' : 'AI'}\n\n${m.content}`
              ).join('\n\n')
              break
            case 'json':
              content = JSON.stringify(sessionMessages, null, 2)
              break
          }
          
          const blob = new Blob([content], { type: 'text/plain' })
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `chat-${sessionId}.${format}`
          a.click()
          URL.revokeObjectURL(url)
        },

        // 消息管理
        sendMessage: async (content: string, options?: Partial<SendOptions>) => {
          const { currentSessionId, selectedKnowledgeBase, selectedModel, chatSettings } = get()
          if (!currentSessionId) return

          const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content,
            created_at: new Date().toISOString(),
            session_id: currentSessionId
          }

          // 添加用户消息
          set(state => ({
            messages: {
              ...state.messages,
              [currentSessionId]: [...(state.messages[currentSessionId] || []), userMessage]
            },
            loading: true,
            streamingMessageId: null,
            streamingContent: ''
          }))

          try {
            const sendOptions: SendOptions = {
              knowledge_base_ids: options?.knowledge_base_ids || (selectedKnowledgeBase ? [selectedKnowledgeBase] : []),
              model_id: options?.model_id || selectedModel,
              settings: { ...chatSettings, ...options?.settings },
              files: options?.files
            }

            // 流式响应处理
            const response = await fetch('/api/chat/stream', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
              },
              body: JSON.stringify({
                message: content,
                session_id: currentSessionId,
                ...sendOptions
              })
            })

            if (!response.ok) throw new Error('发送消息失败')

            const reader = response.body?.getReader()
            if (!reader) throw new Error('无法读取响应流')

            let assistantMessageId = Date.now().toString()
            let assistantContent = ''

            set({ streamingMessageId: assistantMessageId })

            while (true) {
              const { done, value } = await reader.read()
              if (done) break

              const chunk = new TextDecoder().decode(value)
              const lines = chunk.split('\n').filter(line => line.trim())

              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  try {
                    const data: StreamChunk = JSON.parse(line.slice(6))
                    
                    if (data.type === 'content' && data.content) {
                      assistantContent += data.content
                      set({ streamingContent: assistantContent })
                    } else if (data.type === 'done' && data.message_id) {
                      assistantMessageId = data.message_id
                    } else if (data.type === 'error') {
                      throw new Error(data.error || '流式响应错误')
                    }
                  } catch (e) {
                    console.error('解析流数据失败:', e)
                  }
                }
              }
            }

            // 完成流式响应
            const assistantMessage: Message = {
              id: assistantMessageId,
              role: 'assistant',
              content: assistantContent,
              created_at: new Date().toISOString(),
              session_id: currentSessionId,
              metadata: {
                knowledge_base: selectedKnowledgeBase,
                model: selectedModel
              }
            }

            set(state => ({
              messages: {
                ...state.messages,
                [currentSessionId]: [...(state.messages[currentSessionId] || []), assistantMessage]
              },
              streamingMessageId: null,
              streamingContent: '',
              loading: false
            }))

          } catch (error) {
            console.error('发送消息失败:', error)
            set({ loading: false, streamingMessageId: null, streamingContent: '' })
            
            // 添加错误消息
            const errorMessage: Message = {
              id: Date.now().toString(),
              role: 'assistant',
              content: '抱歉，发送消息失败，请重试。',
              created_at: new Date().toISOString(),
              session_id: currentSessionId
            }
            
            set(state => ({
              messages: {
                ...state.messages,
                [currentSessionId]: [...(state.messages[currentSessionId] || []), errorMessage]
              }
            }))
          }
        },

        regenerateMessage: async (messageId: string) => {
          const { currentSessionId, messages } = get()
          if (!currentSessionId) return

          const sessionMessages = messages[currentSessionId] || []
          const messageIndex = sessionMessages.findIndex(m => m.id === messageId)
          if (messageIndex === -1 || messageIndex === 0) return

          // 获取上一条用户消息
          const userMessage = sessionMessages[messageIndex - 1]
          if (userMessage.role !== 'user') return

          // 删除当前AI消息
          set(state => ({
            messages: {
              ...state.messages,
              [currentSessionId]: state.messages[currentSessionId].filter(m => m.id !== messageId)
            }
          }))

          // 重新发送用户消息
          await get().sendMessage(userMessage.content)
        },

        copyMessage: (content: string) => {
          navigator.clipboard.writeText(content)
        },

        feedbackMessage: async (messageId: string, type: 'like' | 'dislike') => {
          try {
            await apiClient.post('/chat/feedback', {
              message_id: messageId,
              type
            })
            
            // 更新消息的反馈状态
            set(state => {
              const { currentSessionId, messages } = state
              if (!currentSessionId) return state
              
              const sessionMessages = messages[currentSessionId] || []
              const updatedMessages = sessionMessages.map(m => 
                m.id === messageId 
                  ? { ...m, metadata: { ...m.metadata, feedback: type } }
                  : m
              )
              
              return {
                messages: {
                  ...messages,
                  [currentSessionId]: updatedMessages
                }
              }
            })
          } catch (error) {
            console.error('提交反馈失败:', error)
          }
        },

        // 配置管理
        updateSettings: (settings: Partial<ChatSettings>) => {
          set(state => ({
            chatSettings: { ...state.chatSettings, ...settings }
          }))
        },

        selectKnowledgeBase: (kbId: string) => {
          set({ selectedKnowledgeBase: kbId })
        },

        selectModel: (modelId: string) => {
          set({ selectedModel: modelId })
        },

        // UI 控制
        toggleSidebar: () => {
          set(state => ({ sidebarCollapsed: !state.sidebarCollapsed }))
        },

        toggleSettings: () => {
          set(state => ({ showSettings: !state.showSettings }))
        },

        clearCurrentSession: () => {
          const { currentSessionId } = get()
          if (currentSessionId) {
            set(state => ({
              messages: {
                ...state.messages,
                [currentSessionId]: []
              }
            }))
          }
        },

        // 数据加载
        loadSessions: async () => {
          try {
            const response = await apiClient.get('/chat/sessions')
            set({ sessions: response.data })
          } catch (error) {
            console.error('加载会话失败:', error)
          }
        },

        loadMessages: async (sessionId: string) => {
          try {
            const response = await apiClient.get(`/chat/sessions/${sessionId}/messages`)
            set(state => ({
              messages: {
                ...state.messages,
                [sessionId]: response.data
              }
            }))
          } catch (error) {
            console.error('加载消息失败:', error)
          }
        },

        loadKnowledgeBases: async () => {
          try {
            const response = await apiClient.get('/kb/')
            set({ availableKnowledgeBases: response.data })
          } catch (error) {
            console.error('加载知识库失败:', error)
          }
        },

        loadModels: async () => {
          try {
            const response = await apiClient.get('/chat/models')
            set({ availableModels: response.data })
          } catch (error) {
            console.error('加载模型失败:', error)
            // 使用默认模型
          }
        }
      }),
      {
        name: 'chat-store',
        partialize: (state) => ({
          sessions: state.sessions,
          currentSessionId: state.currentSessionId,
          selectedKnowledgeBase: state.selectedKnowledgeBase,
          selectedModel: state.selectedModel,
          chatSettings: state.chatSettings,
          sidebarCollapsed: state.sidebarCollapsed
        })
      }
    )
  )
) 