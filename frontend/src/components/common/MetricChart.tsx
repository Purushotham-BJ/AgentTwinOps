import {
  ResponsiveContainer,
  AreaChart, Area,
  LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip,
} from 'recharts';
import type { MetricPoint } from '@/types';

interface MetricChartProps {
  data: MetricPoint[];
  color?: string;
  type?: 'area' | 'line';
  unit?: string;
  height?: number;
  showGrid?: boolean;
  showAxes?: boolean;
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CustomTooltip = ({ active, payload, label, unit }: { active?: boolean; payload?: any[]; label?: string; unit?: string }) => {
  if (!active || !payload?.length) return null;
  const val = payload[0]?.value;
  return (
    <div style={{
      background: 'var(--color-bg-elevated)', border: '1px solid var(--color-border)',
      borderRadius: 'var(--radius-md)', padding: '8px 12px', boxShadow: 'var(--shadow-lg)',
    }}>
      <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginBottom: '4px' }}>
        {label ? formatTime(label) : ''}
      </p>
      <p style={{ fontSize: 'var(--text-sm)', fontWeight: '600', color: 'var(--color-text-primary)' }}>
        {typeof val === 'number' ? val.toFixed(1) : '--'}{unit || '%'}
      </p>
    </div>
  );
};

export function MetricChart({ data, color = 'var(--color-primary)', type = 'area', unit = '%', height = 200, showGrid = true, showAxes = true }: MetricChartProps) {
  const colorClean = color.startsWith('var(') ? color : color;

  if (type === 'line') {
    return (
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-subtle)" vertical={false} />}
          {showAxes && <XAxis dataKey="timestamp" tickFormatter={formatTime} tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} />}
          {showAxes && <YAxis tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} domain={[0, 100]} />}
        <Tooltip content={(props) => <CustomTooltip active={props.active} payload={props.payload} label={props.label} unit={unit} />} />
          <Line type="monotone" dataKey="value" stroke={colorClean} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
        <defs>
          <linearGradient id={`grad-${colorClean.replace(/[^a-z0-9]/gi, '')}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={colorClean} stopOpacity={0.2} />
            <stop offset="95%" stopColor={colorClean} stopOpacity={0.01} />
          </linearGradient>
        </defs>
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-subtle)" vertical={false} />}
        {showAxes && <XAxis dataKey="timestamp" tickFormatter={formatTime} tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} />}
        {showAxes && <YAxis tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }} tickLine={false} axisLine={false} domain={[0, 100]} />}
        <Tooltip content={(props) => <CustomTooltip active={props.active} payload={props.payload} label={props.label} unit={unit} />} />
        <Area type="monotone" dataKey="value" stroke={colorClean} strokeWidth={2} fill={`url(#grad-${colorClean.replace(/[^a-z0-9]/gi, '')})`} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
