import { describe, expect, it } from 'vitest';

import { formatRetry, statusView } from '../statusView';

describe('statusView', () => {
  it('offline bloquea el compositor', () => {
    const view = statusView('idle', 0, 'offline');

    expect(view.offline).toBe(true);
    expect(view.composerBlocked).toBe(true);
  });

  it('degraded avisa pero no bloquea', () => {
    const view = statusView('idle', 0, 'degraded');

    expect(view.degraded).toBe(true);
    expect(view.composerBlocked).toBe(false);
  });

  it('rate_limited bloquea hasta reintentar', () => {
    const view = statusView('rate_limited', 42, 'online');

    expect(view.rateLimited).toBe(true);
    expect(view.composerBlocked).toBe(true);
    expect(view.retryAfter).toBe(42);
  });

  it('estado normal no muestra avisos', () => {
    const view = statusView('idle', 0, 'online');

    expect(view.offline).toBe(false);
    expect(view.degraded).toBe(false);
    expect(view.rateLimited).toBe(false);
    expect(view.composerBlocked).toBe(false);
  });
});

describe('formatRetry', () => {
  it('cuenta atrás y mensaje final', () => {
    expect(formatRetry(42)).toBe('Reintenta en 42 s');
    expect(formatRetry(0)).toBe('Ya puedes reintentar');
  });
});
