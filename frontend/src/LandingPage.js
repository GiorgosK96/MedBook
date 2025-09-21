import React from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

function LandingPage() {
  return (
    <div className="landing-page-container">
      <h1 className="landing-page-title">Patient Appointment Application</h1>

      <div className="landing-page-auth-buttons">
      <p className="landing-page-register-text">If you are a new user you can register here!</p>
        <Link to="/register">
          <button className="landing-page-register-button">Register</button>
        </Link>

        <p className="landing-page-login-text">Already have an account?</p>

        <Link to="/login">
          <button className="landing-page-login-button">Login</button>
        </Link>
      </div>
    </div>
  );
}

export default LandingPage;
