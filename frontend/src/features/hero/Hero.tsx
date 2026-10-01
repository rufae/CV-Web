import { lazy, Suspense } from 'react';
import { Download, MessageCircle } from 'lucide-react';

import { useI18n } from '@/shared/lib/i18n';
import { useEvalReport, formatDecimal, formatPercent } from '@/shared/lib/eval-report';
import { Button } from '@/shared/ui/button';
import { MetricTile } from '@/shared/ui/metric-tile';
import { Reveal } from '@/shared/ui/reveal';
import { StatusPill } from '@/shared/ui/status-pill';

const ChatEmbedded = lazy(() =>
  import('@/features/chat/Chat').then((module) => ({ default: module.ChatEmbedded })),
);

const STACK_TAGS = ['Ollama', 'bge-m3', 'Chroma', 'FastAPI', 'React'];

function focusConsole() {
  const console = document.getElementById('chat-console');
  console?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  console?.querySelector<HTMLTextAreaElement>('textarea')?.focus();
}

export function Hero() {
  const { t } = useI18n();
  const report = useEvalReport();
  const metrics = report.metrics ?? {};
  const leakCount = metrics.leaks ?? 0;

  return (
    <section
      id="hero"
      className="relative flex min-h-[min(100vh,880px)] scroll-mt-16 items-center overflow-hidden bg-background"
    >
      <div aria-hidden="true" className="hero-grid pointer-events-none absolute inset-0" />
      <div aria-hidden="true" className="hero-halo pointer-events-none absolute inset-0" />

      <div className="relative mx-auto w-full max-w-[1120px] px-5 py-16 md:px-6 md:py-20">
        <div className="grid items-center gap-12 lg:grid-cols-12">
          <div className="lg:col-span-7">
            <Reveal>
              <div className="flex flex-wrap items-center gap-3">
                <StatusPill tone="success" label={t.hero.status} pulse />
                <span className="mono-label text-muted-foreground">{t.hero.location}</span>
              </div>
            </Reveal>

            <Reveal delay={0.06}>
              <h1 className="mt-6 text-[clamp(2.25rem,1.2rem+4vw,4rem)] font-bold leading-[1.1] tracking-[-0.02em] text-foreground">
                {t.hero.titleBefore}
                <span className="text-accent-strong">{t.hero.titleAccent}</span>
                {t.hero.titleAfter}
              </h1>
            </Reveal>

            <Reveal delay={0.12}>
              <p className="mt-5 max-w-[60ch] text-lg leading-relaxed text-muted-foreground">
                {t.hero.lead}
              </p>
            </Reveal>

            <Reveal delay={0.18}>
              <div className="mt-8 flex flex-wrap items-center gap-3">
                <Button onClick={focusConsole}>
                  <MessageCircle className="h-4 w-4" />
                  {t.hero.ctaTalk}
                </Button>
                <Button variant="secondary" asChild>
                  <a href="#projects">{t.hero.ctaProjects}</a>
                </Button>
                <a
                  href="/curriculum-vitae.pdf"
                  download="Rafael_CV.pdf"
                  className="inline-flex items-center gap-2 text-sm font-semibold text-accent-strong underline-offset-4 hover:underline"
                >
                  <Download className="h-4 w-4" />
                  {t.hero.ctaCv}
                </a>
              </div>
            </Reveal>

            <Reveal delay={0.24}>
              <ul className="mt-8 flex flex-wrap items-center gap-x-3 gap-y-2">
                {STACK_TAGS.map((tag) => (
                  <li
                    key={tag}
                    className="mono-label rounded-md bg-surface-subtle px-2 py-1 text-muted-foreground"
                  >
                    {tag}
                  </li>
                ))}
              </ul>
            </Reveal>
          </div>

          <div className="lg:col-span-5" id="chat-console">
            <Reveal delay={0.12} className="shadow-elevated rounded-xl">
              <Suspense
                fallback={
                  <div className="h-[420px] w-full animate-pulse rounded-xl border border-border bg-surface-subtle" />
                }
              >
                <ChatEmbedded />
              </Suspense>
            </Reveal>
          </div>
        </div>

        <Reveal delay={0.18} className="mt-14">
          <p className="eyebrow mb-4">{t.hero.metricsLabel}</p>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <MetricTile value={formatDecimal(metrics.recall_at_k)} label={t.metrics.recall} />
            <MetricTile value={formatPercent(metrics.refusal_recall)} label={t.metrics.refusal} />
            <MetricTile value={String(leakCount)} label={t.metrics.leaks} />
            <MetricTile value="—" label={t.metrics.latency} note={t.metrics.latencyNote} />
          </div>
          <p className="mt-3 font-mono text-xs text-muted-foreground">
            {t.metrics.dataset} n={report.cases ?? '—'} · {report.date ?? '—'} ·{' '}
            <a href="#ai-lab" className="text-accent-strong underline">
              {t.metrics.methodology} →
            </a>
          </p>
        </Reveal>
      </div>
    </section>
  );
}
