// ─── API Response Envelope ───────────────────────────────────────────────────
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  timestamp: string;
}

export interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
  };
  timestamp: string;
}

// ─── Auth ────────────────────────────────────────────────────────────────────
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface ProfileResponse {
  id: string;
  name: string;
  email: string;
  role: string;
  created_at: string;
  updated_at: string;
}

// ─── Infrastructure ──────────────────────────────────────────────────────────
export type InfrastructureStatus = 'active' | 'inactive' | 'degraded' | 'healthy' | 'unhealthy';

export interface InfrastructureItem {
  id: string;
  service_name: string;
  service_type: string;
  status: InfrastructureStatus;
  host: string;
  created_at: string;
  updated_at: string;
}

export interface InfrastructureListResponse {
  items: InfrastructureItem[];
  total: number;
}

export interface InfrastructureCreateRequest {
  service_name: string;
  service_type: string;
  status?: InfrastructureStatus;
  host: string;
}

export interface InfrastructureUpdateRequest {
  service_name?: string;
  service_type?: string;
  status?: InfrastructureStatus;
  host?: string;
}

// ─── Incidents ───────────────────────────────────────────────────────────────
export type IncidentSeverity = 'low' | 'medium' | 'high' | 'critical';
export type ResolutionStatus = 'open' | 'in_progress' | 'resolved' | 'closed';

export interface IncidentItem {
  id: string;
  service_id: string;
  severity: IncidentSeverity;
  incident_type: string;
  resolution_status: ResolutionStatus;
  timestamp: string;
  created_at: string;
  updated_at: string;
}

export interface IncidentListResponse {
  items: IncidentItem[];
  total: number;
}

export interface IncidentCreateRequest {
  service_id: string;
  severity?: IncidentSeverity;
  incident_type: string;
  resolution_status?: ResolutionStatus;
}

export interface IncidentUpdateRequest {
  service_id?: string;
  severity?: IncidentSeverity;
  incident_type?: string;
  resolution_status?: ResolutionStatus;
}

// ─── System / Health ─────────────────────────────────────────────────────────
export interface HealthResponse {
  status: string;
  database: string;
  environment: string;
  debug: boolean;
  timestamp: string;
}

export interface VersionResponse {
  app_name: string;
  version: string;
  api_version: string;
  python_version: string;
}

// ─── Digital Twin (frontend-only / future API) ───────────────────────────────
export type TwinSyncStatus = 'synced' | 'syncing' | 'out_of_sync' | 'error';

export interface TwinObject {
  id: string;
  name: string;
  service_id: string;
  service_type: string;
  current_state: TwinState;
  predicted_state: TwinState;
  health_score: number; // 0-100
  sync_status: TwinSyncStatus;
  last_synced: string;
}

export interface TwinState {
  cpu_usage: number;
  memory_usage: number;
  latency_ms: number;
  error_rate: number;
  request_rate: number;
  status: InfrastructureStatus;
  prediction_type?: PredictionResult['prediction_type'];
  predicted_value?: number;
  failure_probability?: number;
  confidence?: number;
  risk_level?: RiskLevel;
  recommended_action?: string;
  prediction_timestamp?: string;
  horizon_minutes?: number;
  prediction_source?: PredictionResult['prediction_source'];
  model_metrics?: Record<string, number | string | null>;
}

// ─── Metrics (frontend-only / future API) ────────────────────────────────────
export interface MetricPoint {
  timestamp: string;
  value: number;
}

export interface ServiceMetrics {
  service_id: string;
  service_name: string;
  cpu: MetricPoint[];
  memory: MetricPoint[];
  latency: MetricPoint[];
  network_in: MetricPoint[];
  network_out: MetricPoint[];
}

// ─── Prediction (frontend-only / future API) ─────────────────────────────────
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface PredictionRequest {
  service_id: string;
  horizon_minutes: number;
}

export interface PredictionResult {
  id: string;
  service_id: string;
  prediction_type: 'cpu' | 'memory' | 'failure';
  predicted_value: number;
  confidence: number; // 0-1
  failure_probability: number; // 0-1
  risk_level: RiskLevel;
  factors: string[];
  recommended_action: string;
  created_at: string;
  horizon_minutes: number;
  data_points: MetricPoint[];
  status: 'SUCCESS' | 'INSUFFICIENT_DATA' | 'ERROR';
  historical_metrics: number[];
  feature_vector: number[][];
  model_metrics: Record<string, number | string | null>;
  prediction_source: 'model' | 'heuristic' | 'fallback' | 'none';
}

// ─── Digital Twin simulation ──────────────────────────────────────────────────
export type SimulationScenario = 'cpu_spike' | 'traffic_surge' | 'database_failure' | 'pod_eviction' | 'custom';

export interface SimulationRequest {
  scenario: SimulationScenario;
  service_id: string;
  parameters: Record<string, number | string>;
  horizon_minutes?: number;
}

export interface SimulationResult {
  id: string;
  scenario: SimulationScenario;
  service_id: string;
  status: 'running' | 'completed' | 'failed';
  baseline_state: Record<string, number | string>;
  scenario_changes: Record<string, number | string>;
  simulated_state: Record<string, number | string>;
  simulated_health_score: number;
  simulated_failure_probability: number;
  simulated_operational_status: string;
  impact_summary: string[];
  predicted_impact: {
    cpu_delta: number;
    memory_delta: number;
    latency_delta: number;
    failure_probability: number;
  };
  timeline: MetricPoint[];
  recommendations: string[];
  created_at: string;
  completed_at?: string;
}

// ─── Recommendations (frontend-only / future API) ─────────────────────────────
export type RecommendationPriority = 'low' | 'medium' | 'high' | 'critical';

export interface Recommendation {
  id: string;
  service_id?: string;
  service_name?: string;
  title: string;
  description: string;
  type: string;
  reason: string;
  action: string;
  priority: RecommendationPriority;
  severity: IncidentSeverity;
  expected_impact: string;
  implementation_steps: string[];
  category: 'scaling' | 'optimization' | 'security' | 'reliability' | 'cost';
  estimated_effort: 'low' | 'medium' | 'high';
  created_at: string;
  source: 'ai' | 'rule' | 'manual';
  confidence: number;
}

// ─── Dashboard aggregates ─────────────────────────────────────────────────────
export interface DashboardSummary {
  infrastructure_health: number; // percentage
  total_services: number;
  healthy_services: number;
  degraded_services: number;
  unhealthy_services: number;
  open_incidents: number;
  critical_incidents: number;
  failure_risk: number; // 0-100
  active_recommendations: number;
}
