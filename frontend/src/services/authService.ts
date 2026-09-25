/**
 * authService — wraps all /auth endpoints.
 * Never called directly from components; use AuthContext or useAuth hook.
 */
import api from './api';
import type {
  ApiResponse,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  ProfileResponse,
} from '@/types';

const PREFIX = '/api/v1/auth';

export const authService = {
  async login(payload: LoginRequest): Promise<TokenResponse> {
    const { data } = await api.post<ApiResponse<TokenResponse>>(`${PREFIX}/login`, payload);
    return data.data;
  },

  async register(payload: RegisterRequest): Promise<ProfileResponse> {
    const { data } = await api.post<ApiResponse<ProfileResponse>>(`${PREFIX}/register`, payload);
    return data.data;
  },

  async logout(): Promise<void> {
    await api.post(`${PREFIX}/logout`);
  },

  async getProfile(): Promise<ProfileResponse> {
    const { data } = await api.get<ApiResponse<ProfileResponse>>(`${PREFIX}/profile`);
    return data.data;
  },

  oauthLoginUrl(provider: 'google' | 'github'): string {
    return `/api/v1/auth/oauth/${provider}/login`;
  },

  async connectedProviders(): Promise<Array<{ provider: string; connected: boolean; provider_email?: string }>> {
    const { data } = await api.get<ApiResponse<{ providers: Array<{ provider: string; connected: boolean; provider_email?: string }> }>>(`${PREFIX}/oauth/providers`);
    return data.data.providers;
  },

  async oauthLinkUrl(provider: 'google' | 'github'): Promise<string> {
    const { data } = await api.post<ApiResponse<{ url: string }>>(`${PREFIX}/oauth/${provider}/start`);
    return data.data.url;
  },
};
