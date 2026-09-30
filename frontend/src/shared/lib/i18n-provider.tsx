import { useEffect, useState, type ReactNode } from 'react';

import type { Lang } from '@/content/types';

import { DESCRIPTIONS, DICTIONARIES, I18nContext, TITLES, detectLang } from './i18n';

const STORAGE_KEY = 'cvweb.lang';

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>('es');

  useEffect(() => {
    setLangState(detectLang());
  }, []);

  const setLang = (next: Lang) => {
    setLangState(next);
    window.localStorage.setItem(STORAGE_KEY, next);
  };

  useEffect(() => {
    document.documentElement.lang = lang;
    document.title = TITLES[lang];
    const description = document.querySelector('meta[name="description"]');
    if (description !== null) {
      description.setAttribute('content', DESCRIPTIONS[lang]);
    }
  }, [lang]);

  return (
    <I18nContext.Provider value={{ lang, t: DICTIONARIES[lang], setLang }}>
      {children}
    </I18nContext.Provider>
  );
}
