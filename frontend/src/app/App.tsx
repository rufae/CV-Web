import { lazy, Suspense, useEffect, useState } from 'react';

import { About } from '@/features/about/About';
import { AiLab } from '@/features/ai-lab/AiLab';
import { Privacy } from '@/features/legal/Privacy';
import { Contact } from '@/features/contact/Contact';
import { Education } from '@/features/education/Education';
import { Experience } from '@/features/experience/Experience';
import { Footer } from '@/features/footer/Footer';
import { Header } from '@/features/header/Header';
import { Hero } from '@/features/hero/Hero';
import { Projects } from '@/features/projects/Projects';
import { Stack } from '@/features/stack/Stack';
import { useI18n } from '@/shared/lib/i18n';
import { I18nProvider } from '@/shared/lib/i18n-provider';
import { Toaster } from '@/shared/ui/sonner';

import { ThemeContext } from './theme-context';

const Chat = lazy(() => import('@/features/chat/Chat'));

const NAV_SECTIONS = ['projects', 'ai-lab', 'experience', 'education', 'stack', 'contact'] as const;

function AppContent() {
  const { t } = useI18n();
  const [theme, setTheme] = useState<'light' | 'dark'>(() =>
    typeof document !== 'undefined' && document.documentElement.classList.contains('dark')
      ? 'dark'
      : 'light',
  );
  const [activeSection, setActiveSection] = useState('hero');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    document.documentElement.style.colorScheme = theme;
  }, [theme]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        }
      },
      { rootMargin: '-40% 0px -55% 0px' },
    );
    for (const id of NAV_SECTIONS) {
      const element = document.getElementById(id);
      if (element !== null) {
        observer.observe(element);
      }
    }
    return () => observer.disconnect();
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <div className="min-h-screen overflow-x-hidden bg-background text-foreground">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded-md focus:bg-accent-strong focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-white"
        >
          {t.common.skipToContent}
        </a>

        <Header theme={theme} onToggleTheme={toggleTheme} activeSection={activeSection} />

        <main id="main" className="pt-16">
          <Hero />
          <Projects />
          <AiLab />
          <Experience />
          <Education />
          <Stack />
          <About />
          <Contact />
          <Privacy />
        </main>

        <Footer />
        {mounted && (
          <>
            <Suspense fallback={null}>
              <Chat />
            </Suspense>
            <Toaster />
          </>
        )}
      </div>
    </ThemeContext.Provider>
  );
}

export default function App() {
  return (
    <I18nProvider>
      <AppContent />
    </I18nProvider>
  );
}
