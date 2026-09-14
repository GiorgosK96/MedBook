"""Booking and availability rules.

Times are stored as zero-padded 'HH:MM' strings, so comparing them as strings
(in Python and in SQL) gives the right order.
"""
from datetime import datetime

from extensions import db
from models import INACTIVE_STATUSES, Appointment, Doctor, DoctorAvailability

SLOT_MINUTES = 30


def parse_date(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


def parse_time(value):
    try:
        parsed = datetime.strptime(value, '%H:%M')
    except (TypeError, ValueError):
        return None
    # Reject unpadded input like '9:00', which would break string comparison.
    return parsed.time() if parsed.strftime('%H:%M') == value else None


def slots_between(start, end):
    """Start times of the 30-minute slots that fit between two 'HH:MM' times."""
    first = int(start[:2]) * 60 + int(start[3:])
    last = int(end[:2]) * 60 + int(end[3:]) - SLOT_MINUTES
    return [f'{m // 60:02d}:{m % 60:02d}' for m in range(first, last + 1, SLOT_MINUTES)]


def offered_slots(doctor_id, day):
    windows = DoctorAvailability.query.filter_by(doctor_id=doctor_id, day_of_week=day.weekday())
    return {slot for w in windows for slot in slots_between(w.start_time, w.end_time)}


def active_appointments(date_str, exclude_id=None):
    return Appointment.query.filter(
        Appointment.date == date_str,
        Appointment.status.notin_(INACTIVE_STATUSES),
        Appointment.id != exclude_id,
    )


def booking_error(client_id, doctor_id, date_str, time_from, time_to, exclude_id=None):
    """Return why a booking isn't allowed, or None if it is."""
    if not str(doctor_id).isdigit() or not db.session.get(Doctor, int(doctor_id)):
        return 'Doctor not found'
    doctor_id = int(doctor_id)

    day, start, end = parse_date(date_str), parse_time(time_from), parse_time(time_to)
    if not (day and start and end):
        return 'Invalid date or time format'
    if end <= start:
        return 'End time must be after the start time'
    if start.minute % SLOT_MINUTES or end.minute % SLOT_MINUTES:
        return 'Appointments must start and end on 30-minute slots'
    if datetime.combine(day, start) < datetime.now():
        return 'Cannot book an appointment in the past'
    if not set(slots_between(time_from, time_to)) <= offered_slots(doctor_id, day):
        return 'The doctor is not available at this time'

    overlapping = active_appointments(date_str, exclude_id).filter(
        Appointment.time_from < time_to, Appointment.time_to > time_from)
    if overlapping.filter_by(doctor_id=doctor_id).first():
        return 'Doctor already has an appointment during this time'
    if overlapping.filter_by(client_id=client_id).first():
        return 'You already have another appointment during this time'
    return None


def free_slots(doctor_id, day, exclude_id=None, now=None):
    """Slot start times that can still be booked with a doctor on a given day."""
    now = now or datetime.now()
    booked = active_appointments(day.isoformat(), exclude_id).filter_by(doctor_id=doctor_id)
    taken = {slot for a in booked for slot in slots_between(a.time_from, a.time_to)}
    return [slot for slot in sorted(offered_slots(doctor_id, day) - taken)
            if datetime.combine(day, parse_time(slot)) > now]


def availability_error(windows):
    """Return why a weekly schedule is invalid, or None if it's fine."""
    by_day = {}
    for w in windows:
        start, end = parse_time(w.get('start_time')), parse_time(w.get('end_time'))
        if w.get('day_of_week') not in range(7):
            return 'Invalid day_of_week'
        if not (start and end):
            return 'Invalid time format, expected HH:MM'
        if start.minute % SLOT_MINUTES or end.minute % SLOT_MINUTES:
            return 'Times must be on 30-minute boundaries'
        if start >= end:
            return 'Start time must be before end time'
        by_day.setdefault(w['day_of_week'], []).append((start, end))

    for day_windows in by_day.values():
        day_windows.sort()
        if any(later[0] < earlier[1] for earlier, later in zip(day_windows, day_windows[1:])):
            return 'Time windows on the same day cannot overlap'
    return None
