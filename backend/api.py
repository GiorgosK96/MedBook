from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from dotenv import load_dotenv
from config import Config
from models import db, bcrypt, Patient, Doctor, Appointment

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

    if role == 'patient':
        
        if Patient.query.filter_by(email=email).first() or Patient.query.filter_by(username=username).first():
            return jsonify({'error': 'Email or Username already registered'}), 400
        
        new_patient = Patient(full_name=full_name, username=username, email=email)
        new_patient.set_password(password)

        db.session.add(new_patient)
        db.session.commit()

        return jsonify({'message': 'Patient registered successfully'}), 201

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

    if role == 'patient':
        
        patient = Patient.query.filter_by(email=email).first()

        if patient and patient.check_password(password):
            token = create_access_token(identity=patient.id)
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'username': patient.username,
                'full_name': patient.full_name,
                'role': 'patient'  
            }), 200
        else:
            return jsonify({'error': 'The email, password or role you entered is incorrect!'}), 401

    elif role == 'doctor':
        
        doctor = Doctor.query.filter_by(email=email).first()

        if doctor and doctor.check_password(password):
            token = create_access_token(identity=doctor.id)
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
    current_user_id = get_jwt_identity()
    
    appointment = Appointment.query.filter_by(id=appointment_id, patient_id=current_user_id).first()

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
        'comments': appointment.comments
    }), 200


@app.route("/ShowAppointment", methods=['GET'])
@jwt_required()
def show_appointment():
    current_patient_id = get_jwt_identity()

    appointments = Appointment.query.filter_by(patient_id=current_patient_id).order_by(Appointment.date.asc(), Appointment.time_from.asc()).all()

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
        'comments': appointment.comments
    } for appointment in appointments]

    return jsonify({'appointments': appointments_list}), 200


@app.route("/AddAppointment", methods=['POST'])
@jwt_required()
def add_appointment():
    data = request.get_json()
    patient_id = get_jwt_identity()
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
        Appointment.time_to > time_from_str
    ).first()

    if overlapping_doctor_appointment:
        return jsonify({'error': 'Doctor already has an appointment during this time'}), 400


    overlapping_patient_appointment = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.date == date_str,
        Appointment.time_from < time_to_str,
        Appointment.time_to > time_from_str
    ).first()

    if overlapping_patient_appointment:
        return jsonify({'error': 'You already have another appointment during this time'}), 400


    new_appointment = Appointment(
        patient_id=patient_id,
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
    data = request.get_json()
    patient_id = get_jwt_identity()


    appointment = Appointment.query.filter_by(id=appointment_id, patient_id=patient_id).first()

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
        Appointment.id != appointment.id  
    ).first()

    if overlapping_doctor_appointment:
        return jsonify({'error': 'Doctor already has an appointment during this time'}), 400


    overlapping_patient_appointment = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.date == new_date,
        Appointment.time_from < new_time_to,
        Appointment.time_to > new_time_from,
        Appointment.id != appointment.id  
    ).first()

    if overlapping_patient_appointment:
        return jsonify({'error': 'You already have another appointment during this time'}), 400


    appointment.date = new_date
    appointment.time_from = new_time_from
    appointment.time_to = new_time_to
    appointment.doctor_id = doctor_id
    appointment.comments = comments

    try:
        db.session.commit()
        return jsonify({'message': 'Appointment updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update appointment: {str(e)}'}), 500


@app.route("/ShowAppointment/<int:appointment_id>", methods=['DELETE'])
@jwt_required()
def delete_appointments(appointment_id):
    current_patient_id = get_jwt_identity()  

   
    appointment = Appointment.query.filter_by(id=appointment_id, patient_id=current_patient_id).first()

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
    doctor_id = get_jwt_identity()

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
    doctor_id = get_jwt_identity()

    appointments = Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.date.asc(), Appointment.time_from.asc()).all()

    appointments_list = [{
        'id': appointment.id,
        'patient': {
            'id': appointment.patient.id,
            'full_name': appointment.patient.full_name,
            'email': appointment.patient.email,
        },
        'date': appointment.date,
        'time_from': appointment.time_from,
        'time_to': appointment.time_to,
        'comments': appointment.comments
    } for appointment in appointments]

    return jsonify({'appointments': appointments_list}), 200


@app.route('/account', methods=['GET'])
@jwt_required()
def account():
    user_id = get_jwt_identity()  
    role = request.args.get('role') 
    
    if role == 'patient':
        
        patient = Patient.query.get(user_id)
        if patient:
            return jsonify({
                'full_name': patient.full_name,
                'username': patient.username,
                'email': patient.email,
                'role': 'patient'
            }), 200
        else:
            return jsonify({'error': 'Patient not found'}), 404

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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)