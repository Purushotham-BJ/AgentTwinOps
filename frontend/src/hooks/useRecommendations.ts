import { useState, useEffect, useCallback } from 'react';
import { recommendationService } from '@/services/recommendationService';
import type { Recommendation, InfrastructureItem, IncidentItem } from '@/types';
import { getErrorMessage } from '@/services/api';

export function useRecommendations(infrastructure: InfrastructureItem[], incidents: IncidentItem[]) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (infrastructure.length === 0) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await recommendationService.list(infrastructure, incidents);
      setRecommendations(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [infrastructure, incidents]);

  useEffect(() => {
    if (infrastructure.length > 0) fetch();
    else setIsLoading(false);
  }, [fetch, infrastructure.length]);

  const generate = useCallback(async (serviceId?: string) => {
    setIsGenerating(true);
    setError(null);
    try {
      const selected = serviceId ? infrastructure.filter((item) => item.id === serviceId) : infrastructure;
      const data = await recommendationService.generate(selected, incidents);
      setRecommendations(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsGenerating(false);
    }
  }, [infrastructure, incidents]);

  return { recommendations, isLoading, isGenerating, error, refetch: fetch, generate };
}
