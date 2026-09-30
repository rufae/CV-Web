// @vitest-environment jsdom
import axe from 'axe-core';
import { act, type ReactElement } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { ChatLauncher } from '../ChatLauncher';
import { ChatPanel } from '../ChatPanel';
import { initialChatState } from '../chatReducer';

let container: HTMLDivElement;
let root: Root;

beforeEach(() => {
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
  vi.stubGlobal(
    'fetch',
    vi.fn(
      async () => new Response(JSON.stringify({ llm: 'online', tier: 'cpu' }), { status: 200 }),
    ),
  );
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

async function seriousViolations(): Promise<axe.Result[]> {
  const results = await axe.run(container);
  return results.violations.filter(
    (violation) => violation.impact === 'serious' || violation.impact === 'critical',
  );
}

describe('accesibilidad del chat', () => {
  it('el lanzador tiene nombre accesible y sin violaciones graves', async () => {
    await render(<ChatLauncher open={false} onToggle={() => undefined} />);

    expect(await seriousViolations()).toEqual([]);
  });

  it('el panel abierto no tiene violaciones graves', async () => {
    await render(
      <ChatPanel
        state={initialChatState}
        onClose={() => undefined}
        onSend={async () => undefined}
        onStop={() => undefined}
        onRetry={async () => undefined}
        onReset={() => undefined}
        onFeedback={() => undefined}
      />,
    );

    expect(await seriousViolations()).toEqual([]);
  });
});
