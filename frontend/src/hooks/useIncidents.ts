import { useState, useEffect, useCallback } from 'react';
import { incidentService } from '@/services/incidentService';
import type { IncidentItem, IncidentCreateRequest, IncidentUpdateRequest } from '@/types';
import { getErrorMessage } from '@/services/api';

export function useIncidents() {
  const [items, setItems] = useState<IncidentItem[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await incidentService.list();
      setItems(resp.items);
      setTotal(resp.total);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetch(); }, [fetch]);

  const create = useCallback(async (payload: IncidentCreateRequest): Promise<IncidentItem> => {
    const created = await incidentService.create(payload);
    setItems((prev) => [created, ...prev]);
    setTotal((t) => t + 1);
    return created;
  }, []);

  const update = useCallback(async (id: string, payload: IncidentUpdateRequest): Promise<IncidentItem> => {
    const updated = await incidentService.update(id, payload);
    setItems((prev) => prev.map((i) => (i.id === id ? updated : i)));
    return updated;
  }, []);

  return { items, total, isLoading, error, refetch: fetch, create, update };
}
