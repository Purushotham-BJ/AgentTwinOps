import React, { useState } from 'react';
import { Lightbulb, RefreshCw, Sparkles, ChevronDown, ChevronRight } from 'lucide-react';
import { useRecommendations } from '@/hooks/useRecommendations';
import { useInfrastructure } from '@/hooks/useInfrastructure';
import { useIncidents } from '@/hooks/useIncidents';
import { Card, CardHeader } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/common/Badge';
import { Select } from '@/components/common/Input';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState } from '@/components/common/ErrorState';
import { formatRelativeTime } from '@/utils/format';
import { getSeverityColor, getRiskColor } from '@/utils/statusHelpers';
import type { Recommendation, RecommendationPriority } from '@/types';

function priVariant(p: RecommendationPriority) {
  return p === 'critical' ? 'error' : p === 'high' ? 'warning' : p === 'medium' ? 'info' : 'muted';
}

function categoryVariant(c: Recommendation['category']) {
  return c === 'scaling' ? 'default' : c === 'reliability' ? 'warning' : c === 'security' ? 'error' : c === 'cost' ? 'success' : 'muted';
}

export function RecommendationsPage() {
  const { items: infra } = useInfrastructure();
  const { items: incidents } = useIncidents();
  const { recommendations, isLoading, isGenerating, error, generate } = useRecommendations(infra, incidents);
  const [priorityFilter, setPriorityFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [serviceFilter, setServiceFilter] = useState('');
  const [expanded, setExpanded] = useState<string | null>(null);

  const filtered = recommendations.filter((r) => {
    const matchPri = !priorityFilter || r.priority === priorityFilter;
    const matchCat = !categoryFilter || r.category === categoryFilter;
    const matchService = !serviceFilter || r.service_id === serviceFilter;
    return matchPri && matchCat && matchService;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <Badge variant="info">Deterministic recommendations from live operational state</Badge>
        <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
          <Select options={[{ value: '', label: 'All services' }, ...infra.map((item) => ({ value: item.id, label: item.service_name }))]} value={serviceFilter} onChange={(e) => setServiceFilter(e.target.value)} style={{ width: '170px' }} />
          <Select options={[{ value: '', label: 'All priorities' }, ...(['critical','high','medium','low'].map(p => ({ value: p, label: p.charAt(0).toUpperCase()+p.slice(1) })))]} value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)} style={{ width: '150px' }} />
          <Select options={[{ value: '', label: 'All categories' }, ...(['scaling','reliability','optimization','security','cost'].map(c => ({ value: c, label: c.charAt(0).toUpperCase()+c.slice(1) })))]} value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} style={{ width: '160px' }} />
          <Button variant="primary" size="sm" onClick={() => generate(serviceFilter || undefined)} isLoading={isGenerating} leftIcon={<Sparkles size={14} />}>
            {isGenerating ? 'Generating...' : 'Generate AI Recommendations'}
          </Button>
        </div>
      </div>

      {/* Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: 'var(--space-3)' }}>
        {(['critical', 'high', 'medium', 'low'] as RecommendationPriority[]).map((p) => {
          const count = recommendations.filter((r) => r.priority === p).length;
          return (
            <div key={p} style={{ background: 'var(--color-bg-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: 'var(--space-4)', textAlign: 'center' }}>
              <div style={{ fontSize: 'var(--text-2xl)', fontWeight: '700', color: priVariant(p) === 'error' ? 'var(--color-red-400)' : priVariant(p) === 'warning' ? 'var(--color-orange-300)' : priVariant(p) === 'info' ? 'var(--color-blue-300)' : 'var(--color-text-muted)' }}>{count}</div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', textTransform: 'capitalize', marginTop: '4px' }}>{p}</div>
            </div>
          );
        })}
      </div>

      {isLoading ? (
        <LoadingState message="Loading AI recommendations..." />
      ) : filtered.length === 0 ? (
        <EmptyState title="No recommendations" description="Click Generate AI Recommendations to analyze your infrastructure." icon={<Lightbulb size={48} />}
          action={<Button variant="primary" size="sm" onClick={() => generate(serviceFilter || undefined)} leftIcon={<Sparkles size={14} />}>Generate</Button>}
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          {filtered.map((rec) => (
            <RecommendationCard key={rec.id} rec={rec} expanded={expanded === rec.id} onToggle={() => setExpanded(expanded === rec.id ? null : rec.id)} />
          ))}
        </div>
      )}
    </div>
  );
}

function RecommendationCard({ rec, expanded, onToggle }: { rec: Recommendation; expanded: boolean; onToggle: () => void }) {
  return (
    <Card hover>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-4)', cursor: 'pointer' }} onClick={onToggle}>
        <div style={{ width: '40px', height: '40px', flexShrink: 0, borderRadius: 'var(--radius-md)', background: priVariant(rec.priority) === 'error' ? 'rgba(248,81,73,0.1)' : 'rgba(255,166,87,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Lightbulb size={20} style={{ color: priVariant(rec.priority) === 'error' ? 'var(--color-red-400)' : 'var(--color-orange-300)' }} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', flexWrap: 'wrap', marginBottom: '6px' }}>
            <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: '600', color: 'var(--color-text-primary)', margin: 0 }}>{rec.title}</h4>
            <Badge variant={priVariant(rec.priority)} dot>{rec.priority}</Badge>
            <Badge variant={categoryVariant(rec.category)}>{rec.category}</Badge>
            {rec.source === 'ai' && <Badge variant="info"><Sparkles style={{ display: 'inline', width: 10 }} /> AI</Badge>}
            <Badge variant="muted">Effort: {rec.estimated_effort}</Badge>
          </div>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', margin: 0, display: '-webkit-box', WebkitLineClamp: expanded ? undefined : 2, WebkitBoxOrient: 'vertical', overflow: expanded ? 'visible' : 'hidden' }}>
            {rec.description}
          </p>
          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginTop: '6px' }}>{formatRelativeTime(rec.created_at)}</div>
        </div>
        <div style={{ color: 'var(--color-text-muted)', flexShrink: 0 }}>
          {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </div>
      </div>

      {expanded && (
        <div style={{ marginTop: 'var(--space-4)', paddingTop: 'var(--space-4)', borderTop: '1px solid var(--color-border)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
            <div>
              <div style={{ fontSize: 'var(--text-xs)', fontWeight: '600', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 'var(--space-2)' }}>Reason</div>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>{rec.reason}</p>
            </div>
            <div>
              <div style={{ fontSize: 'var(--text-xs)', fontWeight: '600', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 'var(--space-2)' }}>Recommended Action</div>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>{rec.action}</p>
            </div>
            <div>
              <div style={{ fontSize: 'var(--text-xs)', fontWeight: '600', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 'var(--space-2)' }}>Expected Impact</div>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>{rec.expected_impact}</p>
            </div>
            <div>
              <div style={{ fontSize: 'var(--text-xs)', fontWeight: '600', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 'var(--space-2)' }}>Implementation Steps</div>
              {rec.implementation_steps.map((step, i) => (
                <div key={i} style={{ display: 'flex', gap: 'var(--space-2)', marginBottom: 'var(--space-2)', fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>
                  <span style={{ color: 'var(--color-primary)', fontWeight: '700', flexShrink: 0 }}>{i + 1}.</span>
                  {step}
                </div>
              ))}
              <div style={{ marginTop: 'var(--space-3)', fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                Rule confidence: {(rec.confidence * 100).toFixed(0)}%
              </div>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
