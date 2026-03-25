import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { LanguageProvider } from './LanguageContext';
import { ToastProvider } from './components/ToastContext';
import Navbar from './components/Navbar';
import LangToggle from './components/LangToggle';
import { ProtectedRoute, PublicRoute } from './components/ProtectedRoute';
import LandingPage from './LandingPage';
import Register from './register';
import Login from './login';
import ManageAppointment from './manageAppointment';
import AddAppointment from './AddAppointment';
import ShowAppointment from './ShowAppointment';
import UpdateAppointment from './UpdateAppointment';
import DoctorsAppointments from './DoctorsAppointments';
import DoctorAvailability from './DoctorAvailability';
import Account from './Account';

function App() {
  return (
    <LanguageProvider>
      <ToastProvider>
      <Router>
        <Navbar />
        <LangToggle />
        <Routes>
          <Route path="/" element={<Navigate replace to="/LandingPage" />} />
          <Route path="/LandingPage" element={<PublicRoute><LandingPage /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/ManageAppointment" element={<ProtectedRoute allowedRole="client"><ManageAppointment /></ProtectedRoute>} />
          <Route path="/AddAppointment" element={<ProtectedRoute allowedRole="client"><AddAppointment /></ProtectedRoute>} />
          <Route path="/ShowAppointment" element={<ProtectedRoute allowedRole="client"><ShowAppointment /></ProtectedRoute>} />
          <Route path="/UpdateAppointment/:appointmentId" element={<ProtectedRoute allowedRole="client"><UpdateAppointment /></ProtectedRoute>} />
          <Route path="/DoctorsAppointments" element={<ProtectedRoute allowedRole="doctor"><DoctorsAppointments /></ProtectedRoute>} />
          <Route path="/DoctorAvailability" element={<ProtectedRoute allowedRole="doctor"><DoctorAvailability /></ProtectedRoute>} />
          <Route path="/Account" element={<ProtectedRoute><Account /></ProtectedRoute>} />
        </Routes>
      </Router>
      </ToastProvider>
    </LanguageProvider>
  );
}

export default App;
