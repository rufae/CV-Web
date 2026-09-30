import { describe, expect, it } from 'vitest';

import { createChatPersistence } from '../persistence';

class FakeStorage {
  private readonly map = new Map<string, string>();

  getItem(key: string): string | null {
    return this.map.get(key) ?? null;
  }

  setItem(key: string, value: string): void {
    this.map.set(key, value);
  }

  removeItem(key: string): void {
    this.map.delete(key);
  }

  corrupt(value: string): void {
    this.map.set('cvweb.chat.messages', value);
  }
}

describe('chatPersistence', () => {
  it('guarda, carga y limpia la conversación', () => {
    const storage = new FakeStorage();
    const persistence = createChatPersistence(storage);
    const messages = [
      { id: 'm1', role: 'user' as const, text: 'hola', sources: [] },
      { id: 'm2', role: 'assistant' as const, text: 'buenas', sources: [] },
    ];

    persistence.save(messages);

    expect(persistence.load()).toEqual(messages);

    persistence.clear();
    expect(persistence.load()).toEqual([]);
  });

  it('tolera JSON corrupto y almacenamiento ausente', () => {
    const storage = new FakeStorage();
    storage.corrupt('{esto no es json');

    expect(createChatPersistence(storage).load()).toEqual([]);
    expect(createChatPersistence(null).load()).toEqual([]);
    expect(() => createChatPersistence(null).save([])).not.toThrow();
  });
});
