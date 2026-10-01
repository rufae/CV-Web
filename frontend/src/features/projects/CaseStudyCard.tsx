import { useEffect, useRef, useState } from 'react';
import { ArrowUpRight, Github, MessageCircle, X } from 'lucide-react';

import type { CaseStudy } from '@/content/dictionary';
import { askAssistant } from '@/features/chat/events';
import { useI18n } from '@/shared/lib/i18n';
import { useFocusTrap } from '@/shared/lib/useFocusTrap';
import { Badge } from '@/shared/ui/badge';
import { Button } from '@/shared/ui/button';
import { Card } from '@/shared/ui/card';
import { MetricTile } from '@/shared/ui/metric-tile';
import { cn } from '@/shared/ui/utils';

import { Diagram } from './Diagram';

interface CaseStudyCardProps {
  study: CaseStudy;
  featured?: boolean;
}

export function CaseStudyCard({ study, featured = false }: CaseStudyCardProps) {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);

  const links = (
    <div className="flex flex-wrap items-center gap-2">
      {study.repo !== undefined && (
        <Button variant="secondary" size="sm" asChild>
          <a href={study.repo} target="_blank" rel="noopener noreferrer">
            <Github className="h-4 w-4" />
            {t.projects.repo}
            <span className="sr-only"> ({t.common.externalLink})</span>
          </a>
        </Button>
      )}
      <Button variant="ghost" size="sm" onClick={() => setOpen(true)}>
        {t.common.openCase}
        <ArrowUpRight className="h-4 w-4" />
      </Button>
      {study.ask !== undefined && (
        <Button variant="ghost" size="sm" onClick={() => askAssistant(study.ask ?? '')}>
          <MessageCircle className="h-4 w-4" />
          {t.projects.askAssistant}
        </Button>
      )}
    </div>
  );

  const content = (
    <>
      <div className="flex flex-wrap items-center gap-2">
        <Badge>{study.type}</Badge>
        {study.pending === true && <Badge variant="secondary">{t.common.pending}</Badge>}
      </div>
      <h3 className="mt-3 text-xl font-semibold leading-snug text-foreground">{study.title}</h3>

      <div className="mt-4">
        <p className="eyebrow mb-1">{t.projects.problemLabel}</p>
        <p className="text-foreground">{study.problem}</p>
      </div>

      <div className="mt-4">
        <p className="eyebrow mb-2">{t.projects.builtLabel}</p>
        <ul className="space-y-1.5">
          {study.built.map((item) => (
            <li key={item} className="flex items-start gap-2 text-sm text-muted-foreground">
              <span
                className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent"
                aria-hidden="true"
              />
              {item}
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-4">
        <p className="eyebrow mb-2">{t.projects.resultsLabel}</p>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {study.results.map((result) => (
            <MetricTile
              key={result.label}
              value={result.value}
              label={result.label}
              note={result.source}
            />
          ))}
        </div>
      </div>

      <div className="mt-4">
        <p className="eyebrow mb-2">{t.projects.stackLabel}</p>
        <ul className="flex flex-wrap gap-2">
          {study.stack.map((tech) => (
            <li key={tech}>
              <Badge variant="outline">{tech}</Badge>
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-5">{links}</div>
    </>
  );

  return (
    <>
      <Card
        className={cn(
          'p-6 transition-colors hover:border-accent/40',
          featured ? 'lg:p-8' : 'h-full',
        )}
      >
        {featured ? (
          <div className="grid items-start gap-8 lg:grid-cols-12">
            <div className="lg:col-span-5">{content}</div>
            <div className="lg:col-span-7">
              <Diagram variant={study.diagram} label={`${study.title} — diagram`} />
            </div>
          </div>
        ) : (
          <div className="flex h-full flex-col gap-6">
            <Diagram variant={study.diagram} label={`${study.title} — diagram`} />
            <div className="flex-1">{content}</div>
          </div>
        )}
      </Card>

      {open && <CaseDrawer study={study} onClose={() => setOpen(false)} />}
    </>
  );
}

function CaseDrawer({ study, onClose }: { study: CaseStudy; onClose: () => void }) {
  const { t } = useI18n();
  const panelRef = useRef<HTMLDivElement>(null);
  useFocusTrap(panelRef, true);

  useEffect(() => {
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <button
        type="button"
        aria-label={t.common.closeCase}
        onClick={onClose}
        className="absolute inset-0 bg-foreground/40 backdrop-blur-sm"
      />
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={`case-${study.id}`}
        className="relative flex h-full w-full max-w-xl flex-col overflow-y-auto border-l border-border bg-surface p-6 shadow-elevated"
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <Badge>{study.type}</Badge>
            <h3 id={`case-${study.id}`} className="mt-3 text-2xl font-bold leading-tight">
              {study.title}
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label={t.common.closeCase}
            className="inline-flex size-11 shrink-0 items-center justify-center rounded-md border border-border bg-surface hover:bg-surface-subtle"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <DrawerSection title={t.projects.problemLabel} items={[study.problem]} />
        <DrawerSection title={t.projects.builtLabel} items={study.built} />
        <DrawerSection title={t.projects.decisionsLabel} items={study.decisions} />
        <DrawerSection title={t.projects.learningsLabel} items={study.learnings} />

        <div className="mt-8">
          <p className="eyebrow mb-2">{t.projects.resultsLabel}</p>
          <div className="grid grid-cols-2 gap-3">
            {study.results.map((result) => (
              <MetricTile
                key={result.label}
                value={result.value}
                label={result.label}
                note={result.source}
              />
            ))}
          </div>
        </div>

        {study.repo !== undefined && (
          <div className="mt-8">
            <Button asChild>
              <a href={study.repo} target="_blank" rel="noopener noreferrer">
                <Github className="h-4 w-4" />
                {t.projects.repo}
              </a>
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

function DrawerSection({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="mt-8">
      <p className="eyebrow mb-2">{title}</p>
      <ul className="space-y-2">
        {items.map((item) => (
          <li key={item} className="flex items-start gap-2 text-sm text-muted-foreground">
            <span
              className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent"
              aria-hidden="true"
            />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
