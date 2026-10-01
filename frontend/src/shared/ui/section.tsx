import type { ReactNode } from 'react';

import { cn } from './utils';

interface SectionProps {
  id: string;
  tone?: 'default' | 'subtle';
  width?: 'wide' | 'narrow';
  children: ReactNode;
  className?: string;
}

/** Sección estándar: padding 96/64, contenedor 1120/880 y gutter 24/20. */
export function Section({
  id,
  tone = 'default',
  width = 'wide',
  children,
  className,
}: SectionProps) {
  return (
    <section
      id={id}
      className={cn(
        'scroll-mt-20 px-5 py-16 md:px-6 md:py-24',
        tone === 'subtle' ? 'bg-surface-subtle' : 'bg-background',
        className,
      )}
    >
      <div className={cn('mx-auto w-full', width === 'wide' ? 'max-w-[1120px]' : 'max-w-[880px]')}>
        {children}
      </div>
    </section>
  );
}

interface SectionHeaderProps {
  eyebrow: string;
  title: string;
  lead?: string;
}

/** Cabecera de sección: eyebrow mono + H2 + lead. Sin barra decorativa. */
export function SectionHeader({ eyebrow, title, lead }: SectionHeaderProps) {
  return (
    <header className="mb-12 max-w-[720px]">
      <p className="eyebrow mb-3">{eyebrow}</p>
      <h2 className="text-[clamp(1.75rem,1.4rem+1.5vw,2.5rem)] font-bold leading-tight tracking-[-0.01em] text-foreground">
        {title}
      </h2>
      {lead !== undefined && (
        <p className="mt-4 max-w-[60ch] text-lg text-muted-foreground">{lead}</p>
      )}
    </header>
  );
}
