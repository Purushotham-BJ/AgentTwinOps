import React from 'react';

interface CardProps {
  children: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
  onClick?: () => void;
}

const PADDING = {
  none: '0',
  sm:   'var(--space-4)',
  md:   'var(--space-6)',
  lg:   'var(--space-8)',
};

export function Card({ children, style, className, padding = 'md', hover, onClick }: CardProps) {
  return (
    <div
      className={className}
      onClick={onClick}
      style={{
        background: 'var(--color-bg-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        padding: PADDING[padding],
        transition: 'border-color var(--transition-fast), box-shadow var(--transition-fast)',
        ...(hover || onClick ? { cursor: onClick ? 'pointer' : undefined } : {}),
        ...style,
      }}
      onMouseEnter={(e) => {
        if (hover || onClick) {
          const el = e.currentTarget;
          el.style.borderColor = 'var(--color-border-muted)';
          el.style.boxShadow = 'var(--shadow-md)';
        }
      }}
      onMouseLeave={(e) => {
        if (hover || onClick) {
          const el = e.currentTarget;
          el.style.borderColor = 'var(--color-border)';
          el.style.boxShadow = 'none';
        }
      }}
    >
      {children}
    </div>
  );
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
}

export function CardHeader({ title, subtitle, action, icon }: CardHeaderProps) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 'var(--space-4)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
        {icon && (
          <div style={{ color: 'var(--color-primary)', flexShrink: 0 }}>
            {icon}
          </div>
        )}
        <div>
          <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 'var(--font-semibold)', color: 'var(--color-text-primary)', margin: 0 }}>
            {title}
          </h3>
          {subtitle && (
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginTop: '2px' }}>
              {subtitle}
            </p>
          )}
        </div>
      </div>
      {action && <div style={{ flexShrink: 0 }}>{action}</div>}
    </div>
  );
}
