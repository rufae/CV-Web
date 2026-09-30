import { describe, expect, it } from 'vitest';

import { cn } from './utils';

describe('cn', () => {
  it('combina clases y resuelve conflictos de Tailwind', () => {
    expect(cn('p-2', 'p-4')).toBe('p-4');
  });

  it('ignora valores vacíos', () => {
    expect(cn('text-sm', undefined, null, 'font-bold')).toBe('text-sm font-bold');
  });
});
