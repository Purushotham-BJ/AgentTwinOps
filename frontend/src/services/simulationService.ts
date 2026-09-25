/**
 * simulationService — scenario simulation interface.
 * Connected to AI Service (LangGraph multi-agent system)
 */
import axios from 'axios';
import type { SimulationRequest, SimulationResult } from '@/types';

const AI_API_BASE = import.meta.env.VITE_AI_API_BASE_URL || 'http://localhost:8001';

const aiClient = axios.create({
  baseURL: AI_API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

aiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const simulationService = {
  /**
   * Run a scenario simulation.
   * POST /api/v1/simulate
   */
  async run(request: SimulationRequest): Promise<SimulationResult> {
    const response = await aiClient.post('/api/v1/simulate', request);
    return response.data.data;
  },

  /**
   * List past simulations.
   * NOTE: Not yet implemented in AI service
   */
  async list(): Promise<SimulationResult[]> {
    return [];
  },
};
