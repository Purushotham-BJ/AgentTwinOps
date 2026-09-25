import React from 'react';
import { Boxes, RefreshCw, Activity, TrendingUp, Clock, AlertCircle } from 'lucide-react';
import { useDigitalTwin } from '@/hooks/useDigitalTwin';
import { Card, CardHeader } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { Button } from '@/components/common/Button';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState, EmptyState } from '@/components/common/ErrorState';
import { ProgressBar } from '@/components/common/ProgressBar';
import { formatRelativeTime, formatMs, formatPercent } from '@/utils/format';
import { getSyncColor, getHealthColor } from '@/utils/statusHelpers';
import type { TwinObject } from '@/types';

function SyncBadge({ status }: { status: TwinObject['sync_status'] }) {
  const variant = status === 'synced' ? 'success' : status === 'syncing' ? 'default' : status === 'error' ? 'error' : 'warning';
  return <Badge variant={variant} dot>{status.replace('_', ' ')}</Badge>;
}

function StatRow({ label, current, predicted, unit = '%' }: { label: string; current: number; predicted: number; unit?: string }) {
  const delta = predicted - current;
  const deltaColor = delta > 5 ? 'var(--color-red-400)' : delta > 0 ? 'var(--color-orange-300)' : 'var(--color-green-400)';
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', padding: 'var(--space-3) 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', fontWeight: '500' }}>{label}</span>
        <div style={{ display: 'flex', gap: 'var(--space-3)', fontSize: 'var(--text-xs)' }}>
          <span style={{ color: 'var(--color-text-secondary)' }}>Now: <strong style={{ color: 'var(--color-text-primary)' }}>{unit === 'ms' ? formatMs(current) : formatPercent(current)}</strong></span>
          <span style={{ color: deltaColor }}>+{delta > 0 ? formatPercent(Math.abs(delta)) : '—'} predicted</span>
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px' }}>
        <ProgressBar value={unit === 'ms' ? Math.min(100, current / 5) : current} color="var(--color-blue-400)" height={5} label="Current" showLabel />
        <ProgressBar value={unit === 'ms' ? Math.min(100, predicted / 5) : predicted} height={5} label="Predicted" showLabel />
      </div>
    </div>
  );
}

export function DigitalTwinPage() {
  const { twins, isLoading, error, lastSynced, refetch } = useDigitalTwin();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)' }}>
            Real-time digital mirrors of your infrastructure — current state vs predicted state
          </p>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center', flexWrap: 'wrap' }}>
          {lastSynced && (
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Clock size={12} />Synced {formatRelativeTime(lastSynced.toISOString())}
            </span>
          )}
          <Button variant="ghost" size="sm" onClick={refetch} leftIcon={<RefreshCw size={14} />}>Sync Twins</Button>
        </div>
      </div>

      {/* Architecture diagram */}
      <Card padding="sm">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--space-3)', flexWrap: 'wrap', padding: 'var(--space-3)' }}>
          {[
            { label: 'Real Infrastructure', icon: <Activity size={16} />, color: 'var(--color-blue-400)' },
            { label: '→', color: 'var(--color-text-muted)', isArrow: true },
            { label: 'Metrics Collector', icon: <TrendingUp size={16} />, color: 'var(--color-cyan-400)' },
            { label: '→', color: 'var(--color-text-muted)', isArrow: true },
            { label: 'Digital Twin', icon: <Boxes size={16} />, color: 'var(--color-purple-400)' },
            { label: '→', color: 'var(--color-text-muted)', isArrow: true },
            { label: 'Predicted State', icon: <AlertCircle size={16} />, color: 'var(--color-orange-300)' },
          ].map((step, i) =>
            step.isArrow ? (
              <span key={i} style={{ color: step.color, fontSize: 'var(--text-xl)' }}>{step.label}</span>
            ) : (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 14px', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', fontSize: 'var(--text-xs)', fontWeight: '500', color: step.color }}>
                {step.icon}{step.label}
              </div>
            )
          )}
        </div>
      </Card>

      {isLoading ? (
        <LoadingState message="Synchronizing digital twins..." />
      ) : error ? (
        <ErrorState message={error} onRetry={refetch} />
      ) : twins.length === 0 ? (
        <EmptyState title="No digital twins available" description="Add infrastructure services to automatically generate their digital twins." icon={<Boxes size={48} />} />
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: 'var(--space-4)' }}>
          {twins.map((twin) => <TwinCard key={twin.id} twin={twin} />)}
        </div>
      )}
    </div>
  );
}

