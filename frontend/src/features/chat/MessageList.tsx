import { useEffect, useRef, useState } from 'react';

import type { ChatMessage, ChatState } from './chatReducer';
import { MessageBubble } from './MessageBubble';

interface MessageListProps {
  state: ChatState;
  onFeedback: (message: ChatMessage, rating: 'up' | 'down') => void;
}

export function MessageList({ state, onFeedback }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [stickToBottom, setStickToBottom] = useState(true);

  useEffect(() => {
    if (stickToBottom) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
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
      role="log"
      aria-live="polite"
    >
      {state.messages.length === 0 && (
        <p className="py-8 text-center text-sm text-muted-foreground">
          Pregúntame por su experiencia, proyectos o stack técnico.
        </p>
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
