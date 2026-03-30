from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from dotenv import load_dotenv
from config import Config
from models import db, bcrypt, Client, Doctor, Appointment, DoctorAvailability

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
CORS(app)
jwt = JWTManager(app)


@app.route("/register", methods=['POST'])
def register():
    data = request.get_json()
    full_name = data.get('full_name')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    specialization = data.get('specialization')

    if role == 'client':

        if Client.query.filter_by(email=email).first() or Client.query.filter_by(username=username).first():
            return jsonify({'error': 'Email or Username already registered'}), 400

        new_client = Client(full_name=full_name, username=username, email=email)
        new_client.set_password(password)

        db.session.add(new_client)
        db.session.commit()

        return jsonify({'message': 'Account registered successfully'}), 201

    elif role == 'doctor':

        if Doctor.query.filter_by(email=email).first() or Doctor.query.filter_by(username=username).first():
            return jsonify({'error': 'Email or Username already registered'}), 400

        if not specialization:
            return jsonify({'error': 'Specialization is required for doctors'}), 400

        new_doctor = Doctor(full_name=full_name, username=username, email=email, specialization=specialization)
        new_doctor.set_password(password)

        db.session.add(new_doctor)
        db.session.commit()

        return jsonify({'message': 'Doctor registered successfully'}), 201

    else:
        return jsonify({'error': 'Invalid role'}), 400


@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if role == 'client':

        client = Client.query.filter_by(email=email).first()

        if client and client.check_password(password):
            token = create_access_token(identity=str(client.id), additional_claims={'role': 'client'})
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'username': client.username,
                'full_name': client.full_name,
                'role': 'client'
            }), 200
        else:
            return jsonify({'error': 'The email, password or role you entered is incorrect!'}), 401

    elif role == 'doctor':

        doctor = Doctor.query.filter_by(email=email).first()

        if doctor and doctor.check_password(password):
            token = create_access_token(identity=str(doctor.id), additional_claims={'role': 'doctor'})
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'username': doctor.username,
                'specialization': doctor.specialization,
                'role': 'doctor'
            }), 200
        else:
            return jsonify({'error': 'The email, password or role you entered is incorrect!'}), 401

    else:
        return jsonify({'error': 'Invalid role'}), 400


