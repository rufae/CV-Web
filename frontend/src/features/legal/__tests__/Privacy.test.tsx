import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import { Privacy } from '../Privacy';

describe('Privacy', () => {
  it('menciona las garantías clave (sin cookies, sin conversaciones, retención)', () => {
    const html = renderToStaticMarkup(<Privacy />);

    expect(html).toContain('No hay cookies de seguimiento');
    expect(html).toContain('No se almacenan tus conversaciones');
    expect(html).toContain('12 meses');
    expect(html).toContain('RGPD');
  });
});
