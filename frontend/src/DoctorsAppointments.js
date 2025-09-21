import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './DoctorsAppointments.css';

function DoctorsAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetch('/doctorAppointments', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Failed to fetch appointments');
        }
      })
      .then(data => {
        setAppointments(data.appointments);
      })
      .catch(error => {
        console.error('Error:', error);
        setMessage('Failed to load appointments. Please try again later.');
      });
  }, []);

  const handleDeleteAppointment = (appointmentId) => {
    fetch(`/doctorAppointments/${appointmentId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(response => {
        if (response.ok) {
          response.json().then(data => {
            setMessage(data.message); 
            setAppointments(appointments.filter(appointment => appointment.id !== appointmentId));
          });
        } else {
          response.json().then(data => {
            setMessage(data.message); 
          });
        }
      })
      .catch((error) => {
        console.error('Error deleting appointment:', error);
        setMessage('An error occurred');
      });
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    navigate('/login');
  };

  const handleAccount = () => {
    navigate('/account');
  };

  return (
    <div className="doctors-appointment-container">
      <h2 className="doctors-appointment-title">Doctor's Appointments</h2>

      <ul className="doctors-appointment-list">
        {appointments.map((appointment) => (
          <li key={appointment.id} className="doctors-appointment-item">
            <p><strong>Patient Name:</strong> {appointment.patient.full_name}</p>
            <p><strong>Email:</strong> {appointment.patient.email}</p>
            <p><strong>Date:</strong> {appointment.date}</p>
            <p><strong>From:</strong> {appointment.time_from}</p>
            <p><strong>To:</strong> {appointment.time_to}</p>
            <p><strong>Comments:</strong> {appointment.comments}</p>
            <button className="doctors-delete-button" onClick={() => handleDeleteAppointment(appointment.id)}>Delete</button>
          </li>
        ))}
      </ul>

      <button className="doctors-logout-button" onClick={handleAccount}>Account</button>
      <button className="doctors-logout-button" onClick={handleLogout}>Logout</button>

      {message && (
        <p className="doctors-message-text">
          {message}
        </p>
      )}
    </div>
  );
}

export default DoctorsAppointments;