@app.route("/ShowAppointment/<int:appointment_id>", methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    if get_jwt().get('role') != 'client':
        return jsonify({'error': 'Clients only'}), 403
    current_user_id = int(get_jwt_identity())

    appointment = Appointment.query.filter_by(id=appointment_id, client_id=current_user_id).first()

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    doctor = Doctor.query.get(appointment.doctor_id)

    return jsonify({
        'id': appointment.id,
        'date': appointment.date,
        'time_from': appointment.time_from,
        'time_to': appointment.time_to,
        'doctor': {
            'id': doctor.id,
            'full_name': doctor.full_name,
            'specialization': doctor.specialization
        },
        'comments': appointment.comments,
        'status': appointment.status
    }), 200


@app.route("/ShowAppointment", methods=['GET'])
@jwt_required()
def show_appointment():
    if get_jwt().get('role') != 'client':
        return jsonify({'error': 'Clients only'}), 403
    current_client_id = int(get_jwt_identity())

    appointments = Appointment.query.filter_by(client_id=current_client_id).order_by(Appointment.date.asc(), Appointment.time_from.asc()).all()

    appointments_list = [{
        'id': appointment.id,
        'date': appointment.date,
        'time_from': appointment.time_from,
        'time_to': appointment.time_to,
        'doctor': {
            'id': appointment.doctor.id,
            'full_name': appointment.doctor.full_name,
            'specialization': appointment.doctor.specialization
        },
        'comments': appointment.comments,
        'status': appointment.status
    } for appointment in appointments]

    return jsonify({'appointments': appointments_list}), 200


@app.route("/AddAppointment", methods=['POST'])
@jwt_required()
def add_appointment():
    if get_jwt().get('role') != 'client':
        return jsonify({'error': 'Clients only'}), 403
    data = request.get_json()
    client_id = int(get_jwt_identity())
    doctor_id = data.get('doctor_id')
    date_str = data.get('date')
    time_from_str = data.get('time_from')
    time_to_str = data.get('time_to')

    try:
        selected_time_from = datetime.strptime(f"{date_str} {time_from_str}", "%Y-%m-%d %H:%M")
        selected_time_to = datetime.strptime(f"{date_str} {time_to_str}", "%Y-%m-%d %H:%M")
        current_time = datetime.now()
    except ValueError:
        return jsonify({'error': 'Invalid date or time format'}), 400


    if selected_time_from < current_time:
        return jsonify({'error': 'Cannot create an appointment in the past'}), 400


    if selected_time_to <= selected_time_from:
        return jsonify({'error': 'End time must be after the start time'}), 400


    overlapping_doctor_appointment = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == date_str,
        Appointment.time_from < time_to_str,
        Appointment.time_to > time_from_str,
        Appointment.status != 'declined'
    ).first()

    if overlapping_doctor_appointment:
        return jsonify({'error': 'Doctor already has an appointment during this time'}), 400


    overlapping_client_appointment = Appointment.query.filter(
        Appointment.client_id == client_id,
        Appointment.date == date_str,
        Appointment.time_from < time_to_str,
        Appointment.time_to > time_from_str,
        Appointment.status != 'declined'
    ).first()

    if overlapping_client_appointment:
        return jsonify({'error': 'You already have another appointment during this time'}), 400


    new_appointment = Appointment(
        client_id=client_id,
        doctor_id=doctor_id,
        date=date_str,
        time_from=time_from_str,
        time_to=time_to_str,
        comments=data.get('comments', '')
    )

    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({'message': 'Appointment created successfully'}), 201


@app.route("/UpdateAppointment/<int:appointment_id>", methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    if get_jwt().get('role') != 'client':
        return jsonify({'error': 'Clients only'}), 403
    data = request.get_json()
    client_id = int(get_jwt_identity())


    appointment = Appointment.query.filter_by(id=appointment_id, client_id=client_id).first()

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404


    new_date = data.get('date', appointment.date)
    new_time_from = data.get('time_from', appointment.time_from)
    new_time_to = data.get('time_to', appointment.time_to)
    doctor_id = data.get('doctor_id', appointment.doctor_id)
    comments = data.get('comments', appointment.comments)

    try:
        selected_time_from = datetime.strptime(f"{new_date} {new_time_from}", "%Y-%m-%d %H:%M")
        selected_time_to = datetime.strptime(f"{new_date} {new_time_to}", "%Y-%m-%d %H:%M")
        current_time = datetime.now()
    except ValueError:
        return jsonify({'error': 'Invalid date or time format'}), 400


    if selected_time_from < current_time:
        return jsonify({'error': 'Cannot update an appointment to a past time'}), 400


    if selected_time_to <= selected_time_from:
        return jsonify({'error': 'End time must be after the start time'}), 400


    overlapping_doctor_appointment = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == new_date,
        Appointment.time_from < new_time_to,
        Appointment.time_to > new_time_from,
        Appointment.id != appointment.id,
        Appointment.status != 'declined'
    ).first()

    if overlapping_doctor_appointment:
        return jsonify({'error': 'Doctor already has an appointment during this time'}), 400


    overlapping_client_appointment = Appointment.query.filter(
        Appointment.client_id == client_id,
        Appointment.date == new_date,
        Appointment.time_from < new_time_to,
        Appointment.time_to > new_time_from,
        Appointment.id != appointment.id,
        Appointment.status != 'declined'
    ).first()

    if overlapping_client_appointment:
        return jsonify({'error': 'You already have another appointment during this time'}), 400


    appointment.date = new_date
    appointment.time_from = new_time_from
    appointment.time_to = new_time_to
    appointment.doctor_id = doctor_id
    appointment.comments = comments
    appointment.status = 'pending'

    try:
        db.session.commit()
        return jsonify({'message': 'Appointment updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update appointment: {str(e)}'}), 500


