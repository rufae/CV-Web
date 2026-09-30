import { describe, expect, it } from 'vitest';

import { validateForm } from '../validation';

describe('validateForm', () => {
  const valid = { name: 'Ana', email: 'ana@example.com', message: 'Hola' };

  it('acepta datos válidos', () => {
    expect(validateForm(valid)).toBeNull();
  });

  it('rechaza nombre vacío o demasiado largo', () => {
    expect(validateForm({ ...valid, name: '  ' })).toContain('nombre');
    expect(validateForm({ ...valid, name: 'x'.repeat(101) })).toContain('nombre');
  });

  it('rechaza email inválido', () => {
    expect(validateForm({ ...valid, email: 'sin-arroba' })).toContain('email');
  });

  it('rechaza mensaje vacío o demasiado largo', () => {
    expect(validateForm({ ...valid, message: ' ' })).toContain('mensaje');
    expect(validateForm({ ...valid, message: 'x'.repeat(2001) })).toContain('mensaje');
  });
});
