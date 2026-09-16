# Fills the database with sample data. Run from backend/: python seed.py
from datetime import date, timedelta

from api import create_app
from extensions import db
from models import Appointment, Client, Doctor, DoctorAvailability


def next_weekday(offset_days):
    d = date.today() + timedelta(days=offset_days)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d.strftime('%Y-%m-%d')


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


clients_data = [
    {'full_name': 'Kostas Papadakis', 'username': 'kpapadakis', 'email': 'kostas@example.com', 'password': 'client123'},
    {'full_name': 'Eleni Karagianni', 'username': 'ekaragianni', 'email': 'eleni@example.com', 'password': 'client123'},
    {'full_name': 'Thanasis Raptis', 'username': 'traptis', 'email': 'thanasis@example.com', 'password': 'client123'},
]


def get_appointments_data():
    return [
        {'client_idx': 0, 'doctor_idx': 0, 'date': next_weekday(3),  'time_from': '09:00', 'time_to': '09:30', 'comments': 'Annual heart checkup', 'status': 'confirmed'},
        {'client_idx': 0, 'doctor_idx': 2, 'date': next_weekday(5),  'time_from': '11:00', 'time_to': '11:30', 'comments': 'Recurring headaches', 'status': 'pending'},
        {'client_idx': 1, 'doctor_idx': 1, 'date': next_weekday(3),  'time_from': '10:00', 'time_to': '10:30', 'comments': 'Skin rash on left arm', 'status': 'confirmed'},
        {'client_idx': 1, 'doctor_idx': 4, 'date': next_weekday(7),  'time_from': '13:00', 'time_to': '13:30', 'comments': '', 'status': 'pending'},
        {'client_idx': 2, 'doctor_idx': 3, 'date': next_weekday(10), 'time_from': '12:30', 'time_to': '13:00', 'comments': 'Knee pain after running', 'status': 'declined'},
        {'client_idx': 2, 'doctor_idx': 6, 'date': next_weekday(14), 'time_from': '12:00', 'time_to': '12:30', 'comments': 'Follow-up session', 'status': 'pending'},
    ]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

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

        # Create clients
        clients = []
        for c in clients_data:
            client = Client(full_name=c['full_name'], username=c['username'], email=c['email'])
            client.set_password(c['password'])
            db.session.add(client)
            clients.append(client)

        db.session.flush()  # so doctors and clients get their ids

        # Create appointments
        appointments_data = get_appointments_data()
        for a in appointments_data:
            appointment = Appointment(
                client_id=clients[a['client_idx']].id,
                doctor_id=doctors[a['doctor_idx']].id,
                date=a['date'],
                time_from=a['time_from'],
                time_to=a['time_to'],
                comments=a['comments'],
                status=a['status'],
            )
            db.session.add(appointment)

        # Mon-Fri, 09:00-14:00
        for doctor in doctors:
            for day in range(5):
                db.session.add(DoctorAvailability(
                    doctor_id=doctor.id,
                    day_of_week=day,
                    start_time='09:00',
                    end_time='14:00',
                ))

        db.session.commit()

        print('Seeded successfully!')
        print(f'  {len(doctors)} doctors')
        print(f'  {len(clients)} clients')
        print(f'  {len(appointments_data)} appointments')
        print(f'  {len(doctors) * 5} availability slots')
        print()
        print('Sample logins:')
        print('  Client: kostas@example.com / client123')
        print('  Doctor: maria.papadopoulou@medbook.com / doctor123')


if __name__ == '__main__':
    seed()
