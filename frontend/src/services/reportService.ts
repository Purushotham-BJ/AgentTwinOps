import api from './api';

export type ExportableReportType = 'infrastructure' | 'incidents' | 'predictions' | 'simulations';

export async function downloadReport(type: ExportableReportType): Promise<{ blob: Blob; filename: string }> {
  const response = await api.get(`/api/v1/reports/${type}`, { responseType: 'blob' });
  const disposition = response.headers['content-disposition'] as string | undefined;
  const match = disposition?.match(/filename="([^"]+)"/i);
  return {
    blob: response.data as Blob,
    filename: match?.[1] || `agenttwinops-${type}-report.csv`,
  };
}
