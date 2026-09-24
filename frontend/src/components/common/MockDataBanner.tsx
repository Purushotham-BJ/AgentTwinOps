import React from 'react';
import { FlaskConical } from 'lucide-react';

interface MockDataBannerProps {
  feature: string;
  apiEndpoint?: string;
}

/**
 * Clearly labels UI sections that use mock/simulated data.
 * Never pretend mock data is real.
 */
export function MockDataBanner({ feature, apiEndpoint }: MockDataBannerProps) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-2)',
      padding: '6px var(--space-3)',
      background: 'rgba(57,213,255,0.06)',
      border: '1px solid rgba(57,213,255,0.2)',
      borderRadius: 'var(--radius-md)',
      fontSize: 'var(--text-xs)',
      color: 'var(--color-cyan-300)',
    }}>
      <FlaskConical size={12} style={{ flexShrink: 0 }} />
      <span>
        <strong>SIMULATED DATA</strong> — {feature}
        {apiEndpoint && (
          <span style={{ color: 'var(--color-text-muted)', marginLeft: '4px' }}>
            (pending: {apiEndpoint})
          </span>
        )}
      </span>
    </div>
  );
}
