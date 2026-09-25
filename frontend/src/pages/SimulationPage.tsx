import React, { useState } from 'react';
import { FlaskConical, Play, Cpu, Zap, Database, Box, CheckCircle } from 'lucide-react';
import { simulationService } from '@/services/simulationService';
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
import { formatPercent } from '@/utils/format';
import { getRiskColor } from '@/utils/statusHelpers';
import { getErrorMessage } from '@/services/api';
import type { SimulationResult, SimulationScenario } from '@/types';

const SCENARIOS: { value: SimulationScenario; label: string; description: string; icon: React.ReactNode; color: string }[] = [
  { value: 'cpu_spike', label: 'CPU Spike', description: 'Simulate sudden CPU saturation event', icon: <Cpu size={18} />, color: 'var(--color-cyan-400)' },
  { value: 'traffic_surge', label: 'Traffic Surge', description: 'Simulate high inbound traffic burst', icon: <Zap size={18} />, color: 'var(--color-blue-400)' },
  { value: 'database_failure', label: 'Database Failure', description: 'Simulate primary DB connection loss', icon: <Database size={18} />, color: 'var(--color-red-400)' },
  { value: 'pod_eviction', label: 'Pod Eviction', description: 'Simulate Kubernetes pod eviction event', icon: <Box size={18} />, color: 'var(--color-orange-300)' },
];

