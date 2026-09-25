import React, { useState } from 'react';
import { Activity, Cpu, MemoryStick, Wifi, Timer, RefreshCw } from 'lucide-react';
import { useInfrastructure } from '@/hooks/useInfrastructure';
import { metricsService } from '@/services/metricsService';
import { Card, CardHeader } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Select } from '@/components/common/Input';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState, ErrorState } from '@/components/common/ErrorState';
import { MetricChart } from '@/components/common/MetricChart';
import { useMetrics } from '@/hooks/useMetrics';
import { formatRelativeTime } from '@/utils/format';
import type { ServiceMetrics } from '@/types';

export function MetricsPage() {
  const { items: infra } = useInfrastructure();
  const { metrics: dashMetrics, isLoading: dashLoading, error: dashError, lastUpdated, refetch } = useMetrics();
  const [serviceId, setServiceId] = useState('');
  const [svcMetrics, setSvcMetrics] = useState<ServiceMetrics | null>(null);
  const [loadingSvc, setLoadingSvc] = useState(false);

  const handleFetchService = async () => {
    const id = serviceId || infra[0]?.id;
    if (!id) return;
    const svc = infra.find(i => i.id === id);
    setLoadingSvc(true);
    const m = await metricsService.getServiceMetrics(id, svc?.service_name ?? id);
    setSvcMetrics(m);
    setLoadingSvc(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
          {lastUpdated && <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>Updated {lastUpdated.toLocaleTimeString()}</span>}
          <Button variant="ghost" size="sm" onClick={refetch} leftIcon={<RefreshCw size={14} />}>Refresh</Button>
        </div>
      </div>

      {/* Platform-wide charts */}
      <h3 style={{ fontSize: 'var(--text-base)', color: 'var(--color-text-secondary)', margin: 0 }}>Platform Overview</h3>
      {dashLoading ? <LoadingState message="Loading metrics..." /> : dashError ? <ErrorState message={dashError} onRetry={refetch} /> : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--space-4)' }}>
          <Card><CardHeader title="CPU Usage" icon={<Cpu size={16} />} subtitle="24h trend" />
            {dashMetrics && <MetricChart data={dashMetrics.cpu} color="var(--color-cyan-400)" height={180} />}
          </Card>
          <Card><CardHeader title="Memory Usage" icon={<MemoryStick size={16} />} subtitle="24h trend" />
            {dashMetrics && <MetricChart data={dashMetrics.memory} color="var(--color-purple-400)" height={180} />}
          </Card>
          <Card><CardHeader title="Latency" icon={<Timer size={16} />} subtitle="avg ms" />
            {dashMetrics && <MetricChart data={dashMetrics.latency} color="var(--color-orange-300)" unit="ms" height={180} />}
          </Card>
          <Card><CardHeader title="Network" icon={<Wifi size={16} />} subtitle="traffic" />
            {dashMetrics && <MetricChart data={dashMetrics.network} color="var(--color-blue-300)" type="line" height={180} />}
          </Card>
        </div>
      )}

      {/* Per-service drill-down */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', flexWrap: 'wrap', marginTop: 'var(--space-2)' }}>
        <h3 style={{ fontSize: 'var(--text-base)', color: 'var(--color-text-secondary)', margin: 0 }}>Service Drill-Down</h3>
        <Select
          options={infra.length > 0 ? infra.map(i => ({ value: i.id, label: i.service_name })) : [{ value: '', label: 'No services' }]}
          value={serviceId || infra[0]?.id || ''}
          onChange={(e) => setServiceId(e.target.value)}
          style={{ width: '220px' }}
        />
        <Button variant="primary" size="sm" onClick={handleFetchService} isLoading={loadingSvc} leftIcon={<Activity size={14} />} disabled={infra.length === 0}>
          Load Service Metrics
        </Button>
      </div>

      {loadingSvc ? <LoadingState message="Loading service metrics..." /> :
       svcMetrics ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--space-4)' }}>
          <Card><CardHeader title="CPU" subtitle={svcMetrics.service_name} />
            <MetricChart data={svcMetrics.cpu} color="var(--color-cyan-400)" height={160} />
          </Card>
          <Card><CardHeader title="Memory" subtitle={svcMetrics.service_name} />
            <MetricChart data={svcMetrics.memory} color="var(--color-purple-400)" height={160} />
          </Card>
          <Card><CardHeader title="Latency" subtitle={svcMetrics.service_name} />
            <MetricChart data={svcMetrics.latency} color="var(--color-orange-300)" unit="ms" height={160} />
          </Card>
          <Card><CardHeader title="Network In" subtitle={svcMetrics.service_name} />
            <MetricChart data={svcMetrics.network_in} color="var(--color-green-400)" type="line" height={160} />
          </Card>
        </div>
      ) : (
        <EmptyState title="Select a service" description="Choose a service above and click Load to view its metrics." icon={<Activity size={48} />} />
      )}
    </div>
  );
}
