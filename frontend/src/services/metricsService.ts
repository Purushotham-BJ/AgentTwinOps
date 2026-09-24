/**
 * metricsService — interface for metrics data.
 *
 * ⚠️  NO BACKEND METRICS API EXISTS YET.
 * This service returns realistic mock data isolated in one place.
 * When a real /api/v1/metrics endpoint is available, replace the mock
 * implementations below with real API calls. All component code remains
 * unchanged because they consume this service, not raw API calls.
 */
import type { ServiceMetrics, MetricPoint, DashboardSummary } from '@/types';

function generateTimeSeries(
  baseValue: number,
  variance: number,
  points = 24,
  intervalMinutes = 60
): MetricPoint[] {
  const now = Date.now();
  return Array.from({ length: points }, (_, i) => ({
    timestamp: new Date(now - (points - 1 - i) * intervalMinutes * 60000).toISOString(),
    value: Math.max(0, Math.min(100, baseValue + (Math.random() - 0.5) * variance)),
  }));
}

export const metricsService = {
  /**
   * [MOCK] Fetch metrics for a specific service.
   * Replace with: GET /api/v1/metrics/{service_id}
   */
  async getServiceMetrics(serviceId: string, serviceName: string): Promise<ServiceMetrics> {
    await new Promise((r) => setTimeout(r, 300)); // simulate latency
    return {
      service_id: serviceId,
      service_name: serviceName,
      cpu: generateTimeSeries(45, 30),
      memory: generateTimeSeries(60, 20),
      latency: generateTimeSeries(120, 80).map((p) => ({ ...p, value: p.value * 3 })),
      network_in: generateTimeSeries(50, 40),
      network_out: generateTimeSeries(30, 25),
    };
  },

  /**
   * [MOCK] Aggregate metrics across all services for the dashboard.
   * Replace with: GET /api/v1/metrics/summary
   */
  async getDashboardMetrics(): Promise<{
    cpu: MetricPoint[];
    memory: MetricPoint[];
    latency: MetricPoint[];
    network: MetricPoint[];
  }> {
    await new Promise((r) => setTimeout(r, 200));
    return {
      cpu: generateTimeSeries(52, 25),
      memory: generateTimeSeries(68, 15),
      latency: generateTimeSeries(95, 40).map((p) => ({ ...p, value: p.value * 2 })),
      network: generateTimeSeries(45, 30),
    };
  },

  /**
   * Compute dashboard summary from real infrastructure + incident data.
   * Augments real data with mock AI metrics.
   */
  computeDashboardSummary(
    totalServices: number,
    statusCounts: Record<string, number>,
    openIncidents: number,
    criticalIncidents: number
  ): DashboardSummary {
    const healthy = (statusCounts['healthy'] ?? 0) + (statusCounts['active'] ?? 0);
    const degraded = statusCounts['degraded'] ?? 0;
    const unhealthy = (statusCounts['unhealthy'] ?? 0) + (statusCounts['inactive'] ?? 0);
    const healthPct = totalServices > 0 ? Math.round((healthy / totalServices) * 100) : 0;
    const riskScore = Math.min(
      100,
      criticalIncidents * 20 + openIncidents * 5 + degraded * 10 + unhealthy * 15
    );

    return {
      infrastructure_health: healthPct,
      total_services: totalServices,
      healthy_services: healthy,
      degraded_services: degraded,
      unhealthy_services: unhealthy,
      open_incidents: openIncidents,
      critical_incidents: criticalIncidents,
      failure_risk: riskScore,
      active_recommendations: Math.max(1, Math.floor(riskScore / 15)),
    };
  },
};
