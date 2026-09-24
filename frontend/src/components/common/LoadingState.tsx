import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function LoadingState({ message = 'Loading...', size = 'md' }: LoadingStateProps) {
  const iconSize = size === 'sm' ? 20 : size === 'lg' ? 40 : 28;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 'var(--space-12)', gap: 'var(--space-4)' }}>
      <Loader2 size={iconSize} style={{ color: 'var(--color-primary)', animation: 'spin 1s linear infinite' }} />
      <p style={{ color: 'var(--color-text-muted)', fontSize: size === 'sm' ? 'var(--text-xs)' : 'var(--text-sm)' }}>{message}</p>
    </div>
  );
}

interface SkeletonProps {
  width?: string;
  height?: string;
  style?: React.CSSProperties;
}

export function Skeleton({ width = '100%', height = '16px', style }: SkeletonProps) {
  return (
    <div
      style={{
        width, height,
        background: 'linear-gradient(90deg, var(--color-bg-elevated) 25%, var(--color-bg-hover) 50%, var(--color-bg-elevated) 75%)',
        backgroundSize: '400% 100%',
        animation: 'shimmer 1.5s ease-in-out infinite',
        borderRadius: 'var(--radius-sm)',
        ...style,
      }}
    />
  );
}
