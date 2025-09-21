import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import './login.css'; 

function Login() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    role: 'patient'
  });

  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  
  const validate = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    return newErrors;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    fetch('/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData), 
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          setMessage(data.error);
        } else {
          setMessage(data.message); 
          if (data.token) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('username', data.username);
            localStorage.setItem('role', data.role);

            if (data.role === 'patient') {
              navigate("/manageAppointment");
            } else if (data.role === 'doctor') {
              navigate("/DoctorsAppointments");
            }
          }
        }
      })
      .catch((error) => {
        console.error('Error:', error);
        setMessage('An error occurred.');
      });
  };

  const handleBackToLanding = () => {
    navigate("/");
  };

  return (
    <div className="login-container">
      <h2 className="login-title">User Login</h2>
      <form onSubmit={handleSubmit} noValidate className="login-form">
        <div className="login-form-group">
          <label>Email:</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
          {errors.email && <p className="login-error-text">{errors.email}</p>}
        </div>
        <div className="login-form-group">
          <label>Password:</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
          {errors.password && <p className="login-error-text">{errors.password}</p>}
        </div>
        <div className="login-form-group">
          <label>Role:</label>
          <select name="role" value={formData.role} onChange={handleChange}>
            <option value="patient">Patient</option>
            <option value="doctor">Doctor</option>
          </select>
        </div>
        <button type="submit" className="login-button">Login</button>
      </form>
      <button onClick={handleBackToLanding} className="login-back-button">
      Back to Home
      </button>
      {message && <p className="login-message-text">{message}</p>}
    </div>
  );
}

export default Login;
