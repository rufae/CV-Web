import { Sparkles, Swords } from 'lucide-react';

import { useI18n } from '@/shared/lib/i18n';

interface StartersProps {
  compact?: boolean;
  onSelect: (text: string) => void;
}

export function Starters({ compact = false, onSelect }: StartersProps) {
  const { t } = useI18n();
  const prompts = compact ? t.chat.starters.slice(0, 3) : t.chat.starters.slice(0, 4);

  return (
    <div className="space-y-2">
      <p className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
        <Sparkles className="h-3.5 w-3.5" />
        {t.chat.startersLabel}
      </p>
      <div className="flex flex-col gap-2">
        {prompts.map((starter) => (
          <button
            key={starter}
            type="button"
            onClick={() => onSelect(starter)}
            className="min-h-11 rounded-lg border border-border px-3 py-3 text-left text-sm text-foreground transition-colors hover:border-accent/50 hover:bg-accent-soft/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {starter}
          </button>
        ))}
        <a
          href="#ai-lab"
          className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-dashed border-border px-3 py-3 text-left text-sm font-medium text-accent-strong transition-colors hover:border-accent/50 hover:bg-accent-soft/60"
        >
          <Swords className="h-4 w-4 shrink-0" aria-hidden="true" />
          {t.chat.starters[4]}
        </a>
      </div>
    </div>
  );
}
