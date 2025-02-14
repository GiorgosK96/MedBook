import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import './register.css';

function Register() {
  const [formData, setFormData] = useState({
    full_name: '',
    username: '',
    email: '',
    password: '',
    role: 'patient',
    specialization: ''
  });

  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();

  const specializations = [
    'Cardiologist',
    'Dermatologist',
    'Neurologist',
    'Orthopedist',
    'Pediatrician',
    'Ophthalmologist',
    'Oncologist',
    'Gastroenterologist',
    'Endocrinologist',
    'Psychiatrist',,
    'Urologist',
    'Gynecologist',
  ];
  

  const validatePassword = (password) => {
    return /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/.test(password);
  };

  const validateEmail = (email) => {
    return /\S+@\S+\.\S+/.test(email);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.full_name) {
      newErrors.full_name = 'Full name is required';
    } else if (formData.full_name.length < 2) {
      newErrors.full_name = 'Full name must be at least 2 characters';
    }

    if (!formData.username) {
      newErrors.username = 'Username is required';
    }

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Email format is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    } else if (!validatePassword(formData.password)) {
      newErrors.password = 'Password must contain both letters and numbers';
    }

    if (formData.role === 'doctor' && !formData.specialization) {
      newErrors.specialization = 'Specialization is required for doctors';
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

    fetch('/register', {
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
          navigate("/login"); 
        }
      })
      .catch((error) => {
        console.error('Error:', error);
        setMessage('An error occurred.');
      });
  };

  const handleLoginRedirect = () => {
    navigate("/login");
  };

  const handleBackToLanding = () => {
    navigate("/");
  };

  return (
    <div className="register-container">
      <h2 className="register-title">User Registration</h2>
      <form onSubmit={handleSubmit} noValidate className="register-form">
        <div className="register-form-group">
          <label>Full Name:</label>
          <input
            type="text"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            required
          />
          {errors.full_name && <p className="register-error-text">{errors.full_name}</p>}
        </div>
        <div className="register-form-group">
          <label>Username:</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        {errors.username && <p className="register-error-text">{errors.username}</p>}
        </div>
        <div className="register-form-group">
          <label>Email:</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
          {errors.email && <p className="register-error-text">{errors.email}</p>}
        </div>
        <div className="register-form-group">
          <label>Password:</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
         {errors.password && <p className="register-error-text">{errors.password}</p>}
        </div>
        <div className="register-form-group">
          <label>Role:</label>
          <select name="role" value={formData.role} onChange={handleChange}>
            <option value="patient">Patient</option>
            <option value="doctor">Doctor</option>
          </select>
        </div>

        {}
        {formData.role === 'doctor' && (
          <div className="register-form-group">
            <label>Specialization:</label>
            <select 
              name="specialization"
              value={formData.specialization}
              onChange={handleChange}
              required
            >
              <option value="">Select Specialization</option>
              {specializations.map((spec, index) => (
                <option key={index} value={spec}>
                  {spec}
                </option>
              ))}
            </select>
            {errors.specialization && <p className="register-error-text">{errors.specialization}</p>}
          </div>
        )}

        <button type="submit" className="register-button">Register</button>
        <div>
          <button onClick={handleLoginRedirect} className="register-login-redirect-button">Go to Login</button>
        </div>
      </form>
      <button onClick={handleBackToLanding} className="register-back-button">Back to Landing Page</button>
      {message && <p className="register-message-text">{message}</p>}
    </div>
  );
}

export default Register;
