import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import { ES } from '@/content/es';

import { Starters } from '../Starters';

describe('Starters', () => {
  it('renderiza los botones iniciales', () => {
    const html = renderToStaticMarkup(<Starters onSelect={() => undefined} />);

    for (const starter of ES.chat.starters) {
      expect(html).toContain(starter);
    }
    expect(html).toContain('Prueba con');
  });
});
