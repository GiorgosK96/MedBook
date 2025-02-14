import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
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
    <Router>
      <Routes>
        {/* Default Route: Redirect to LandingPage */}
        <Route path="/" element={<Navigate replace to="/LandingPage" />} />

        {/* Landing Page */}
        <Route path="/LandingPage" element={<LandingPage />} />

        {/* Registration Page */}
        <Route path="/register" element={<Register />} />

        {/* Login Page */}
        <Route path="/login" element={<Login />} />

        {/* Manage Appointments */}
        <Route path="/ManageAppointment" element={<ManageAppointment />} />

        {/* Add Appointment */}
        <Route path="/AddAppointment" element={<AddAppointment />} />

        {/* Show Appointment */}
        <Route path="/ShowAppointment" element={<ShowAppointment />} />

        {/* Update Appointment */}
        <Route path="/UpdateAppointment/:appointmentId" element={<UpdateAppointment />} />

        {/* Doctors Appointment */}
        <Route path="/DoctorsAppointments" element={<DoctorsAppointments />} />

        {/*Account*/}
        <Route path="/Account" element={<Account/>} />

      </Routes>
    </Router>
  );
}

export default App;
