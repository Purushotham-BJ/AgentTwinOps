import React from 'react';
import { AlertTriangle, RefreshCw, WifiOff, Lock, Search } from 'lucide-react';
import { Button } from './Button';

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
  type?: 'network' | 'auth' | 'notfound' | 'generic';
}

export function ErrorState({ message, onRetry, type = 'generic' }: ErrorStateProps) {
  const Icon = type === 'network' ? WifiOff : type === 'auth' ? Lock : type === 'notfound' ? Search : AlertTriangle;
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      padding: 'var(--space-12)', gap: 'var(--space-4)', textAlign: 'center',
    }}>
      <div style={{
        width: '56px', height: '56px', borderRadius: '50%',
        background: 'rgba(248,81,73,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <Icon size={28} style={{ color: 'var(--color-error)' }} />
      </div>
      <div>
        <h4 style={{ color: 'var(--color-text-primary)', marginBottom: '4px' }}>
          {type === 'network' ? 'Connection Error' :
           type === 'auth' ? 'Access Denied' :
           type === 'notfound' ? 'Not Found' : 'Something went wrong'}
        </h4>
        <p style={{ color: 'var(--color-text-muted)', fontSize: 'var(--text-sm)', maxWidth: '360px' }}>{message}</p>
      </div>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry} leftIcon={<RefreshCw size={14} />}>
          Try again
        </Button>
      )}
    </div>
  );
}

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export function EmptyState({ title, description, icon, action }: EmptyStateProps) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      padding: 'var(--space-12)', gap: 'var(--space-4)', textAlign: 'center',
    }}>
      {icon && (
        <div style={{ color: 'var(--color-text-muted)', opacity: 0.5 }}>
          {icon}
        </div>
      )}
      <div>
        <h4 style={{ color: 'var(--color-text-secondary)', marginBottom: '6px' }}>{title}</h4>
        {description && <p style={{ color: 'var(--color-text-muted)', fontSize: 'var(--text-sm)', maxWidth: '360px' }}>{description}</p>}
      </div>
      {action}
    </div>
  );
}
