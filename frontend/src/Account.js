import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Account.css';

function Account() {
  const [accountData, setAccountData] = useState({});
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    
    const role = localStorage.getItem('role');
    
    fetch(`/account?role=${role}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        setMessage(data.error);
      } else {
        setAccountData(data);
      }
    })
    .catch(error => {
      console.error('Error fetching account data:', error);
      setMessage('Failed to load account details');
    });
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    navigate('/login'); 
  };

  const handleBackToManage = () => {
    const role = localStorage.getItem('role');
    if (role === 'patient') {
      navigate('/manageAppointment'); 
    } else if (role === 'doctor') {
      navigate('/DoctorsAppointments');
    }
  };

  return (
    <div className="account-container">
      <h2>Account Information</h2>
      {message && <p className="account-error-text">{message}</p>}
      {accountData && (
        <div className="account-details">
          <p><strong>Full Name:</strong> {accountData.full_name}</p>
          <p><strong>Username:</strong> {accountData.username}</p>
          <p><strong>Email:</strong> {accountData.email}</p>
          {accountData.role === 'doctor' && (
            <p><strong>Specialization:</strong> {accountData.specialization}</p>
          )}
        </div>
      )}
      <button className="show-back-to-manage-button" onClick={handleBackToManage}>Back</button>
      <button className="account-logout-button" onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default Account;
