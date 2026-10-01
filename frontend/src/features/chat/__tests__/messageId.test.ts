// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest';

import { newMessageId } from '../useChat';

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('newMessageId', () => {
  it('usa crypto.randomUUID cuando está disponible', () => {
    const randomUUID = vi.fn(() => '123e4567-e89b-42d3-a456-426614174000');
    vi.stubGlobal('crypto', { randomUUID });

    expect(newMessageId()).toBe('123e4567-e89b-42d3-a456-426614174000');
    expect(randomUUID).toHaveBeenCalled();
  });

  it('genera un id válido en contextos no seguros (sin randomUUID)', () => {
    vi.stubGlobal('crypto', {});

    const id = newMessageId();

    expect(typeof id).toBe('string');
    expect(id.length).toBeGreaterThan(8);
    expect(newMessageId()).not.toBe(id);
  });
});
