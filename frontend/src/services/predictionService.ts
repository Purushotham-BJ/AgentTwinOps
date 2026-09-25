/**
 * predictionService — AI prediction interface.
 * Connected to the AI service prediction endpoints.
 */
import type { PredictionResult, PredictionRequest } from '@/types';
import aiClient from './aiClient';

export const predictionService = {
  /**
   * Predict CPU usage for a service.
   * POST /api/v1/predict/cpu
   */
  async predictCpu(request: PredictionRequest): Promise<PredictionResult> {
    const response = await aiClient.post('/api/v1/predict/cpu', request);
    return response.data.data;
  },

  /**
   * Predict memory usage for a service.
   * POST /api/v1/predict/memory
   */
  async predictMemory(request: PredictionRequest): Promise<PredictionResult> {
    const response = await aiClient.post('/api/v1/predict/memory', request);
    return response.data.data;
  },

  /**
   * Predict failure probability for a service.
   * POST /api/v1/predict/failure
   */
  async predictFailure(request: PredictionRequest): Promise<PredictionResult> {
    const response = await aiClient.post('/api/v1/predict/failure', request);
    return response.data.data;
  },

  /**
   * List historical predictions.
   * NOTE: Not yet implemented in AI service
   */
  async listPredictions(): Promise<PredictionResult[]> {
    return [];
  },
};
