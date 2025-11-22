# Medical Appointment Management System

A web-based system for patients to book and manage their medical appointments with doctors using Flask for the backend and React for the frontend.

## Features
- Secure user authentication (patients & doctors)
- Patients can book, update, and cancel appointments
- Doctors can manage their schedules and appointments
- Real-time appointment validation (no duplicate bookings)
- Clean, modern medical-themed UI

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/GiorgosK96/Medical_Appointment_App.git
cd Medical_Appointment_App
```

### 2. Install Backend Dependencies
```bash
cd backend
pip install -r ../requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 4. Set Up Environment Variables
Create a `.env` file in the backend directory with:
```
SQLALCHEMY_DATABASE_URI=sqlite:///appointments.db
JWT_SECRET_KEY=your_secret_key_here
```

### 5. Start the Application

**Start the backend:**
```bash
cd backend
python api.py
```

**Start the frontend (in a new terminal):**
```bash
cd frontend
npm start
```

The application will be available at `http://localhost:3000`

## Technologies
- **Backend:** Flask, SQLAlchemy, Flask-JWT-Extended, Flask-Bcrypt
- **Frontend:** React 18, React Router, CSS3
- **Database:** SQLite
- **Authentication:** JWT tokens with bcrypt hashing
