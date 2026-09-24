import React, { useState } from 'react';
import { Plus, Search, Server, RefreshCw, Trash2, Edit2, Globe } from 'lucide-react';
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
import type { InfrastructureItem, InfrastructureStatus, InfrastructureCreateRequest } from '@/types';

const STATUS_OPTIONS = [
  { value: 'active', label: 'Active' },
  { value: 'healthy', label: 'Healthy' },
  { value: 'degraded', label: 'Degraded' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'unhealthy', label: 'Unhealthy' },
];

function statusVariant(s: InfrastructureStatus) {
  return s === 'healthy' ? 'success' : s === 'active' ? 'default' : s === 'degraded' ? 'warning' : s === 'unhealthy' ? 'error' : 'muted';
}

const EMPTY_FORM = { service_name: '', service_type: '', host: '', status: 'active' as InfrastructureStatus };

export function InfrastructurePage() {
  const { items, total, isLoading, error, refetch, create, update, remove } = useInfrastructure();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [createOpen, setCreateOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<InfrastructureItem | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<InfrastructureItem | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');

  const filtered = items.filter((i) => {
    const matchSearch = !search || i.service_name.toLowerCase().includes(search.toLowerCase()) || i.service_type.toLowerCase().includes(search.toLowerCase()) || i.host.toLowerCase().includes(search.toLowerCase());
    const matchStatus = !statusFilter || i.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const openCreate = () => { setForm(EMPTY_FORM); setFormError(''); setCreateOpen(true); };
  const openEdit = (item: InfrastructureItem) => { setEditTarget(item); setForm({ service_name: item.service_name, service_type: item.service_type, host: item.host, status: item.status }); setFormError(''); };
  const closeAll = () => { setCreateOpen(false); setEditTarget(null); setDeleteTarget(null); setFormError(''); };

  const handleSubmitCreate = async () => {
    if (!form.service_name || !form.service_type || !form.host) { setFormError('All fields are required'); return; }
    setSubmitting(true);
    try {
      await create(form as InfrastructureCreateRequest);
      closeAll();
    } catch (err) { setFormError(getErrorMessage(err)); }
    finally { setSubmitting(false); }
  };

  const handleSubmitEdit = async () => {
    if (!editTarget) return;
    setSubmitting(true);
    try {
      await update(editTarget.id, form);
      closeAll();
    } catch (err) { setFormError(getErrorMessage(err)); }
    finally { setSubmitting(false); }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setSubmitting(true);
    try {
      await remove(deleteTarget.id);
      closeAll();
    } catch (err) { setFormError(getErrorMessage(err)); }
    finally { setSubmitting(false); }
  };

  if (error) return <ErrorState message={error} onRetry={refetch} type="network" />;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>

      {/* Stats row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 'var(--space-3)' }}>
        {[
          { label: 'Total', value: total, color: 'var(--color-blue-400)' },
          { label: 'Healthy/Active', value: items.filter(i => i.status === 'healthy' || i.status === 'active').length, color: 'var(--color-green-400)' },
          { label: 'Degraded', value: items.filter(i => i.status === 'degraded').length, color: 'var(--color-orange-300)' },
          { label: 'Unhealthy', value: items.filter(i => i.status === 'unhealthy').length, color: 'var(--color-red-400)' },
          { label: 'Inactive', value: items.filter(i => i.status === 'inactive').length, color: 'var(--color-text-muted)' },
        ].map((s) => (
          <div key={s.label} style={{ background: 'var(--color-bg-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: 'var(--space-4)', textAlign: 'center' }}>
            <div style={{ fontSize: 'var(--text-2xl)', fontWeight: '700', color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginTop: '4px' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Main table card */}
      <Card>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-4)', flexWrap: 'wrap' }}>
          <CardHeader title="Services" subtitle={`${filtered.length} of ${total} services`} icon={<Server size={16} />} />
          <div style={{ flex: 1 }} />
          <div style={{ display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap', alignItems: 'center' }}>
            <Input
              placeholder="Search services..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              leftIcon={<Search size={14} />}
              style={{ width: '220px' }}
            />
            <Select
              options={[{ value: '', label: 'All statuses' }, ...STATUS_OPTIONS]}
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{ width: '150px' }}
            />
            <Button variant="ghost" size="sm" onClick={refetch} leftIcon={<RefreshCw size={14} />}>Refresh</Button>
            <Button variant="primary" size="sm" onClick={openCreate} leftIcon={<Plus size={14} />}>Add Service</Button>
          </div>
        </div>

        {isLoading ? (
          <LoadingState message="Loading infrastructure..." />
        ) : filtered.length === 0 ? (
          <EmptyState title="No services found" description={search ? 'Try adjusting your search or filters.' : 'Add your first infrastructure service to get started.'} icon={<Server size={48} />} action={<Button variant="primary" size="sm" onClick={openCreate} leftIcon={<Plus size={14} />}>Add Service</Button>} />
        ) : (
          <Table
            data={filtered}
            keyExtractor={(r) => r.id}
            columns={[
              {
                key: 'name', header: 'Service', width: '25%',
                render: (r) => (
                  <div>
                    <div style={{ fontWeight: '500', color: 'var(--color-text-primary)' }}>{r.service_name}</div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>{r.service_type}</div>
                  </div>
                ),
              },
              {
                key: 'host', header: 'Host', width: '20%',
                render: (r) => (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
                    <Globe size={12} />{r.host}
                  </span>
                ),
              },
              {
                key: 'status', header: 'Status', width: '15%',
                render: (r) => <Badge variant={statusVariant(r.status)} dot>{r.status}</Badge>,
              },
              {
                key: 'updated', header: 'Last Updated', width: '15%',
                render: (r) => <span style={{ fontSize: 'var(--text-xs)' }}>{formatRelativeTime(r.updated_at)}</span>,
              },
              {
                key: 'actions', header: '', width: '10%',
                render: (r) => (
                  <div style={{ display: 'flex', gap: 'var(--space-2)', justifyContent: 'flex-end' }}>
                    <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); openEdit(r); }} style={{ padding: '6px' }} title="Edit"><Edit2 size={14} /></Button>
                    <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setDeleteTarget(r); setFormError(''); }} style={{ padding: '6px', color: 'var(--color-error)' }} title="Delete"><Trash2 size={14} /></Button>
                  </div>
                ),
              },
            ]}
          />
        )}
      </Card>

      {/* Create Modal */}
      <Modal isOpen={createOpen} onClose={closeAll} title="Add Infrastructure Service" size="md"
        footer={<>
          <Button variant="secondary" onClick={closeAll}>Cancel</Button>
          <Button variant="primary" onClick={handleSubmitCreate} isLoading={submitting}>Create Service</Button>
        </>}
      >
        <InfrastructureForm form={form} onChange={setForm} error={formError} />
      </Modal>

      {/* Edit Modal */}
      <Modal isOpen={!!editTarget} onClose={closeAll} title="Edit Service" size="md"
        footer={<>
          <Button variant="secondary" onClick={closeAll}>Cancel</Button>
          <Button variant="primary" onClick={handleSubmitEdit} isLoading={submitting}>Save Changes</Button>
        </>}
      >
        <InfrastructureForm form={form} onChange={setForm} error={formError} />
      </Modal>

      {/* Delete confirmation */}
      <Modal isOpen={!!deleteTarget} onClose={closeAll} title="Delete Service" size="sm"
        footer={<>
          <Button variant="secondary" onClick={closeAll}>Cancel</Button>
          <Button variant="danger" onClick={handleDelete} isLoading={submitting}>Delete</Button>
        </>}
      >
        <p style={{ color: 'var(--color-text-secondary)' }}>
          Are you sure you want to delete <strong style={{ color: 'var(--color-text-primary)' }}>{deleteTarget?.service_name}</strong>?
          This will fail if the service has linked incidents.
        </p>
        {formError && <p style={{ color: 'var(--color-error)', fontSize: 'var(--text-sm)', marginTop: 'var(--space-3)' }}>{formError}</p>}
      </Modal>
    </div>
  );
}

type FormState = { service_name: string; service_type: string; host: string; status: InfrastructureStatus };

function InfrastructureForm({ form, onChange, error }: { form: FormState; onChange: (f: FormState) => void; error: string }) {
  const set = (key: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    onChange({ ...form, [key]: e.target.value as InfrastructureStatus });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      <Input label="Service Name" placeholder="e.g. api-gateway" value={form.service_name} onChange={set('service_name')} required />
      <Input label="Service Type" placeholder="e.g. kubernetes, docker, vm" value={form.service_type} onChange={set('service_type')} required />
      <Input label="Host / Endpoint" placeholder="e.g. 10.0.0.1 or api.internal" value={form.host} onChange={set('host')} required />
      <Select label="Status" options={STATUS_OPTIONS} value={form.status} onChange={set('status')} />
      {error && <p style={{ color: 'var(--color-error)', fontSize: 'var(--text-sm)' }}>{error}</p>}
    </div>
  );
}
