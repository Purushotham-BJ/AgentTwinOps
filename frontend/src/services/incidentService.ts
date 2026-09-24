/**
 * incidentService — wraps all /api/v1/incidents endpoints.
 */
import api from './api';
import type {
  ApiResponse,
  IncidentItem,
  IncidentListResponse,
  IncidentCreateRequest,
  IncidentUpdateRequest,
} from '@/types';

const PREFIX = '/api/v1/incidents';

export const incidentService = {
  async list(offset = 0, limit = 100): Promise<IncidentListResponse> {
    const { data } = await api.get<ApiResponse<IncidentListResponse>>(PREFIX, {
      params: { offset, limit },
    });
    return data.data;
  },

  async get(id: string): Promise<IncidentItem> {
    const { data } = await api.get<ApiResponse<IncidentItem>>(`${PREFIX}/${id}`);
    return data.data;
  },

  async create(payload: IncidentCreateRequest): Promise<IncidentItem> {
    const { data } = await api.post<ApiResponse<IncidentItem>>(PREFIX, payload);
    return data.data;
  },

  async update(id: string, payload: IncidentUpdateRequest): Promise<IncidentItem> {
    const { data } = await api.put<ApiResponse<IncidentItem>>(`${PREFIX}/${id}`, payload);
    return data.data;
  },
};
