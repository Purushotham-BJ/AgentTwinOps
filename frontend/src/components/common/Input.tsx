import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export function Input({ label, error, hint, leftIcon, rightIcon, style, id, ...props }: InputProps) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
      {label && (
        <label
          htmlFor={inputId}
          style={{
            fontSize: 'var(--text-sm)',
            fontWeight: 'var(--font-medium)',
            color: 'var(--color-text-secondary)',
          }}
        >
          {label}
        </label>
      )}
      <div style={{ position: 'relative' }}>
        {leftIcon && (
          <span style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)', pointerEvents: 'none', display: 'flex' }}>
            {leftIcon}
          </span>
        )}
        <input
          id={inputId}
          style={{
            width: '100%',
            height: '38px',
            padding: `0 ${rightIcon ? '40px' : '12px'} 0 ${leftIcon ? '40px' : '12px'}`,
            background: 'var(--color-bg-elevated)',
            border: `1px solid ${error ? 'var(--color-error)' : 'var(--color-border)'}`,
            borderRadius: 'var(--radius-md)',
            color: 'var(--color-text-primary)',
            fontSize: 'var(--text-sm)',
            fontFamily: 'var(--font-sans)',
            outline: 'none',
            transition: 'border-color var(--transition-fast)',
            ...style,
          }}
          onFocus={(e) => { e.currentTarget.style.borderColor = error ? 'var(--color-error)' : 'var(--color-primary)'; }}
          onBlur={(e) => { e.currentTarget.style.borderColor = error ? 'var(--color-error)' : 'var(--color-border)'; }}
          {...props}
        />
        {rightIcon && (
          <span style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)', display: 'flex' }}>
            {rightIcon}
          </span>
        )}
      </div>
      {error && <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-error)' }}>{error}</span>}
      {hint && !error && <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>{hint}</span>}
    </div>
  );
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: { value: string; label: string }[];
}

export function Select({ label, error, options, style, id, ...props }: SelectProps) {
  const selectId = id || label?.toLowerCase().replace(/\s+/g, '-');
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
      {label && (
        <label htmlFor={selectId} style={{ fontSize: 'var(--text-sm)', fontWeight: 'var(--font-medium)', color: 'var(--color-text-secondary)' }}>
          {label}
        </label>
      )}
      <select
        id={selectId}
        style={{
          width: '100%',
          height: '38px',
          padding: '0 12px',
          background: 'var(--color-bg-elevated)',
          border: `1px solid ${error ? 'var(--color-error)' : 'var(--color-border)'}`,
          borderRadius: 'var(--radius-md)',
          color: 'var(--color-text-primary)',
          fontSize: 'var(--text-sm)',
          fontFamily: 'var(--font-sans)',
          outline: 'none',
          cursor: 'pointer',
          ...style,
        }}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value} style={{ background: 'var(--color-bg-elevated)' }}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-error)' }}>{error}</span>}
    </div>
  );
}
