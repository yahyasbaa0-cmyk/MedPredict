import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import useAuthStore from '../store/useAuthStore';

// Assuming we will build Sidebar and Topbar later
// import Sidebar from './Sidebar';
// import Topbar from './Topbar';

export const ProtectedRoute = ({ allowedRoles }) => {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  const user = useAuthStore(state => state.user);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    if (user?.role === 'PATIENT') {
      return <Navigate to="/my-appointments" replace />;
    }
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};