export function SimulationPage() {
  const { items: infraItems } = useInfrastructure();
  const [serviceId, setServiceId] = useState('');
  const [scenario, setScenario] = useState<SimulationScenario>('cpu_spike');
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState('');

  const handleRun = async () => {
    const id = serviceId || infraItems[0]?.id;
    if (!id) return;
    setIsRunning(true);
    setError('');
    try {
      const r = await simulationService.run({ scenario, service_id: id, parameters: {} });
      setResult(r);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsRunning(false);
    }
  };

  const selectedScenario = SCENARIOS.find((s) => s.value === scenario);
  const failureProb = result?.predicted_impact.failure_probability ?? 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
        <MockDataBanner feature="Simulation engine" apiEndpoint="POST /api/simulate/{scenario}" />
      </div>

      {/* Scenario selection */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-3)' }}>
        {SCENARIOS.map((s) => (
          <div
            key={s.value}
            onClick={() => setScenario(s.value)}
            style={{
              background: 'var(--color-bg-surface)',
              border: `1px solid ${scenario === s.value ? s.color : 'var(--color-border)'}`,
              borderRadius: 'var(--radius-lg)',
              padding: 'var(--space-4)',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)',
              boxShadow: scenario === s.value ? `0 0 0 1px ${s.color}40` : 'none',
            }}
          >
            <div style={{ color: s.color, marginBottom: 'var(--space-2)' }}>{s.icon}</div>
            <div style={{ fontSize: 'var(--text-sm)', fontWeight: '600', color: 'var(--color-text-primary)', marginBottom: '4px' }}>{s.label}</div>
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>{s.description}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(280px, 340px) 1fr', gap: 'var(--space-5)', alignItems: 'start' }}>
        {/* Config */}
        <Card>
          <CardHeader title="Simulation Parameters" icon={<FlaskConical size={16} />} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <Select
              label="Target Service"
              options={infraItems.length > 0 ? infraItems.map(i => ({ value: i.id, label: i.service_name })) : [{ value: '', label: 'No services yet' }]}
              value={serviceId || infraItems[0]?.id || ''}
              onChange={(e) => setServiceId(e.target.value)}
            />
            <div style={{ padding: 'var(--space-3)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: 'var(--space-2)' }}>Selected Scenario</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: selectedScenario?.color }}>
                {selectedScenario?.icon}
                <span style={{ fontWeight: '600', fontSize: 'var(--text-sm)', color: 'var(--color-text-primary)' }}>{selectedScenario?.label}</span>
              </div>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginTop: '4px' }}>{selectedScenario?.description}</p>
            </div>
            <Button
              variant="primary"
              size="md"
              onClick={handleRun}
              isLoading={isRunning}
              leftIcon={<Play size={14} />}
              disabled={infraItems.length === 0}
              style={{ width: '100%' }}
            >
              {isRunning ? 'Simulating...' : 'Run Simulation'}
            </Button>
            {error && <p style={{ color: 'var(--color-error)', fontSize: 'var(--text-sm)' }}>{error}</p>}
          </div>
        </Card>

        {/* Results */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {isRunning && <LoadingState message="Running simulation..." />}
          {!isRunning && !result && (
            <EmptyState title="No simulation results yet" description="Select a scenario and click Run Simulation to see the predicted impact." icon={<FlaskConical size={48} />} />
          )}
          {!isRunning && result && (
            <>
              <Card>
                <CardHeader title="Baseline vs Simulated State" icon={<FlaskConical size={16} />} />
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
                  {(['baseline_state', 'simulated_state'] as const).map((key) => (
                    <div key={key} style={{ background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', padding: 'var(--space-3)' }}>
                      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: 'var(--space-2)' }}>
                        {key === 'baseline_state' ? 'Baseline' : 'Simulated'}
                      </div>
                      {Object.entries(result[key]).map(([name, value]) => (
                        <div key={name} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>
                          <span>{name.replace('_', ' ')}</span><strong>{typeof value === 'number' ? value.toFixed(1) : value}</strong>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
                <div style={{ marginTop: 'var(--space-3)', display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
                  <Badge variant="info">Health {result.simulated_health_score.toFixed(0)}%</Badge>
                  <Badge variant={result.simulated_operational_status === 'CRITICAL' ? 'error' : result.simulated_operational_status === 'WARNING' ? 'warning' : 'success'}>
                    {result.simulated_operational_status}
                  </Badge>
                </div>
                <ul style={{ margin: 'var(--space-3) 0 0', paddingLeft: 'var(--space-5)', color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)' }}>
                  {result.impact_summary.map((item) => <li key={item}>{item}</li>)}
                </ul>
              </Card>
              {/* Impact summary */}
              <Card>
                <CardHeader title="Predicted Impact" icon={<FlaskConical size={16} />}
                  action={<Badge variant={failureProb > 0.6 ? 'error' : failureProb > 0.3 ? 'warning' : 'success'}>{result.status}</Badge>}
                />
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 'var(--space-3)' }}>
                  {[
                    { label: 'CPU Delta', value: `+${result.predicted_impact.cpu_delta.toFixed(1)}%`, color: 'var(--color-cyan-400)' },
                    { label: 'Memory Delta', value: `+${result.predicted_impact.memory_delta.toFixed(1)}%`, color: 'var(--color-purple-400)' },
                    { label: 'Latency Delta', value: `+${result.predicted_impact.latency_delta.toFixed(0)}ms`, color: 'var(--color-orange-300)' },
                    { label: 'Failure Risk', value: formatPercent(failureProb * 100), color: getRiskColor(failureProb > 0.7 ? 'critical' : failureProb > 0.4 ? 'high' : 'medium') },
                  ].map((m) => (
                    <div key={m.label} style={{ background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', padding: 'var(--space-3)', textAlign: 'center' }}>
                      <div style={{ fontSize: 'var(--text-xl)', fontWeight: '700', color: m.color }}>{m.value}</div>
                      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginTop: '4px' }}>{m.label}</div>
                    </div>
                  ))}
                </div>
                <div style={{ marginTop: 'var(--space-3)' }}>
                  <ProgressBar value={failureProb * 100} height={8} animated label="Failure Probability" showLabel />
                </div>
              </Card>

              {/* Timeline chart */}
              <Card>
                <CardHeader title="Impact Timeline" subtitle="Simulated metric projection over 60 minutes" />
                <MetricChart data={result.timeline} color={getRiskColor(failureProb > 0.7 ? 'critical' : failureProb > 0.4 ? 'high' : 'medium')} height={200} />
              </Card>

              {/* Recommendations */}
              <Card>
                <CardHeader title="Recommendations" icon={<CheckCircle size={16} />} />
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                  {result.recommendations.map((r, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)', padding: 'var(--space-3)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)' }}>
                      <span style={{ color: 'var(--color-primary)', fontWeight: '700', flexShrink: 0, fontSize: 'var(--text-sm)' }}>{i + 1}.</span>
                      <span style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>{r}</span>
                    </div>
                  ))}
                </div>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
