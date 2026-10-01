import { useEffect, useState } from 'react';

export interface EvalReport {
  date?: string;
  embed_model?: string;
  top_k?: number;
  min_score?: number;
  cases?: number;
  passed?: boolean;
  gates?: {
    recall_at_k?: number;
    refusal_recall?: number;
    leaks?: number;
  };
  metrics?: {
    recall_at_k?: number;
    mrr?: number;
    hit_rate?: number;
    refusal_recall?: number;
    refusal_precision?: number;
    leaks?: number;
    answerable?: number;
    refusal_cases?: number;
    injection_cases?: number;
    injection_refused?: number;
  };
}

const FALLBACK: EvalReport = {
  metrics: { recall_at_k: 1, refusal_recall: 1, leaks: 0 },
  gates: { recall_at_k: 0.9, refusal_recall: 0.95, leaks: 0 },
  embed_model: 'bge-m3',
};

/** Lee el informe de evaluación copiado en build (`/eval-latest.json`). */
export function useEvalReport(): EvalReport {
  const [report, setReport] = useState<EvalReport>(FALLBACK);

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

  return report;
}

export function formatPercent(value: number | undefined, digits = 1): string {
  if (value === undefined) {
    return '—';
  }
  return `${(value * 100).toFixed(digits).replace('.', ',')} %`;
}

export function formatDecimal(value: number | undefined, digits = 3): string {
  if (value === undefined) {
    return '—';
  }
  return value.toFixed(digits).replace('.', ',');
}
