import { useState, useEffect, useCallback } from 'react';
import { twinService } from '@/services/twinService';
import { useInfrastructure } from './useInfrastructure';
import type { TwinObject } from '@/types';
import { getErrorMessage } from '@/services/api';

export function useDigitalTwin() {
  const { items: infrastructure, isLoading: infraLoading } = useInfrastructure();
  const [twins, setTwins] = useState<TwinObject[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastSynced, setLastSynced] = useState<Date | null>(null);

  const fetch = useCallback(async () => {
    if (infraLoading || infrastructure.length === 0) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await twinService.getTwins(infrastructure);
      setTwins(data);
      setLastSynced(new Date());
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [infrastructure, infraLoading]);

  useEffect(() => {
    if (!infraLoading) fetch();
  }, [fetch, infraLoading]);

  return {
    twins,
    isLoading: isLoading || infraLoading,
    error,
    lastSynced,
    refetch: fetch,
  };
}
