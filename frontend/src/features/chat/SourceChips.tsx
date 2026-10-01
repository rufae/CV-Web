import type { SourceItem } from '@/shared/api/types';
import { useI18n } from '@/shared/lib/i18n';

interface SourceChipsProps {
  sources: SourceItem[];
}

export function SourceChips({ sources }: SourceChipsProps) {
  const { t } = useI18n();
  if (sources.length === 0) {
    return null;
  }
  return (
    <div className="mt-2 flex flex-wrap gap-1.5" aria-label={t.chat.sources}>
      {sources.map((source) => (
        <span
          key={source.n}
          className="rounded-full bg-accent-soft px-2 py-0.5 font-mono text-xs text-accent-strong"
        >
          [{source.n}] {source.title}
          {source.section !== '' ? ` › ${source.section}` : ''}
        </span>
      ))}
    </div>
  );
}
