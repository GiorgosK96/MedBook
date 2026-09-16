from datetime import date, datetime

from helpers import auth_headers, doctor_token, first_doctor_id
from scheduling import availability_error, free_slots, slots_between


def test_slots_between_only_counts_full_slots():
    assert slots_between('09:00', '10:45') == ['09:00', '09:30', '10:00']
    assert slots_between('09:00', '09:15') == []


def test_overlapping_windows_detected_in_any_order():
    windows = [
        {'day_of_week': 2, 'start_time': '13:00', 'end_time': '15:00'},
        {'day_of_week': 2, 'start_time': '09:00', 'end_time': '13:30'},
    ]
    assert 'overlap' in availability_error(windows)


def test_slots_that_already_started_today_are_hidden(client):
    day = date(2099, 12, 1)
    client.put('/doctorAvailability', json={'availability': [
        {'day_of_week': day.weekday(), 'start_time': '09:00', 'end_time': '11:00'},
    ]}, headers=auth_headers(doctor_token(client)))

    assert free_slots(first_doctor_id(client), day, now=datetime(2099, 12, 1, 9, 40)) == ['10:00', '10:30']
