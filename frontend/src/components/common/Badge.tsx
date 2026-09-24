import React from 'react';

type BadgeVariant = 'default' | 'success' | 'warning' | 'error' | 'info' | 'muted';
type BadgeSize = 'sm' | 'md';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: BadgeSize;
  style?: React.CSSProperties;
  dot?: boolean;
}

const VARIANT_STYLES: Record<BadgeVariant, React.CSSProperties> = {
  default: { color: 'var(--color-blue-300)',   background: 'rgba(56,139,253,0.12)',  border: '1px solid rgba(56,139,253,0.25)' },
  success: { color: 'var(--color-green-300)',  background: 'rgba(63,185,80,0.12)',   border: '1px solid rgba(63,185,80,0.25)' },
  warning: { color: 'var(--color-orange-300)', background: 'rgba(255,166,87,0.12)',  border: '1px solid rgba(255,166,87,0.25)' },
  error:   { color: 'var(--color-red-300)',    background: 'rgba(248,81,73,0.12)',   border: '1px solid rgba(248,81,73,0.25)' },
  info:    { color: 'var(--color-cyan-300)',   background: 'rgba(57,213,255,0.1)',   border: '1px solid rgba(57,213,255,0.2)' },
  muted:   { color: 'var(--color-text-muted)', background: 'rgba(110,118,129,0.1)', border: '1px solid rgba(110,118,129,0.2)' },
};

const SIZE_STYLES: Record<BadgeSize, React.CSSProperties> = {
  sm: { fontSize: '0.65rem', padding: '2px 6px', lineHeight: '1.4' },
  md: { fontSize: '0.75rem', padding: '3px 8px', lineHeight: '1.4' },
};

export function Badge({ children, variant = 'default', size = 'sm', style, dot }: BadgeProps) {
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        borderRadius: 'var(--radius-full)',
        fontWeight: 'var(--font-medium)',
        fontFamily: 'var(--font-sans)',
        whiteSpace: 'nowrap',
        ...VARIANT_STYLES[variant],
        ...SIZE_STYLES[size],
        ...style,
      }}
    >
      {dot && (
        <span
          style={{
            width: 6,
            height: 6,
            borderRadius: '50%',
            backgroundColor: 'currentColor',
            flexShrink: 0,
          }}
        />
      )}
      {children}
    </span>
  );
}
