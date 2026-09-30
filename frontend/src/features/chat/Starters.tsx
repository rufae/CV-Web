import { Sparkles } from 'lucide-react';

import { useI18n } from '@/shared/lib/i18n';

interface StartersProps {
  onSelect: (text: string) => void;
}

export function Starters({ onSelect }: StartersProps) {
  const { t } = useI18n();
  return (
    <div className="space-y-2">
      <p className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
        <Sparkles className="h-3.5 w-3.5" />
        Prueba con…
      </p>
      <div className="flex flex-col gap-2">
        {t.chat.starters.map((starter) => (
          <button
            key={starter}
            type="button"
            onClick={() => onSelect(starter)}
            className="min-h-11 rounded-lg border border-border px-3 py-3 text-left text-sm transition-colors hover:border-accent/50 hover:bg-accent/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          >
            {starter}
          </button>
        ))}
      </div>
    </div>
  );
}
