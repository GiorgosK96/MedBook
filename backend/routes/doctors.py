from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from auth import current_user_id, role_required
from extensions import db
from models import Appointment, Doctor, DoctorAvailability
from scheduling import availability_error, free_slots, parse_date

doctors_bp = Blueprint('doctors', __name__)

# Status changes a doctor may make, keyed by the appointment's current status.
DOCTOR_TRANSITIONS = {'pending': ('confirmed', 'declined'), 'confirmed': ('cancelled',)}


@doctors_bp.route('/doctors', methods=['GET'])
def list_doctors():
    return jsonify({'doctors': [
        {'id': d.id, 'full_name': d.full_name, 'specialization': d.specialization} for d in Doctor.query.all()
    ]}), 200


@doctors_bp.route('/doctors/<int:doctor_id>/availableSlots', methods=['GET'])
@jwt_required()
def available_slots(doctor_id):
    db.get_or_404(Doctor, doctor_id, description='Doctor not found')
    day = parse_date(request.args.get('date'))
    if not day:
        return jsonify({'error': 'A date parameter in YYYY-MM-DD format is required'}), 400

    # Only a client editing their own appointment may have its slot counted as free.
    exclude_id = request.args.get('exclude_appointment_id', type=int)
    if exclude_id and not (get_jwt()['role'] == 'client' and
                           Appointment.query.filter_by(id=exclude_id, client_id=current_user_id()).first()):
        exclude_id = None

    return jsonify({'slots': free_slots(doctor_id, day, exclude_id)}), 200


@doctors_bp.route('/doctorAppointments', methods=['GET'])
@role_required('doctor')
def list_doctor_appointments():
    appointments = Appointment.query.filter_by(doctor_id=current_user_id()) \
        .order_by(Appointment.date, Appointment.time_from).all()
    return jsonify({'appointments': [a.to_dict() for a in appointments]}), 200


@doctors_bp.route('/doctorAppointments/<int:appointment_id>/status', methods=['PATCH'])
@role_required('doctor')
def update_appointment_status(appointment_id):
    new_status = (request.get_json(silent=True) or {}).get('status')
    if new_status not in ('confirmed', 'declined', 'cancelled'):
        return jsonify({'error': 'Invalid status'}), 400

    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=current_user_id()) \
        .first_or_404(description='Appointment not found')
    if new_status not in DOCTOR_TRANSITIONS.get(appointment.status, ()):
        return jsonify({'error': f'Cannot change a {appointment.status} appointment to {new_status}'}), 409

    appointment.status = new_status
    db.session.commit()
    return jsonify({'message': f'Appointment {new_status} successfully'}), 200


@doctors_bp.route('/doctorAvailability', methods=['GET'])
@role_required('doctor')
def get_availability():
    windows = DoctorAvailability.query.filter_by(doctor_id=current_user_id()) \
        .order_by(DoctorAvailability.day_of_week, DoctorAvailability.start_time).all()
    return jsonify({'availability': [w.to_dict() for w in windows]}), 200


@doctors_bp.route('/doctorAvailability', methods=['PUT'])
@role_required('doctor')
def set_availability():
    windows = (request.get_json(silent=True) or {}).get('availability', [])
    error = availability_error(windows)
    if error:
        return jsonify({'error': error}), 400

    doctor_id = current_user_id()
    DoctorAvailability.query.filter_by(doctor_id=doctor_id).delete()
    db.session.add_all(DoctorAvailability(doctor_id=doctor_id, day_of_week=w['day_of_week'],
                                          start_time=w['start_time'], end_time=w['end_time']) for w in windows)
    db.session.commit()
    return jsonify({'message': 'Availability updated successfully'}), 200
