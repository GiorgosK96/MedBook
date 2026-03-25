import { Navigate } from 'react-router-dom';

function getAuth() {
  return {
    token: localStorage.getItem('token'),
    role: localStorage.getItem('role'),
  };
}

function getDashboard(role) {
  return role === 'doctor' ? '/DoctorsAppointments' : '/ManageAppointment';
}

export function ProtectedRoute({ children, allowedRole }) {
  const { token, role } = getAuth();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRole && role !== allowedRole) {
    return <Navigate to={getDashboard(role)} replace />;
  }

  return children;
}

export function PublicRoute({ children }) {
  const { token, role } = getAuth();

  if (token) {
    return <Navigate to={getDashboard(role)} replace />;
  }

  return children;
}
