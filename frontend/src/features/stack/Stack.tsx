import { ArrowUpRight } from 'lucide-react';

import { useI18n } from '@/shared/lib/i18n';
import { Badge } from '@/shared/ui/badge';
import { Card } from '@/shared/ui/card';
import { Reveal } from '@/shared/ui/reveal';
import { Section, SectionHeader } from '@/shared/ui/section';

const EVIDENCE: Record<string, string> = {
  'IA y datos': '#ai-lab',
  Backend: '#projects',
  Frontend: '#projects',
  Móvil: '#experience',
  'Infra y DevOps': '#ai-lab',
  'Base de formación': '#education',
};

const EN_EVIDENCE: Record<string, string> = {
  'AI and data': '#ai-lab',
  Backend: '#projects',
  Frontend: '#projects',
  Mobile: '#experience',
  'Infra and DevOps': '#ai-lab',
  'Academic base': '#education',
};

function LevelRow({
  label,
  items,
  href,
  evidence,
}: {
  label: string;
  items: string[];
  href: string;
  evidence: string;
}) {
  return (
    <div className="flex flex-col gap-1.5 border-b border-border py-3 last:border-0 sm:flex-row sm:items-start sm:gap-4">
      <p className="mono-label w-32 shrink-0 pt-0.5 text-muted-foreground">{label}</p>
      <div className="flex flex-1 flex-wrap items-center gap-2">
        {items.length === 0 ? (
          <span className="text-sm text-muted-foreground">—</span>
        ) : (
          items.map((item) => (
            <Badge key={item} variant="outline">
              {item}
            </Badge>
          ))
        )}
      </div>
      <a
        href={href}
        aria-label={`${evidence}: ${items.join(', ')}`}
        className="hidden shrink-0 text-muted-foreground transition-colors hover:text-accent-strong sm:inline-flex"
      >
        <ArrowUpRight className="h-4 w-4" />
      </a>
    </div>
  );
}

export function Stack() {
  const { t } = useI18n();
  const [daily, projects] = t.stack.levels;

  return (
    <Section id="stack">
      <Reveal>
        <SectionHeader eyebrow={t.stack.eyebrow} title={t.stack.title} lead={t.stack.lead} />
      </Reveal>

      <div className="grid gap-6 md:grid-cols-2">
        {t.stack.groups.map((group, index) => {
          const href = EVIDENCE[group.title] ?? EN_EVIDENCE[group.title] ?? '#projects';
          return (
            <Reveal key={group.title} delay={Math.min(index, 3) * 0.06}>
              <Card className="h-full p-6">
                <h3 className="text-xl font-semibold">{group.title}</h3>
                <div className="mt-3">
                  <LevelRow
                    label={daily}
                    items={group.daily}
                    href={href}
                    evidence={t.stack.evidence}
                  />
                  <LevelRow
                    label={projects}
                    items={group.projects}
                    href={href}
                    evidence={t.stack.evidence}
                  />
                </div>
              </Card>
            </Reveal>
          );
        })}
      </div>

      <Reveal>
        <Card className="mt-6 p-6">
          <h3 className="text-xl font-semibold">{t.stack.now.title}</h3>
          <div className="mt-4 grid gap-6 md:grid-cols-2">
            <div>
              <p className="eyebrow mb-2">{t.stack.now.workingTitle}</p>
              <ul className="space-y-3">
                {t.stack.now.working.map((item) => (
                  <li key={item.name}>
                    <p className="font-semibold text-foreground">{item.name}</p>
                    <p className="text-sm text-muted-foreground">{item.detail}</p>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="eyebrow mb-2">{t.stack.now.learningTitle}</p>
              <ul className="flex flex-wrap gap-2">
                {t.stack.now.learning.map((item) => (
                  <li key={item}>
                    <Badge variant="outline">{item}</Badge>
                  </li>
                ))}
              </ul>
              <p className="mt-4 text-sm text-muted-foreground">{t.stack.now.improving}</p>
            </div>
          </div>
        </Card>
      </Reveal>
    </Section>
  );
}
