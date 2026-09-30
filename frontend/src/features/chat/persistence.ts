import type { ChatMessage } from './chatReducer';

interface StorageLike {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
  removeItem(key: string): void;
}

const KEY = 'cvweb.chat.messages';

export function createChatPersistence(storage: StorageLike | null) {
  return {
    load(): ChatMessage[] {
      try {
        const raw = storage?.getItem(KEY);
        return raw ? (JSON.parse(raw) as ChatMessage[]) : [];
      } catch {
        return [];
      }
    },
    save(messages: ChatMessage[]): void {
      try {
        storage?.setItem(KEY, JSON.stringify(messages));
      } catch {
        // almacenamiento lleno o no disponible: la conversación sigue en memoria
      }
    },
    clear(): void {
      storage?.removeItem(KEY);
    },
  };
}

export const chatPersistence = createChatPersistence(
  typeof window !== 'undefined' ? window.sessionStorage : null,
);
