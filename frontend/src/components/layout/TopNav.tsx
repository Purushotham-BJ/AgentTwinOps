import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Menu, RefreshCw, User, LogOut, ChevronDown, Activity } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/common/Button';
import { NotificationBell } from './NotificationBell';

const PAGE_TITLES: Record<string, string> = {
  '/dashboard':       'Dashboard',
  '/infrastructure':  'Infrastructure',
  '/incidents':       'Incidents',
  '/digital-twin':    'Digital Twin',
  '/prediction':      'AI Prediction',
  '/simulation':      'Simulation',
  '/recommendations': 'AI Recommendations',
  '/reports':         'Reports',
  '/settings':        'Settings',
};

interface TopNavProps {
  onMenuClick: () => void;
  lastUpdated?: Date | null;
  onRefresh?: () => void;
}

export function TopNav({ onMenuClick, lastUpdated, onRefresh }: TopNavProps) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const title = PAGE_TITLES[location.pathname] || 'AgentTwinOps';

  const initials = user?.name
    ? user.name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : 'U';

  return (
    <header
      style={{
        height: 'var(--topnav-height)',
        background: 'var(--color-bg-surface)',
        borderBottom: '1px solid var(--color-border)',
        display: 'flex',
        alignItems: 'center',
        padding: '0 var(--space-5)',
        gap: 'var(--space-4)',
        position: 'sticky', top: 0,
        zIndex: 'var(--z-topnav)',
        flexShrink: 0,
      }}
    >
      {/* Mobile menu button */}
      <button
        onClick={onMenuClick}
        style={{
          display: 'none',
          padding: '6px', background: 'transparent', border: 'none',
          cursor: 'pointer', color: 'var(--color-text-secondary)', borderRadius: 'var(--radius-md)',
        }}
        aria-label="Open navigation menu"
        className="mobile-menu-btn"
      >
        <Menu size={20} />
      </button>

      {/* Page title */}
      <div style={{ flex: 1 }}>
        <h1 style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--font-semibold)', margin: 0, color: 'var(--color-text-primary)' }}>
          {title}
        </h1>
        {lastUpdated && (
          <p style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', margin: 0 }}>
            Updated {lastUpdated.toLocaleTimeString()}
          </p>
        )}
      </div>

      {/* System status indicator */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '4px 10px', background: 'rgba(63,185,80,0.1)', borderRadius: 'var(--radius-full)', border: '1px solid rgba(63,185,80,0.2)' }}>
        <Activity size={12} style={{ color: 'var(--color-green-400)' }} />
        <span style={{ fontSize: '0.7rem', color: 'var(--color-green-400)', fontWeight: '500' }}>LIVE</span>
      </div>

      {/* Refresh */}
      {onRefresh && (
        <Button variant="ghost" size="sm" onClick={onRefresh} style={{ padding: '6px' }} title="Refresh data" aria-label="Refresh data">
          <RefreshCw size={16} />
        </Button>
      )}

      <NotificationBell userId={user?.id} />

      {/* User menu */}
      <div style={{ position: 'relative' }}>
        <button
          onClick={() => setUserMenuOpen((o) => !o)}
          style={{
            display: 'flex', alignItems: 'center', gap: 'var(--space-2)',
            padding: '6px 10px', background: 'transparent',
            border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)',
            cursor: 'pointer', color: 'var(--color-text-primary)', transition: 'all var(--transition-fast)',
          }}
          onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--color-bg-elevated)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
          aria-haspopup="true"
          aria-expanded={userMenuOpen}
        >
          <div style={{
            width: '26px', height: '26px', borderRadius: '50%',
            background: 'linear-gradient(135deg, var(--color-blue-500), var(--color-cyan-400))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.7rem', fontWeight: '700', color: '#fff', flexShrink: 0,
          }}>
            {initials}
          </div>
          <span style={{ fontSize: 'var(--text-sm)', maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {user?.name || 'User'}
          </span>
          <ChevronDown size={14} style={{ color: 'var(--color-text-muted)', flexShrink: 0 }} />
        </button>

        {userMenuOpen && (
          <div
            style={{
              position: 'absolute', top: 'calc(100% + 8px)', right: 0,
              minWidth: '200px',
              background: 'var(--color-bg-elevated)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-lg)',
              zIndex: 'var(--z-dropdown)',
              padding: 'var(--space-2)',
              animation: 'fadeIn 0.15s ease',
            }}
          >
            <div style={{ padding: 'var(--space-3) var(--space-3)', borderBottom: '1px solid var(--color-border)', marginBottom: 'var(--space-2)' }}>
              <div style={{ fontSize: 'var(--text-sm)', fontWeight: '600', color: 'var(--color-text-primary)' }}>{user?.name}</div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>{user?.email}</div>
              <div style={{ fontSize: '0.65rem', color: 'var(--color-blue-300)', marginTop: '2px', textTransform: 'uppercase', fontWeight: '600' }}>{user?.role}</div>
            </div>

            <MenuButton icon={<User size={14} />} label="Profile" onClick={() => setUserMenuOpen(false)} to="/settings" />
            <div style={{ height: '1px', background: 'var(--color-border)', margin: 'var(--space-2) 0' }} />
            <MenuButton
              icon={<LogOut size={14} />}
              label="Sign out"
              onClick={() => { setUserMenuOpen(false); logout(); }}
              danger
            />
          </div>
        )}

        {userMenuOpen && (
          <div style={{ position: 'fixed', inset: 0, zIndex: 'calc(var(--z-dropdown) - 1)' }} onClick={() => setUserMenuOpen(false)} />
        )}
      </div>
    </header>
  );
}

function MenuButton({ icon, label, onClick, to, danger }: { icon: React.ReactNode; label: string; onClick: () => void; to?: string; danger?: boolean }) {
  return (
    <button
      onClick={onClick}
      style={{
        width: '100%', display: 'flex', alignItems: 'center', gap: 'var(--space-2)',
        padding: '8px var(--space-3)', background: 'transparent', border: 'none',
        cursor: 'pointer', borderRadius: 'var(--radius-md)',
        color: danger ? 'var(--color-error)' : 'var(--color-text-secondary)',
        fontSize: 'var(--text-sm)', textAlign: 'left',
        transition: 'all var(--transition-fast)',
      }}
      onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--color-bg-hover)'; e.currentTarget.style.color = danger ? 'var(--color-red-300)' : 'var(--color-text-primary)'; }}
      onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = danger ? 'var(--color-error)' : 'var(--color-text-secondary)'; }}
    >
      {icon}
      {label}
    </button>
  );
}