@app.route("/ShowAppointment/<int:appointment_id>", methods=['DELETE'])
@jwt_required()
def delete_appointments(appointment_id):
    if get_jwt().get('role') != 'client':
        return jsonify({'error': 'Clients only'}), 403
    current_client_id = int(get_jwt_identity())

    appointment = Appointment.query.filter_by(id=appointment_id, client_id=current_client_id).first()

    if appointment:
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({'message': 'Appointment deleted successfully'}), 202
    else:
        return jsonify({'error': 'Appointment not found or not authorized to delete this appointment'}), 404


@app.route("/doctors", methods=['GET'])
def get_doctors():
    doctors = Doctor.query.all()
    doctors_list = [{'id': doctor.id, 'full_name': doctor.full_name, 'specialization': doctor.specialization} for doctor in doctors]
    return jsonify({'doctors': doctors_list}), 200


@app.route("/doctorAppointments/<int:appointment_id>", methods=['DELETE'])
@jwt_required()
def delete_doctor_appointments(appointment_id):
    if get_jwt().get('role') != 'doctor':
        return jsonify({'error': 'Doctors only'}), 403
    doctor_id = int(get_jwt_identity())

    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=doctor_id).first()

    if not appointment:
        return jsonify({'error': 'Appointment not found or not authorized to delete this appointment'}), 404

    try:
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({'message': 'Appointment deleted successfully'}), 202
    except Exception as e:
        return jsonify({'error': f'Failed to delete appointment: {str(e)}'}), 500


@app.route("/doctorAppointments", methods=['GET'])
@jwt_required()
def get_doctor_appointments():
    if get_jwt().get('role') != 'doctor':
        return jsonify({'error': 'Doctors only'}), 403
    doctor_id = int(get_jwt_identity())

    appointments = Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.date.asc(), Appointment.time_from.asc()).all()

    appointments_list = [{
        'id': appointment.id,
        'client': {
            'id': appointment.client.id,
            'full_name': appointment.client.full_name,
            'email': appointment.client.email,
        },
        'date': appointment.date,
        'time_from': appointment.time_from,
        'time_to': appointment.time_to,
        'comments': appointment.comments,
        'status': appointment.status
    } for appointment in appointments]

    return jsonify({'appointments': appointments_list}), 200


@app.route("/doctorAppointments/<int:appointment_id>/status", methods=['PATCH'])
@jwt_required()
def update_appointment_status(appointment_id):
    if get_jwt().get('role') != 'doctor':
        return jsonify({'error': 'Doctors only'}), 403
    doctor_id = int(get_jwt_identity())
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ('confirmed', 'declined'):
        return jsonify({'error': 'Invalid status'}), 400

    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=doctor_id).first()
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    appointment.status = new_status
    db.session.commit()

    return jsonify({'message': f'Appointment {new_status} successfully'}), 200


@app.route("/doctorAvailability", methods=['GET'])
@jwt_required()
def get_doctor_availability():
    if get_jwt().get('role') != 'doctor':
        return jsonify({'error': 'Doctors only'}), 403
    doctor_id = int(get_jwt_identity())
    slots = DoctorAvailability.query.filter_by(doctor_id=doctor_id)\
        .order_by(DoctorAvailability.day_of_week, DoctorAvailability.start_time).all()
    return jsonify({'availability': [{
        'id': s.id,
        'day_of_week': s.day_of_week,
        'start_time': s.start_time,
        'end_time': s.end_time,
    } for s in slots]}), 200


