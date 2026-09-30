import { useEffect } from 'react';
import { Bot, RotateCcw, X } from 'lucide-react';

import { Button } from '@/shared/ui/button';

import type { ChatMessage, ChatState } from './chatReducer';
import { Composer } from './Composer';
import { MessageList } from './MessageList';

interface ChatPanelProps {
  state: ChatState;
  onClose: () => void;
  onSend: (text: string) => Promise<void>;
  onStop: () => void;
  onRetry: () => Promise<void>;
  onReset: () => void;
  onFeedback: (message: ChatMessage, rating: 'up' | 'down') => void;
}

export function ChatPanel({
  state,
  onClose,
  onSend,
  onStop,
  onRetry,
  onReset,
  onFeedback,
}: ChatPanelProps) {
  useEffect(() => {
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onClose]);

  const showRetry = state.status === 'error' || state.status === 'rate_limited';
  const streaming = state.status === 'streaming' || state.status === 'retrieving';

  return (
    <section
      role="dialog"
      aria-modal="true"
      aria-labelledby="chat-title"
      className="chat-window fixed inset-0 z-50 flex flex-col sm:inset-auto sm:bottom-24 sm:right-6 sm:h-[600px] sm:w-[400px]"
    >
      <header className="flex items-center justify-between border-b border-border bg-accent p-4 text-accent-foreground">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-accent-foreground">
            <Bot className="h-5 w-5 text-accent" />
          </div>
          <div>
            <h3 id="chat-title" className="font-semibold">
              Asistente de Rafael
            </h3>
            <p className="text-xs opacity-90">
              Asistente de IA; solo responde con información pública del portfolio
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={onReset}
            aria-label="Nueva conversación"
            className="text-accent-foreground hover:bg-white/10"
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            aria-label="Cerrar el asistente"
            className="text-accent-foreground hover:bg-white/10"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </header>

      {state.status === 'rate_limited' && (
        <p className="bg-amber-500/10 px-4 py-2 text-sm text-amber-700 dark:text-amber-400">
          Has alcanzado el límite de mensajes
          {state.retryAfter > 0 ? `; prueba de nuevo en ${state.retryAfter} s` : ''}.
        </p>
      )}
      {state.status === 'error' && (
        <p className="bg-red-500/10 px-4 py-2 text-sm text-red-600">
          El asistente no está disponible ahora mismo.
        </p>
      )}
      {showRetry && (
        <div className="px-4 pt-2">
          <Button size="sm" variant="outline" onClick={() => void onRetry()}>
            Reintentar
          </Button>
        </div>
      )}

      <MessageList state={state} onFeedback={onFeedback} />
      <Composer
        disabled={state.status === 'rate_limited'}
        streaming={streaming}
        onSend={(text) => void onSend(text)}
        onStop={onStop}
      />
    </section>
  );
}
