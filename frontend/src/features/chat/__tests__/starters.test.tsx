import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import { STARTERS } from '@/content/starters';

import { Starters } from '../Starters';

describe('Starters', () => {
  it('renderiza los botones iniciales', () => {
    const html = renderToStaticMarkup(<Starters onSelect={() => undefined} />);

    for (const starter of STARTERS) {
      expect(html).toContain(starter);
    }
    expect(html).toContain('Prueba con');
  });
});
