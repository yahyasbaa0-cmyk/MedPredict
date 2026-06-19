import React from 'react';
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

function App() {
  return (
    <>
      <ToastProvider />
      <BrowserRouter>
        <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/book" element={<PublicBooking />} />
        
        {/* Protected routes */}
        <Route element={<ProtectedRoute />}>
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
            
          </Route>
        </Route>
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
    </>
  );
}

export default App;
