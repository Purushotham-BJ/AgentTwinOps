import React from 'react';
import { Loader2 } from 'lucide-react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const BASE: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: '8px',
  fontFamily: 'var(--font-sans)',
  fontWeight: '500',
  borderRadius: 'var(--radius-md)',
  border: '1px solid transparent',
  cursor: 'pointer',
  transition: 'all var(--transition-fast)',
  whiteSpace: 'nowrap',
  userSelect: 'none',
  textDecoration: 'none',
};

const VARIANTS: Record<ButtonVariant, React.CSSProperties> = {
  primary:   { background: 'var(--color-blue-500)',  color: '#fff', borderColor: 'var(--color-blue-600)' },
  secondary: { background: 'var(--color-bg-elevated)', color: 'var(--color-text-primary)', borderColor: 'var(--color-border)' },
  ghost:     { background: 'transparent', color: 'var(--color-text-secondary)', borderColor: 'transparent' },
  danger:    { background: 'rgba(248,81,73,0.12)', color: 'var(--color-red-300)', borderColor: 'rgba(248,81,73,0.3)' },
  outline:   { background: 'transparent', color: 'var(--color-primary)', borderColor: 'var(--color-primary)' },
};

const SIZES: Record<ButtonSize, React.CSSProperties> = {
  sm: { fontSize: '0.8125rem', padding: '6px 12px', height: '32px' },
  md: { fontSize: '0.875rem',  padding: '8px 16px', height: '38px' },
  lg: { fontSize: '1rem',      padding: '10px 20px', height: '44px' },
};

export function Button({
  children,
  variant = 'secondary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  disabled,
  style,
  ...props
}: ButtonProps) {
  const isDisabled = disabled || isLoading;

  return (
    <button
      disabled={isDisabled}
      style={{
        ...BASE,
        ...VARIANTS[variant],
        ...SIZES[size],
        ...(isDisabled ? { opacity: 0.5, cursor: 'not-allowed' } : {}),
        ...style,
      }}
      onMouseEnter={(e) => {
        if (!isDisabled) {
          const el = e.currentTarget;
          if (variant === 'primary') el.style.background = 'var(--color-blue-400)';
          else if (variant === 'secondary') el.style.background = 'var(--color-bg-hover)';
          else if (variant === 'ghost') { el.style.background = 'var(--color-bg-elevated)'; el.style.color = 'var(--color-text-primary)'; }
          else if (variant === 'danger') el.style.background = 'rgba(248,81,73,0.2)';
          else if (variant === 'outline') el.style.background = 'rgba(56,139,253,0.1)';
        }
      }}
      onMouseLeave={(e) => {
        if (!isDisabled) {
          const el = e.currentTarget;
          Object.assign(el.style, VARIANTS[variant]);
        }
      }}
      {...props}
    >
      {isLoading ? (
        <Loader2 size={size === 'sm' ? 14 : 16} className="animate-spin" />
      ) : leftIcon}
      {children}
      {!isLoading && rightIcon}
    </button>
  );
}
