import { useState, useEffect, useCallback } from 'react';
import { infrastructureService } from '@/services/infrastructureService';
import type { InfrastructureItem, InfrastructureCreateRequest, InfrastructureUpdateRequest } from '@/types';
import { getErrorMessage } from '@/services/api';

export function useInfrastructure() {
  const [items, setItems] = useState<InfrastructureItem[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await infrastructureService.list();
      setItems(resp.items);
      setTotal(resp.total);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetch(); }, [fetch]);

  const create = useCallback(async (payload: InfrastructureCreateRequest): Promise<InfrastructureItem> => {
    const created = await infrastructureService.create(payload);
    setItems((prev) => [created, ...prev]);
    setTotal((t) => t + 1);
    return created;
  }, []);

  const update = useCallback(async (id: string, payload: InfrastructureUpdateRequest): Promise<InfrastructureItem> => {
    const updated = await infrastructureService.update(id, payload);
    setItems((prev) => prev.map((i) => (i.id === id ? updated : i)));
    return updated;
  }, []);

  const remove = useCallback(async (id: string): Promise<void> => {
    await infrastructureService.delete(id);
    setItems((prev) => prev.filter((i) => i.id !== id));
    setTotal((t) => t - 1);
  }, []);

  return { items, total, isLoading, error, refetch: fetch, create, update, remove };
}
