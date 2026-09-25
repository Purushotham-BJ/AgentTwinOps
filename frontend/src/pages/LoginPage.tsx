import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Eye, EyeOff, Activity, LogIn, UserPlus } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { Input } from '@/components/common/Input';
import { Button } from '@/components/common/Button';
import { getErrorMessage } from '@/services/api';
import { authService } from '@/services/authService';

type Mode = 'login' | 'register';

export function LoginPage() {
  const { login, register, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState<Mode>('login');
  const [showPass, setShowPass] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [form, setForm] = useState({ name: '', email: '', password: '' });

  const startOAuth = (provider: 'google' | 'github') => {
    window.location.assign(authService.oauthLoginUrl(provider));
  };

  useEffect(() => {
    if (isAuthenticated) navigate('/dashboard', { replace: true });
  }, [isAuthenticated, navigate]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      if (mode === 'login') {
        await login({ email: form.email, password: form.password });
      } else {
        if (!form.name.trim()) { setError('Name is required'); setSubmitting(false); return; }
        await register({ name: form.name, email: form.email, password: form.password });
      }
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  if (isLoading) return null;

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--color-bg-base)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 'var(--space-6)',
    }}>
      {/* Background grid */}
      <div style={{
        position: 'fixed', inset: 0, pointerEvents: 'none', opacity: 0.03,
        backgroundImage: 'linear-gradient(var(--color-blue-400) 1px, transparent 1px), linear-gradient(90deg, var(--color-blue-400) 1px, transparent 1px)',
        backgroundSize: '40px 40px',
      }} />

      <div style={{ width: '100%', maxWidth: '420px', animation: 'fadeIn 0.2s ease' }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-8)' }}>
          <div style={{
            width: '56px', height: '56px', margin: '0 auto var(--space-4)',
            background: 'linear-gradient(135deg, var(--color-blue-500), var(--color-cyan-400))',
            borderRadius: 'var(--radius-xl)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 32px rgba(31,111,235,0.3)',
          }}>
            <Activity size={28} color="#fff" />
          </div>
          <h1 style={{ fontSize: 'var(--text-2xl)', marginBottom: '6px' }}>AgentTwinOps</h1>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)' }}>
            AI-Powered Digital Twin Platform
          </p>
        </div>

        {/* Card */}
        <div style={{
          background: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-xl)',
          padding: 'var(--space-8)',
          boxShadow: 'var(--shadow-xl)',
        }}>
          {/* Mode tabs */}
          <div style={{
            display: 'flex', gap: '4px', padding: '4px',
            background: 'var(--color-bg-base)',
            borderRadius: 'var(--radius-md)', marginBottom: 'var(--space-6)',
          }}>
            {(['login', 'register'] as Mode[]).map((m) => (
              <button
                key={m}
                onClick={() => { setMode(m); setError(''); }}
                style={{
                  flex: 1, padding: '8px', borderRadius: 'var(--radius-sm)',
                  border: 'none', cursor: 'pointer', fontSize: 'var(--text-sm)', fontWeight: '500',
                  background: mode === m ? 'var(--color-bg-elevated)' : 'transparent',
                  color: mode === m ? 'var(--color-text-primary)' : 'var(--color-text-muted)',
                  transition: 'all var(--transition-fast)',
                }}
              >
                {m === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            {mode === 'register' && (
              <Input
                label="Full Name"
                name="name"
                type="text"
                placeholder="John Doe"
                value={form.name}
                onChange={handleChange}
                autoComplete="name"
                required
              />
            )}

            <Input
              label="Email"
              name="email"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={handleChange}
              autoComplete="email"
              required
            />

            <Input
              label="Password"
              name="password"
              type={showPass ? 'text' : 'password'}
              placeholder={mode === 'register' ? 'Min 6 characters' : '••••••••'}
              value={form.password}
              onChange={handleChange}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              required
              minLength={mode === 'register' ? 6 : 1}
              rightIcon={
                <button type="button" onClick={() => setShowPass((s) => !s)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', display: 'flex', padding: 0 }}>
                  {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              }
            />

            {error && (
              <div style={{ padding: 'var(--space-3)', background: 'rgba(248,81,73,0.1)', border: '1px solid rgba(248,81,73,0.3)', borderRadius: 'var(--radius-md)', fontSize: 'var(--text-sm)', color: 'var(--color-red-300)' }}>
                {error}
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              size="md"
              isLoading={submitting}
              leftIcon={mode === 'login' ? <LogIn size={16} /> : <UserPlus size={16} />}
              style={{ width: '100%', marginTop: 'var(--space-2)' }}
            >
              {mode === 'login' ? 'Sign In' : 'Create Account'}
            </Button>
          </form>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', margin: 'var(--space-5) 0' }}>
            <div style={{ flex: 1, height: 1, background: 'var(--color-border)' }} />
            <span style={{ color: 'var(--color-text-muted)', fontSize: 'var(--text-xs)' }}>OR CONTINUE WITH</span>
            <div style={{ flex: 1, height: 1, background: 'var(--color-border)' }} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
            {(['google', 'github'] as const).map((provider) => (
              <button key={provider} type="button" onClick={() => startOAuth(provider)} style={{
                padding: '10px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)',
                background: 'var(--color-bg-elevated)', color: 'var(--color-text-primary)', cursor: 'pointer',
              }}>
                {provider === 'google' ? 'Continue with Google' : 'Continue with GitHub'}
              </button>
            ))}
          </div>
        </div>

        <p style={{ textAlign: 'center', fontSize: 'var(--text-xs)', color: 'var(--color-text-disabled)', marginTop: 'var(--space-5)' }}>
          AgentTwinOps v1.0 — Multi-Agent Digital Twin Platform
        </p>
      </div>
    </div>
  );
}
