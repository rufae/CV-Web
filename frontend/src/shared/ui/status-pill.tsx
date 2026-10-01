import { cn } from './utils';

type StatusTone = 'success' | 'warning' | 'danger' | 'neutral';

const DOT_STYLES: Record<StatusTone, string> = {
  success: 'bg-success',
  warning: 'bg-warning',
  danger: 'bg-danger',
  neutral: 'bg-muted-foreground',
};

interface StatusPillProps {
  tone: StatusTone;
  label: string;
  detail?: string;
  pulse?: boolean;
  className?: string;
}

/** Pill de estado: dot 8 px + etiqueta 13 px. */
export function StatusPill({ tone, label, detail, pulse, className }: StatusPillProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1 text-[0.8125rem] font-medium text-foreground',
        className,
      )}
    >
      <span
        aria-hidden="true"
        className={cn('h-2 w-2 shrink-0 rounded-full', DOT_STYLES[tone], pulse && 'pulse-dot')}
      />
      {label}
      {detail !== undefined && (
        <span className="font-normal text-muted-foreground">· {detail}</span>
      )}
    </span>
  );
}
