import { useEffect, useState } from 'react';
import { Activity, BookOpen, Github, ShieldCheck, Swords } from 'lucide-react';

import { askAssistant } from '@/features/chat/events';
import { useApiStatus } from '@/features/chat/useApiStatus';
import { useI18n } from '@/shared/lib/i18n';
import { formatDecimal, formatPercent, useEvalReport } from '@/shared/lib/eval-report';
import { Badge } from '@/shared/ui/badge';
import { Button } from '@/shared/ui/button';
import { Card } from '@/shared/ui/card';
import { Reveal } from '@/shared/ui/reveal';
import { Section, SectionHeader } from '@/shared/ui/section';
import { StatusPill } from '@/shared/ui/status-pill';

const REPO_URL = 'https://github.com/rufae/CV-Web';
const STATUS_TONE = { online: 'success', degraded: 'warning', offline: 'danger' } as const;

/** Latencia en ms -> texto corto ('420 ms', '1,24 s'); null si no hay datos. */
function formatLatency(ms: number | null | undefined): string | null {
  if (ms === null || ms === undefined) return null;
  if (ms < 1000) return `${Math.round(ms)} ms`;
  return `${(ms / 1000).toFixed(2).replace('.', ',')} s`;
}

export function AiLab() {
  const { t } = useI18n();
  const status = useApiStatus(true);
  const report = useEvalReport();
  const metrics = report.metrics ?? {};
  const gates = report.gates ?? {};
  const llm = status?.llm ?? null;

  const statusLabels = {
    online: t.aiLab.online,
    degraded: t.aiLab.degraded,
    offline: t.aiLab.offline,
  } as const;

  const [lastChecked, setLastChecked] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    if (status !== null) {
      setLastChecked(Date.now());
    }
  }, [status]);

  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 5000);
    return () => window.clearInterval(timer);
  }, []);

  const secondsAgo =
    lastChecked === null ? null : Math.max(0, Math.round((now - lastChecked) / 1000));

  const recallPass =
    metrics.recall_at_k !== undefined &&
    gates.recall_at_k !== undefined &&
    metrics.recall_at_k >= gates.recall_at_k;
  const refusalPass =
    metrics.refusal_recall !== undefined &&
    gates.refusal_recall !== undefined &&
    metrics.refusal_recall >= gates.refusal_recall;
  const leaksPass = (metrics.leaks ?? 0) === (gates.leaks ?? 0);

  const rows = [
    {
      metric: t.metrics.recall,
      value: formatDecimal(metrics.recall_at_k),
      threshold: `≥ ${formatDecimal(gates.recall_at_k, 2)}`,
      pass: recallPass,
      pending: false,
    },
    {
      metric: t.metrics.refusal,
      value: formatPercent(metrics.refusal_recall),
      threshold: `≥ ${formatPercent(gates.refusal_recall, 0)}`,
      pass: refusalPass,
      pending: false,
    },
    {
      metric: t.metrics.leaks,
      value: String(metrics.leaks ?? 0),
      threshold: '0',
      pass: leaksPass,
      pending: false,
    },
    {
      metric: t.metrics.injection,
      value: `${metrics.injection_refused ?? '—'}/${metrics.injection_cases ?? '—'}`,
      // Objetivo: rechazar el 100 % de los intentos de inyección (el eval
      // registra inyecciones rechazadas / totales).
      threshold: '100 %',
      pass:
        metrics.injection_cases !== undefined &&
        metrics.injection_refused !== undefined &&
        metrics.injection_refused >= metrics.injection_cases,
      pending: false,
    },
  ];

  return (
    <Section id="ai-lab" tone="subtle">
      <Reveal>
        <SectionHeader eyebrow={t.aiLab.eyebrow} title={t.aiLab.title} lead={t.aiLab.lead} />
      </Reveal>

      <div className="grid gap-6 lg:grid-cols-12">
        <Reveal className="lg:col-span-7">
          <Card className="h-full p-6">
            <h3 className="text-xl font-semibold">{t.aiLab.architectureTitle}</h3>
            <img
              src="/architecture.svg"
              alt={t.aiLab.diagramAlt}
              loading="lazy"
              width={960}
              height={380}
              className="mt-4 w-full rounded-lg border border-border"
            />
            <ol className="mt-4 grid gap-2 sm:grid-cols-2">
              {t.aiLab.steps.map((step, index) => (
                <li key={step} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <span className="mono-label mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-accent-soft text-accent-strong">
                    {index + 1}
                  </span>
                  {step}
                </li>
              ))}
            </ol>
            <ul className="mt-5 space-y-1.5 border-t border-border pt-4">
              {t.aiLab.specs.map((spec) => (
                <li key={spec} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" aria-hidden="true" />
                  {spec}
                </li>
              ))}
            </ul>
          </Card>
        </Reveal>

        <Reveal delay={0.06} className="lg:col-span-5">
          <Card className="flex h-full flex-col p-6">
            <h3 className="flex items-center gap-2 text-xl font-semibold">
              <Activity className="h-5 w-5 text-accent-strong" aria-hidden="true" />
              {t.aiLab.statusTitle}
            </h3>
            <div className="mt-4">
              {llm !== null ? (
                <StatusPill
                  tone={STATUS_TONE[llm]}
                  label={statusLabels[llm]}
                  detail={status !== null ? `${t.aiLab.tier} ${status.tier}` : undefined}
                  pulse={llm === 'online'}
                  className="px-4 py-2 text-sm"
                />
              ) : (
                <StatusPill tone="neutral" label={t.aiLab.checking} className="px-4 py-2 text-sm" />
              )}
            </div>
            <dl className="mt-6 grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-muted-foreground">{t.aiLab.p50}</dt>
                <dd className="tabular mt-1 font-mono text-base">
                  {formatLatency(status?.p50_ms) ?? t.aiLab.noData}
                </dd>
              </div>
              <div>
                <dt className="text-muted-foreground">{t.aiLab.p95}</dt>
                <dd className="tabular mt-1 font-mono text-base">
                  {formatLatency(status?.p95_ms) ?? t.aiLab.noData}
                </dd>
              </div>
            </dl>
            {secondsAgo !== null && (
              <p className="mt-6 font-mono text-xs text-muted-foreground">
                {t.aiLab.lastChecked.replace('{seconds}', String(secondsAgo))}
              </p>
            )}
          </Card>
        </Reveal>

        <Reveal className="lg:col-span-12">
          <Card className="p-6">
            <h3 className="text-xl font-semibold">{t.aiLab.evalTitle}</h3>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full min-w-[520px] border-collapse text-left text-sm">
                <caption className="sr-only">{t.aiLab.evalTitle}</caption>
                <thead>
                  <tr className="border-b border-border">
                    <th scope="col" className="py-2 pr-4 font-medium text-muted-foreground">
                      {t.aiLab.tableMetric}
                    </th>
                    <th scope="col" className="py-2 pr-4 font-medium text-muted-foreground">
                      {t.aiLab.tableValue}
                    </th>
                    <th scope="col" className="py-2 pr-4 font-medium text-muted-foreground">
                      {t.aiLab.tableThreshold}
                    </th>
                    <th scope="col" className="py-2 font-medium text-muted-foreground">
                      {t.aiLab.tableStatus}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr key={row.metric} className="border-b border-border last:border-0">
                      <th scope="row" className="py-3 pr-4 font-normal text-foreground">
                        {row.metric}
                      </th>
                      <td className="tabular py-3 pr-4 font-mono">{row.value}</td>
                      <td className="tabular py-3 pr-4 font-mono text-muted-foreground">
                        {row.threshold}
                      </td>
                      <td className="py-3">
                        {row.pending ? (
                          <Badge variant="secondary">{t.aiLab.noData}</Badge>
                        ) : (
                          <Badge variant={row.pass ? 'default' : 'destructive'}>
                            {row.pass ? `✓ ${t.aiLab.pass}` : `✗ ${t.aiLab.fail}`}
                          </Badge>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-4 font-mono text-xs text-muted-foreground">
              {t.aiLab.reportFooter
                .replace('{cases}', String(report.cases ?? '—'))
                .replace('{model}', report.embed_model ?? '—')
                .replace('{date}', report.date ?? '—')}
            </p>
            <div className="mt-3 flex flex-wrap gap-4 text-sm">
              <a
                href={`${REPO_URL}/blob/main/docs/evaluation.md`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-accent-strong hover:underline"
              >
                <BookOpen className="h-4 w-4" />
                {t.aiLab.methodology}
              </a>
              <a
                href={REPO_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-accent-strong hover:underline"
              >
                <Github className="h-4 w-4" />
                {t.aiLab.repo}
              </a>
            </div>
          </Card>
        </Reveal>

        <Reveal className="lg:col-span-6">
          <Card className="h-full p-6">
            <h3 className="flex items-center gap-2 text-xl font-semibold">
              <ShieldCheck className="h-5 w-5 text-accent-strong" aria-hidden="true" />
              {t.aiLab.guardsTitle}
            </h3>
            <div className="mt-4 space-y-4">
              <div>
                <p className="font-medium text-foreground">{t.aiLab.canSeeTitle}</p>
                <p className="mt-1 text-sm text-muted-foreground">{t.aiLab.canSeeText}</p>
              </div>
              <div>
                <p className="font-medium text-foreground">{t.aiLab.wontDoTitle}</p>
                <p className="mt-1 text-sm text-muted-foreground">{t.aiLab.wontDoText}</p>
              </div>
            </div>
          </Card>
        </Reveal>

        <Reveal delay={0.06} className="lg:col-span-6">
          <Card className="flex h-full flex-col p-6">
            <h3 className="flex items-center gap-2 text-xl font-semibold">
              <Swords className="h-5 w-5 text-accent-strong" aria-hidden="true" />
              {t.aiLab.challengeTitle}
            </h3>
            <p className="mt-2 text-sm text-muted-foreground">{t.aiLab.challengeText}</p>
            <div className="mt-4 flex flex-col gap-2">
              {t.aiLab.challengePrompts.map((prompt) => (
                <Button
                  key={prompt}
                  variant="secondary"
                  className="justify-start whitespace-normal text-left"
                  onClick={() => askAssistant(prompt)}
                >
                  {prompt}
                </Button>
              ))}
            </div>
          </Card>
        </Reveal>
      </div>
    </Section>
  );
}
