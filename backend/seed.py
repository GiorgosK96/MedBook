"""
Seed script — populates the database with sample doctors, patients, and appointments.

Usage:
    cd backend
    python seed.py
"""

from api import app
from models import db, bcrypt, Patient, Doctor, Appointment

doctors_data = [
    {'full_name': 'Dr. Maria Papadopoulou', 'username': 'mpapadopoulou', 'email': 'maria.papadopoulou@medbook.com', 'password': 'doctor123', 'specialization': 'Cardiologist'},
    {'full_name': 'Dr. Nikos Georgiou', 'username': 'ngeorgiou', 'email': 'nikos.georgiou@medbook.com', 'password': 'doctor123', 'specialization': 'Dermatologist'},
    {'full_name': 'Dr. Elena Kostopoulou', 'username': 'ekostopoulou', 'email': 'elena.kostopoulou@medbook.com', 'password': 'doctor123', 'specialization': 'Neurologist'},
    {'full_name': 'Dr. Alexandros Dimitriou', 'username': 'adimitriou', 'email': 'alex.dimitriou@medbook.com', 'password': 'doctor123', 'specialization': 'Orthopedist'},
    {'full_name': 'Dr. Sofia Antoniadou', 'username': 'santoniadou', 'email': 'sofia.antoniadou@medbook.com', 'password': 'doctor123', 'specialization': 'Pediatrician'},
    {'full_name': 'Dr. Dimitris Vlachos', 'username': 'dvlachos', 'email': 'dimitris.vlachos@medbook.com', 'password': 'doctor123', 'specialization': 'Ophthalmologist'},
    {'full_name': 'Dr. Anna Nikolaou', 'username': 'anikolaou', 'email': 'anna.nikolaou@medbook.com', 'password': 'doctor123', 'specialization': 'Psychiatrist'},
    {'full_name': 'Dr. Giorgos Makris', 'username': 'gmakris', 'email': 'giorgos.makris@medbook.com', 'password': 'doctor123', 'specialization': 'Gastroenterologist'},
]

patients_data = [
    {'full_name': 'Kostas Papadakis', 'username': 'kpapadakis', 'email': 'kostas@example.com', 'password': 'patient123'},
    {'full_name': 'Eleni Karagianni', 'username': 'ekaragianni', 'email': 'eleni@example.com', 'password': 'patient123'},
    {'full_name': 'Thanasis Raptis', 'username': 'traptis', 'email': 'thanasis@example.com', 'password': 'patient123'},
]

appointments_data = [
    {'patient_idx': 0, 'doctor_idx': 0, 'date': '2026-03-27', 'time_from': '09:00', 'time_to': '09:30', 'comments': 'Annual heart checkup'},
    {'patient_idx': 0, 'doctor_idx': 2, 'date': '2026-03-28', 'time_from': '11:00', 'time_to': '11:30', 'comments': 'Recurring headaches'},
    {'patient_idx': 1, 'doctor_idx': 1, 'date': '2026-03-27', 'time_from': '10:00', 'time_to': '10:30', 'comments': 'Skin rash on left arm'},
    {'patient_idx': 1, 'doctor_idx': 4, 'date': '2026-03-30', 'time_from': '14:00', 'time_to': '14:30', 'comments': ''},
    {'patient_idx': 2, 'doctor_idx': 3, 'date': '2026-03-29', 'time_from': '16:00', 'time_to': '16:45', 'comments': 'Knee pain after running'},
    {'patient_idx': 2, 'doctor_idx': 6, 'date': '2026-04-01', 'time_from': '12:00', 'time_to': '12:50', 'comments': 'Follow-up session'},
]


def seed():
    with app.app_context():
        db.create_all()

        # Check if data already exists
        if Doctor.query.first():
            print('Database already has data. To re-seed, delete backend/instance/appointments.db and run again.')
            return

        # Create doctors
        doctors = []
        for d in doctors_data:
            doctor = Doctor(full_name=d['full_name'], username=d['username'], email=d['email'], specialization=d['specialization'])
            doctor.set_password(d['password'])
            db.session.add(doctor)
            doctors.append(doctor)

        # Create patients
        patients = []
        for p in patients_data:
            patient = Patient(full_name=p['full_name'], username=p['username'], email=p['email'])
            patient.set_password(p['password'])
            db.session.add(patient)
            patients.append(patient)

        db.session.flush()  # Get IDs assigned

        # Create appointments
        for a in appointments_data:
            appointment = Appointment(
                patient_id=patients[a['patient_idx']].id,
                doctor_id=doctors[a['doctor_idx']].id,
                date=a['date'],
                time_from=a['time_from'],
                time_to=a['time_to'],
                comments=a['comments'],
            )
            db.session.add(appointment)

        db.session.commit()

        print('Seeded successfully!')
        print(f'  {len(doctors)} doctors')
        print(f'  {len(patients)} patients')
        print(f'  {len(appointments_data)} appointments')
        print()
        print('Sample logins:')
        print('  Patient: kostas@example.com / patient123')
        print('  Doctor:  maria.papadopoulou@medbook.com / doctor123')


if __name__ == '__main__':
    seed()
