import type { InfrastructureStatus, IncidentSeverity, ResolutionStatus, RiskLevel, TwinSyncStatus } from '@/types';

// ─── Infrastructure Status ────────────────────────────────────────────────────
export function getStatusColor(status: InfrastructureStatus): string {
  switch (status) {
    case 'healthy':  return 'var(--color-green-400)';
    case 'active':   return 'var(--color-blue-400)';
    case 'degraded': return 'var(--color-orange-300)';
    case 'inactive': return 'var(--color-text-muted)';
    case 'unhealthy':return 'var(--color-red-400)';
    default:         return 'var(--color-text-muted)';
  }
}

export function getStatusBg(status: InfrastructureStatus): string {
  switch (status) {
    case 'healthy':  return 'rgba(63, 185, 80, 0.1)';
    case 'active':   return 'rgba(56, 139, 253, 0.1)';
    case 'degraded': return 'rgba(255, 166, 87, 0.1)';
    case 'inactive': return 'rgba(110, 118, 129, 0.1)';
    case 'unhealthy':return 'rgba(248, 81, 73, 0.1)';
    default:         return 'rgba(110, 118, 129, 0.1)';
  }
}

// ─── Incident Severity ────────────────────────────────────────────────────────
export function getSeverityColor(severity: IncidentSeverity): string {
  switch (severity) {
    case 'critical': return 'var(--color-red-400)';
    case 'high':     return 'var(--color-orange-300)';
    case 'medium':   return 'var(--color-yellow-300)';
    case 'low':      return 'var(--color-blue-300)';
    default:         return 'var(--color-text-muted)';
  }
}

export function getSeverityBg(severity: IncidentSeverity): string {
  switch (severity) {
    case 'critical': return 'rgba(248, 81, 73, 0.1)';
    case 'high':     return 'rgba(255, 166, 87, 0.1)';
    case 'medium':   return 'rgba(240, 192, 64, 0.1)';
    case 'low':      return 'rgba(88, 166, 255, 0.1)';
    default:         return 'rgba(110, 118, 129, 0.1)';
  }
}

// ─── Resolution Status ────────────────────────────────────────────────────────
export function getResolutionColor(status: ResolutionStatus): string {
  switch (status) {
    case 'open':        return 'var(--color-red-400)';
    case 'in_progress': return 'var(--color-yellow-300)';
    case 'resolved':    return 'var(--color-green-400)';
    case 'closed':      return 'var(--color-text-muted)';
    default:            return 'var(--color-text-muted)';
  }
}

export function getResolutionBg(status: ResolutionStatus): string {
  switch (status) {
    case 'open':        return 'rgba(248, 81, 73, 0.1)';
    case 'in_progress': return 'rgba(240, 192, 64, 0.1)';
    case 'resolved':    return 'rgba(63, 185, 80, 0.1)';
    case 'closed':      return 'rgba(110, 118, 129, 0.1)';
    default:            return 'rgba(110, 118, 129, 0.1)';
  }
}

// ─── Risk Level ───────────────────────────────────────────────────────────────
export function getRiskColor(level: RiskLevel): string {
  switch (level) {
    case 'critical': return 'var(--color-red-400)';
    case 'high':     return 'var(--color-orange-300)';
    case 'medium':   return 'var(--color-yellow-300)';
    case 'low':      return 'var(--color-green-400)';
    default:         return 'var(--color-text-muted)';
  }
}

// ─── Twin Sync Status ─────────────────────────────────────────────────────────
export function getSyncColor(status: TwinSyncStatus): string {
  switch (status) {
    case 'synced':      return 'var(--color-green-400)';
    case 'syncing':     return 'var(--color-blue-400)';
    case 'out_of_sync': return 'var(--color-orange-300)';
    case 'error':       return 'var(--color-red-400)';
    default:            return 'var(--color-text-muted)';
  }
}

// ─── Health score ─────────────────────────────────────────────────────────────
export function getHealthColor(score: number): string {
  if (score >= 80) return 'var(--color-green-400)';
  if (score >= 60) return 'var(--color-yellow-300)';
  if (score >= 40) return 'var(--color-orange-300)';
  return 'var(--color-red-400)';
}
