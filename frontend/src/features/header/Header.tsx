import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { Menu, Moon, Sun, X } from 'lucide-react';

import { useI18n } from '@/shared/lib/i18n';
import { useFocusTrap } from '@/shared/lib/useFocusTrap';
import { cn } from '@/shared/ui/utils';

export interface NavItem {
  id: string;
  label: string;
}

interface HeaderProps {
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  activeSection: string;
}

export function Header({ theme, onToggleTheme, activeSection }: HeaderProps) {
  const { lang, t, setLang } = useI18n();
  const [menuOpen, setMenuOpen] = useState(false);
  const sheetRef = useRef<HTMLDivElement>(null);
  useFocusTrap(sheetRef, menuOpen);

  const navItems: NavItem[] = [
    { id: 'projects', label: t.header.nav.projects },
    { id: 'ai-lab', label: t.header.nav.lab },
    { id: 'experience', label: t.header.nav.experience },
    { id: 'education', label: t.header.nav.education },
    { id: 'stack', label: t.header.nav.stack },
    { id: 'contact', label: t.header.nav.contact },
  ];

  useEffect(() => {
    if (!menuOpen) {
      return;
    }
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setMenuOpen(false);
      }
    };
    document.body.style.overflow = 'hidden';
    window.addEventListener('keydown', handleKey);
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKey);
    };
  }, [menuOpen]);

  const langControl = (
    <div
      role="group"
      aria-label={t.header.language}
      className="flex items-center rounded-md border border-border bg-surface p-0.5"
    >
      {(['es', 'en'] as const).map((option) => (
        <button
          key={option}
          type="button"
          onClick={() => setLang(option)}
          aria-pressed={lang === option}
          className={cn(
            'rounded-[4px] px-2.5 py-1 font-mono text-xs font-medium uppercase transition-colors',
            lang === option
              ? 'bg-accent-strong text-white'
              : 'text-muted-foreground hover:text-foreground',
          )}
        >
          {option}
        </button>
      ))}
    </div>
  );

  const themeButton = (
    <button
      type="button"
      onClick={onToggleTheme}
      aria-label={theme === 'light' ? t.header.themeToDark : t.header.themeToLight}
      className="inline-flex size-11 items-center justify-center rounded-md border border-border bg-surface text-foreground transition-colors hover:bg-surface-subtle sm:size-10"
    >
      {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
    </button>
  );

  return (
    <header className="fixed inset-x-0 top-0 z-40 border-b border-border bg-surface/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-[1120px] items-center justify-between gap-4 px-5 md:px-6">
        <a href="#hero" className="group flex min-w-0 flex-col">
          <span className="truncate text-base font-semibold leading-tight text-foreground">
            Rafael Castaño
          </span>
          <span className="mono-label text-muted-foreground">{t.header.role}</span>
        </a>

        <nav aria-label="Principal" className="hidden items-center gap-1 lg:flex">
          {navItems.map((item) => {
            const isActive = activeSection === item.id;
            return (
              <a
                key={item.id}
                href={`#${item.id}`}
                aria-current={isActive ? 'true' : undefined}
                className={cn(
                  'relative px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'text-accent-strong after:absolute after:inset-x-3 after:-bottom-[3px] after:h-0.5 after:rounded-full after:bg-accent-strong'
                    : 'text-muted-foreground hover:text-foreground',
                )}
              >
                {item.label}
              </a>
            );
          })}
        </nav>

        <div className="hidden items-center gap-2 lg:flex">
          {langControl}
          {themeButton}
        </div>

        <button
          type="button"
          onClick={() => setMenuOpen(true)}
          aria-label={t.header.openMenu}
          aria-expanded={menuOpen}
          className="inline-flex size-11 items-center justify-center rounded-md border border-border bg-surface text-foreground transition-colors hover:bg-surface-subtle lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </button>
      </div>

      {menuOpen &&
        typeof document !== 'undefined' &&
        createPortal(
          <div
            ref={sheetRef}
            role="dialog"
            aria-modal="true"
            aria-label={t.header.menu}
            className="fixed inset-0 z-50 flex flex-col bg-background lg:hidden"
          >
            <div className="flex h-16 items-center justify-between border-b border-border px-5">
              <span className="text-base font-semibold">Rafael Castaño</span>
              <button
                type="button"
                onClick={() => setMenuOpen(false)}
                aria-label={t.header.closeMenu}
                className="inline-flex size-11 items-center justify-center rounded-md border border-border bg-surface text-foreground hover:bg-surface-subtle"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <nav aria-label="Principal" className="flex-1 overflow-y-auto px-5 py-4">
              {navItems.map((item) => (
                <a
                  key={item.id}
                  href={`#${item.id}`}
                  onClick={() => setMenuOpen(false)}
                  aria-current={activeSection === item.id ? 'true' : undefined}
                  className={cn(
                    'flex h-12 items-center border-b border-border text-lg font-medium transition-colors',
                    activeSection === item.id ? 'text-accent-strong' : 'text-foreground',
                  )}
                >
                  {item.label}
                </a>
              ))}
            </nav>

            <div className="flex items-center justify-between gap-4 border-t border-border px-5 py-4">
              {langControl}
              {themeButton}
            </div>
          </div>,
          document.body,
        )}
    </header>
  );
}
