/**
 * twinService — Digital Twin interface.
 * Connected to AI Service (LangGraph multi-agent system)
 */
import type { TwinObject, InfrastructureItem, InfrastructureStatus, TwinState } from '@/types';
import api from './api';

type JsonRecord = Record<string, unknown>;

function mapTwin(raw: JsonRecord): TwinObject {
  const current = (raw.current_state as JsonRecord | undefined) ?? {};
  const predicted = (raw.predicted_state as JsonRecord | undefined) ?? {};
  const toState = (state: JsonRecord, fallback: TwinState): TwinState => ({
    cpu_usage: Number(state.cpu_usage ?? state.cpu ?? fallback.cpu_usage),
    memory_usage: Number(state.memory_usage ?? state.memory ?? fallback.memory_usage),
    latency_ms: Number(state.latency_ms ?? state.latency ?? fallback.latency_ms),
    error_rate: Number(state.error_rate ?? fallback.error_rate),
    request_rate: Number(state.request_rate ?? fallback.request_rate),
    status: (state.status ?? fallback.status) as InfrastructureStatus,
    prediction_type: state.prediction_type as TwinState['prediction_type'],
    predicted_value: state.predicted_value as number | undefined,
    failure_probability: state.failure_probability as number | undefined,
    confidence: state.confidence as number | undefined,
    risk_level: state.risk_level as TwinState['risk_level'],
    recommended_action: state.recommended_action as string | undefined,
    prediction_timestamp: state.prediction_timestamp as string | undefined,
    horizon_minutes: state.horizon_minutes as number | undefined,
    prediction_source: state.prediction_source as TwinState['prediction_source'],
    model_metrics: state.model_metrics as TwinState['model_metrics'],
  });
  const base = toState(current, {
    cpu_usage: 0, memory_usage: 0, latency_ms: 0, error_rate: 0, request_rate: 0,
    status: 'unknown' as InfrastructureStatus,
  });
  return {
    id: String(raw.id),
    name: String(raw.service_name ?? raw.service_id),
    service_id: String(raw.service_id),
    service_type: String(raw.service_type ?? 'unknown'),
    current_state: base,
    predicted_state: toState(predicted, base),
    health_score: Number(raw.health_score ?? 0),
    sync_status: 'synced',
    last_synced: String(raw.last_sync),
  };
}

export const twinService = {
  /**
   * Get all digital twins.
   * GET /api/v1/twins
   */
  async getTwins(infrastructure: InfrastructureItem[]): Promise<TwinObject[]> {
    const response = await api.get('/twins/');
    return (response.data ?? []).map(mapTwin);
  },

  /**
   * Get a single twin by twin ID.
   * GET /api/v1/twins/{twin_id}
   */
  async getTwin(serviceId: string, serviceName: string): Promise<TwinObject> {
    const response = await api.get(`/twins/by-service/${serviceId}`);
    return mapTwin(response.data);
  },
};
