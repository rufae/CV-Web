import type { SourceItem } from '@/shared/api/types';

interface SourceChipsProps {
  sources: SourceItem[];
}

export function SourceChips({ sources }: SourceChipsProps) {
  if (sources.length === 0) {
    return null;
  }
  return (
    <div className="mt-2 flex flex-wrap gap-1.5" aria-label="Fuentes consultadas">
      {sources.map((source) => (
        <span key={source.n} className="rounded-full bg-accent/15 px-2 py-0.5 text-xs text-accent">
          [{source.n}] {source.title}
          {source.section !== '' ? ` › ${source.section}` : ''}
        </span>
      ))}
    </div>
  );
}
