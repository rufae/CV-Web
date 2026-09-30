import { useEffect, useState } from 'react';
import { Activity, BookOpen, Github, ShieldCheck } from 'lucide-react';

import { useApiStatus } from '@/features/chat/useApiStatus';
import { useI18n } from '@/shared/lib/i18n';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';

interface EvalReport {
  metrics?: {
    recall_at_k?: number;
    refusal_recall?: number;
    leaks?: number;
  };
  embed_model?: string;
  date?: string;
}

const FALLBACK_REPORT: EvalReport = {
  metrics: { recall_at_k: 1, refusal_recall: 1, leaks: 0 },
  embed_model: 'bge-m3',
};

const STATUS_STYLES = {
  online: 'bg-green-500',
  degraded: 'bg-amber-500',
  offline: 'bg-red-500',
} as const;

const REPO_URL = 'https://github.com/rufae/CV-Web';

export function AiLab() {
  const { t } = useI18n();
  const status = useApiStatus(true);
  const [report, setReport] = useState<EvalReport>(FALLBACK_REPORT);

  useEffect(() => {
    let cancelled = false;
    fetch('/eval-latest.json')
      .then((response) => (response.ok ? (response.json() as Promise<EvalReport>) : null))
      .then((data) => {
        if (!cancelled && data !== null) {
          setReport(data);
        }
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, []);

  const llm = status?.llm ?? 'offline';
  const metrics = report.metrics ?? {};
  const metric = (value: number | undefined) => (value ?? 0).toFixed(3);

  return (
    <section id="ai-lab" className="bg-muted/20 px-6 py-20">
      <div className="mx-auto max-w-6xl">
        <div className="mb-16 text-center">
          <h2 className="mb-4">{t.aiLab.title}</h2>
          <div className="mx-auto h-1 w-20 rounded-full bg-accent" />
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">{t.aiLab.subtitle}</p>
        </div>

        <div className="grid gap-8 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-accent" />
                {t.aiLab.statusTitle}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-2 text-sm">
                <span
                  className={`h-2.5 w-2.5 rounded-full ${STATUS_STYLES[llm]}`}
                  aria-hidden="true"
                />
                <span className="font-medium">{t.aiLab[llm]}</span>
                {status !== null && (
                  <span className="text-muted-foreground">· tier {status.tier}</span>
                )}
              </div>
              <img
                src="/architecture.svg"
                alt={t.aiLab.diagramAlt}
                loading="lazy"
                className="w-full rounded-lg border border-border bg-card"
              />
            </CardContent>
          </Card>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>{t.aiLab.metricsTitle}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl">{metric(metrics.recall_at_k)}</div>
                    <div className="text-sm text-muted-foreground">{t.aiLab.recall}</div>
                  </div>
                  <div>
                    <div className="text-2xl">{metric(metrics.refusal_recall)}</div>
                    <div className="text-sm text-muted-foreground">{t.aiLab.refusal}</div>
                  </div>
                  <div>
                    <div className="text-2xl">{metrics.leaks ?? 0}</div>
                    <div className="text-sm text-muted-foreground">{t.aiLab.leaks}</div>
                  </div>
                </div>
                <p className="mt-4 text-sm text-muted-foreground">
                  {t.aiLab.model}: <span className="font-medium">{report.embed_model}</span>
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShieldCheck className="h-5 w-5 text-accent" />
                  {t.aiLab.privacyTitle}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{t.aiLab.privacyText}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>{t.aiLab.linksTitle}</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col gap-2 text-sm">
                <a
                  href={REPO_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-accent hover:underline"
                >
                  <Github className="h-4 w-4" />
                  {t.aiLab.repo}
                </a>
                <a
                  href={`${REPO_URL}/blob/main/docs/evaluation.md`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-accent hover:underline"
                >
                  <BookOpen className="h-4 w-4" />
                  {t.aiLab.evaluation}
                </a>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
}
