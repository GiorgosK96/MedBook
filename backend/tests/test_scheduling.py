from datetime import date, datetime

from helpers import auth_headers, get_token, login_doctor, register_doctor
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
    register_doctor(client)
    day = date(2099, 12, 1)
    client.put('/doctorAvailability', json={'availability': [
        {'day_of_week': day.weekday(), 'start_time': '09:00', 'end_time': '11:00'},
    ]}, headers=auth_headers(get_token(login_doctor(client))))
    doctor_id = client.get('/doctors').get_json()['doctors'][0]['id']

    assert free_slots(doctor_id, day, now=datetime(2099, 12, 1, 9, 40)) == ['10:00', '10:30']
