import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';

export function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handler = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (!mobile) setMobileOpen(false);
    };
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, []);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--color-bg-base)' }}>
      {/* Desktop sidebar */}
      {!isMobile && <Sidebar />}

      {/* Mobile sidebar (overlay) */}
      {isMobile && (
        <Sidebar mobileOpen={mobileOpen} onMobileClose={() => setMobileOpen(false)} />
      )}

      {/* Main area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, overflow: 'hidden' }}>
        <TopNav onMenuClick={() => setMobileOpen(true)} />
        <main
          className="page-enter"
          style={{
            flex: 1,
            padding: 'var(--space-6)',
            overflowY: 'auto',
            overflowX: 'hidden',
          }}
        >
          <div style={{ maxWidth: 'var(--content-max-width)', margin: '0 auto' }}>
            <Outlet />
          </div>
        </main>
      </div>

      {/* Mobile CSS overrides */}
      <style>{`
        @media (max-width: 767px) {
          .mobile-menu-btn { display: flex !important; }
        }
      `}</style>
    </div>
  );
}
