import type {
  MetaBoxClientOptions,
  QueryRequest,
  QueryResponse,
  SearchRequest,
  SearchResponse,
  KbInfoResponse,
  KbListResponse
} from './types';
import { MetaBoxAPI, streamRequest } from './api';

export class MetaBoxClient {
  private api: MetaBoxAPI;

  constructor(options: MetaBoxClientOptions) {
    this.api = new MetaBoxAPI(options.baseUrl || '/api/v1', options.apiKey);
  }

  async query(data: QueryRequest): Promise<QueryResponse> {
    return this.api.query(data);
  }

  async search(data: SearchRequest): Promise<SearchResponse> {
    const kbId = data.kb_ids && data.kb_ids.length > 0 ? data.kb_ids[0] : '';
    return this.api.search(data.query, kbId, data.top_k || 10);
  }

  async getKbList(): Promise<KbListResponse> {
    return this.api.getKnowledgeBases();
  }

  async getKbInfo(kb_id: string): Promise<KbInfoResponse> {
    return this.api.getKnowledgeBase(kb_id);
  }

  streamQuery(
    data: QueryRequest,
    onMessage: (msg: any) => void,
    onError?: (err: any) => void
  ) {
    const baseUrl = (this.api as any).baseUrl;
    const apiKey = (this.api as any).apiKey || '';
    return streamRequest(`${baseUrl}/chat/query`, data, apiKey, onMessage, onError);
  }
} 