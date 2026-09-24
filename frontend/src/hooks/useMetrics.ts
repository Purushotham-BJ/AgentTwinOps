import { useState, useEffect, useCallback } from 'react';
import { metricsService } from '@/services/metricsService';
import type { MetricPoint } from '@/types';
import { getErrorMessage } from '@/services/api';

interface DashboardMetrics {
  cpu: MetricPoint[];
  memory: MetricPoint[];
  latency: MetricPoint[];
  network: MetricPoint[];
}

export function useMetrics() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await metricsService.getDashboardMetrics();
      setMetrics(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
    // Refresh every 60 seconds
    const interval = setInterval(fetch, 60000);
    return () => clearInterval(interval);
  }, [fetch]);

  return { metrics, isLoading, error, lastUpdated, refetch: fetch };
}
