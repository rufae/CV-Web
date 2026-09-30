import { useEffect, useState } from 'react';
import { AlertTriangle, WifiOff } from 'lucide-react';

import type { ChatStatus as ChatStatusValue } from './chatReducer';
import { formatRetry, statusView, type LlmState } from './statusView';

interface ChatStatusProps {
  chat: ChatStatusValue;
  retryAfter: number;
  llm: LlmState | null;
}

export function ChatStatus({ chat, retryAfter, llm }: ChatStatusProps) {
  const [remaining, setRemaining] = useState(retryAfter);

  useEffect(() => {
    setRemaining(retryAfter);
  }, [retryAfter]);

  useEffect(() => {
    if (remaining <= 0) {
      return;
    }
    const timer = window.setTimeout(() => setRemaining((value) => Math.max(0, value - 1)), 1000);
    return () => window.clearTimeout(timer);
  }, [remaining]);

  const view = statusView(chat, remaining, llm);
  const visible =
    view.offline || view.degraded || view.rateLimited || chat === 'error' || chat === 'refused';
  if (!visible) {
    return null;
  }

  return (
    <div>
      {view.offline && (
        <p className="flex flex-wrap items-center gap-1.5 bg-amber-500/10 px-4 py-2 text-sm text-amber-700 dark:text-amber-400">
          <WifiOff className="h-4 w-4" />
          El asistente está en mantenimiento.
          <a href="#contact" className="underline">
            Escríbeme por el formulario
          </a>
          .
        </p>
      )}
      {view.degraded && !view.offline && (
        <p className="bg-amber-500/10 px-4 py-2 text-sm text-amber-700 dark:text-amber-400">
          Respuestas algo más lentas de lo normal.
        </p>
      )}
      {view.rateLimited && (
        <p className="bg-amber-500/10 px-4 py-2 text-sm text-amber-700 dark:text-amber-400">
          {formatRetry(remaining)}.
        </p>
      )}
      {chat === 'error' && (
        <p className="flex items-center gap-1.5 bg-red-500/10 px-4 py-2 text-sm text-red-600">
          <AlertTriangle className="h-4 w-4" />
          El asistente no está disponible ahora mismo.
        </p>
      )}
      {chat === 'refused' && (
        <p className="bg-muted px-4 py-2 text-sm text-muted-foreground">
          ¿Prefieres hablar con Rafael?{' '}
          <a href="#contact" className="text-accent underline">
            Usa el formulario de contacto
          </a>
          .
        </p>
      )}
    </div>
  );
}
