import { useState } from 'react';
import { Send, Square } from 'lucide-react';

import { MAX_MESSAGE_CHARS } from '@/shared/api/types';
import { Button } from '@/shared/ui/button';
import { Textarea } from '@/shared/ui/textarea';

interface ComposerProps {
  disabled: boolean;
  streaming: boolean;
  onSend: (text: string) => void;
  onStop: () => void;
}

export function Composer({ disabled, streaming, onSend, onStop }: ComposerProps) {
  const [text, setText] = useState('');

  const submit = () => {
    const trimmed = text.trim();
    if (trimmed === '' || disabled) {
      return;
    }
    onSend(trimmed);
    setText('');
  };

  return (
    <div className="border-t border-border p-3">
      <div className="flex items-end gap-2">
        <Textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault();
              submit();
            }
          }}
          placeholder="Escribe tu pregunta…"
          rows={1}
          maxLength={MAX_MESSAGE_CHARS}
          disabled={disabled}
          aria-label="Mensaje para el asistente"
          className="max-h-32 min-h-10 flex-1 resize-none bg-input-background text-base"
        />
        {streaming ? (
          <Button
            type="button"
            size="icon"
            variant="outline"
            onClick={onStop}
            aria-label="Detener la respuesta"
          >
            <Square className="h-4 w-4" />
          </Button>
        ) : (
          <Button
            type="button"
            size="icon"
            onClick={submit}
            disabled={disabled || text.trim() === ''}
            aria-label="Enviar mensaje"
            className="bg-accent text-accent-foreground hover:bg-accent/90"
          >
            <Send className="h-4 w-4" />
          </Button>
        )}
      </div>
      {text.length > 350 && (
        <p className="mt-1 text-right text-xs text-muted-foreground">
          {text.length}/{MAX_MESSAGE_CHARS}
        </p>
      )}
    </div>
  );
}
