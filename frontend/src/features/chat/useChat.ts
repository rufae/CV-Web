import { useCallback, useEffect, useReducer, useRef } from 'react';

import { streamChat } from '@/shared/api/chatStream';
import { ApiError } from '@/shared/api/client';
import type { ErrorData, ServerEvent } from '@/shared/api/types';

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

export function useChat(): UseChat {
  const [state, dispatch] = useReducer(chatReducer, initialChatState, (initial): ChatState => ({
    ...initial,
    messages: chatPersistence.load(),
  }));
  const stateRef = useRef(state);
  const abortRef = useRef<AbortController | null>(null);
  const bufferRef = useRef('');
  const frameRef = useRef<number | null>(null);
  const lastPromptRef = useRef<string | null>(null);

  stateRef.current = state;

  useEffect(() => {
    chatPersistence.save(state.messages);
  }, [state.messages]);

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
        userMessageId: crypto.randomUUID(),
        assistantMessageId: crypto.randomUUID(),
      });

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        await streamChat(
          { message: trimmed, history: buildHistory(stateRef.current.messages) },
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
    [flushTokens, scheduleFlush],
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
