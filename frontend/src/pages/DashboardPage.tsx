import React, { useMemo } from 'react';
import {
  Server, AlertTriangle, Cpu, MemoryStick, ShieldAlert, Lightbulb,
  Activity, CheckCircle, RefreshCw, Clock,
} from 'lucide-react';
import { useInfrastructure } from '@/hooks/useInfrastructure';
import { useIncidents } from '@/hooks/useIncidents';
import { useMetrics } from '@/hooks/useMetrics';
import { metricsService } from '@/services/metricsService';
import { StatCard } from '@/components/common/StatCard';
import { Card, CardHeader } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { MetricChart } from '@/components/common/MetricChart';
import { ProgressBar } from '@/components/common/ProgressBar';
import { formatRelativeTime, formatPercent, formatRiskScore } from '@/utils/format';
import { getSeverityColor, getSeverityBg, getResolutionColor, getResolutionBg } from '@/utils/statusHelpers';
import type { InfrastructureStatus } from '@/types';

function getStatusBadgeVariant(status: InfrastructureStatus) {
  switch (status) {
    case 'healthy': return 'success';
    case 'active': return 'default';
    case 'degraded': return 'warning';
    case 'unhealthy': return 'error';
    case 'inactive': return 'muted';
    default: return 'muted';
  }
}

