import { lazy, Suspense, useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';

import { About } from '@/features/about/About';
import { AiLab } from '@/features/ai-lab/AiLab';
import { Contact } from '@/features/contact/Contact';
import { Experience } from '@/features/experience/Experience';
import { Footer } from '@/features/footer/Footer';
import { Hero } from '@/features/hero/Hero';
import { Projects } from '@/features/projects/Projects';
import { Skills } from '@/features/skills/Skills';
import { useI18n } from '@/shared/lib/i18n';
import { I18nProvider } from '@/shared/lib/i18n-provider';
import { Button } from '@/shared/ui/button';
import { Toaster } from '@/shared/ui/sonner';

import { ThemeContext } from './theme-context';

const Chat = lazy(() => import('@/features/chat/Chat'));
const SECTIONS = [
  'hero',
  'about',
  'experience',
  'projects',
  'skills',
  'ai-lab',
  'contact',
] as const;

function AppContent() {
  const { lang, t, setLang } = useI18n();
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
    for (const id of SECTIONS) {
      const element = document.getElementById(id);
      if (element !== null) {
        observer.observe(element);
      }
    }
    return () => observer.disconnect();
  }, []);

  const navLabels = [
    t.nav.home,
    t.nav.about,
    t.nav.experience,
    t.nav.projects,
    t.nav.skills,
    t.nav.lab,
    t.nav.contact,
  ];

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <div className="min-h-screen overflow-x-hidden bg-background text-foreground">
        {/* Controles fijos: idioma + tema */}
        <div className="fixed top-6 right-6 z-50 flex items-center gap-2">
          <div
            role="group"
            aria-label="Idioma / Language"
            className="flex rounded-full border border-border/50 bg-card/80 p-1 backdrop-blur-sm"
          >
            {(['es', 'en'] as const).map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setLang(option)}
                aria-pressed={lang === option}
                className={`rounded-full px-2 py-1 text-xs font-semibold transition-colors ${
                  lang === option
                    ? 'bg-accent text-accent-foreground'
                    : 'text-muted-foreground hover:text-accent'
                }`}
              >
                {option.toUpperCase()}
              </button>
            ))}
          </div>
          <Button
            variant="outline"
            size="icon"
            onClick={toggleTheme}
            aria-label={theme === 'light' ? 'Activar tema oscuro' : 'Activar tema claro'}
            className="rounded-full border-border/50 bg-card/80 backdrop-blur-sm hover:bg-accent hover:text-accent-foreground"
          >
            {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="fixed top-6 left-1/2 transform -translate-x-1/2 z-40 bg-card/80 backdrop-blur-sm border border-border/50 rounded-full px-6 py-2">
          <div className="flex space-x-6">
            {navLabels.map((item, index) => {
              const sectionId = SECTIONS[index];
              const isActive = activeSection === sectionId;
              return (
                <a
                  key={sectionId}
                  href={`#${sectionId}`}
                  aria-current={isActive ? 'true' : undefined}
                  className={`text-sm font-medium transition-colors duration-200 hover:text-accent ${
                    isActive ? 'text-accent' : ''
                  }`}
                >
                  {item}
                </a>
              );
            })}
          </div>
        </nav>

        <main>
          <Hero />
          <About />
          <Experience />
          <Projects />
          <Skills />
          <AiLab />
          <Contact />
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
