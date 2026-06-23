/**
 * Root application component.
 * Handles role-based routing:
 * - Not logged in → AuthScreen
 * - Logged in as Manager → ManagerDashboard
 * - Logged in as Employee → EmployeeDashboard
 */

import React from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ToastProvider } from './components/Toast';
import AuthScreen from './components/AuthScreen';
import Topbar from './components/Topbar';
import ManagerDashboard from './pages/ManagerDashboard';
import EmployeeDashboard from './pages/EmployeeDashboard';

function AppContent() {
  const { currentUser, userProfile, loading } = useAuth();

  // Show loading spinner while checking auth state
  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <div className="loading-text">Initializing…</div>
      </div>
    );
  }

  // Not logged in or not registered → show auth screen
  if (!currentUser || !userProfile) {
    return <AuthScreen />;
  }

  // Logged in — render role-appropriate dashboard
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Topbar />
      {userProfile.role === 'manager' ? <ManagerDashboard /> : <EmployeeDashboard />}
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AppContent />
      </ToastProvider>
    </AuthProvider>
  );
}// This should fail
