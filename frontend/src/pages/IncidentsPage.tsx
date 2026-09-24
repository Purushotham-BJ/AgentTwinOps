import React, { useState, useMemo } from 'react';
import { Plus, Search, AlertTriangle, RefreshCw, Edit2 } from 'lucide-react';
import { useIncidents } from '@/hooks/useIncidents';
import { useInfrastructure } from '@/hooks/useInfrastructure';
import { Card, CardHeader } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/common/Badge';
import { Input, Select } from '@/components/common/Input';
import { Modal } from '@/components/common/Modal';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState, EmptyState } from '@/components/common/ErrorState';
import { Table } from '@/components/common/Table';
import { formatRelativeTime } from '@/utils/format';
import { getErrorMessage } from '@/services/api';
import type { IncidentItem, IncidentSeverity, ResolutionStatus, IncidentCreateRequest } from '@/types';

const SEVERITY_OPTIONS = [
  { value: 'low', label: 'Low' }, { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' }, { value: 'critical', label: 'Critical' },
];
const RESOLUTION_OPTIONS = [
  { value: 'open', label: 'Open' }, { value: 'in_progress', label: 'In Progress' },
  { value: 'resolved', label: 'Resolved' }, { value: 'closed', label: 'Closed' },
];

function sevVariant(s: IncidentSeverity) {
  return s === 'critical' ? 'error' : s === 'high' ? 'warning' : s === 'medium' ? 'info' : 'muted';
}
function resVariant(s: ResolutionStatus) {
  return s === 'open' ? 'error' : s === 'in_progress' ? 'warning' : s === 'resolved' ? 'success' : 'muted';
}

const EMPTY_FORM = { service_id: '', severity: 'medium' as IncidentSeverity, incident_type: '', resolution_status: 'open' as ResolutionStatus };

export function IncidentsPage() {
  const { items, total, isLoading, error, refetch, create, update } = useIncidents();
  const { items: infraItems } = useInfrastructure();

  const [search, setSearch] = useState('');
  const [sevFilter, setSevFilter] = useState('');
  const [resFilter, setResFilter] = useState('');
  const [createOpen, setCreateOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<IncidentItem | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');

  const infraMap = useMemo(() => new Map(infraItems.map((i) => [i.id, i.service_name])), [infraItems]);

  const filtered = items.filter((i) => {
    const matchSearch = !search || i.incident_type.toLowerCase().includes(search.toLowerCase());
    const matchSev = !sevFilter || i.severity === sevFilter;
    const matchRes = !resFilter || i.resolution_status === resFilter;
    return matchSearch && matchSev && matchRes;
  });

  const openCreate = () => {
    setForm({ ...EMPTY_FORM, service_id: infraItems[0]?.id ?? '' });
    setFormError('');
    setCreateOpen(true);
  };
  const openEdit = (item: IncidentItem) => {
    setEditTarget(item);
    setForm({ service_id: item.service_id, severity: item.severity, incident_type: item.incident_type, resolution_status: item.resolution_status });
    setFormError('');
  };
  const closeAll = () => { setCreateOpen(false); setEditTarget(null); setFormError(''); };

  const handleCreate = async () => {
    if (!form.service_id || !form.incident_type) { setFormError('Service and incident type are required'); return; }
    setSubmitting(true);
    try { await create(form as IncidentCreateRequest); closeAll(); }
    catch (err) { setFormError(getErrorMessage(err)); }
    finally { setSubmitting(false); }
  };

  const handleUpdate = async () => {
    if (!editTarget) return;
    setSubmitting(true);
    try { await update(editTarget.id, form); closeAll(); }
    catch (err) { setFormError(getErrorMessage(err)); }
    finally { setSubmitting(false); }
  };

  if (error) return <ErrorState message={error} onRetry={refetch} type="network" />;

  const openCount = items.filter(i => i.resolution_status === 'open').length;
  const criticalCount = items.filter(i => i.severity === 'critical').length;
  const inProgressCount = items.filter(i => i.resolution_status === 'in_progress').length;
  const resolvedCount = items.filter(i => i.resolution_status === 'resolved' || i.resolution_status === 'closed').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 'var(--space-3)' }}>
        {[
          { label: 'Total', value: total, color: 'var(--color-blue-400)' },
          { label: 'Open', value: openCount, color: 'var(--color-red-400)' },
          { label: 'Critical', value: criticalCount, color: 'var(--color-red-300)' },
          { label: 'In Progress', value: inProgressCount, color: 'var(--color-yellow-300)' },
          { label: 'Resolved', value: resolvedCount, color: 'var(--color-green-400)' },
        ].map((s) => (
          <div key={s.label} style={{ background: 'var(--color-bg-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: 'var(--space-4)', textAlign: 'center' }}>
            <div style={{ fontSize: 'var(--text-2xl)', fontWeight: '700', color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginTop: '4px' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Table */}
      <Card>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-4)', flexWrap: 'wrap' }}>
          <CardHeader title="Incidents" subtitle={`${filtered.length} of ${total}`} icon={<AlertTriangle size={16} />} />
          <div style={{ flex: 1 }} />
          <Input placeholder="Search type..." value={search} onChange={(e) => setSearch(e.target.value)} leftIcon={<Search size={14} />} style={{ width: '180px' }} />
          <Select options={[{ value: '', label: 'All severities' }, ...SEVERITY_OPTIONS]} value={sevFilter} onChange={(e) => setSevFilter(e.target.value)} style={{ width: '140px' }} />
          <Select options={[{ value: '', label: 'All statuses' }, ...RESOLUTION_OPTIONS]} value={resFilter} onChange={(e) => setResFilter(e.target.value)} style={{ width: '140px' }} />
          <Button variant="ghost" size="sm" onClick={refetch} leftIcon={<RefreshCw size={14} />}>Refresh</Button>
          <Button variant="primary" size="sm" onClick={openCreate} leftIcon={<Plus size={14} />} disabled={infraItems.length === 0}>New Incident</Button>
        </div>

        {isLoading ? (
          <LoadingState message="Loading incidents..." />
        ) : filtered.length === 0 ? (
          <EmptyState title="No incidents found" description={search ? 'Try adjusting filters.' : 'No incidents have been recorded yet.'} icon={<AlertTriangle size={48} />} />
        ) : (
          <Table
            data={filtered}
            keyExtractor={(r) => r.id}
            columns={[
              {
                key: 'type', header: 'Incident Type', width: '25%',
                render: (r) => <span style={{ color: 'var(--color-text-primary)', fontWeight: '500' }}>{r.incident_type}</span>,
              },
              {
                key: 'service', header: 'Service', width: '20%',
                render: (r) => <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>{infraMap.get(r.service_id) ?? r.service_id.slice(0, 8) + '...'}</span>,
              },
              {
                key: 'severity', header: 'Severity', width: '12%',
                render: (r) => <Badge variant={sevVariant(r.severity)} dot>{r.severity}</Badge>,
              },
              {
                key: 'resolution', header: 'Status', width: '15%',
                render: (r) => <Badge variant={resVariant(r.resolution_status)}>{r.resolution_status.replace('_', ' ')}</Badge>,
              },
              {
                key: 'timestamp', header: 'Occurred', width: '15%',
                render: (r) => <span style={{ fontSize: 'var(--text-xs)' }}>{formatRelativeTime(r.timestamp)}</span>,
              },
              {
                key: 'actions', header: '', width: '8%',
                render: (r) => (
                  <Button variant="ghost" size="sm" onClick={() => openEdit(r)} style={{ padding: '6px' }} title="Edit incident">
                    <Edit2 size={14} />
                  </Button>
                ),
              },
            ]}
          />
        )}
      </Card>

      {/* Create modal */}
      <Modal isOpen={createOpen} onClose={closeAll} title="Create Incident" size="md"
        footer={<>
          <Button variant="secondary" onClick={closeAll}>Cancel</Button>
          <Button variant="primary" onClick={handleCreate} isLoading={submitting}>Create</Button>
        </>}
      >
        <IncidentForm form={form} onChange={setForm} infraItems={infraItems} error={formError} />
      </Modal>

      {/* Edit modal */}
      <Modal isOpen={!!editTarget} onClose={closeAll} title="Update Incident" size="md"
        footer={<>
          <Button variant="secondary" onClick={closeAll}>Cancel</Button>
          <Button variant="primary" onClick={handleUpdate} isLoading={submitting}>Save</Button>
        </>}
      >
        <IncidentForm form={form} onChange={setForm} infraItems={infraItems} error={formError} />
      </Modal>
    </div>
  );
}

type IFormState = { service_id: string; severity: IncidentSeverity; incident_type: string; resolution_status: ResolutionStatus };

function IncidentForm({ form, onChange, infraItems, error }: {
  form: IFormState;
  onChange: (f: IFormState) => void;
  infraItems: { id: string; service_name: string }[];
  error: string;
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      <Select
        label="Service"
        options={infraItems.map((i) => ({ value: i.id, label: i.service_name }))}
        value={form.service_id}
        onChange={(e) => onChange({ ...form, service_id: e.target.value })}
      />
      <Input
        label="Incident Type"
        placeholder="e.g. CPU spike, OOM, Timeout"
        value={form.incident_type}
        onChange={(e) => onChange({ ...form, incident_type: e.target.value })}
        required
      />
      <Select
        label="Severity"
        options={SEVERITY_OPTIONS}
        value={form.severity}
        onChange={(e) => onChange({ ...form, severity: e.target.value as IncidentSeverity })}
      />
      <Select
        label="Resolution Status"
        options={RESOLUTION_OPTIONS}
        value={form.resolution_status}
        onChange={(e) => onChange({ ...form, resolution_status: e.target.value as ResolutionStatus })}
      />
      {error && <p style={{ color: 'var(--color-error)', fontSize: 'var(--text-sm)' }}>{error}</p>}
    </div>
  );
}
