import axios from 'axios';

const aiClient = axios.create({
  baseURL: import.meta.env.VITE_AI_API_BASE_URL || 'http://localhost:8001',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

aiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

aiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_profile');
      window.dispatchEvent(new CustomEvent('auth:expired'));
    }
    return Promise.reject(error);
  }
);

export default aiClient;
