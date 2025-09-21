import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './ShowAppointment.css';

function ShowAppointment() {
  const [appointments, setAppointments] = useState([]);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetch('/ShowAppointment', {
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

  const handleEditAppointment = (appointmentId) => {
    navigate(`/UpdateAppointment/${appointmentId}`);
  };

  const handleDeleteAppointment = (appointmentId) => {
    fetch(`/ShowAppointment/${appointmentId}`, {
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

  const handleBackToManage = () => {
    navigate('/manageAppointment');
  };

  return (
    <div className="show-appointment-container">
      <h2 className="show-appointment-title">Your Appointments</h2>

      <ul className="show-appointment-list">
        {appointments.map((appointment) => (
          <li key={appointment.id} className="show-appointment-item">
            <p><strong>Date:</strong> {appointment.date}</p>
            <p><strong>From:</strong> {appointment.time_from}</p>
            <p><strong>To:</strong> {appointment.time_to}</p>
            <p><strong>Doctor:</strong> {appointment.doctor.full_name} ({appointment.doctor.specialization})</p>
            <p><strong>Comments:</strong> {appointment.comments}</p>
            <button className="show-edit-button" onClick={() => handleEditAppointment(appointment.id)}>Edit</button>
            <button className="show-delete-button" onClick={() => handleDeleteAppointment(appointment.id)}>Delete</button>
          </li>
        ))}
      </ul>
      <button className="show-back-to-manage-button" onClick={handleBackToManage}>Back to Manage Appointments</button>
      <button className="show-logout-button" onClick={handleLogout}>Logout</button>
      {message && (
        <p className="show-message-text">
          {message}
        </p>
      )}
    </div>
  );
}

export default ShowAppointment;
