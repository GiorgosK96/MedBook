import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './AddAppointment.css';

export const AddAppointment = () => {
  const [date, setDate] = useState('');
  const [timeFrom, setTimeFrom] = useState('');
  const [timeTo, setTimeTo] = useState('');
  const [doctorId, setDoctorId] = useState('');
  const [comment, setComment] = useState('');
  const [message, setMessage] = useState('');
  const [isAccepted, setIsAccepted] = useState(null);
  const [doctors, setDoctors] = useState([]);
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
    .catch(error => {
      console.error('Error fetching doctors:', error);
    });
  }, []);

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

    fetch('/AddAppointment', {
      method: 'POST',
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
        setDate('');
        setTimeFrom('');
        setTimeTo('');
        setDoctorId('');
        setComment('');
      }
    })
    .catch((error) => {
      setMessage('An error occurred');
      setIsAccepted(false);
      console.error(error);
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
    <div className="add-appointment-container">
      <h2 className="add-appointment-title">Add Appointment</h2>
      <form className="add-appointment-form">
        <div className="add-form-group">
          <label>Date</label>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>
        <div className="add-form-group">
          <label>From</label>
          <input type="time" value={timeFrom} onChange={(e) => setTimeFrom(e.target.value)} />
        </div>
        <div className="add-form-group">
          <label>To</label>
          <input type="time" value={timeTo} onChange={(e) => setTimeTo(e.target.value)} />
        </div>
        <div className="add-form-group">
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
        <div className="add-form-group">
          <label>Comments</label>
          <textarea value={comment} onChange={(e) => setComment(e.target.value)} />
        </div>
        <button type="button" onClick={handleSubmit} className="add-appointment-button">Add Appointment</button>
      </form>
      <button onClick={handleBackToManage} className="add-back-button">Back to Manage Appointments</button>
      <button onClick={handleLogout} className="add-logout-button">Logout</button>
      {message && (
        <p className={`add-message-text ${isAccepted ? 'add-success-text' : 'add-error-text'}`}>
          {message}
        </p>
      )}
    </div>
  );
};

export default AddAppointment;
