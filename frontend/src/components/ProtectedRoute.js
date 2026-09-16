import { Navigate } from 'react-router-dom';

export function getDashboard(role) {
  return role === 'doctor' ? '/DoctorsAppointments' : '/ManageAppointment';
}

export function ProtectedRoute({ children, allowedRole }) {
  const role = localStorage.getItem('role');

  if (!role) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRole && role !== allowedRole) {
    return <Navigate to={getDashboard(role)} replace />;
  }

  return children;
}

export function PublicRoute({ children }) {
  const role = localStorage.getItem('role');

  if (role) {
    return <Navigate to={getDashboard(role)} replace />;
  }

  return children;
}
