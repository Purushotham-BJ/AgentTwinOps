import React from 'react';
import type { LucideIcon } from 'lucide-react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  iconColor?: string;
  iconBg?: string;
  trend?: number; // positive = up, negative = down
  trendLabel?: string;
  alert?: boolean;
}

export function StatCard({
  title, value, subtitle, icon: Icon, iconColor, iconBg, trend, trendLabel, alert,
}: StatCardProps) {
  const TrendIcon = trend === undefined ? null : trend > 0 ? TrendingUp : trend < 0 ? TrendingDown : Minus;
  const trendColor = trend === undefined ? undefined : trend > 0 ? 'var(--color-green-400)' : trend < 0 ? 'var(--color-red-400)' : 'var(--color-text-muted)';

  return (
    <div
      style={{
        background: 'var(--color-bg-surface)',
        border: `1px solid ${alert ? 'rgba(248,81,73,0.3)' : 'var(--color-border)'}`,
        borderRadius: 'var(--radius-lg)',
        padding: 'var(--space-5)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-3)',
        transition: 'border-color var(--transition-fast)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)', fontWeight: '500' }}>
          {title}
        </span>
        <div style={{
          width: '36px', height: '36px', borderRadius: 'var(--radius-md)',
          background: iconBg || 'rgba(56,139,253,0.1)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        }}>
          <Icon size={18} style={{ color: iconColor || 'var(--color-primary)' }} />
        </div>
      </div>
      <div>
        <div style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--font-bold)', color: alert ? 'var(--color-error)' : 'var(--color-text-primary)', lineHeight: 1.2 }}>
          {value}
        </div>
        {subtitle && (
          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginTop: '4px' }}>{subtitle}</p>
        )}
      </div>
      {TrendIcon && trendLabel && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <TrendIcon size={14} style={{ color: trendColor }} />
          <span style={{ fontSize: 'var(--text-xs)', color: trendColor }}>{trendLabel}</span>
        </div>
      )}
    </div>
  );
}
