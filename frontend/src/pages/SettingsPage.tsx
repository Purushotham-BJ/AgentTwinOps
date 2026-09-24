import React, { useState } from 'react';
import { User, Bell, Info, LogOut, Save, Shield, Activity } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { Card, CardHeader } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Badge } from '@/components/common/Badge';
import { formatDate } from '@/utils/format';
import { systemService } from '@/services/systemService';

export function SettingsPage() {
  const { user, logout, refreshProfile } = useAuth();
  const [apiVersion, setApiVersion] = useState<{ app_name: string; version: string; api_version: string; python_version: string } | null>(null);
  const [loadingVersion, setLoadingVersion] = useState(false);

  const fetchVersion = async () => {
    setLoadingVersion(true);
    try {
      const v = await systemService.version();
      setApiVersion(v);
    } catch { /* ignore */ }
    finally { setLoadingVersion(false); }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)', maxWidth: '720px' }}>

      {/* Profile */}
      <Card>
        <CardHeader title="Profile" icon={<User size={16} />} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
            <div style={{
              width: '64px', height: '64px', borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--color-blue-500), var(--color-cyan-400))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 'var(--text-2xl)', fontWeight: '700', color: '#fff', flexShrink: 0,
            }}>
              {user?.name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'U'}
            </div>
            <div>
              <h3 style={{ fontSize: 'var(--text-lg)', margin: '0 0 4px' }}>{user?.name}</h3>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)', margin: 0 }}>{user?.email}</p>
              <Badge variant="default" style={{ marginTop: '6px' }}>{user?.role}</Badge>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
            <div style={{ background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', padding: 'var(--space-3)' }}>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: '4px' }}>User ID</div>
              <div style={{ fontSize: 'var(--text-xs)', fontFamily: 'var(--font-mono)', color: 'var(--color-text-secondary)' }}>{user?.id?.slice(0, 16)}...</div>
            </div>
            <div style={{ background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', padding: 'var(--space-3)' }}>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: '4px' }}>Member Since</div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>{user?.created_at ? formatDate(user.created_at) : '—'}</div>
            </div>
          </div>

          <Button variant="secondary" size="sm" leftIcon={<User size={14} />} onClick={refreshProfile} style={{ alignSelf: 'flex-start' }}>
            Refresh Profile
          </Button>
        </div>
      </Card>

      {/* Notifications (static preferences — no backend) */}
      <Card>
        <CardHeader title="Notification Preferences" icon={<Bell size={16} />} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          {[
            { label: 'Critical incident alerts', enabled: true },
            { label: 'High failure risk warnings', enabled: true },
            { label: 'AI recommendation generated', enabled: false },
            { label: 'Simulation completed', enabled: false },
            { label: 'Infrastructure status changes', enabled: true },
          ].map(({ label, enabled }) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: 'var(--space-3)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)' }}>
              <span style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>{label}</span>
              <Badge variant={enabled ? 'success' : 'muted'}>{enabled ? 'Enabled' : 'Disabled'}</Badge>
            </div>
          ))}
          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
            Notification preference persistence requires a user preferences API (pending).
          </p>
        </div>
      </Card>

      {/* Security */}
      <Card>
        <CardHeader title="Security" icon={<Shield size={16} />} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          <div style={{ padding: 'var(--space-3)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: 'var(--text-sm)', fontWeight: '500', color: 'var(--color-text-primary)' }}>Authentication</div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>JWT Bearer token · Stateless</div>
            </div>
            <Badge variant="success" dot>Active</Badge>
          </div>
          <div style={{ padding: 'var(--space-3)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: 'var(--text-sm)', fontWeight: '500', color: 'var(--color-text-primary)' }}>Token expires</div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>60 minutes from login</div>
            </div>
            <Badge variant="warning">60 min</Badge>
          </div>
        </div>
      </Card>

      {/* System info */}
      <Card>
        <CardHeader title="System Information" icon={<Info size={16} />} action={
          <Button variant="ghost" size="sm" onClick={fetchVersion} isLoading={loadingVersion} leftIcon={<Activity size={12} />}>
            Check API
          </Button>
        } />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
          {[
            { label: 'Frontend Version', value: '1.0.0' },
            { label: 'React', value: '18.3' },
            { label: 'Build', value: 'Vite 5.4' },
            { label: 'Backend API', value: apiVersion?.version ?? '—' },
            { label: 'API Version', value: apiVersion?.api_version ?? '—' },
            { label: 'Python', value: apiVersion?.python_version ?? '—' },
          ].map(({ label, value }) => (
            <div key={label} style={{ background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', padding: 'var(--space-3)' }}>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: '4px' }}>{label}</div>
              <div style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>{value}</div>
            </div>
          ))}
        </div>
      </Card>

      {/* Sign out */}
      <Card>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h4 style={{ margin: '0 0 4px' }}>Sign Out</h4>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)', margin: 0 }}>
              Discard your session token and return to the login screen.
            </p>
          </div>
          <Button variant="danger" size="sm" onClick={logout} leftIcon={<LogOut size={14} />}>
            Sign Out
          </Button>
        </div>
      </Card>
    </div>
  );
}
