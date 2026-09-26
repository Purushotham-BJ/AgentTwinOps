import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Server, AlertTriangle, Cpu, Brain, Bot,
  FlaskConical, Lightbulb, FileText, Settings,
  ChevronLeft, ChevronRight, Activity, Boxes,
} from 'lucide-react';

interface NavItem {
  path: string;
  label: string;
  icon: React.ElementType;
  badge?: number;
}

const NAV_ITEMS: NavItem[] = [
  { path: '/dashboard',        label: 'Dashboard',       icon: LayoutDashboard },
  { path: '/infrastructure',   label: 'Infrastructure',  icon: Server },
  { path: '/incidents',        label: 'Incidents',       icon: AlertTriangle },
  { path: '/digital-twin',     label: 'Digital Twin',    icon: Boxes },
  { path: '/prediction',       label: 'Prediction',      icon: Brain },
  { path: '/simulation',       label: 'Simulation',      icon: FlaskConical },
  { path: '/recommendations',  label: 'Recommendations', icon: Lightbulb },
  { path: '/operations',       label: 'Operations',      icon: Bot },
  { path: '/reports',          label: 'Reports',         icon: FileText },
  { path: '/settings',         label: 'Settings',        icon: Settings },
];

interface SidebarProps {
  mobileOpen?: boolean;
  onMobileClose?: () => void;
}

export function Sidebar({ mobileOpen, onMobileClose }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  const sidebarContent = (
    <aside
      style={{
        width: collapsed ? 'var(--sidebar-width-collapsed)' : 'var(--sidebar-width)',
        minHeight: '100vh',
        background: 'var(--color-bg-surface)',
        borderRight: '1px solid var(--color-border)',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width var(--transition-slow)',
        flexShrink: 0,
        overflow: 'hidden',
      }}
    >
      {/* Logo */}
      <div style={{
        height: 'var(--topnav-height)',
        display: 'flex',
        alignItems: 'center',
        padding: '0 var(--space-4)',
        borderBottom: '1px solid var(--color-border)',
        gap: 'var(--space-3)',
        flexShrink: 0,
      }}>
        <div style={{
          width: '32px', height: '32px', flexShrink: 0,
          background: 'linear-gradient(135deg, var(--color-blue-500), var(--color-cyan-400))',
          borderRadius: 'var(--radius-md)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Activity size={18} color="#fff" />
        </div>
        {!collapsed && (
          <div style={{ overflow: 'hidden' }}>
            <div style={{ fontSize: 'var(--text-sm)', fontWeight: 'var(--font-bold)', color: 'var(--color-text-primary)', whiteSpace: 'nowrap' }}>
              AgentTwinOps
            </div>
            <div style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)', whiteSpace: 'nowrap' }}>
              Digital Twin Platform
            </div>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: 'var(--space-3) var(--space-2)', overflowY: 'auto', overflowX: 'hidden' }}>
        {!collapsed && (
          <div style={{ fontSize: '0.65rem', fontWeight: '600', color: 'var(--color-text-disabled)', textTransform: 'uppercase', letterSpacing: '0.08em', padding: '4px var(--space-2) var(--space-2)' }}>
            Navigation
          </div>
        )}
        {NAV_ITEMS.map(({ path, label, icon: Icon, badge }) => {
          const isActive = location.pathname === path || location.pathname.startsWith(path + '/');
          return (
            <NavLink
              key={path}
              to={path}
              onClick={onMobileClose}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-3)',
                padding: collapsed ? '10px 16px' : '9px var(--space-3)',
                borderRadius: 'var(--radius-md)',
                marginBottom: '2px',
                textDecoration: 'none',
                color: isActive ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
                background: isActive ? 'var(--color-bg-elevated)' : 'transparent',
                borderLeft: isActive ? '2px solid var(--color-primary)' : '2px solid transparent',
                transition: 'all var(--transition-fast)',
                overflow: 'hidden',
                whiteSpace: 'nowrap',
                justifyContent: collapsed ? 'center' : undefined,
              }}
              title={collapsed ? label : undefined}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.background = 'var(--color-bg-elevated)';
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.background = 'transparent';
              }}
            >
              <Icon size={18} style={{ flexShrink: 0, color: isActive ? 'var(--color-primary)' : 'inherit' }} />
              {!collapsed && (
                <>
                  <span style={{ fontSize: 'var(--text-sm)', flex: 1 }}>{label}</span>
                  {badge !== undefined && badge > 0 && (
                    <span style={{
                      fontSize: '0.65rem', fontWeight: '600',
                      background: 'var(--color-red-500)',
                      color: '#fff', borderRadius: 'var(--radius-full)',
                      padding: '1px 6px', flexShrink: 0,
                    }}>
                      {badge}
                    </span>
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Collapse toggle */}
      <div style={{ padding: 'var(--space-3) var(--space-2)', borderTop: '1px solid var(--color-border)' }}>
        <button
          onClick={() => setCollapsed((c) => !c)}
          style={{
            width: '100%', display: 'flex', alignItems: 'center', justifyContent: collapsed ? 'center' : 'flex-end',
            gap: 'var(--space-2)', padding: '8px var(--space-2)',
            background: 'transparent', border: 'none', cursor: 'pointer',
            color: 'var(--color-text-muted)', borderRadius: 'var(--radius-md)',
            transition: 'all var(--transition-fast)',
            fontSize: 'var(--text-xs)',
          }}
          onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--color-bg-elevated)'; e.currentTarget.style.color = 'var(--color-text-primary)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--color-text-muted)'; }}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight size={16} /> : <><ChevronLeft size={16} /><span>Collapse</span></>}
        </button>
      </div>
    </aside>
  );

  // Mobile overlay
  if (mobileOpen !== undefined) {
    return (
      <>
        {mobileOpen && (
          <div
            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', zIndex: 'var(--z-sidebar)', backdropFilter: 'blur(2px)' }}
            onClick={onMobileClose}
          />
        )}
        <div
          style={{
            position: 'fixed', top: 0, left: 0, bottom: 0,
            transform: mobileOpen ? 'translateX(0)' : 'translateX(-100%)',
            transition: 'transform var(--transition-slow)',
            zIndex: 'calc(var(--z-sidebar) + 1)',
          }}
        >
          {sidebarContent}
        </div>
      </>
    );
  }

  return sidebarContent;
}