function TwinCard({ twin }: { twin: TwinObject }) {
  const healthColor = getHealthColor(twin.health_score);
  const predicted = twin.predicted_state;
  const predictedValue = (metric: 'cpu_usage' | 'memory_usage') => {
    const direct = predicted[metric];
    if (typeof direct === 'number') return direct;
    return predicted.prediction_type === (metric === 'cpu_usage' ? 'cpu' : 'memory')
      ? predicted.predicted_value ?? twin.current_state[metric]
      : twin.current_state[metric];
  };

  return (
    <Card>
      {/* Twin header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 'var(--space-4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: 'var(--radius-md)', background: 'rgba(188,140,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Boxes size={20} style={{ color: 'var(--color-purple-400)' }} />
          </div>
          <div>
            <div style={{ fontSize: 'var(--text-sm)', fontWeight: '600', color: 'var(--color-text-primary)' }}>{twin.name}</div>
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>{twin.service_type}</div>
          </div>
        </div>
        <SyncBadge status={twin.sync_status} />
      </div>

      {/* Health score */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-4)', padding: 'var(--space-3)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)' }}>
        <div>
          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: '2px' }}>Health Score</div>
          <div style={{ fontSize: 'var(--text-2xl)', fontWeight: '700', color: healthColor }}>{twin.health_score}</div>
        </div>
        <div style={{ width: '64px', height: '64px', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <svg width="64" height="64" style={{ transform: 'rotate(-90deg)' }}>
            <circle cx="32" cy="32" r="26" fill="none" stroke="var(--color-bg-overlay)" strokeWidth="6" />
            <circle cx="32" cy="32" r="26" fill="none" stroke={healthColor} strokeWidth="6"
              strokeDasharray={`${(twin.health_score / 100) * 163} 163`} strokeLinecap="round" />
          </svg>
          <span style={{ position: 'absolute', fontSize: '0.65rem', fontWeight: '600', color: healthColor }}>{twin.health_score}</span>
        </div>
      </div>

      {/* State comparison */}
      <div>
        <StatRow label="CPU Usage" current={twin.current_state.cpu_usage} predicted={predictedValue('cpu_usage')} />
        <StatRow label="Memory Usage" current={twin.current_state.memory_usage} predicted={predictedValue('memory_usage')} />
        <StatRow label="Latency" current={twin.current_state.latency_ms} predicted={twin.predicted_state.latency_ms ?? twin.current_state.latency_ms} unit="ms" />
        <StatRow label="Error Rate" current={twin.current_state.error_rate} predicted={twin.predicted_state.error_rate ?? twin.current_state.error_rate} />
      </div>

      {predicted.prediction_source && (
        <div style={{ marginTop: 'var(--space-3)', padding: 'var(--space-3)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
          Predicted state from <strong style={{ color: 'var(--color-text-secondary)' }}>{predicted.prediction_source}</strong>
          {predicted.prediction_timestamp && <> · {formatRelativeTime(predicted.prediction_timestamp)}</>}
          {predicted.horizon_minutes && <> · horizon {predicted.horizon_minutes}m</>}
          {predicted.model_metrics && Object.keys(predicted.model_metrics).length > 0 && (
            <div style={{ marginTop: '6px' }}>
              Metrics: {Object.entries(predicted.model_metrics).map(([key, value]) => `${key}=${value}`).join(' · ')}
            </div>
          )}
        </div>
      )}

      {/* Last synced */}
      <div style={{ marginTop: 'var(--space-3)', display: 'flex', alignItems: 'center', gap: '4px', fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
        <Clock size={11} />
        Last synced {formatRelativeTime(twin.last_synced)}
      </div>
    </Card>
  );
}
