// @vitest-environment jsdom
import { act, type ReactElement } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { AiLab } from '../AiLab';

let container: HTMLDivElement;
let root: Root;

beforeEach(() => {
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
});

afterEach(async () => {
  await act(async () => {
    root.unmount();
  });
  container.remove();
  vi.unstubAllGlobals();
});

async function render(element: ReactElement): Promise<void> {
  await act(async () => {
    root.render(element);
  });
}

function stubFetch(handler: (url: string) => Promise<Response>): void {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL) => handler(String(input))),
  );
}

describe('AiLab', () => {
  it('muestra las métricas del informe y el estado en vivo', async () => {
    stubFetch(async (url) => {
      if (url.includes('/eval-latest.json')) {
        return new Response(
          JSON.stringify({
            metrics: { recall_at_k: 0.95, refusal_recall: 0.97, leaks: 0 },
            embed_model: 'bge-m3:latest',
          }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({ llm: 'online', tier: 'gpu' }), { status: 200 });
    });

    await render(<AiLab />);

    expect(container.textContent).toContain('0.950');
    expect(container.textContent).toContain('0.970');
    expect(container.textContent).toContain('En línea');
    expect(container.textContent).toContain('bge-m3:latest');
  });

  it('degrada a datos estáticos si la API y el informe no están disponibles', async () => {
    stubFetch(async () => {
      throw new Error('sin red');
    });

    await render(<AiLab />);

    expect(container.textContent).toContain('1.000');
    expect(container.textContent).toContain('Sin conexión');
    expect(container.textContent).toContain('bge-m3');
  });
});
