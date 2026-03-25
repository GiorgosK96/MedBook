# MedBook

Medical appointment booking app. Clients book appointments with doctors, doctors manage their schedule and accept or decline requests.

## Tech Stack

**Backend** — Python / Flask
- Flask with SQLAlchemy (SQLite)

**Frontend** — React
- Tailwind CSS for styling

## How to Run

### 1. Clone
```bash
git clone https://github.com/GiorgosK96/Medbook.git
cd Medbook
```

### 2. Backend
```bash
cd backend
pip install -r ../requirements.txt
```

Create a `.env` file in `backend/`:
```
SQLALCHEMY_DATABASE_URI=sqlite:///appointments.db
JWT_SECRET_KEY=your_secret_key_here
```

Seed the database with sample data (optional):
```bash
python seed.py
```

Start the server:
```bash
python api.py
```

Runs on `http://localhost:5000`.

### 3. Frontend
```bash
cd frontend
npm install
npm start
```

Runs on `http://localhost:3000`.

## What It Does

**Clients** can:
- Register, log in, edit their profile
- Book appointments by choosing a doctor, date, and available time slot
- View, edit, and cancel their appointments
- See appointment status (pending / confirmed / declined)

**Doctors** can:
- Set their weekly availability (per day, multiple time windows)
- Accept or decline incoming appointment requests
- Cancel confirmed appointments
- Edit their profile

The app validates overlapping bookings, blocks past dates, and dynamically shows only available time slots based on each doctor's schedule.
