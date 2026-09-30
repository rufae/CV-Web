import type { ContactPayload, ContactResponse, FeedbackPayload } from './types';

export const API_URL: string = import.meta.env.VITE_API_URL ?? '';

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly retryAfter?: number;

  constructor(status: number, code: string, retryAfter?: number) {
    super(`${code} (HTTP ${status})`);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.retryAfter = retryAfter;
  }
}

export async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
    throw new ApiError(response.status, `http_${response.status}`);
  }
  return (await response.json()) as T;
}

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    let code = `http_${response.status}`;
    let retryAfter: number | undefined;
    try {
      const data: unknown = await response.json();
      if (typeof data === 'object' && data !== null) {
        const record = data as Record<string, unknown>;
        if (typeof record.code === 'string') code = record.code;
        if (typeof record.retry_after_s === 'number') retryAfter = record.retry_after_s;
      }
    } catch {
      // respuesta sin JSON: se conserva el código HTTP
    }
    throw new ApiError(response.status, code, retryAfter);
  }

  return (await response.json()) as T;
}

export const sendContactForm = async (formData: ContactPayload): Promise<ContactResponse> => {
  return postJson<ContactResponse>('/contact', formData);
};

export const sendFeedback = async (payload: FeedbackPayload): Promise<void> => {
  await postJson<{ status: string }>('/api/feedback', payload);
};
