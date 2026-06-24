import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './components/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Patients from './pages/Patients';
import Consultations from './pages/Consultations';

import Appointments from './pages/Appointments';
import Prescriptions from './pages/Prescriptions';
import ToastProvider from './components/ToastProvider';
import PublicBooking from './pages/PublicBooking';
import PatientPortal from './pages/PatientPortal';
import AdminPanel from './pages/AdminPanel';
import { useThemeStore } from './store/useThemeStore';

function App() {
  const initTheme = useThemeStore(state => state.initTheme);

  useEffect(() => {
    // Initialize theme from localStorage on app load
    initTheme();
  }, [initTheme]);

  return (
    <>
      <ToastProvider />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/book" element={<PublicBooking />} />
          
          {/* Protected staff routes */}
          <Route element={<ProtectedRoute allowedRoles={['ADMIN', 'DOCTOR', 'SECRETARY']} />}>
            <Route element={<Layout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/patients" element={<Patients />} />
              <Route path="/appointments" element={<Appointments />} />
              
              {/* Doctor and Admin */}
              <Route element={<ProtectedRoute allowedRoles={['DOCTOR', 'ADMIN']} />}>
                 <Route path="/consultations" element={<Consultations />} />
              </Route>

              {/* Doctor, Secretary, and Admin */}
              <Route element={<ProtectedRoute allowedRoles={['DOCTOR', 'SECRETARY', 'ADMIN']} />}>
                 <Route path="/prescriptions" element={<Prescriptions />} />
              </Route>

              {/* Admin only */}
              <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
                 <Route path="/admin-panel" element={<AdminPanel />} />
              </Route>
            </Route>
          </Route>

          {/* Protected patient routes */}
          <Route element={<ProtectedRoute allowedRoles={['PATIENT']} />}>
            <Route path="/my-appointments" element={<PatientPortal />} />
          </Route>
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
