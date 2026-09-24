import React, { useState } from 'react';
import { Brain, Play, AlertTriangle, TrendingUp, Clock } from 'lucide-react';
import { usePredictions } from '@/hooks/usePredictions';
import { useInfrastructure } from '@/hooks/useInfrastructure';
import { Card, CardHeader } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/common/Badge';
import { Select } from '@/components/common/Input';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState } from '@/components/common/ErrorState';
import { MetricChart } from '@/components/common/MetricChart';
import { MockDataBanner } from '@/components/common/MockDataBanner';
import { ProgressBar } from '@/components/common/ProgressBar';
import { formatRelativeTime, formatPercent, formatConfidence } from '@/utils/format';
import { getRiskColor } from '@/utils/statusHelpers';
import type { PredictionResult } from '@/types';

const PRED_TYPES = [
  { value: 'cpu', label: 'CPU Usage Forecast' },
  { value: 'memory', label: 'Memory Usage Forecast' },
  { value: 'failure', label: 'Failure Risk Prediction' },
];

export function PredictionPage() {
  const { items: infraItems } = useInfrastructure();
  const { results, isLoading, error, predictCpu, predictMemory, predictFailure } = usePredictions();
  const [serviceId, setServiceId] = useState('');
  const [predType, setPredType] = useState<'cpu' | 'memory' | 'failure'>('failure');
  const [selected, setSelected] = useState<PredictionResult | null>(null);

  const handleRun = async () => {
    const id = serviceId || infraItems[0]?.id;
    if (!id) return;
    const req = { service_id: id };
    let result: PredictionResult;
    if (predType === 'cpu') result = await predictCpu(req);
    else if (predType === 'memory') result = await predictMemory(req);
    else result = await predictFailure(req);
    setSelected(result);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
        <MockDataBanner feature="AI predictions" apiEndpoint="POST /api/predict/{cpu|memory|failure}" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 380px) 1fr', gap: 'var(--space-5)', alignItems: 'start' }}>
        {/* Config panel */}
        <Card>
          <CardHeader title="Run Prediction" icon={<Brain size={16} />} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <Select
              label="Service"
              options={infraItems.length > 0 ? infraItems.map(i => ({ value: i.id, label: i.service_name })) : [{ value: '', label: 'No services yet' }]}
              value={serviceId || infraItems[0]?.id || ''}
              onChange={(e) => setServiceId(e.target.value)}
            />
            <Select
              label="Prediction Type"
              options={PRED_TYPES}
              value={predType}
              onChange={(e) => setPredType(e.target.value as typeof predType)}
            />
            <div style={{ padding: 'var(--space-3)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
              Horizon: <strong style={{ color: 'var(--color-text-secondary)' }}>6 hours</strong> · Model: <strong style={{ color: 'var(--color-text-secondary)' }}>XGBoost + Prophet</strong>
            </div>
            <Button
              variant="primary"
              size="md"
              onClick={handleRun}
              isLoading={isLoading}
              leftIcon={<Play size={14} />}
              disabled={infraItems.length === 0}
              style={{ width: '100%' }}
            >
              {isLoading ? 'Predicting...' : 'Run Prediction'}
            </Button>
          </div>

          {/* Previous results list */}
          {results.length > 0 && (
            <div style={{ marginTop: 'var(--space-5)' }}>
              <div style={{ fontSize: 'var(--text-xs)', fontWeight: '600', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 'var(--space-2)' }}>History</div>
              {results.slice(0, 5).map((r) => (
                <button
                  key={r.id}
                  onClick={() => setSelected(r)}
                  style={{
                    width: '100%', display: 'flex', alignItems: 'center', gap: 'var(--space-2)',
                    padding: '8px var(--space-2)', background: selected?.id === r.id ? 'var(--color-bg-elevated)' : 'transparent',
                    border: 'none', borderRadius: 'var(--radius-md)', cursor: 'pointer',
                    color: 'var(--color-text-secondary)', fontSize: 'var(--text-xs)',
                    transition: 'background var(--transition-fast)',
                    textAlign: 'left',
                  }}
                >
                  <Brain size={12} style={{ flexShrink: 0, color: getRiskColor(r.risk_level) }} />
                  <span style={{ flex: 1 }}>{r.prediction_type.toUpperCase()} · {r.risk_level}</span>
                  <Clock size={11} />
                  <span>{formatRelativeTime(r.created_at)}</span>
                </button>
              ))}
            </div>
          )}
        </Card>

        {/* Results */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {isLoading && <LoadingState message="Running AI prediction..." />}

          {!isLoading && !selected && (
            <EmptyState
              title="No prediction results yet"
              description="Select a service and prediction type, then click Run Prediction."
              icon={<Brain size={48} />}
            />
          )}

          {selected && !isLoading && (
            <>
              {/* Risk card */}
              <Card style={{ border: `1px solid ${getRiskColor(selected.risk_level)}40` }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 'var(--space-4)', padding: 'var(--space-2)' }}>
                  <div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: '4px' }}>RISK LEVEL</div>
                    <div style={{ fontSize: 'var(--text-2xl)', fontWeight: '800', color: getRiskColor(selected.risk_level) }}>{selected.risk_level.toUpperCase()}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: '4px' }}>FAILURE PROBABILITY</div>
                    <div style={{ fontSize: 'var(--text-2xl)', fontWeight: '700', color: getRiskColor(selected.risk_level) }}>{formatPercent(selected.failure_probability * 100)}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: '4px' }}>CONFIDENCE</div>
                    <div style={{ fontSize: 'var(--text-2xl)', fontWeight: '700', color: 'var(--color-text-primary)' }}>{formatConfidence(selected.confidence)}</div>
                  </div>
                </div>
                <div style={{ marginTop: 'var(--space-3)' }}>
                  <ProgressBar value={selected.failure_probability * 100} height={8} animated />
                </div>
              </Card>

              {/* Chart */}
              <Card>
                <CardHeader title={`${selected.prediction_type.toUpperCase()} Forecast`} subtitle={`Next ${selected.horizon_minutes / 60}h prediction`} icon={<TrendingUp size={16} />} />
                <MetricChart data={selected.data_points} color={getRiskColor(selected.risk_level)} height={200} type="area" />
              </Card>

              {/* Factors + Action */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                <Card>
                  <CardHeader title="Contributing Factors" icon={<AlertTriangle size={16} />} />
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                    {selected.factors.map((f, i) => (
                      <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-2)', padding: '6px 0', borderBottom: '1px solid var(--color-border-subtle)', fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>
                        <span style={{ color: getRiskColor(selected.risk_level), marginTop: '2px' }}>•</span>
                        {f}
                      </div>
                    ))}
                  </div>
                </Card>
                <Card style={{ border: '1px solid rgba(56,139,253,0.3)' }}>
                  <CardHeader title="Recommended Action" icon={<Brain size={16} />} />
                  <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.7 }}>{selected.recommended_action}</p>
                  <div style={{ marginTop: 'var(--space-4)', display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
                    <Badge variant="info">AI Generated</Badge>
                    <Badge variant="muted">{formatRelativeTime(selected.created_at)}</Badge>
                    <Badge variant="muted">Not guaranteed</Badge>
                  </div>
                </Card>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
