import { describe, expect, it } from 'vitest';

import { EN } from '@/content/en';
import { ES } from '@/content/es';
import { pickLang } from '@/shared/lib/i18n';

function flattenKeys(value: object, prefix = ''): string[] {
  return Object.entries(value).flatMap(([key, child]) => {
    const path = prefix === '' ? key : `${prefix}.${key}`;
    if (typeof child === 'object' && child !== null && !Array.isArray(child)) {
      return flattenKeys(child, path);
    }
    return [path];
  });
}

describe('diccionarios i18n', () => {
  it('ES y EN tienen exactamente las mismas claves', () => {
    expect(flattenKeys(EN).sort()).toEqual(flattenKeys(ES).sort());
  });

  it('los arrays tienen la misma longitud', () => {
    expect(EN.chat.starters).toHaveLength(ES.chat.starters.length);
    expect(EN.about.facts).toHaveLength(ES.about.facts.length);
  });
});

describe('pickLang', () => {
  it('respeta la preferencia guardada', () => {
    expect(pickLang('en', 'es-ES')).toBe('en');
    expect(pickLang('es', 'en-US')).toBe('es');
  });

  it('detecta por navegador cuando no hay preferencia', () => {
    expect(pickLang(null, 'en-GB')).toBe('en');
    expect(pickLang(null, 'es-ES')).toBe('es');
    expect(pickLang(null, 'fr-FR')).toBe('es');
  });
});
