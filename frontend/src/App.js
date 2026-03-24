import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { LanguageProvider } from './LanguageContext';
import LangToggle from './components/LangToggle';
import LandingPage from './LandingPage';
import Register from './register';
import Login from './login';
import ManageAppointment from './manageAppointment';
import AddAppointment from './AddAppointment';
import ShowAppointment from './ShowAppointment';
import UpdateAppointment from './UpdateAppointment';
import DoctorsAppointments from './DoctorsAppointments';
import Account from './Account';

function App() {
  return (
    <LanguageProvider>
      <Router>
        <div className="h-1 bg-blue-600 w-full fixed top-0 left-0 z-50" />
        <LangToggle />
        <Routes>
          <Route path="/" element={<Navigate replace to="/LandingPage" />} />
          <Route path="/LandingPage" element={<LandingPage />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/ManageAppointment" element={<ManageAppointment />} />
          <Route path="/AddAppointment" element={<AddAppointment />} />
          <Route path="/ShowAppointment" element={<ShowAppointment />} />
          <Route path="/UpdateAppointment/:appointmentId" element={<UpdateAppointment />} />
          <Route path="/DoctorsAppointments" element={<DoctorsAppointments />} />
          <Route path="/Account" element={<Account />} />
        </Routes>
      </Router>
    </LanguageProvider>
  );
}

export default App;
