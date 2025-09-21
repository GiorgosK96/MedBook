import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './UpdateAppointment.css';

export const UpdateAppointment = () => {
  const [date, setDate] = useState('');
  const [timeFrom, setTimeFrom] = useState('');
  const [timeTo, setTimeTo] = useState('');
  const [doctorId, setDoctorId] = useState('');
  const [comment, setComment] = useState('');
  const [message, setMessage] = useState('');
  const [isAccepted, setIsAccepted] = useState(null);
  const [doctors, setDoctors] = useState([]);
  const { appointmentId } = useParams();
  const navigate = useNavigate(); 


  useEffect(() => {
    fetch('/doctors', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(response => response.json())
      .then(data => {
        setDoctors(data.doctors);
      })
      .catch((error) => {
        console.error('Failed to fetch doctors', error);
      });
  }, []);


  useEffect(() => {
    fetch(`/ShowAppointment/${appointmentId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(response => response.json())
      .then(data => {
        setDate(data.date);
        setTimeFrom(data.time_from);
        setTimeTo(data.time_to);
        setDoctorId(data.doctor.id); 
        setComment(data.comments);
      })
      .catch((error) => {
        console.error('Failed to fetch appointment', error);
        setMessage('Failed to load appointment details.');
        setIsAccepted(false); 
      });
  }, [appointmentId]);

  const handleSubmit = () => {
    if (!date || !timeFrom || !timeTo || !doctorId) {
      setMessage('All fields are required');
      setIsAccepted(false); 
      return;
    }

    const data = {
      date,
      time_from: timeFrom,
      time_to: timeTo,
      doctor_id: doctorId, 
      comments: comment,
    };

    fetch(`/UpdateAppointment/${appointmentId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          setMessage(`Error: ${data.error}`);
          setIsAccepted(false); 
        } else {
          setMessage(data.message);
          setIsAccepted(true); 
        }
      })
      .catch((error) => {
        console.error('Error updating appointment:', error);
        setMessage('An error occurred');
        setIsAccepted(false); 
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
    <div className="update-appointment-container">
      <h2 className="update-appointment-title">Update Appointment</h2>
      <form className="update-appointment-form">
        <div className="update-form-group">
          <label>Date</label>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>
        <div className="update-form-group">
          <label>From</label>
          <input type="time" value={timeFrom} onChange={(e) => setTimeFrom(e.target.value)} />
        </div>
        <div className="update-form-group">
          <label>To</label>
          <input type="time" value={timeTo} onChange={(e) => setTimeTo(e.target.value)} />
        </div>
        <div className="update-form-group">
          <label>Doctor</label>
          <select value={doctorId} onChange={(e) => setDoctorId(e.target.value)}>
            <option value="">Select Doctor</option>
            {doctors.map((doctor) => (
              <option key={doctor.id} value={doctor.id}>
                {doctor.full_name} ({doctor.specialization})
              </option>
            ))}
          </select>
        </div>
        <div className="update-form-group">
          <label>Comments</label>
          <textarea value={comment} onChange={(e) => setComment(e.target.value)} />
        </div>
        <button type="button" onClick={handleSubmit} className="update-appointment-button">Update Appointment</button>
      </form>
      <button className="update-back-button" onClick={handleBackToManage}>Back to Manage Appointments</button>
      <button onClick={handleLogout} className="update-logout-button">Logout</button>
      {message && (
        <p className={`update-message-text ${isAccepted ? 'update-success-text' : 'update-error-text'}`}>
          {message}
        </p>
      )}
    </div>
  );
};

export default UpdateAppointment;
