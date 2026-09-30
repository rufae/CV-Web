import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import { renderMarkdown } from '../markdown';

function html(text: string): string {
  return renderToStaticMarkup(<>{renderMarkdown(text)}</>);
}

describe('renderMarkdown', () => {
  it('convierte negritas y listas', () => {
    const result = html('**Hola**\n- uno\n- dos');

    expect(result).toContain('<strong>Hola</strong>');
    expect(result).toContain('<li>uno</li>');
    expect(result).toContain('<li>dos</li>');
  });

  it('convierte citas [n] en superíndices', () => {
    expect(html('Trabaja en AePTIC [1].')).toContain('<sup class="text-accent">1</sup>');
  });

  it('renderiza enlaces http(s) seguros con rel', () => {
    const result = html('Ver [GitHub](https://github.com/rufae).');

    expect(result).toContain('href="https://github.com/rufae"');
    expect(result).toContain('rel="noopener noreferrer"');
    expect(result).toContain('target="_blank"');
  });

  it('no convierte javascript: en enlace (queda como texto)', () => {
    const result = html('[click](javascript:alert(1))');

    expect(result).not.toContain('<a');
    expect(result).toContain('javascript:alert(1)');
  });

  it('escapa HTML crudo', () => {
    const result = html('<script>alert(1)</script>');

    expect(result).not.toContain('<script>');
    expect(result).toContain('&lt;script&gt;');
  });
});
