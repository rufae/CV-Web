import { describe, expect, it } from 'vitest';

import type { ErrorData } from '@/shared/api/types';

import {
  buildHistory,
  chatReducer,
  initialChatState,
  type ChatAction,
  type ChatState,
} from '../chatReducer';

function reduce(actions: ChatAction[]): ChatState {
  return actions.reduce(chatReducer, initialChatState);
}

const SEND: ChatAction = {
  type: 'send',
  text: '¿Dónde trabaja?',
  userMessageId: 'u1',
  assistantMessageId: 'a1',
};

describe('chatReducer', () => {
  it('send pasa a retrieving y añade usuario + asistente vacío', () => {
    const state = reduce([SEND]);

    expect(state.status).toBe('retrieving');
    expect(state.messages).toHaveLength(2);
    expect(state.messages[0]).toMatchObject({ role: 'user', text: '¿Dónde trabaja?' });
    expect(state.messages[1]).toMatchObject({ role: 'assistant', text: '' });
  });

  it('meta asigna id, versión y tier al asistente', () => {
    const state = reduce([
      SEND,
      { type: 'meta', messageId: 'm1', promptVersion: 'v1', tier: 'gpu' },
    ]);

    expect(state.messages[1]).toMatchObject({
      messageId: 'm1',
      promptVersion: 'v1',
      tier: 'gpu',
    });
  });

  it('sources y token se acumulan y pasa a streaming', () => {
    const state = reduce([
      SEND,
      { type: 'sources', sources: [{ n: 1, title: 'Experiencia', section: 'AePTIC' }] },
      { type: 'token', text: 'Rafael ' },
      { type: 'token', text: 'trabaja en AePTIC' },
    ]);

    expect(state.status).toBe('streaming');
    expect(state.messages[1].text).toBe('Rafael trabaja en AePTIC');
    expect(state.messages[1].sources).toHaveLength(1);
  });

  it('refusal marca refused con el mensaje estándar', () => {
    const state = reduce([
      SEND,
      { type: 'refusal', message: 'No dispongo de esa información', reason: 'no_context' },
    ]);

    expect(state.status).toBe('refused');
    expect(state.messages[1]).toMatchObject({
      text: 'No dispongo de esa información',
      refused: true,
    });
  });

  it('done vuelve a idle', () => {
    const state = reduce([SEND, { type: 'done', firstTokenMs: 10, totalMs: 50 }]);

    expect(state.status).toBe('idle');
  });

  it('done tras refusal mantiene el aviso de rechazo', () => {
    const state = reduce([
      SEND,
      { type: 'refusal', message: 'No dispongo de esa información', reason: 'no_context' },
      { type: 'done', firstTokenMs: null, totalMs: 10 },
    ]);

    expect(state.status).toBe('refused');
  });

  it('rate_limited guarda retry_after', () => {
    const error: ErrorData = {
      code: 'rate_limited',
      message: 'demasiadas peticiones',
      retry_after_s: 42,
    };

    const state = reduce([SEND, { type: 'error', error }]);

    expect(state.status).toBe('rate_limited');
    expect(state.retryAfter).toBe(42);
  });

  it('error genérico pasa a error', () => {
    const state = reduce([
      SEND,
      {
        type: 'error',
        error: { code: 'provider_unavailable', message: 'caído', retry_after_s: null },
      },
    ]);

    expect(state.status).toBe('error');
    expect(state.error?.code).toBe('provider_unavailable');
  });

  it('stop conserva el texto recibido y vuelve a idle', () => {
    const state = reduce([SEND, { type: 'token', text: 'parcial' }, { type: 'stop' }]);

    expect(state.status).toBe('idle');
    expect(state.messages[1].text).toBe('parcial');
  });

  it('reset limpia el estado', () => {
    const state = reduce([SEND, { type: 'reset' }]);

    expect(state).toEqual(initialChatState);
  });
});

describe('buildHistory', () => {
  it('excluye mensajes vacíos y recorta a 12 entradas', () => {
    const messages = Array.from({ length: 20 }, (_, index) => ({
      id: `m${index}`,
      role: (index % 2 === 0 ? 'user' : 'assistant') as 'user' | 'assistant',
      text: `mensaje ${index}`,
      sources: [],
    }));

    const history = buildHistory([
      ...messages,
      { id: 'vacio', role: 'assistant', text: '  ', sources: [] },
    ]);

    expect(history).toHaveLength(12);
    expect(history[0].content).toBe('mensaje 8');
    expect(history.at(-1)?.content).toBe('mensaje 19');
  });
});
