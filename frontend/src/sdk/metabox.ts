import type {
  MetaBoxClientOptions,
  QueryRequest,
  QueryResponse,
  SearchRequest,
  SearchResponse,
  KbInfoResponse,
  KbListResponse
} from './types';
import { apiRequest, streamRequest } from './api';

export class MetaBoxClient {
  private apiKey: string;
  private baseUrl: string;

  constructor(options: MetaBoxClientOptions) {
    this.apiKey = options.apiKey;
    this.baseUrl = options.baseUrl || '/api/v1';
  }

  async query(data: QueryRequest): Promise<QueryResponse> {
    return apiRequest<QueryResponse>(`${this.baseUrl}/chat/query`, data, this.apiKey);
  }

  async search(data: SearchRequest): Promise<SearchResponse> {
    return apiRequest<SearchResponse>(`${this.baseUrl}/retrieval/search`, data, this.apiKey);
  }

  async getKbList(): Promise<KbListResponse> {
    return apiRequest<KbListResponse>(`${this.baseUrl}/kb/list`, {}, this.apiKey);
  }

  async getKbInfo(kb_id: string): Promise<KbInfoResponse> {
    return apiRequest<KbInfoResponse>(`${this.baseUrl}/kb/${kb_id}/info`, {}, this.apiKey);
  }

  streamQuery(
    data: QueryRequest,
    onMessage: (msg: any) => void,
    onError?: (err: any) => void
  ) {
    return streamRequest(`${this.baseUrl}/chat/query`, data, this.apiKey, onMessage, onError);
  }
} 