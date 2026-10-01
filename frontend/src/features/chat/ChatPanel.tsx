import { useEffect, useRef, useState } from 'react';
import { Bot, RotateCcw, X } from 'lucide-react';

import { Button } from '@/shared/ui/button';
import { StatusPill } from '@/shared/ui/status-pill';
import { cn } from '@/shared/ui/utils';

import type { ChatMessage, ChatState } from './chatReducer';
import { ChatStatus } from './ChatStatus';
import { Composer } from './Composer';
import { MessageList } from './MessageList';
import { statusView } from './statusView';
import { useApiStatus } from './useApiStatus';
import { useI18n } from '@/shared/lib/i18n';
import { useFocusTrap } from '@/shared/lib/useFocusTrap';

export type ChatMode = 'embedded' | 'floating';

interface ChatPanelProps {
  mode: ChatMode;
  state: ChatState;
  onClose?: () => void;
  onSend: (text: string) => Promise<void>;
  onStop: () => void;
  onRetry: () => Promise<void>;
  onReset: () => void;
  onFeedback: (message: ChatMessage, rating: 'up' | 'down') => void;
}

const STATUS_TONE = { online: 'success', degraded: 'warning', offline: 'danger' } as const;

export function ChatPanel({
  mode,
  state,
  onClose,
  onSend,
  onStop,
  onRetry,
  onReset,
  onFeedback,
}: ChatPanelProps) {
  const { t } = useI18n();
  const panelRef = useRef<HTMLElement>(null);
  const previousStatus = useRef(state.status);
  const [announcement, setAnnouncement] = useState('');

  useFocusTrap(panelRef, mode === 'floating');
  const apiStatus = useApiStatus(true);
  const view = statusView(state.status, state.retryAfter, apiStatus?.llm ?? null);

  useEffect(() => {
    if (mode !== 'floating') {
      return;
    }
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose?.();
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [mode, onClose]);

  useEffect(() => {
    const finished =
      (previousStatus.current === 'streaming' || previousStatus.current === 'retrieving') &&
      state.status === 'idle';
    if (finished) {
      const lastAssistant = [...state.messages]
        .reverse()
        .find((message) => message.role === 'assistant' && message.text !== '');
      if (lastAssistant !== undefined) {
        setAnnouncement(lastAssistant.text);
      }
    }
    previousStatus.current = state.status;
  }, [state.status, state.messages]);

  const statusLabels = {
    online: t.aiLab.online,
    degraded: t.aiLab.degraded,
    offline: t.aiLab.offline,
  } as const;
  const showRetry = state.status === 'error' || state.status === 'rate_limited';
  const streaming = state.status === 'streaming' || state.status === 'retrieving';
  const llm = apiStatus?.llm ?? null;

  return (
    <section
      ref={panelRef}
      role={mode === 'floating' ? 'dialog' : 'region'}
      aria-modal={mode === 'floating' ? 'true' : undefined}
      aria-labelledby={`chat-title-${mode}`}
      className={cn(
        'chat-window flex flex-col overflow-hidden border border-border bg-surface',
        mode === 'floating'
          ? 'fixed inset-0 z-50 sm:inset-auto sm:bottom-24 sm:right-6 sm:h-[600px] sm:w-[400px]'
          : 'h-full max-h-[520px] min-h-[320px] w-full',
      )}
    >
      <header className="flex items-start justify-between gap-3 border-b border-border bg-surface p-4">
        <div className="flex min-w-0 items-start gap-3">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-accent-soft text-accent-strong">
            <Bot className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <h3 id={`chat-title-${mode}`} className="text-base font-semibold leading-tight">
              {t.chat.title}
            </h3>
            <p className="mt-0.5 text-xs text-muted-foreground">{t.chat.disclaimer}</p>
            <div className="mt-2">
              {llm !== null ? (
                <StatusPill
                  tone={STATUS_TONE[llm]}
                  label={statusLabels[llm]}
                  detail={apiStatus !== null ? `${t.aiLab.tier} ${apiStatus.tier}` : undefined}
                  pulse={llm === 'online'}
                  className="px-2 py-0.5 text-xs"
                />
              ) : (
                <StatusPill
                  tone="neutral"
                  label={t.aiLab.checking}
                  className="px-2 py-0.5 text-xs"
                />
              )}
            </div>
          </div>
        </div>
        {mode === 'floating' && (
          <div className="flex shrink-0 items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={onReset}
              aria-label={t.chat.newConversation}
              className="size-10 sm:size-9"
            >
              <RotateCcw className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              aria-label={t.chat.close}
              className="size-10 sm:size-9"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        )}
      </header>

      <ChatStatus chat={state.status} retryAfter={state.retryAfter} llm={llm} />
      {showRetry && (
        <div className="px-4 pt-2">
          <Button size="sm" variant="outline" onClick={() => void onRetry()}>
            {t.chat.retry}
          </Button>
        </div>
      )}

      <p className="sr-only" aria-live="polite">
        {announcement}
      </p>

      <MessageList
        state={state}
        compact={mode === 'embedded'}
        onFeedback={onFeedback}
        onSelectStarter={(text) => void onSend(text)}
      />
      <Composer
        disabled={view.composerBlocked}
        streaming={streaming}
        onSend={(text) => void onSend(text)}
        onStop={onStop}
      />
    </section>
  );
}
