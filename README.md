# Medical Appointment Management System

A web-based system for clients to book and manage their medical appointments with doctors using Flask for the backend and React for the frontend.

## Features
- Secure user authentication (clients & doctors)
- Clients can book, update, and cancel appointments
- Doctors can manage their schedules and appointments
- Real-time appointment validation (no duplicate bookings)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/GiorgosK96/Medbook.git
cd Medbook
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
