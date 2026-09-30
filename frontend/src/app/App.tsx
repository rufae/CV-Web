import { lazy, Suspense, useState, useEffect } from 'react';
import { ThemeContext } from './theme-context';
import { Moon, Sun } from 'lucide-react';
import { Button } from '@/shared/ui/button';
import { Toaster } from '@/shared/ui/sonner';
import { Hero } from '@/features/hero/Hero';
import { About } from '@/features/about/About';
import { Experience } from '@/features/experience/Experience';
import { Projects } from '@/features/projects/Projects';
import { Skills } from '@/features/skills/Skills';
import { Contact } from '@/features/contact/Contact';
import { Footer } from '@/features/footer/Footer';

const Chat = lazy(() => import('@/features/chat/Chat'));

function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    if (savedTheme) {
      setTheme(savedTheme);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setTheme('dark');
    }
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <div className="min-h-screen bg-background text-foreground">
        {/* Theme Toggle Button */}
        <div className="fixed top-6 right-6 z-50">
          <Button
            variant="outline"
            size="icon"
            onClick={toggleTheme}
            className="rounded-full bg-card/80 backdrop-blur-sm border-border/50 hover:bg-accent hover:text-accent-foreground"
          >
            {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="fixed top-6 left-1/2 transform -translate-x-1/2 z-40 bg-card/80 backdrop-blur-sm border border-border/50 rounded-full px-6 py-2">
          <div className="flex space-x-6">
            {['Inicio', 'Sobre mí', 'Experiencia', 'Proyectos', 'Habilidades', 'Contacto'].map(
              (item, index) => (
                <a
                  key={item}
                  href={`#${['hero', 'about', 'experience', 'projects', 'skills', 'contact'][index]}`}
                  className="text-sm font-medium hover:text-accent transition-colors duration-200"
                >
                  {item}
                </a>
              ),
            )}
          </div>
        </nav>

        <main>
          <Hero />
          <About />
          <Experience />
          <Projects />
          <Skills />
          <Contact />
        </main>

        <Footer />
        <Suspense fallback={null}>
          <Chat />
        </Suspense>
        <Toaster />
      </div>
    </ThemeContext.Provider>
  );
}

export default App;
