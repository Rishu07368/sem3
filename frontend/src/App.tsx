import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import Layout from '@/components/common/Layout';
import LoginPage from '@/pages/Login';
import DashboardPage from '@/pages/Dashboard';
import CalendarPage from '@/pages/Calendar';
import ADSAPage from '@/pages/ADSA';
import DBMSPage from '@/pages/DBMS';
import COAPage from '@/pages/COA';
import ProbabilityPage from '@/pages/Probability';
import AMCUTPage from '@/pages/AMCAT';
import AnalyticsPage from '@/pages/Analytics';
import SettingsPage from '@/pages/Settings';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="calendar" element={<CalendarPage />} />
        <Route path="subjects/adsa" element={<ADSAPage />} />
        <Route path="subjects/dbms" element={<DBMSPage />} />
        <Route path="subjects/coa" element={<COAPage />} />
        <Route path="subjects/probability" element={<ProbabilityPage />} />
        <Route path="amcat" element={<AMCUTPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
