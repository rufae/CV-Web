import { useEffect, useState } from 'react';

import { API_URL } from '@/shared/api/client';
import type { ApiStatus } from '@/shared/api/types';

const POLL_MS = 30000;

/** Sondea `/api/status` cada 30 s mientras el panel está abierto y visible. */
export function useApiStatus(active: boolean): ApiStatus | null {
  const [status, setStatus] = useState<ApiStatus | null>(null);

  useEffect(() => {
    if (!active) {
      return;
    }
    let cancelled = false;

    const poll = async () => {
      if (typeof document !== 'undefined' && document.visibilityState === 'hidden') {
        return;
      }
      try {
        const response = await fetch(`${API_URL}/api/status`);
        if (response.ok) {
          const data = (await response.json()) as ApiStatus;
          if (!cancelled) {
            setStatus(data);
          }
        }
      } catch {
        if (!cancelled) {
          setStatus({ llm: 'offline', tier: 'cpu' });
        }
      }
    };

    void poll();
    const interval = window.setInterval(() => void poll(), POLL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [active]);

  return status;
}
