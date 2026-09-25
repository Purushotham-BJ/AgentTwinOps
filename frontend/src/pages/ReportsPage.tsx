import React, { useState } from 'react';
import { FileText, Download, Calendar, Server, Brain, FlaskConical, AlertTriangle } from 'lucide-react';
import { useInfrastructure } from '@/hooks/useInfrastructure';
import { useIncidents } from '@/hooks/useIncidents';
import { Card, CardHeader } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/common/Badge';
import { LoadingState } from '@/components/common/LoadingState';
import { formatDate, formatDateTime } from '@/utils/format';

type ReportType = 'infrastructure' | 'incidents' | 'prediction' | 'simulation';

const REPORT_CONFIGS = [
  { type: 'infrastructure' as ReportType, title: 'Infrastructure Report', description: 'Service inventory, health status, uptime, and configuration overview', icon: Server, color: 'var(--color-blue-400)', bg: 'rgba(56,139,253,0.1)' },
  { type: 'incidents' as ReportType, title: 'Incident Report', description: 'Incident history, severity distribution, resolution times, and trends', icon: AlertTriangle, color: 'var(--color-orange-300)', bg: 'rgba(255,166,87,0.1)' },
  { type: 'prediction' as ReportType, title: 'Prediction Report', description: 'AI prediction accuracy, risk trends, and failure forecasts', icon: Brain, color: 'var(--color-purple-400)', bg: 'rgba(188,140,255,0.1)' },
  { type: 'simulation' as ReportType, title: 'Simulation Report', description: 'Scenario results, impact analysis, and mitigation recommendations', icon: FlaskConical, color: 'var(--color-cyan-400)', bg: 'rgba(57,213,255,0.1)' },
];

export function ReportsPage() {
  const { items: infra, isLoading: infraLoading } = useInfrastructure();
  const { items: incidents, isLoading: incLoading } = useIncidents();

  if (infraLoading || incLoading) return <LoadingState message="Loading report data..." />;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
        <Badge variant="muted">Report export API is not available</Badge>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '6px', fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
          <Calendar size={12} />Report date: {formatDate(new Date().toISOString())}
        </div>
      </div>

      {/* Report cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)' }}>
        {REPORT_CONFIGS.map(({ type, title, description, icon: Icon, color, bg }) => (
          <Card key={type} hover>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
              <div style={{ width: '44px', height: '44px', flexShrink: 0, background: bg, borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon size={22} style={{ color }} />
              </div>
              <div>
                <h3 style={{ fontSize: 'var(--text-base)', fontWeight: '600', color: 'var(--color-text-primary)', margin: '0 0 4px' }}>{title}</h3>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', margin: 0 }}>{description}</p>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
              <Button variant="secondary" size="sm" disabled leftIcon={<Download size={13} />} style={{ flex: 1 }}>Export unavailable</Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Infrastructure summary table */}
      <Card>
        <CardHeader title="Infrastructure Summary" subtitle={`${infra.length} services · Generated ${formatDateTime(new Date().toISOString())}`} icon={<Server size={16} />} />
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--text-sm)' }}>
            <thead>
              <tr>
                {['Service Name', 'Type', 'Host', 'Status', 'Last Updated'].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: 'var(--space-2) var(--space-3)', fontSize: 'var(--text-xs)', fontWeight: '600', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--color-border)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {infra.map((s) => (
                <tr key={s.id} style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
                  <td style={{ padding: 'var(--space-2) var(--space-3)', color: 'var(--color-text-primary)', fontWeight: '500' }}>{s.service_name}</td>
                  <td style={{ padding: 'var(--space-2) var(--space-3)', color: 'var(--color-text-muted)' }}>{s.service_type}</td>
                  <td style={{ padding: 'var(--space-2) var(--space-3)', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>{s.host}</td>
                  <td style={{ padding: 'var(--space-2) var(--space-3)' }}>
                    <Badge variant={s.status === 'healthy' || s.status === 'active' ? 'success' : s.status === 'degraded' ? 'warning' : 'error'}>{s.status}</Badge>
                  </td>
                  <td style={{ padding: 'var(--space-2) var(--space-3)', color: 'var(--color-text-muted)', fontSize: 'var(--text-xs)' }}>{formatDate(s.updated_at)}</td>
                </tr>
              ))}
              {infra.length === 0 && (
                <tr><td colSpan={5} style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--color-text-muted)' }}>No infrastructure data</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Incident summary */}
      <Card>
        <CardHeader title="Incident Summary" subtitle={`${incidents.length} total incidents`} icon={<AlertTriangle size={16} />} />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 'var(--space-3)' }}>
          {[
            { label: 'Critical', value: incidents.filter(i => i.severity === 'critical').length, color: 'var(--color-red-400)' },
            { label: 'High', value: incidents.filter(i => i.severity === 'high').length, color: 'var(--color-orange-300)' },
            { label: 'Medium', value: incidents.filter(i => i.severity === 'medium').length, color: 'var(--color-yellow-300)' },
            { label: 'Low', value: incidents.filter(i => i.severity === 'low').length, color: 'var(--color-blue-300)' },
            { label: 'Open', value: incidents.filter(i => i.resolution_status === 'open').length, color: 'var(--color-red-400)' },
            { label: 'Resolved', value: incidents.filter(i => i.resolution_status === 'resolved' || i.resolution_status === 'closed').length, color: 'var(--color-green-400)' },
          ].map((s) => (
            <div key={s.label} style={{ background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', padding: 'var(--space-3)', textAlign: 'center' }}>
              <div style={{ fontSize: 'var(--text-xl)', fontWeight: '700', color: s.color }}>{s.value}</div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginTop: '4px' }}>{s.label}</div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
