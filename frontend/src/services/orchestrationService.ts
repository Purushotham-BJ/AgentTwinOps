import axios from 'axios';
import type { OrchestrationResult } from '@/types';

const client = axios.create({
  baseURL: import.meta.env.VITE_AI_API_BASE_URL || 'http://localhost:8001',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const orchestrationService = {
  async run(serviceId: string): Promise<OrchestrationResult> {
    const response = await client.post('/api/v1/agents/orchestrate', {
      service_id: serviceId,
      include_prediction: true,
      include_simulation: true,
      include_recovery: true,
    });
    return response.data;
  },
};
