import type { QueryRequest, SearchRequest } from './types';

export async function apiRequest<T>(url: string, data: any, apiKey: string): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

export function streamRequest(
  url: string,
  data: QueryRequest,
  apiKey: string,
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