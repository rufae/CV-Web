import { API_URL, ApiError } from './client';
import { parseSseStream } from './sse';
import type { ChatRequest, ServerEvent } from './types';

export interface ChatStreamHandlers {
  signal?: AbortSignal;
  onEvent: (event: ServerEvent) => void;
}

/**
 * Abre `POST /api/chat` (SSE) y entrega los eventos tipados.
 * Sin reconexión automática: cada intento consume presupuesto.
 */
export async function streamChat(
  request: ChatRequest,
  handlers: ChatStreamHandlers,
): Promise<void> {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
    signal: handlers.signal,
  });

  if (!response.ok) {
    let code = `http_${response.status}`;
    let retryAfter: number | undefined;
    try {
      const data = (await response.json()) as Record<string, unknown>;
      if (typeof data.code === 'string') {
        code = data.code;
      }
      if (typeof data.retry_after_s === 'number') {
        retryAfter = data.retry_after_s;
      }
    } catch {
      // respuesta sin JSON: se conserva el código HTTP
    }
    throw new ApiError(response.status, code, retryAfter);
  }

  if (!response.body) {
    throw new ApiError(0, 'no_stream');
  }

  for await (const event of parseSseStream(response.body)) {
    handlers.onEvent(event);
  }
}
