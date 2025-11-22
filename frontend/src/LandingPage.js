import React from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

function LandingPage() {
  return (
    <div className="landing-bg">
      <div className="landing-page-container">
        {/* Medical illustration SVG */}
        <div className="landing-page-hero-image">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" className="landing-page-illustration">
            {/* Calendar/Schedule background */}
            <rect x="80" y="80" width="240" height="240" rx="20" fill="#ffffff" stroke="#0066cc" strokeWidth="4"/>
            
            {/* Calendar header */}
            <rect x="80" y="80" width="240" height="60" rx="20" fill="#0066cc"/>
            <circle cx="120" cy="110" r="8" fill="#ffffff"/>
            <circle cx="280" cy="110" r="8" fill="#ffffff"/>
            
            {/* Calendar grid */}
            <line x1="130" y1="170" x2="270" y2="170" stroke="#e0e0e0" strokeWidth="2"/>
            <line x1="130" y1="210" x2="270" y2="210" stroke="#e0e0e0" strokeWidth="2"/>
            <line x1="130" y1="250" x2="270" y2="250" stroke="#e0e0e0" strokeWidth="2"/>
            
            {/* Checkmarks */}
            <polyline points="140,185 150,195 170,175" fill="none" stroke="#28a745" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            <polyline points="140,225 150,235 170,215" fill="none" stroke="#28a745" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            
            {/* Medical cross */}
            <g transform="translate(320, 280)">
              <circle cx="0" cy="0" r="50" fill="#dc3545"/>
              <rect x="-25" y="-8" width="50" height="16" rx="3" fill="#ffffff"/>
              <rect x="-8" y="-25" width="16" height="50" rx="3" fill="#ffffff"/>
            </g>
            
            {/* Stethoscope */}
            <g transform="translate(60, 280)">
              <circle cx="0" cy="0" r="15" fill="none" stroke="#0066cc" strokeWidth="4"/>
              <path d="M 0,-15 Q -30,-40 -35,-80" fill="none" stroke="#0066cc" strokeWidth="4" strokeLinecap="round"/>
              <path d="M 0,-15 Q 30,-40 35,-80" fill="none" stroke="#0066cc" strokeWidth="4" strokeLinecap="round"/>
              <circle cx="-35" cy="-80" r="12" fill="#0099ff"/>
              <circle cx="35" cy="-80" r="12" fill="#0099ff"/>
            </g>
          </svg>
        </div>
        
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
    </div>
  );
}

export default LandingPage;
