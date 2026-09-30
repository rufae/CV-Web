import type { ChatStatus } from './chatReducer';

export type LlmState = 'online' | 'degraded' | 'offline';

export interface StatusView {
  offline: boolean;
  degraded: boolean;
  rateLimited: boolean;
  retryAfter: number;
  composerBlocked: boolean;
}

/** Deriva qué avisos mostrar y si el compositor debe bloquearse. */
export function statusView(chat: ChatStatus, retryAfter: number, llm: LlmState | null): StatusView {
  const offline = llm === 'offline';
  const degraded = llm === 'degraded';
  const rateLimited = chat === 'rate_limited';
  return {
    offline,
    degraded,
    rateLimited,
    retryAfter,
    composerBlocked: offline || rateLimited,
  };
}

export function formatRetry(seconds: number): string {
  return seconds > 0 ? `Reintenta en ${seconds} s` : 'Ya puedes reintentar';
}
