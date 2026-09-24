/**
 * AuthContext — single source of truth for authentication state.
 * Provides login, register, logout, and current user to the entire app.
 */
import React, { createContext, useContext, useEffect, useReducer, useCallback } from 'react';
import { authService } from '@/services/authService';
import type { ProfileResponse, LoginRequest, RegisterRequest } from '@/types';

// ─── State ────────────────────────────────────────────────────────────────────
interface AuthState {
  user: ProfileResponse | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: ProfileResponse; token: string } }
  | { type: 'AUTH_ERROR'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'SET_USER'; payload: ProfileResponse };

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, isLoading: true, error: null };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        isLoading: false,
        isAuthenticated: true,
        user: action.payload.user,
        token: action.payload.token,
        error: null,
      };
    case 'AUTH_ERROR':
      return { ...state, isLoading: false, error: action.payload };
    case 'LOGOUT':
      return { user: null, token: null, isLoading: false, isAuthenticated: false, error: null };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    case 'SET_USER':
      return { ...state, user: action.payload };
    default:
      return state;
  }
}

// ─── Context ─────────────────────────────────────────────────────────────────
interface AuthContextValue extends AuthState {
  login: (payload: LoginRequest) => Promise<void>;
  register: (payload: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

// ─── Provider ────────────────────────────────────────────────────────────────
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    token: localStorage.getItem('access_token'),
    isLoading: true,
    isAuthenticated: false,
    error: null,
  });

  // Restore session on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const stored = localStorage.getItem('user_profile');
    if (token && stored) {
      try {
        const user = JSON.parse(stored) as ProfileResponse;
        dispatch({ type: 'AUTH_SUCCESS', payload: { user, token } });
        // Silently re-validate the token
        authService.getProfile().then((fresh) => {
          localStorage.setItem('user_profile', JSON.stringify(fresh));
          dispatch({ type: 'SET_USER', payload: fresh });
        }).catch(() => {
          // Token invalid — clean up
          localStorage.removeItem('access_token');
          localStorage.removeItem('user_profile');
          dispatch({ type: 'LOGOUT' });
        });
      } catch {
        dispatch({ type: 'LOGOUT' });
      }
    } else {
      dispatch({ type: 'AUTH_ERROR', payload: '' }); // clears loading
      dispatch({ type: 'LOGOUT' });
    }
  }, []);

  // Listen for expired-token events from Axios interceptor
  useEffect(() => {
    const handler = () => dispatch({ type: 'LOGOUT' });
    window.addEventListener('auth:expired', handler);
    return () => window.removeEventListener('auth:expired', handler);
  }, []);

  const login = useCallback(async (payload: LoginRequest) => {
    dispatch({ type: 'AUTH_START' });
    try {
      const tokenResp = await authService.login(payload);
      localStorage.setItem('access_token', tokenResp.access_token);
      const profile = await authService.getProfile();
      localStorage.setItem('user_profile', JSON.stringify(profile));
      dispatch({ type: 'AUTH_SUCCESS', payload: { user: profile, token: tokenResp.access_token } });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Login failed';
      dispatch({ type: 'AUTH_ERROR', payload: msg });
      throw err;
    }
  }, []);

  const register = useCallback(async (payload: RegisterRequest) => {
    dispatch({ type: 'AUTH_START' });
    try {
      await authService.register(payload);
      // Auto-login after registration
      const tokenResp = await authService.login({ email: payload.email, password: payload.password });
      localStorage.setItem('access_token', tokenResp.access_token);
      const profile = await authService.getProfile();
      localStorage.setItem('user_profile', JSON.stringify(profile));
      dispatch({ type: 'AUTH_SUCCESS', payload: { user: profile, token: tokenResp.access_token } });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Registration failed';
      dispatch({ type: 'AUTH_ERROR', payload: msg });
      throw err;
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch {
      // ignore server-side logout errors; client cleanup always happens
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_profile');
      dispatch({ type: 'LOGOUT' });
    }
  }, []);

  const clearError = useCallback(() => dispatch({ type: 'CLEAR_ERROR' }), []);

  const refreshProfile = useCallback(async () => {
    const profile = await authService.getProfile();
    localStorage.setItem('user_profile', JSON.stringify(profile));
    dispatch({ type: 'SET_USER', payload: profile });
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout, clearError, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

// ─── Hook ─────────────────────────────────────────────────────────────────────
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
