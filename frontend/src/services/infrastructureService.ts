/**
 * infrastructureService — wraps all /api/v1/infrastructure endpoints.
 */
import api from './api';
import type {
  ApiResponse,
  InfrastructureItem,
  InfrastructureListResponse,
  InfrastructureCreateRequest,
  InfrastructureUpdateRequest,
} from '@/types';

const PREFIX = '/api/v1/infrastructure';

export const infrastructureService = {
  async list(offset = 0, limit = 100): Promise<InfrastructureListResponse> {
    const { data } = await api.get<ApiResponse<InfrastructureListResponse>>(PREFIX, {
      params: { offset, limit },
    });
    return data.data;
  },

  async get(id: string): Promise<InfrastructureItem> {
    const { data } = await api.get<ApiResponse<InfrastructureItem>>(`${PREFIX}/${id}`);
    return data.data;
  },

  async create(payload: InfrastructureCreateRequest): Promise<InfrastructureItem> {
    const { data } = await api.post<ApiResponse<InfrastructureItem>>(PREFIX, payload);
    return data.data;
  },

  async update(id: string, payload: InfrastructureUpdateRequest): Promise<InfrastructureItem> {
    const { data } = await api.put<ApiResponse<InfrastructureItem>>(`${PREFIX}/${id}`, payload);
    return data.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`${PREFIX}/${id}`);
  },
};
