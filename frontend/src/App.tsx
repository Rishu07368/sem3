import { Routes, Route } from 'react-router-dom';
import Layout from '@/components/common/Layout';
import DashboardPage from '@/pages/Dashboard';
import CalendarPage from '@/pages/Calendar';
import ADSAPage from '@/pages/ADSA';
import DBMSPage from '@/pages/DBMS';
import COAPage from '@/pages/COA';
import ProbabilityPage from '@/pages/Probability';
import AMCUTPage from '@/pages/AMCAT';
import AnalyticsPage from '@/pages/Analytics';
import SettingsPage from '@/pages/Settings';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
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
