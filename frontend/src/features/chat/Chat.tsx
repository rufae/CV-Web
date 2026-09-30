import { useEffect, useRef, useState } from 'react';

import { sendFeedback } from '@/shared/api/client';

import type { ChatMessage } from './chatReducer';
import { ChatLauncher } from './ChatLauncher';
import { ChatPanel } from './ChatPanel';
import './chat.css';
import { useI18n } from '@/shared/lib/i18n';
import { useChat } from './useChat';

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

  const handleFeedback = (message: ChatMessage, rating: 'up' | 'down') => {
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

  return (
    <>
      <ChatLauncher open={open} onToggle={() => setOpen((previous) => !previous)} />
      {open && (
        <ChatPanel
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
