import { useCallback, useEffect, useReducer, useRef } from 'react';

import { streamChat } from '@/shared/api/chatStream';
import { ApiError } from '@/shared/api/client';
import type { ErrorData, ServerEvent } from '@/shared/api/types';
import type { Lang } from '@/content/types';

import {
  buildHistory,
  chatReducer,
  initialChatState,
  type ChatAction,
  type ChatState,
} from './chatReducer';
import { chatPersistence } from './persistence';

function mapEvent(event: ServerEvent): ChatAction | null {
  switch (event.event) {
    case 'meta':
      return {
        type: 'meta',
        messageId: event.data.message_id,
        promptVersion: event.data.prompt_version,
        tier: event.data.tier,
      };
    case 'sources':
      return { type: 'sources', sources: event.data.sources };
    case 'token':
      return { type: 'token', text: event.data.t };
    case 'refusal':
      return { type: 'refusal', message: event.data.message, reason: event.data.reason };
    case 'done':
      return {
        type: 'done',
        firstTokenMs: event.data.first_token_ms,
        totalMs: event.data.total_ms,
      };
    case 'error':
      return { type: 'error', error: event.data };
    default:
      return null;
  }
}

export interface UseChat {
  state: ChatState;
  send: (text: string) => Promise<void>;
  stop: () => void;
  retry: () => Promise<void>;
  reset: () => void;
}

export interface UseChatOptions {
  persist?: boolean;
}

/**
 * `crypto.randomUUID` solo existe en contextos seguros (HTTPS o localhost).
 * La web puede servirse por HTTP en la red local (p. ej. http://cv-web.home),
 * así que se usa un fallback para que el chat funcione igual.
 */
export function newMessageId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

export function useChat(lang: Lang = 'es', options: UseChatOptions = {}): UseChat {
  const persist = options.persist !== false;
  const [state, dispatch] = useReducer(chatReducer, initialChatState, (initial): ChatState => ({
    ...initial,
    messages: persist ? chatPersistence.load() : [],
  }));
  const stateRef = useRef(state);
  const abortRef = useRef<AbortController | null>(null);
  const bufferRef = useRef('');
  const frameRef = useRef<number | null>(null);
  const lastPromptRef = useRef<string | null>(null);

  stateRef.current = state;

  useEffect(() => {
    if (persist) {
      chatPersistence.save(state.messages);
    }
  }, [persist, state.messages]);

  const flushTokens = useCallback(() => {
    frameRef.current = null;
    if (bufferRef.current !== '') {
      const text = bufferRef.current;
      bufferRef.current = '';
      dispatch({ type: 'token', text });
    }
  }, []);

  const scheduleFlush = useCallback(() => {
    if (frameRef.current !== null) {
      return;
    }
    if (typeof requestAnimationFrame === 'function') {
      frameRef.current = requestAnimationFrame(flushTokens);
    } else {
      frameRef.current = window.setTimeout(flushTokens, 16);
    }
  }, [flushTokens]);

  const run = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (trimmed === '') {
        return;
      }
      lastPromptRef.current = trimmed;
      dispatch({
        type: 'send',
        text: trimmed,
        userMessageId: newMessageId(),
        assistantMessageId: newMessageId(),
      });

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        await streamChat(
          { message: trimmed, history: buildHistory(stateRef.current.messages), lang },
          {
            signal: controller.signal,
            onEvent: (event) => {
              if (event.event === 'token') {
                bufferRef.current += event.data.t;
                scheduleFlush();
                return;
              }
              flushTokens();
              const action = mapEvent(event);
              if (action !== null) {
                dispatch(action);
              }
            },
          },
        );
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
          dispatch({ type: 'stop' });
        } else {
          const data: ErrorData =
            error instanceof ApiError
              ? {
                  code: 'provider_unavailable',
                  message: 'El asistente no está disponible ahora mismo.',
                  retry_after_s: error.retryAfter ?? null,
                }
              : {
                  code: 'internal',
                  message: 'Ocurrió un error inesperado. Inténtalo más tarde.',
                  retry_after_s: null,
                };
          dispatch({ type: 'error', error: data });
        }
      } finally {
        flushTokens();
        abortRef.current = null;
      }
    },
    [flushTokens, scheduleFlush, lang],
  );

  const send = useCallback((text: string) => run(text), [run]);

  const stop = useCallback(() => {
    abortRef.current?.abort();
    dispatch({ type: 'stop' });
  }, []);

  const retry = useCallback(async () => {
    if (lastPromptRef.current !== null) {
      await run(lastPromptRef.current);
    }
  }, [run]);

  const reset = useCallback(() => {
    chatPersistence.clear();
    dispatch({ type: 'reset' });
  }, []);

  return { state, send, stop, retry, reset };
}
