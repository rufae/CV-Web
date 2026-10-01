import { useState } from 'react';
import { Check, Copy, ThumbsDown, ThumbsUp } from 'lucide-react';

import type { ChatMessage } from './chatReducer';
import { renderMarkdown } from './markdown';
import { useI18n } from '@/shared/lib/i18n';
import { SourceChips } from './SourceChips';

interface MessageBubbleProps {
  message: ChatMessage;
  onFeedback: (message: ChatMessage, rating: 'up' | 'down') => void;
}

const MODEL: string =
  (import.meta.env.VITE_LLM_MODEL as string | undefined) ?? 'gemma4:12b';

export function MessageBubble({ message, onFeedback }: MessageBubbleProps) {
  const { t } = useI18n();
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';
  const latency =
    typeof message.firstTokenMs === 'number'
      ? `${(message.firstTokenMs / 1000).toFixed(1).replace('.', ',')} s`
      : null;
  const provider = message.tier === 'gpu' ? t.chat.providerGpu : t.chat.providerCpu;

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

        {!isUser && message.text !== '' && message.tier !== undefined && (
          <p
            className="mt-2 flex flex-wrap items-center gap-1.5 font-mono text-xs text-muted-foreground"
            title={t.chat.providerTooltip}
          >
            <span>{provider}</span>
            {MODEL !== '' && (
              <>
                <span aria-hidden="true">·</span>
                <span>{MODEL}</span>
              </>
            )}
            {latency !== null && (
              <>
                <span aria-hidden="true">·</span>
                <span className="tabular">{latency}</span>
              </>
            )}
          </p>
        )}

        {!isUser && message.text !== '' && (
          <div className="mt-1 flex items-center gap-1 text-muted-foreground">
            <button
              type="button"
              onClick={() => void copy()}
              aria-label={t.chat.copy}
              className="flex h-11 w-11 items-center justify-center rounded transition-colors hover:text-accent-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring sm:h-7 sm:w-7"
            >
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </button>
            {message.messageId !== undefined && message.refused !== true && (
              <>
                <button
                  type="button"
                  onClick={() => onFeedback(message, 'up')}
                  aria-label={t.chat.useful}
                  className="flex h-11 w-11 items-center justify-center rounded transition-colors hover:text-accent-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring sm:h-7 sm:w-7"
                >
                  <ThumbsUp className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  onClick={() => onFeedback(message, 'down')}
                  aria-label={t.chat.notUseful}
                  className="flex h-11 w-11 items-center justify-center rounded transition-colors hover:text-accent-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring sm:h-7 sm:w-7"
                >
                  <ThumbsDown className="h-4 w-4" />
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
