import { Navigate } from 'react-router-dom';

function getAuth() {
  return {
    role: localStorage.getItem('role'),
  };
}

function getDashboard(role) {
  return role === 'doctor' ? '/DoctorsAppointments' : '/ManageAppointment';
}

export function ProtectedRoute({ children, allowedRole }) {
  const { role } = getAuth();

  if (!role) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRole && role !== allowedRole) {
    return <Navigate to={getDashboard(role)} replace />;
  }

  return children;
}

export function PublicRoute({ children }) {
  const { role } = getAuth();

  if (role) {
    return <Navigate to={getDashboard(role)} replace />;
  }

  return children;
}
