import type { ChatTurn, ErrorData, RefusalReason, SourceItem, Tier } from '@/shared/api/types';

export type ChatStatus = 'idle' | 'retrieving' | 'streaming' | 'error' | 'rate_limited' | 'refused';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  sources: SourceItem[];
  messageId?: string;
  promptVersion?: string;
  tier?: Tier;
  refused?: boolean;
}

export interface ChatState {
  status: ChatStatus;
  messages: ChatMessage[];
  error: ErrorData | null;
  retryAfter: number;
}

export type ChatAction =
  | { type: 'send'; text: string; userMessageId: string; assistantMessageId: string }
  | { type: 'meta'; messageId: string; promptVersion: string; tier: Tier }
  | { type: 'sources'; sources: SourceItem[] }
  | { type: 'token'; text: string }
  | { type: 'refusal'; message: string; reason: RefusalReason }
  | { type: 'done'; firstTokenMs: number | null; totalMs: number }
  | { type: 'error'; error: ErrorData }
  | { type: 'stop' }
  | { type: 'reset' };

export const MAX_HISTORY_TURNS = 6;

export const initialChatState: ChatState = {
  status: 'idle',
  messages: [],
  error: null,
  retryAfter: 0,
};

export function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'send':
      return {
        ...state,
        status: 'retrieving',
        error: null,
        retryAfter: 0,
        messages: [
          ...state.messages,
          {
            id: action.userMessageId,
            role: 'user',
            text: action.text,
            sources: [],
          },
          {
            id: action.assistantMessageId,
            role: 'assistant',
            text: '',
            sources: [],
          },
        ],
      };

    case 'meta':
      return updateLastAssistant(state, (message) => ({
        ...message,
        messageId: action.messageId,
        promptVersion: action.promptVersion,
        tier: action.tier,
      }));

    case 'sources':
      return updateLastAssistant(state, (message) => ({
        ...message,
        sources: action.sources,
      }));

    case 'token':
      return {
        ...updateLastAssistant(state, (message) => ({
          ...message,
          text: message.text + action.text,
        })),
        status: 'streaming',
      };

    case 'refusal':
      return {
        ...updateLastAssistant(state, (message) => ({
          ...message,
          text: action.message,
          refused: true,
        })),
        status: 'refused',
      };

    case 'done':
      return { ...state, status: state.status === 'refused' ? 'refused' : 'idle' };

    case 'error': {
      const limited =
        action.error.code === 'rate_limited' || action.error.code === 'daily_budget_exhausted';
      return {
        ...state,
        status: limited ? 'rate_limited' : 'error',
        error: action.error,
        retryAfter: action.error.retry_after_s ?? 0,
      };
    }

    case 'stop':
      return { ...state, status: 'idle' };

    case 'reset':
      return initialChatState;

    default:
      return state;
  }
}

function updateLastAssistant(
  state: ChatState,
  update: (message: ChatMessage) => ChatMessage,
): ChatState {
  const messages = [...state.messages];
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    if (messages[index].role === 'assistant') {
      messages[index] = update(messages[index]);
      break;
    }
  }
  return { ...state, messages };
}

export function buildHistory(
  messages: ChatMessage[],
  maxTurns: number = MAX_HISTORY_TURNS,
): ChatTurn[] {
  const usable = messages.filter((message) => message.text.trim() !== '');
  return usable
    .slice(-(maxTurns * 2))
    .map((message) => ({ role: message.role, content: message.text }));
}
