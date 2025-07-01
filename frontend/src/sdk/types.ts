export interface MetaBoxClientOptions {
  apiKey: string;
  baseUrl?: string;
}

export interface QueryRequest {
  message: string;
  kb_ids?: string[];
  model_id?: string;
  session_id?: string;
  options?: {
    temperature?: number;
    max_tokens?: number;
    top_k?: number;
    similarity_threshold?: number;
  };
  stream?: boolean;
}

export interface QueryResponse {
  success: boolean;
  data?: {
    answer: string;
    sources: Array<{
      kb_id: string;
      chunk_id: string;
      content: string;
      similarity: number;
    }>;
    usage: {
      prompt_tokens: number;
      completion_tokens: number;
      total_tokens: number;
    };
    session_id?: string;
  };
  error?: {
    code: string;
    message: string;
  };
}

export interface SearchRequest {
  query: string;
  kb_ids?: string[];
  top_k?: number;
  similarity_threshold?: number;
  filters?: {
    metadata?: Record<string, any>;
    date_range?: {
      start: string;
      end: string;
    };
  };
}

export interface SearchResponse {
  success: boolean;
  data?: {
    results: Array<{
      chunk_id: string;
      content: string;
      similarity: number;
      metadata: Record<string, any>;
      kb_id: string;
    }>;
    total: number;
    query_time: number;
  };
  error?: {
    code: string;
    message: string;
  };
}

export interface KbInfoResponse {
  success: boolean;
  data?: {
    id: string;
    name: string;
    description: string;
    created_at: string;
    updated_at?: string;
    document_count: number;
    chunk_count: number;
    embedding_model?: string;
    chunk_size?: number;
    chunk_overlap?: number;
  };
  error?: {
    code: string;
    message: string;
  };
}

export interface KbListResponse {
  success: boolean;
  data?: {
    knowledge_bases: Array<{
      id: string;
      name: string;
      description: string;
      created_at: string;
      document_count: number;
      chunk_count: number;
    }>;
    total: number;
  };
  error?: {
    code: string;
    message: string;
  };
} 