// @vitest-environment jsdom
import axe from 'axe-core';
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import App from '@/app/App';

let container: HTMLDivElement;
let root: Root;

class FakeIntersectionObserver {
  observe(): void {
    return;
  }

  unobserve(): void {
    return;
  }

  disconnect(): void {
    return;
  }
}

beforeEach(() => {
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
  vi.stubGlobal('IntersectionObserver', FakeIntersectionObserver);
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes('/api/status')) {
        return new Response(JSON.stringify({ llm: 'online', tier: 'gpu' }), { status: 200 });
      }
      if (url.includes('/eval-latest.json')) {
        return new Response(
          JSON.stringify({
            metrics: { recall_at_k: 1, refusal_recall: 1, leaks: 0 },
            embed_model: 'bge-m3',
          }),
          { status: 200 },
        );
      }
      return new Response('{}', { status: 200 });
    }),
  );
});

afterEach(async () => {
  await act(async () => {
    root.unmount();
  });
  container.remove();
  document.documentElement.classList.remove('dark');
  vi.unstubAllGlobals();
});

async function seriousViolations(): Promise<axe.Result[]> {
  const results = await axe.run(container, {
    rules: { 'color-contrast': { enabled: false } },
  });
  return results.violations.filter(
    (violation) => violation.impact === 'serious' || violation.impact === 'critical',
  );
}

describe('accesibilidad de la app completa', () => {
  it('sin violaciones graves en tema claro', async () => {
    await act(async () => {
      root.render(<App />);
    });

    expect(await seriousViolations()).toEqual([]);
  });

  it('sin violaciones graves en tema oscuro', async () => {
    document.documentElement.classList.add('dark');
    await act(async () => {
      root.render(<App />);
    });

    expect(await seriousViolations()).toEqual([]);
  });
});
