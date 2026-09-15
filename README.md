# MedBook

Medical appointment booking app. Clients book appointments with doctors, doctors manage their schedule and accept or decline requests.

## Tech Stack

**Backend** - Python / Flask
- Flask with SQLAlchemy (SQLite)
- JWT auth in httpOnly cookies with CSRF protection, bcrypt password hashing, rate-limited login
- pytest test suite, run on every push by GitHub Actions

**Frontend** - React
- Tailwind CSS for styling

## What It Does

**Clients** can:
- Register, log in, edit their profile
- Book appointments by choosing a doctor, date, and available time slot
- Edit pending appointments, cancel pending or confirmed ones
- See appointment status (pending / confirmed / declined / cancelled)

**Doctors** can:
- Set their weekly availability (per day, multiple time windows)
- Accept or decline incoming appointment requests
- Cancel confirmed appointments
- Edit their profile

Appointments use 30-minute slots inside the doctor's availability, can't be in the past and can't overlap.

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

## Tests

```bash
pip install -r requirements-dev.txt
cd backend
python -m pytest
```
