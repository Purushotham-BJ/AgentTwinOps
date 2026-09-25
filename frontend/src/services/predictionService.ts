/**
 * predictionService — AI prediction interface.
 * Connected to the AI service prediction endpoints.
 */
import axios from 'axios';
import type { PredictionResult, PredictionRequest } from '@/types';

const AI_API_BASE = import.meta.env.VITE_AI_API_BASE_URL || 'http://localhost:8001';

const aiClient = axios.create({
  baseURL: AI_API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

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
