import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { Button } from './Button';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  footer?: React.ReactNode;
}

const SIZE_WIDTHS = { sm: '420px', md: '560px', lg: '720px' };

export function Modal({ isOpen, onClose, title, children, size = 'md', footer }: ModalProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    if (isOpen) document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed', inset: 0,
        background: 'rgba(0,0,0,0.7)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 'var(--z-modal)',
        padding: '16px',
        backdropFilter: 'blur(4px)',
      }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        className="animate-fade-in"
        style={{
          background: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-xl)',
          width: '100%',
          maxWidth: SIZE_WIDTHS[size],
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: 'var(--shadow-xl)',
        }}
      >
        {/* Header */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: 'var(--space-5) var(--space-6)',
          borderBottom: '1px solid var(--color-border)',
          flexShrink: 0,
        }}>
          <h2 style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--font-semibold)', margin: 0 }}>{title}</h2>
          <Button variant="ghost" size="sm" onClick={onClose} style={{ padding: '6px', height: 'auto' }}>
            <X size={18} />
          </Button>
        </div>

        {/* Body */}
        <div style={{ padding: 'var(--space-6)', overflowY: 'auto', flex: 1 }}>
          {children}
        </div>

        {/* Footer */}
        {footer && (
          <div style={{
            padding: 'var(--space-4) var(--space-6)',
            borderTop: '1px solid var(--color-border)',
            display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)',
            flexShrink: 0,
          }}>
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
