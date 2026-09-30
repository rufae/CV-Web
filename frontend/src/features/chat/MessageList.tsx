import { useEffect, useRef, useState } from 'react';

import type { ChatMessage, ChatState } from './chatReducer';
import { MessageBubble } from './MessageBubble';
import { useI18n } from '@/shared/lib/i18n';
import { Starters } from './Starters';

interface MessageListProps {
  state: ChatState;
  onFeedback: (message: ChatMessage, rating: 'up' | 'down') => void;
  onSelectStarter: (text: string) => void;
}

export function MessageList({ state, onFeedback, onSelectStarter }: MessageListProps) {
  const { t } = useI18n();
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [stickToBottom, setStickToBottom] = useState(true);

  useEffect(() => {
    const target = bottomRef.current;
    if (stickToBottom && target !== null && typeof target.scrollIntoView === 'function') {
      target.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [state.messages, stickToBottom]);

  const handleScroll = () => {
    const container = containerRef.current;
    if (container === null) {
      return;
    }
    const nearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 48;
    setStickToBottom(nearBottom);
  };

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className="chat-messages flex-1 space-y-4 overflow-y-auto p-4 text-base"
      role="group"
      aria-label="Conversación"
    >
      {state.messages.length === 0 && (
        <div className="py-4">
          <p className="mb-3 text-center text-sm text-muted-foreground">{t.chat.empty}</p>
          <Starters onSelect={onSelectStarter} />
        </div>
      )}

      {state.messages.map((message) => (
        <MessageBubble key={message.id} message={message} onFeedback={onFeedback} />
      ))}

      {state.status === 'retrieving' && (
        <div className="flex justify-start">
          <div className="typing-indicator" aria-label="Buscando información">
            <div />
            <div />
            <div />
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
