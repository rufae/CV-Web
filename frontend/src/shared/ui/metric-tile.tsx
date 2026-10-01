import { cn } from './utils';

interface MetricTileProps {
  value: string;
  label: string;
  note?: string;
  className?: string;
}

/** Tile de métrica: valor mono tabular 28/600 + etiqueta 13 + nota/fuente 12. */
export function MetricTile({ value, label, note, className }: MetricTileProps) {
  return (
    <div className={cn('rounded-xl border border-border bg-surface p-4', className)}>
      <div className="tabular text-2xl font-semibold leading-none text-foreground">{value}</div>
      <div className="mt-2 text-[0.8125rem] leading-snug text-muted-foreground">{label}</div>
      {note !== undefined && (
        <div className="mt-1 font-mono text-xs text-muted-foreground">{note}</div>
      )}
    </div>
  );
}
