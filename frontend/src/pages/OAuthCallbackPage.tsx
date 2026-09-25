import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '@/services/authService';

export function OAuthCallbackPage() {
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.slice(1));
    const token = params.get('access_token');
    window.history.replaceState({}, document.title, '/oauth/callback');
    if (!token) {
      navigate('/login?oauth_error=missing_token', { replace: true });
      return;
    }
    localStorage.setItem('access_token', token);
    authService.getProfile()
      .then((profile) => {
        localStorage.setItem('user_profile', JSON.stringify(profile));
        window.location.replace('/dashboard');
      })
      .catch(() => {
        localStorage.removeItem('access_token');
        navigate('/login?oauth_error=invalid_session', { replace: true });
      });
  }, [navigate]);

  return <div style={{ padding: 'var(--space-8)', textAlign: 'center' }}>Completing sign-in…</div>;
}
