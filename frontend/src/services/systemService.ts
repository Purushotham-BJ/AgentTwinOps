/**
 * systemService — wraps /api/v1/health and /api/v1/version endpoints.
 */
import api from './api';
import type { ApiResponse, HealthResponse, VersionResponse } from '@/types';

export const systemService = {
  async health(): Promise<HealthResponse> {
    const { data } = await api.get<ApiResponse<HealthResponse>>('/api/v1/health');
    return data.data;
  },

  async version(): Promise<VersionResponse> {
    const { data } = await api.get<ApiResponse<VersionResponse>>('/api/v1/version');
    return data.data;
  },
};