@app.route("/doctorAvailability", methods=['PUT'])
@jwt_required()
def set_doctor_availability():
    if get_jwt().get('role') != 'doctor':
        return jsonify({'error': 'Doctors only'}), 403
    doctor_id = int(get_jwt_identity())
    data = request.get_json()
    slots = data.get('availability', [])

    for s in slots:
        if s.get('day_of_week') not in range(7):
            return jsonify({'error': 'Invalid day_of_week'}), 400
        if s.get('start_time', '') >= s.get('end_time', ''):
            return jsonify({'error': 'Start time must be before end time'}), 400

    DoctorAvailability.query.filter_by(doctor_id=doctor_id).delete()
    for s in slots:
        db.session.add(DoctorAvailability(
            doctor_id=doctor_id,
            day_of_week=s['day_of_week'],
            start_time=s['start_time'],
            end_time=s['end_time'],
        ))
    db.session.commit()
    return jsonify({'message': 'Availability updated successfully'}), 200


@app.route("/doctors/<int:doctor_id>/availableSlots", methods=['GET'])
@jwt_required()
def get_available_slots(doctor_id):
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'date parameter required'}), 400

    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    day_of_week = selected_date.weekday()  # 0=Monday

    windows = DoctorAvailability.query.filter_by(
        doctor_id=doctor_id, day_of_week=day_of_week
    ).all()

    if not windows:
        return jsonify({'slots': []}), 200

    # Generate 30-min slots from availability windows
    all_slots = []
    for w in windows:
        current = w.start_time
        while current < w.end_time:
            all_slots.append(current)
            h, m = map(int, current.split(':'))
            m += 30
            if m >= 60:
                h += 1
                m -= 60
            current = f"{h:02d}:{m:02d}"

    # Remove slots that overlap with booked appointments
    booked = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == date_str,
        Appointment.status != 'declined'
    ).all()

    available = []
    for slot in all_slots:
        h, m = map(int, slot.split(':'))
        m += 30
        if m >= 60:
            h += 1
            m -= 60
        slot_end = f"{h:02d}:{m:02d}"

        if not any(appt.time_from < slot_end and appt.time_to > slot for appt in booked):
            available.append(slot)

    return jsonify({'slots': available}), 200


@app.route('/account', methods=['GET'])
@jwt_required()
def account():
    user_id = int(get_jwt_identity())
    role = get_jwt().get('role')

    if role == 'client':

        client = Client.query.get(user_id)
        if client:
            return jsonify({
                'full_name': client.full_name,
                'username': client.username,
                'email': client.email,
                'role': 'client'
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404

    elif role == 'doctor':

        doctor = Doctor.query.get(user_id)
        if doctor:
            return jsonify({
                'full_name': doctor.full_name,
                'username': doctor.username,
                'email': doctor.email,
                'specialization': doctor.specialization,
                'role': 'doctor'
            }), 200
        else:
            return jsonify({'error': 'Doctor not found'}), 404

    else:
        return jsonify({'error': 'Invalid role'}), 400


@app.route('/account', methods=['PUT'])
@jwt_required()
def update_account():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    role = get_jwt().get('role')

    if role == 'client':
        user = Client.query.get(user_id)
    elif role == 'doctor':
        user = Doctor.query.get(user_id)
    else:
        return jsonify({'error': 'Invalid role'}), 400

    if not user:
        return jsonify({'error': 'User not found'}), 404

    new_full_name = data.get('full_name', '').strip()
    new_email = data.get('email', '').strip()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if new_full_name and len(new_full_name) < 2:
        return jsonify({'error': 'Full name must be at least 2 characters'}), 400

    if new_email and new_email != user.email:
        Model = Client if role == 'client' else Doctor
        if Model.query.filter(Model.email == new_email, Model.id != user_id).first():
            return jsonify({'error': 'Email already in use'}), 400

    if new_password:
        if not current_password:
            return jsonify({'error': 'Current password is required to set a new password'}), 400
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        user.set_password(new_password)

    if new_full_name:
        user.full_name = new_full_name
    if new_email:
        user.email = new_email

    try:
        db.session.commit()
        return jsonify({
            'message': 'Account updated successfully',
            'full_name': user.full_name,
            'username': user.username,
            'email': user.email,
            'role': role,
            **(({'specialization': user.specialization}) if role == 'doctor' else {}),
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update account: {str(e)}'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
