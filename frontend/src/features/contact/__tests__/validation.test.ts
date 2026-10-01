import { describe, expect, it } from 'vitest';

import { validateForm } from '../validation';

describe('validateForm', () => {
  const valid = { name: 'Ana', email: 'ana@example.com', message: 'Hola' };

  it('acepta datos válidos', () => {
    expect(validateForm(valid)).toBeNull();
  });

  it('rechaza nombre vacío o demasiado largo', () => {
    expect(validateForm({ ...valid, name: '  ' })).toBe('name');
    expect(validateForm({ ...valid, name: 'x'.repeat(101) })).toBe('name');
  });

  it('rechaza email inválido', () => {
    expect(validateForm({ ...valid, email: 'sin-arroba' })).toBe('email');
  });

  it('rechaza mensaje vacío o demasiado largo', () => {
    expect(validateForm({ ...valid, message: ' ' })).toBe('message');
    expect(validateForm({ ...valid, message: 'x'.repeat(2001) })).toBe('message');
  });
});
