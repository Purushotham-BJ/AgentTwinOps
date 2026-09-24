import React from 'react';

interface ProgressBarProps {
  value: number; // 0-100
  color?: string;
  height?: number;
  showLabel?: boolean;
  label?: string;
  animated?: boolean;
  style?: React.CSSProperties;
}

function getAutoColor(value: number): string {
  if (value >= 90) return 'var(--color-red-400)';
  if (value >= 75) return 'var(--color-orange-300)';
  if (value >= 60) return 'var(--color-yellow-300)';
  return 'var(--color-green-400)';
}

export function ProgressBar({ value, color, height = 6, showLabel, label, animated, style }: ProgressBarProps) {
  const pct = Math.max(0, Math.min(100, value));
  const barColor = color || getAutoColor(pct);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', ...style }}>
      {(showLabel || label) && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {label && <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>{label}</span>}
          {showLabel && <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', fontWeight: '500' }}>{pct.toFixed(1)}%</span>}
        </div>
      )}
      <div style={{
        height: `${height}px`,
        background: 'var(--color-bg-overlay)',
        borderRadius: 'var(--radius-full)',
        overflow: 'hidden',
      }}>
        <div
          style={{
            height: '100%',
            width: `${pct}%`,
            background: barColor,
            borderRadius: 'var(--radius-full)',
            transition: animated ? 'width 0.6s ease' : 'none',
          }}
        />
      </div>
    </div>
  );
}
