import { createContext, useContext } from 'react';

import type { Dictionary } from '@/content/dictionary';
import { EN } from '@/content/en';
import { ES } from '@/content/es';
import type { Lang } from '@/content/types';

const STORAGE_KEY = 'cvweb.lang';
export const DICTIONARIES: Record<Lang, Dictionary> = { es: ES, en: EN };

export const TITLES: Record<Lang, string> = {
  es: 'Rafael Castaño — Ingeniero de software e IA aplicada',
  en: 'Rafael Castaño — Software & Applied AI Engineer',
};

export const DESCRIPTIONS: Record<Lang, string> = {
  es: 'Portfolio de Rafael Castaño, ingeniero de software especializado en IA aplicada: LLM locales, RAG, evaluación medible y un asistente con el que puedes hablar.',
  en: 'Portfolio of Rafael Castaño, software engineer specialised in applied AI: local LLMs, RAG, measurable evaluation and an assistant you can talk to.',
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
