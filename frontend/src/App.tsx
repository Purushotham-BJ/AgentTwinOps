import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { AppLayout } from '@/components/layout/AppLayout';
import { LoginPage } from '@/pages/LoginPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { InfrastructurePage } from '@/pages/InfrastructurePage';
import { IncidentsPage } from '@/pages/IncidentsPage';
import { DigitalTwinPage } from '@/pages/DigitalTwinPage';
import { PredictionPage } from '@/pages/PredictionPage';
import { SimulationPage } from '@/pages/SimulationPage';
import { RecommendationsPage } from '@/pages/RecommendationsPage';
import { ReportsPage } from '@/pages/ReportsPage';
import { SettingsPage } from '@/pages/SettingsPage';
import { MetricsPage } from '@/pages/MetricsPage';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected application */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard"       element={<DashboardPage />} />
            <Route path="infrastructure"  element={<InfrastructurePage />} />
            <Route path="incidents"       element={<IncidentsPage />} />
            <Route path="digital-twin"    element={<DigitalTwinPage />} />
            <Route path="prediction"      element={<PredictionPage />} />
            <Route path="simulation"      element={<SimulationPage />} />
            <Route path="recommendations" element={<RecommendationsPage />} />
            <Route path="metrics"         element={<MetricsPage />} />
            <Route path="reports"         element={<ReportsPage />} />
            <Route path="settings"        element={<SettingsPage />} />

            {/* 404 fallback */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
