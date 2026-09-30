import { createContext, useContext } from 'react';

import type { Dictionary } from '@/content/dictionary';
import { EN } from '@/content/en';
import { ES } from '@/content/es';
import type { Lang } from '@/content/types';

const STORAGE_KEY = 'cvweb.lang';
export const DICTIONARIES: Record<Lang, Dictionary> = { es: ES, en: EN };

export const TITLES: Record<Lang, string> = {
  es: 'Rafael Castaño — Full Stack Developer',
  en: 'Rafael Castaño — Full Stack Developer (English)',
};

export const DESCRIPTIONS: Record<Lang, string> = {
  es: 'Portfolio de Rafael Castaño, desarrollador Full Stack en Sevilla: experiencia, proyectos con IA, habilidades y asistente virtual con RAG.',
  en: 'Portfolio of Rafael Castaño, Full Stack developer in Seville: experience, AI projects, skills and a RAG-powered virtual assistant.',
};

export function pickLang(stored: string | null, navigatorLang: string): Lang {
  if (stored === 'es' || stored === 'en') {
    return stored;
  }
  return navigatorLang.toLowerCase().startsWith('en') ? 'en' : 'es';
}

export function detectLang(): Lang {
  if (typeof window === 'undefined') {
    return 'es';
  }
  return pickLang(window.localStorage.getItem(STORAGE_KEY), window.navigator.language);
}

export interface I18nValue {
  lang: Lang;
  t: Dictionary;
  setLang: (lang: Lang) => void;
}

export const I18nContext = createContext<I18nValue>({
  lang: 'es',
  t: ES,
  setLang: () => undefined,
});

export function useI18n(): I18nValue {
  return useContext(I18nContext);
}
