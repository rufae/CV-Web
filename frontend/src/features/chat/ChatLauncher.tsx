import { useEffect, useState } from 'react';
import { MessageCircle, X } from 'lucide-react';

import { Button } from '@/shared/ui/button';
import { useI18n } from '@/shared/lib/i18n';

interface ChatLauncherProps {
  open: boolean;
  onToggle: () => void;
}

const TEASER_KEY = 'cvweb.chat.teaser';

export function ChatLauncher({ open, onToggle }: ChatLauncherProps) {
  const { t } = useI18n();
  const [teaser, setTeaser] = useState(false);

  useEffect(() => {
    if (open || typeof window === 'undefined') {
      return;
    }
    if (window.sessionStorage.getItem(TEASER_KEY) !== null) {
      return;
    }
    const timer = window.setTimeout(() => setTeaser(true), 8000);
    return () => window.clearTimeout(timer);
  }, [open]);

  const dismissTeaser = () => {
    setTeaser(false);
    try {
      window.sessionStorage.setItem(TEASER_KEY, '1');
    } catch {
      // sin almacenamiento: el teaser vuelve a aparecer en la sesión
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
      {teaser && !open && (
        <div className="flex max-w-[240px] items-start gap-2 rounded-xl border border-border bg-surface p-3 text-sm shadow-elevated">
          <p className="text-foreground">{t.chat.teaser}</p>
          <button
            type="button"
            onClick={dismissTeaser}
            aria-label={t.chat.close}
            className="shrink-0 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}
      <Button
        onClick={onToggle}
        aria-label={open ? t.chat.close : t.chat.open}
        aria-expanded={open}
        data-chat-launcher
        className="chat-launcher h-14 w-14 rounded-full bg-accent-strong text-white shadow-elevated transition-all duration-300 hover:bg-accent-strong/90 motion-reduce:animate-none"
      >
        {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </Button>
    </div>
  );
}
