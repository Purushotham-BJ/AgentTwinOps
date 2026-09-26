import api from './api';
import type { ServiceMetrics, MetricPoint, DashboardSummary } from '@/types';

const PREFIX = '/api/v1/metrics';

interface BackendMetric {
  timestamp: string;
  cpu_usage: number;
  memory_usage: number;
  latency: number;
  network_usage: number;
}

function mapMetrics(items: BackendMetric[], serviceId: string, serviceName: string): ServiceMetrics {
  return {
    service_id: serviceId,
    service_name: serviceName,
    cpu: items.map((item) => ({ timestamp: item.timestamp, value: item.cpu_usage })),
    memory: items.map((item) => ({ timestamp: item.timestamp, value: item.memory_usage })),
    latency: items.map((item) => ({ timestamp: item.timestamp, value: item.latency })),
    network_in: items.map((item) => ({ timestamp: item.timestamp, value: item.network_usage })),
    network_out: [],
  };
}

export const metricsService = {
  async getServiceMetrics(serviceId: string, serviceName: string): Promise<ServiceMetrics> {
    const response = await api.get(`${PREFIX}/service/${serviceId}`, { params: { limit: 100 } });
    return mapMetrics(response.data.items ?? [], serviceId, serviceName);
  },

  async getDashboardMetrics(): Promise<{
    cpu: MetricPoint[];
    memory: MetricPoint[];
    latency: MetricPoint[];
    network: MetricPoint[];
  }> {
    const response = await api.get(PREFIX, { params: { limit: 1000 } });
    const items = response.data.items ?? [];
    return {
      cpu: items.map((item: BackendMetric) => ({ timestamp: item.timestamp, value: item.cpu_usage })),
      memory: items.map((item: BackendMetric) => ({ timestamp: item.timestamp, value: item.memory_usage })),
      latency: items.map((item: BackendMetric) => ({ timestamp: item.timestamp, value: item.latency })),
      network: items.map((item: BackendMetric) => ({ timestamp: item.timestamp, value: item.network_usage })),
    };
  },

  computeDashboardSummary(
    totalServices: number,
    statusCounts: Record<string, number>,
    openIncidents: number,
    criticalIncidents: number
  ): DashboardSummary {
    const healthy = (statusCounts.healthy ?? 0) + (statusCounts.active ?? 0);
    const degraded = statusCounts.degraded ?? 0;
    const unhealthy = (statusCounts.unhealthy ?? 0) + (statusCounts.inactive ?? 0);
    const healthPct = totalServices > 0 ? Math.round((healthy / totalServices) * 100) : 0;
    const riskScore = Math.min(100, criticalIncidents * 20 + openIncidents * 5 + degraded * 10 + unhealthy * 15);
    return {
      infrastructure_health: healthPct,
      total_services: totalServices,
      healthy_services: healthy,
      degraded_services: degraded,
      unhealthy_services: unhealthy,
      open_incidents: openIncidents,
      critical_incidents: criticalIncidents,
      failure_risk: riskScore,
      active_recommendations: 0,
    };
  },
};
