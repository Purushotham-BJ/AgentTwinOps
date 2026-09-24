/**
 * Axios instance — single source of truth for all HTTP calls.
 * All API calls go through this; never call axios directly in components.
 */
import axios, { AxiosError } from 'axios';

// Use environment variable for backend API URL
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// ─── Request interceptor — attach JWT ────────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Response interceptor — normalise errors ────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    console.error('API Error:', error);
    if (error.response?.status === 401) {
      // Token expired or invalid — clear storage and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_profile');
      // Avoid hard redirect inside interceptor for SSR safety; emit custom event
      window.dispatchEvent(new CustomEvent('auth:expired'));
    }
    return Promise.reject(error);
  }
);

export default api;

/** Extract a human-readable message from an Axios error */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as { error?: { message?: string }; detail?: string } | undefined;
    return (
      data?.error?.message ||
      data?.detail ||
      error.message ||
      'An unexpected error occurred'
    );
  }
  if (error instanceof Error) return error.message;
  return 'An unexpected error occurred';
}
