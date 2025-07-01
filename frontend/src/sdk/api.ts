import type { QueryRequest } from './types';

export class MetaBoxAPI {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string = '/api/v1', apiKey?: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const response = await fetch(url, {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  async query(
    data: QueryRequest,
  ): Promise<any> {
    return this.request('/chat/query', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async search(
    query: string,
    kbId: string,
    limit: number = 10
  ): Promise<any> {
    return this.request('/search', {
      method: 'POST',
      body: JSON.stringify({
        query,
        kb_id: kbId,
        limit,
      }),
    });
  }

  async getKnowledgeBases(): Promise<any> {
    return this.request('/knowledge-bases');
  }

  async getKnowledgeBase(id: string): Promise<any> {
    return this.request(`/knowledge-bases/${id}`);
  }

  async createKnowledgeBase(data: any): Promise<any> {
    return this.request('/knowledge-bases', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateKnowledgeBase(id: string, data: any): Promise<any> {
    return this.request(`/knowledge-bases/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteKnowledgeBase(id: string): Promise<any> {
    return this.request(`/knowledge-bases/${id}`, {
      method: 'DELETE',
    });
  }

  async uploadDocument(kbId: string, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const url = `${this.baseUrl}/knowledge-bases/${kbId}/documents`;
    const headers: Record<string, string> = {};

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getApiKeys(): Promise<any> {
    return this.request('/api-keys');
  }

  async createApiKey(data: any): Promise<any> {
    return this.request('/api-keys', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteApiKey(id: string): Promise<any> {
    return this.request(`/api-keys/${id}`, {
      method: 'DELETE',
    });
  }
}

export function streamRequest(
  url: string,
  _data: QueryRequest,
  _apiKey: string,
  onMessage: (msg: any) => void,
  onError?: (err: any) => void
) {
  const es = new EventSource(url + '?stream=true', {
    withCredentials: false,
  } as any);
  es.onmessage = (event) => {
    try {
      const parsed = JSON.parse(event.data);
      onMessage(parsed);
    } catch (e) {
      onError?.(e);
    }
  };
  es.onerror = (err) => {
    onError?.(err);
    es.close();
  };
  // 发送POST数据需用fetch+SSE polyfill，或后端支持GET参数流式
  return es;
} 