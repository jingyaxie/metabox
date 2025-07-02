// Chat 相关类型定义

export interface Session {
  id: string
  title: string
  created_at: string
  updated_at: string
  kb_ids?: string[]
  model_id?: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
  session_id: string
  metadata?: {
    feedback?: 'like' | 'dislike'
    tokens_used?: number
    model_used?: string
    model?: string
    knowledge_base?: string
    tokens?: number
    [key: string]: any
  }
}

export interface KnowledgeBase {
  id: string
  name: string
  description: string
  type: string
  created_at: string
  text_model_info?: any
  image_model_info?: any
  embedding_model_info?: any
  image_embedding_model_info?: any
}

export interface Model {
  id: string
  name: string
  model_name?: string
  provider: string
  provider_type?: string
  model_type?: string
  description: string
  max_tokens: number
  temperature: number
  is_default?: boolean
}

export interface ChatSettings {
  temperature: number
  max_tokens: number
  top_p: number
  frequency_penalty: number
  presence_penalty: number
  system_prompt: string
}

export interface SendOptions {
  knowledge_base_ids: string[]
  model_id: string
  settings: Partial<ChatSettings>
  files?: File[]
}

export interface ChatState {
  // 会话管理
  sessions: Session[]
  currentSessionId: string | null
  
  // 消息管理
  messages: Record<string, Message[]>
  streamingMessageId: string | null
  streamingContent: string
  
  // 配置管理
  selectedKnowledgeBase: string
  selectedModel: string
  chatSettings: ChatSettings
  
  // UI 状态
  loading: boolean
  sidebarCollapsed: boolean
  showSettings: boolean
  
  // 可用选项
  availableKnowledgeBases: KnowledgeBase[]
  availableModels: Model[]
}

export interface ChatActions {
  // 会话管理
  createSession: (title?: string) => Promise<void>
  switchSession: (sessionId: string) => void
  deleteSession: (sessionId: string) => Promise<void>
  renameSession: (sessionId: string, title: string) => Promise<void>
  exportSession: (sessionId: string, format: 'txt' | 'md' | 'json') => void
  
  // 消息管理
  sendMessage: (content: string, options?: Partial<SendOptions>) => Promise<void>
  regenerateMessage: (messageId: string) => Promise<void>
  copyMessage: (content: string) => void
  feedbackMessage: (messageId: string, type: 'like' | 'dislike') => void
  
  // 配置管理
  updateSettings: (settings: Partial<ChatSettings>) => void
  selectKnowledgeBase: (kbId: string) => void
  selectModel: (modelId: string) => void
  
  // UI 控制
  toggleSidebar: () => void
  toggleSettings: () => void
  clearCurrentSession: () => void
  
  // 数据加载
  loadSessions: () => Promise<void>
  loadMessages: (sessionId: string) => Promise<void>
  loadKnowledgeBases: () => Promise<void>
  loadModels: () => Promise<void>
}

export type ChatStore = ChatState & ChatActions

// 流式响应类型
export interface StreamChunk {
  type: 'content' | 'done' | 'error'
  content?: string
  message_id?: string
  error?: string
}

// 文件上传类型
export interface UploadedFile {
  id: string
  name: string
  size: number
  type: string
  url: string
}

// 消息反馈类型
export interface MessageFeedback {
  message_id: string
  type: 'like' | 'dislike'
  created_at: string
} 