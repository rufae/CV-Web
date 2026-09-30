import { useState } from 'react';
import { Check, Copy, ThumbsDown, ThumbsUp } from 'lucide-react';

import type { ChatMessage } from './chatReducer';
import { renderMarkdown } from './markdown';
import { SourceChips } from './SourceChips';

interface MessageBubbleProps {
  message: ChatMessage;
  onFeedback: (message: ChatMessage, rating: 'up' | 'down') => void;
}

export function MessageBubble({ message, onFeedback }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(message.text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // sin permiso de portapapeles
    }
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] break-words rounded-2xl p-3.5 ${
          isUser ? 'message-user' : 'message-bot'
        }`}
      >
        <div className="space-y-2 leading-relaxed">
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.text}</p>
          ) : (
            renderMarkdown(message.text)
          )}
        </div>

        {!isUser && <SourceChips sources={message.sources} />}

        {!isUser && message.text !== '' && (
          <div className="mt-2 flex items-center gap-1 text-muted-foreground">
            <button
              type="button"
              onClick={copy}
              aria-label="Copiar respuesta"
              className="rounded p-1 transition-colors hover:text-accent"
            >
              {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
            </button>
            {message.messageId !== undefined && message.refused !== true && (
              <>
                <button
                  type="button"
                  onClick={() => onFeedback(message, 'up')}
                  aria-label="Respuesta útil"
                  className="rounded p-1 transition-colors hover:text-accent"
                >
                  <ThumbsUp className="h-3.5 w-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => onFeedback(message, 'down')}
                  aria-label="Respuesta no útil"
                  className="rounded p-1 transition-colors hover:text-accent"
                >
                  <ThumbsDown className="h-3.5 w-3.5" />
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
