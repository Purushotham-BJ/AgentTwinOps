import React, { useState } from 'react';
import { Bot, Play } from 'lucide-react';
import { useInfrastructure } from '@/hooks/useInfrastructure';
import { orchestrationService } from '@/services/orchestrationService';
import { getErrorMessage } from '@/services/api';
import { Card, CardHeader } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/common/Badge';
import { Select } from '@/components/common/Input';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState } from '@/components/common/ErrorState';
import type { OrchestrationResult } from '@/types';

export function OperationsPage() {
  const { items } = useInfrastructure();
  const [serviceId, setServiceId] = useState('');
  const [result, setResult] = useState<OrchestrationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const run = async () => {
    const id = serviceId || items[0]?.id;
    if (!id) return;
    setLoading(true);
    setError('');
    try { setResult(await orchestrationService.run(id)); } catch (err) { setError(getErrorMessage(err)); } finally { setLoading(false); }
  };
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
      <Card>
        <CardHeader title="Multi-Agent Operations" icon={<Bot size={16} />} />
        <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'end', flexWrap: 'wrap' }}>
          <Select label="Target Service" options={items.map((item) => ({ value: item.id, label: item.service_name }))} value={serviceId || items[0]?.id || ''} onChange={(event) => setServiceId(event.target.value)} />
          <Button onClick={run} isLoading={loading} leftIcon={<Play size={14} />} disabled={!items.length}>Run Operations Workflow</Button>
        </div>
        {error && <p style={{ color: 'var(--color-error)', fontSize: 'var(--text-sm)' }}>{error}</p>}
      </Card>
      {loading && <LoadingState message="Coordinating agents..." />}
      {!loading && !result && <EmptyState title="No workflow result" description="Select a service and run the coordinated operations workflow." icon={<Bot size={48} />} />}
      {!loading && result && (
        <>
          <Card>
            <CardHeader title="Operational Decision" />
            <div style={{ display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
              <Badge variant={result.operational_status === 'CRITICAL' ? 'error' : result.operational_status === 'WARNING' ? 'warning' : 'success'}>{result.operational_status}</Badge>
              <Badge variant="info">Health {result.health_score.toFixed(0)}%</Badge>
              <Badge variant="muted">Failure {((result.failure_probability || 0) * 100).toFixed(0)}%</Badge>
            </div>
          </Card>
          <Card>
            <CardHeader title="Agent Execution" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              {result.agents.map((agent) => <div key={agent.agent} style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)' }}><span>{agent.agent}</span><Badge variant={agent.status === 'SUCCESS' ? 'success' : agent.status === 'FAILED' ? 'error' : 'muted'}>{agent.status}</Badge></div>)}
            </div>
          </Card>
          <Card>
            <CardHeader title="Recommendations and Recovery" />
            {result.recommendations.map((item) => <div key={item.id} style={{ padding: 'var(--space-2)', color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)' }}><strong>{item.title}</strong> — {item.action}</div>)}
            {result.recovery_actions.map((item, index) => <div key={`${item.action}-${index}`} style={{ padding: 'var(--space-2)', color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)' }}>Proposal: {item.action} (human approval required)</div>)}
            {!result.recommendations.length && !result.recovery_actions.length && <p style={{ color: 'var(--color-text-muted)' }}>No operational action required.</p>}
          </Card>
        </>
      )}
    </div>
  );
}
