import { useEffect, useMemo, useState } from 'react';
import { Bell, Check, Loader2 } from 'lucide-react';
import { incidentService } from '@/services/incidentService';
import type { IncidentItem } from '@/types';
import { getErrorMessage } from '@/services/api';

const READ_KEY = 'agenttwinops:read-notifications';

function readIds(userId: string | undefined): Set<string> {
  if (!userId) return new Set();
  try {
    const stored = JSON.parse(localStorage.getItem(`${READ_KEY}:${userId}`) || '[]');
    return new Set(Array.isArray(stored) ? stored.filter((id): id is string => typeof id === 'string') : []);
  } catch {
    return new Set();
  }
}

export function NotificationBell({ userId }: { userId?: string }) {
  const [open, setOpen] = useState(false);
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [read, setRead] = useState<Set<string>>(() => readIds(userId));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadNotifications = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await incidentService.list(0, 50);
      setIncidents(response.items.filter((incident) => incident.resolution_status !== 'closed' && incident.resolution_status !== 'resolved'));
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setRead(readIds(userId));
    if (userId) void loadNotifications();
  }, [userId]);

  const unread = useMemo(() => incidents.filter((incident) => !read.has(incident.id)), [incidents, read]);

  const persistRead = (next: Set<string>) => {
    setRead(next);
    if (userId) localStorage.setItem(`${READ_KEY}:${userId}`, JSON.stringify([...next]));
  };

  const markAllRead = () => persistRead(new Set(incidents.map((incident) => incident.id)));

  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={() => { setOpen((value) => !value); if (!open) void loadNotifications(); }}
        style={{
          position: 'relative', padding: '6px', background: 'transparent', border: 'none',
          cursor: 'pointer', color: 'var(--color-text-secondary)', borderRadius: 'var(--radius-md)',
          display: 'flex', alignItems: 'center',
        }}
        aria-label={`Notifications${unread.length ? `, ${unread.length} unread` : ''}`}
        aria-expanded={open}
      >
        <Bell size={18} />
        {unread.length > 0 && (
          <span style={{
            position: 'absolute', top: '0px', right: '0px', minWidth: '16px', height: '16px',
            padding: '0 3px', borderRadius: 'var(--radius-full)', background: 'var(--color-red-400)',
            border: '2px solid var(--color-bg-surface)', color: '#fff', fontSize: '9px',
            lineHeight: '12px', textAlign: 'center', fontWeight: 700,
          }}>
            {unread.length > 9 ? '9+' : unread.length}
          </span>
        )}
      </button>

      {open && (
        <>
          <div style={{ position: 'fixed', inset: 0, zIndex: 'calc(var(--z-dropdown) - 1)' }} onClick={() => setOpen(false)} />
          <section
            aria-label="Notifications panel"
            style={{
              position: 'absolute', top: 'calc(100% + 8px)', right: 0, width: '340px',
              maxWidth: 'calc(100vw - 32px)', background: 'var(--color-bg-elevated)',
              border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-lg)', zIndex: 'var(--z-dropdown)', overflow: 'hidden',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', borderBottom: '1px solid var(--color-border)' }}>
              <strong style={{ fontSize: 'var(--text-sm)' }}>Notifications</strong>
              <button onClick={markAllRead} disabled={!unread.length} style={{ border: 0, background: 'transparent', color: unread.length ? 'var(--color-blue-300)' : 'var(--color-text-muted)', cursor: unread.length ? 'pointer' : 'default', fontSize: 'var(--text-xs)' }}>
                Mark all read
              </button>
            </div>
            <div style={{ maxHeight: '360px', overflowY: 'auto' }}>
              {loading && <div style={{ padding: '24px', textAlign: 'center', color: 'var(--color-text-muted)' }}><Loader2 size={18} className="spin" /></div>}
              {!loading && error && <div style={{ padding: '18px', color: 'var(--color-red-300)', fontSize: 'var(--text-xs)' }}>{error}</div>}
              {!loading && !error && !incidents.length && <div style={{ padding: '24px', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: 'var(--text-sm)' }}>No active notifications</div>}
              {!loading && !error && incidents.map((incident) => (
                <button
                  key={incident.id}
                  onClick={() => persistRead(new Set([...read, incident.id]))}
                  style={{ width: '100%', display: 'flex', gap: '10px', textAlign: 'left', padding: '12px 14px', border: 0, borderBottom: '1px solid var(--color-border)', background: read.has(incident.id) ? 'transparent' : 'rgba(31,111,235,0.08)', color: 'var(--color-text-primary)', cursor: 'pointer' }}
                >
                  <span style={{ color: incident.severity === 'critical' || incident.severity === 'high' ? 'var(--color-red-400)' : 'var(--color-yellow-400)', paddingTop: '2px' }}>
                    {read.has(incident.id) ? <Check size={14} /> : <Bell size={14} />}
                  </span>
                  <span style={{ display: 'flex', flexDirection: 'column', gap: '3px', minWidth: 0 }}>
                    <span style={{ fontSize: 'var(--text-xs)', fontWeight: read.has(incident.id) ? 400 : 600 }}>{incident.incident_type}</span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>{incident.severity.toUpperCase()} · {incident.resolution_status.replace('_', ' ')}</span>
                  </span>
                </button>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
