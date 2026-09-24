import { useState, useCallback } from 'react';
import { predictionService } from '@/services/predictionService';
import type { PredictionResult, PredictionRequest } from '@/types';
import { getErrorMessage } from '@/services/api';

export function usePredictions() {
  const [results, setResults] = useState<PredictionResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const predictCpu = useCallback(async (request: PredictionRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const r = await predictionService.predictCpu(request);
      setResults((prev) => [r, ...prev]);
      return r;
    } catch (err) {
      setError(getErrorMessage(err));
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const predictMemory = useCallback(async (request: PredictionRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const r = await predictionService.predictMemory(request);
      setResults((prev) => [r, ...prev]);
      return r;
    } catch (err) {
      setError(getErrorMessage(err));
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const predictFailure = useCallback(async (request: PredictionRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const r = await predictionService.predictFailure(request);
      setResults((prev) => [r, ...prev]);
      return r;
    } catch (err) {
      setError(getErrorMessage(err));
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearResults = useCallback(() => setResults([]), []);

  return { results, isLoading, error, predictCpu, predictMemory, predictFailure, clearResults };
}
