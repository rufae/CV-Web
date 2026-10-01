import { useEffect, useRef, useState } from 'react';

import { sendFeedback } from '@/shared/api/client';
import { useI18n } from '@/shared/lib/i18n';

import type { ChatMessage } from './chatReducer';
import { ChatLauncher } from './ChatLauncher';
import { ChatPanel } from './ChatPanel';
import './chat.css';
import { CHAT_PROMPT_EVENT } from './events';
import { useChat } from './useChat';

function useFeedbackHandler() {
  return (message: ChatMessage, rating: 'up' | 'down') => {
    if (message.messageId === undefined) {
      return;
    }
    void sendFeedback({
      message_id: message.messageId,
      rating,
      prompt_version: message.promptVersion,
      sources: message.sources.map((source) => source.n),
      tier: message.tier,
      refused: message.refused ?? false,
    }).catch(() => undefined);
  };
}

/** Consola del asistente embebida en el hero (sin persistencia de sesión). */
export function ChatEmbedded() {
  const { lang } = useI18n();
  const { state, send, stop, retry, reset } = useChat(lang, { persist: false });
  const handleFeedback = useFeedbackHandler();

  useEffect(() => {
    const handler = (event: Event) => {
      const prompt = (event as CustomEvent<string>).detail;
      document.getElementById('hero')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      void send(prompt);
    };
    window.addEventListener(CHAT_PROMPT_EVENT, handler);
    return () => window.removeEventListener(CHAT_PROMPT_EVENT, handler);
  }, [send]);

  return (
    <ChatPanel
      mode="embedded"
      state={state}
      onSend={send}
      onStop={stop}
      onRetry={retry}
      onReset={reset}
      onFeedback={handleFeedback}
    />
  );
}

export default function Chat() {
  const { lang } = useI18n();
  const { state, send, stop, retry, reset } = useChat(lang);
  const [open, setOpen] = useState(false);
  const wasOpen = useRef(false);

  useEffect(() => {
    if (wasOpen.current && !open) {
      document.querySelector<HTMLButtonElement>('[data-chat-launcher]')?.focus();
    }
    wasOpen.current = open;
  }, [open]);

  const handleFeedback = useFeedbackHandler();

  return (
    <>
      <ChatLauncher open={open} onToggle={() => setOpen((previous) => !previous)} />
      {open && (
        <ChatPanel
          mode="floating"
          state={state}
          onClose={() => setOpen(false)}
          onSend={send}
          onStop={stop}
          onRetry={retry}
          onReset={reset}
          onFeedback={handleFeedback}
        />
      )}
    </>
  );
}
