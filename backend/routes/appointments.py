from flask import Blueprint, jsonify, request

from auth import current_user_id, role_required
from extensions import db
from models import Appointment
from scheduling import booking_error

appointments_bp = Blueprint('appointments', __name__)


def own_appointment(appointment_id):
    return Appointment.query.filter_by(id=appointment_id, client_id=current_user_id()) \
        .first_or_404(description='Appointment not found')


@appointments_bp.route('/ShowAppointment', methods=['GET'])
@role_required('client')
def list_appointments():
    appointments = Appointment.query.filter_by(client_id=current_user_id()) \
        .order_by(Appointment.date, Appointment.time_from).all()
    return jsonify({'appointments': [a.to_dict() for a in appointments]}), 200


@appointments_bp.route('/ShowAppointment/<int:appointment_id>', methods=['GET'])
@role_required('client')
def get_appointment(appointment_id):
    return jsonify(own_appointment(appointment_id).to_dict()), 200


@appointments_bp.route('/AddAppointment', methods=['POST'])
@role_required('client')
def book_appointment():
    data = request.get_json(silent=True) or {}
    error = booking_error(current_user_id(), data.get('doctor_id'), data.get('date'),
                          data.get('time_from'), data.get('time_to'))
    if error:
        return jsonify({'error': error}), 400

    db.session.add(Appointment(
        client_id=current_user_id(),
        doctor_id=int(data['doctor_id']),
        date=data['date'],
        time_from=data['time_from'],
        time_to=data['time_to'],
        comments=data.get('comments') or '',
    ))
    db.session.commit()
    return jsonify({'message': 'Appointment created successfully'}), 201


@appointments_bp.route('/UpdateAppointment/<int:appointment_id>', methods=['PUT'])
@role_required('client')
def update_appointment(appointment_id):
    appointment = own_appointment(appointment_id)
    if appointment.status != 'pending':
        return jsonify({'error': f'A {appointment.status} appointment can no longer be edited'}), 409

    data = request.get_json(silent=True) or {}
    doctor_id = data.get('doctor_id', appointment.doctor_id)
    date = data.get('date', appointment.date)
    time_from = data.get('time_from', appointment.time_from)
    time_to = data.get('time_to', appointment.time_to)

    error = booking_error(appointment.client_id, doctor_id, date, time_from, time_to, exclude_id=appointment.id)
    if error:
        return jsonify({'error': error}), 400

    appointment.doctor_id = int(doctor_id)
    appointment.date = date
    appointment.time_from = time_from
    appointment.time_to = time_to
    appointment.comments = data.get('comments', appointment.comments)
    db.session.commit()
    return jsonify({'message': 'Appointment updated successfully'}), 200


@appointments_bp.route('/ShowAppointment/<int:appointment_id>', methods=['DELETE'])
@role_required('client')
def cancel_appointment(appointment_id):
    # Cancelled rather than deleted, so the doctor still sees it.
    appointment = own_appointment(appointment_id)
    if appointment.status not in ('pending', 'confirmed'):
        return jsonify({'error': f'A {appointment.status} appointment cannot be cancelled'}), 409

    appointment.status = 'cancelled'
    db.session.commit()
    return jsonify({'message': 'Appointment cancelled successfully'}), 200
