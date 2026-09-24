/**
 * recommendationService — AI recommendations interface.
 * Connected to AI Service (LangGraph multi-agent system)
 */
import axios from 'axios';
import type { Recommendation, InfrastructureItem, IncidentItem } from '@/types';

const AI_API_BASE = import.meta.env.VITE_AI_API_BASE_URL || 'http://localhost:8001';

const aiClient = axios.create({
  baseURL: AI_API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

export const recommendationService = {
  /**
   * Fetch current AI recommendations.
   * GET /api/v1/recommendations
   */
  async list(
    infrastructure: InfrastructureItem[],
    incidents: IncidentItem[]
  ): Promise<Recommendation[]> {
    const response = await aiClient.get('/api/v1/recommendations');
    return response.data.data;
  },

  /**
   * Trigger AI recommendation generation.
   * POST /api/v1/recommendations/generate
   */
  async generate(
    infrastructure: InfrastructureItem[],
    incidents: IncidentItem[]
  ): Promise<Recommendation[]> {
    const response = await aiClient.post('/api/v1/recommendations/generate', {
      infrastructure_ids: infrastructure.map(i => i.id),
      incident_ids: incidents.map(i => i.id),
      force_regenerate: true,
    });
    return response.data.data;
  },
};
