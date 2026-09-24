/**
 * twinService — Digital Twin interface.
 * Connected to AI Service (LangGraph multi-agent system)
 */
import axios from 'axios';
import type { TwinObject, InfrastructureItem } from '@/types';

const AI_API_BASE = import.meta.env.VITE_AI_API_BASE_URL || 'http://localhost:8001';

const aiClient = axios.create({
  baseURL: AI_API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

export const twinService = {
  /**
   * Get all digital twins.
   * GET /api/v1/twins
   */
  async getTwins(infrastructure: InfrastructureItem[]): Promise<TwinObject[]> {
    const response = await aiClient.get('/api/v1/twins');
    return response.data.data;
  },

  /**
   * Get a single twin by twin ID.
   * GET /api/v1/twins/{twin_id}
   */
  async getTwin(serviceId: string, serviceName: string): Promise<TwinObject> {
    const response = await aiClient.get(`/api/v1/twins/twin_${serviceId}`);
    return response.data.data;
  },
};