export function DashboardPage() {
  const infra = useInfrastructure();
  const incidents = useIncidents();
  const { metrics, isLoading: metricsLoading, error: metricsError, lastUpdated, refetch: refetchMetrics } = useMetrics();

  const summary = useMemo(() => {
    if (infra.isLoading || incidents.isLoading) return null;
    const statusCounts = infra.items.reduce<Record<string, number>>((acc, item) => {
      acc[item.status] = (acc[item.status] ?? 0) + 1;
      return acc;
    }, {});
    const openIncidents = incidents.items.filter((i) => i.resolution_status === 'open' || i.resolution_status === 'in_progress').length;
    const criticalIncidents = incidents.items.filter((i) => i.severity === 'critical').length;
    return metricsService.computeDashboardSummary(infra.total, statusCounts, openIncidents, criticalIncidents);
  }, [infra.items, infra.total, infra.isLoading, incidents.items, incidents.isLoading]);

  const recentIncidents = incidents.items.slice(0, 6);
  const criticalServices = infra.items.filter((s) => s.status === 'unhealthy' || s.status === 'degraded').slice(0, 5);

  const isLoading = infra.isLoading || incidents.isLoading;
  const hasError = infra.error || incidents.error || metricsError;

  if (hasError) {
    return <ErrorState message={infra.error || incidents.error || metricsError || 'Failed to load dashboard'} onRetry={() => { infra.refetch(); incidents.refetch(); refetchMetrics(); }} />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>

      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <p style={{ color: 'var(--color-text-muted)', fontSize: 'var(--text-sm)', marginTop: '4px' }}>
            Real-time infrastructure health, AI predictions, and system status
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          {lastUpdated && (
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Clock size={12} />
              {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={() => { infra.refetch(); incidents.refetch(); refetchMetrics(); }}
            style={{ padding: '6px', background: 'transparent', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', cursor: 'pointer', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center' }}
            title="Refresh all data"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* Stat cards */}
      {isLoading ? (
        <LoadingState message="Loading dashboard..." />
      ) : (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 'var(--space-4)' }}>
            <StatCard
              title="Infrastructure Health"
              value={`${summary?.infrastructure_health ?? 0}%`}
              subtitle={`${summary?.healthy_services ?? 0}/${summary?.total_services ?? 0} services healthy`}
              icon={Activity}
              iconColor="var(--color-green-400)"
              iconBg="rgba(63,185,80,0.1)"
            />
            <StatCard
              title="Total Services"
              value={summary?.total_services ?? 0}
              subtitle={`${summary?.degraded_services ?? 0} degraded · ${summary?.unhealthy_services ?? 0} unhealthy`}
              icon={Server}
              iconColor="var(--color-blue-400)"
              iconBg="rgba(56,139,253,0.1)"
            />
            <StatCard
              title="Open Incidents"
              value={summary?.open_incidents ?? 0}
              subtitle={`${summary?.critical_incidents ?? 0} critical`}
              icon={AlertTriangle}
              iconColor="var(--color-orange-300)"
              iconBg="rgba(255,166,87,0.1)"
              alert={(summary?.critical_incidents ?? 0) > 0}
            />
            <StatCard
              title="CPU Usage"
              value={metrics ? `${metrics.cpu[metrics.cpu.length - 1]?.value.toFixed(1) ?? '--'}%` : '--'}
              subtitle="Average across services"
              icon={Cpu}
              iconColor="var(--color-cyan-400)"
              iconBg="rgba(0,180,216,0.1)"
            />
            <StatCard
              title="Memory Usage"
              value={metrics ? `${metrics.memory[metrics.memory.length - 1]?.value.toFixed(1) ?? '--'}%` : '--'}
              subtitle="Average across services"
              icon={MemoryStick}
              iconColor="var(--color-purple-400)"
              iconBg="rgba(188,140,255,0.1)"
            />
            <StatCard
              title="Failure Risk"
              value={summary ? `${summary.failure_risk}%` : '--'}
              subtitle={formatRiskScore(summary?.failure_risk ?? 0).label}
              icon={ShieldAlert}
              iconColor={getRiskIconColor(summary?.failure_risk ?? 0)}
              iconBg={getRiskIconBg(summary?.failure_risk ?? 0)}
              alert={(summary?.failure_risk ?? 0) >= 50}
            />
            <StatCard
              title="Recommendations"
              value={summary ? summary.active_recommendations : '--'}
              subtitle="AI-generated actions"
              icon={Lightbulb}
              iconColor="var(--color-yellow-300)"
              iconBg="rgba(240,192,64,0.1)"
            />
            <StatCard
              title="System Status"
              value={summary ? (summary.unhealthy_services === 0 ? 'Healthy' : 'Degraded') : '--'}
              subtitle={summary ? 'Overall platform state' : 'Unavailable'}
              icon={CheckCircle}
              iconColor={summary && summary.unhealthy_services === 0 ? 'var(--color-green-400)' : 'var(--color-orange-300)'}
              iconBg={summary && summary.unhealthy_services === 0 ? 'rgba(63,185,80,0.1)' : 'rgba(255,166,87,0.1)'}
            />
          </div>

          {/* Charts row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-4)' }}>
            <Card>
              <CardHeader title="CPU Usage" subtitle="24-hour trend" icon={<Cpu size={16} />} />
              {metricsLoading ? <LoadingState size="sm" /> : metrics ? (
                <MetricChart data={metrics.cpu} color="var(--color-cyan-400)" height={160} />
              ) : null}
            </Card>

            <Card>
              <CardHeader title="Memory Usage" subtitle="24-hour trend" icon={<MemoryStick size={16} />} />
              {metricsLoading ? <LoadingState size="sm" /> : metrics ? (
                <MetricChart data={metrics.memory} color="var(--color-purple-400)" height={160} />
              ) : null}
            </Card>

            <Card>
              <CardHeader title="Latency" subtitle="Average response time" />
              {metricsLoading ? <LoadingState size="sm" /> : metrics ? (
                <MetricChart data={metrics.latency} color="var(--color-orange-300)" unit="ms" height={160} />
              ) : null}
            </Card>

            <Card>
              <CardHeader title="Network" subtitle="Traffic volume" />
              {metricsLoading ? <LoadingState size="sm" /> : metrics ? (
                <MetricChart data={metrics.network} color="var(--color-blue-300)" type="line" height={160} />
              ) : null}
            </Card>
          </div>

          {/* Bottom row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 'var(--space-4)' }}>
            {/* Recent incidents */}
            <Card>
              <CardHeader title="Recent Incidents" subtitle={`${incidents.total} total`} icon={<AlertTriangle size={16} />} />
              {recentIncidents.length === 0 ? (
                <div style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--color-text-muted)', fontSize: 'var(--text-sm)' }}>
                  <CheckCircle size={28} style={{ margin: '0 auto var(--space-2)', display: 'block', opacity: 0.3 }} />
                  No incidents recorded
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                  {recentIncidents.map((inc) => (
                    <div key={inc.id} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', padding: 'var(--space-2) 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-primary)', fontWeight: '500', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {inc.incident_type}
                        </div>
                        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                          {formatRelativeTime(inc.timestamp)}
                        </div>
                      </div>
                      <Badge
                        variant={inc.severity === 'critical' ? 'error' : inc.severity === 'high' ? 'warning' : inc.severity === 'medium' ? 'info' : 'muted'}
                        dot
                      >
                        {inc.severity}
                      </Badge>
                      <Badge variant={inc.resolution_status === 'open' ? 'error' : inc.resolution_status === 'in_progress' ? 'warning' : 'success'}>
                        {inc.resolution_status.replace('_', ' ')}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            {/* Infrastructure health */}
            <Card>
              <CardHeader title="Infrastructure Health" subtitle={`${infra.total} services monitored`} icon={<Server size={16} />} />
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                {infra.items.slice(0, 6).map((svc) => (
                  <div key={svc.id} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {svc.service_name}
                      </div>
                      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>{svc.service_type} · {svc.host}</div>
                    </div>
                    <Badge variant={getStatusBadgeVariant(svc.status)} dot>
                      {svc.status}
                    </Badge>
                  </div>
                ))}
                {infra.items.length === 0 && (
                  <div style={{ textAlign: 'center', color: 'var(--color-text-muted)', fontSize: 'var(--text-sm)', padding: 'var(--space-6)' }}>
                    No services configured
                  </div>
                )}
              </div>
            </Card>

            {/* AI Failure Risk */}
            <Card style={{ background: 'var(--color-bg-surface)' }}>
              <CardHeader title="AI Failure Risk" subtitle="Simulated · pending /api/predict/failure" icon={<ShieldAlert size={16} />} />
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                <div style={{ textAlign: 'center', padding: 'var(--space-4)' }}>
                  <div style={{
                    fontSize: '3rem', fontWeight: '800',
                    color: getRiskIconColor(summary?.failure_risk ?? 0),
                    lineHeight: 1,
                  }}>
                    {formatRiskScore(summary?.failure_risk ?? 0).label.toUpperCase()}
                  </div>
                  <div style={{ fontSize: 'var(--text-2xl)', fontWeight: '600', color: 'var(--color-text-primary)', marginTop: '8px' }}>
                    {summary?.failure_risk ?? 0}%
                  </div>
                  <ProgressBar value={summary?.failure_risk ?? 0} height={8} animated style={{ marginTop: 'var(--space-3)' }} />
                </div>
                <div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 'var(--space-2)' }}>
                    Contributing Factors
                  </div>
                  {criticalServices.length > 0 ? criticalServices.map((s) => (
                    <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', padding: '4px 0', fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>
                      <span style={{ color: 'var(--color-error)' }}>•</span>
                      {s.service_name} ({s.status})
                    </div>
                  )) : (
                    <div style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)' }}>
                      {(summary?.critical_incidents ?? 0) > 0
                        ? `${summary?.critical_incidents} critical incidents outstanding`
                        : 'No critical risk factors detected'}
                    </div>
                  )}
                </div>
              </div>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}

function getRiskIconColor(risk: number): string {
  if (risk >= 75) return 'var(--color-red-400)';
  if (risk >= 50) return 'var(--color-orange-300)';
  if (risk >= 25) return 'var(--color-yellow-300)';
  return 'var(--color-green-400)';
}

function getRiskIconBg(risk: number): string {
  if (risk >= 75) return 'rgba(248,81,73,0.1)';
  if (risk >= 50) return 'rgba(255,166,87,0.1)';
  if (risk >= 25) return 'rgba(240,192,64,0.1)';
  return 'rgba(63,185,80,0.1)';
}
