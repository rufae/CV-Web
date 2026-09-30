import { useEffect, useState } from 'react';
import { AlertTriangle, WifiOff } from 'lucide-react';

import type { ChatStatus as ChatStatusValue } from './chatReducer';
import { useI18n } from '@/shared/lib/i18n';
import { statusView, type LlmState } from './statusView';

interface ChatStatusProps {
  chat: ChatStatusValue;
  retryAfter: number;
  llm: LlmState | null;
}

export function ChatStatus({ chat, retryAfter, llm }: ChatStatusProps) {
  const { t } = useI18n();
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
          {t.chat.offline}{' '}
          <a href="#contact" className="underline">
            {t.chat.contact}
          </a>
          .
        </p>
      )}
      {view.degraded && !view.offline && (
        <p className="bg-amber-500/10 px-4 py-2 text-sm text-amber-700 dark:text-amber-400">
          {t.chat.degraded}
        </p>
      )}
      {view.rateLimited && (
        <p className="bg-amber-500/10 px-4 py-2 text-sm text-amber-700 dark:text-amber-400">
          {remaining > 0
            ? `${t.chat.limit} ${t.chat.limitRetry.replace('{seconds}', String(remaining))}`
            : t.chat.retry}
        </p>
      )}
      {chat === 'error' && (
        <p className="flex items-center gap-1.5 bg-red-500/10 px-4 py-2 text-sm text-red-600">
          <AlertTriangle className="h-4 w-4" />
          {t.chat.offline}
        </p>
      )}
      {chat === 'refused' && (
        <p className="bg-muted px-4 py-2 text-sm text-muted-foreground">
          {t.chat.refused}{' '}
          <a href="#contact" className="text-accent underline">
            {t.chat.contact}
          </a>
          .
        </p>
      )}
    </div>
  );
}
