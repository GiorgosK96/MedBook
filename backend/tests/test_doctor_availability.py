from datetime import date, timedelta

from helpers import (auth_headers, book, client_token, doctor_token, first_appointment, first_doctor_id,
                     second_client_token, set_status)


def next_monday():
    today = date.today()
    return (today + timedelta(days=7 - today.weekday())).isoformat()


def set_availability(client, token, windows):
    return client.put('/doctorAvailability', json={'availability': windows}, headers=auth_headers(token))


def get_availability(client, token):
    return client.get('/doctorAvailability', headers=auth_headers(token))


def get_slots(client, token, doctor_id, day, **params):
    return client.get(f'/doctors/{doctor_id}/availableSlots', query_string={'date': day, **params},
                      headers=auth_headers(token))


def monday_9_to_11(client):
    doctor = doctor_token(client)
    set_availability(client, doctor, [{'day_of_week': 0, 'start_time': '09:00', 'end_time': '11:00'}])
    return doctor, client_token(client), first_doctor_id(client), next_monday()


def book_9am(client, token, doctor_id, monday):
    book(client, token, doctor_id, date=monday, time_from='09:00', time_to='09:30')
    return first_appointment(client, token)['id']


class TestGetDoctorAvailability:
    def test_empty_by_default(self, client):
        res = get_availability(client, doctor_token(client))
        assert res.status_code == 200
        assert res.get_json()['availability'] == []

    def test_returns_saved_windows(self, client):
        token = doctor_token(client)
        set_availability(client, token, [{'day_of_week': 0, 'start_time': '09:00', 'end_time': '12:00'}])
        windows = get_availability(client, token).get_json()['availability']
        assert len(windows) == 1
        assert (windows[0]['day_of_week'], windows[0]['start_time'], windows[0]['end_time']) == (0, '09:00', '12:00')

    def test_requires_auth(self, client):
        assert get_availability(client, 'badtoken').status_code == 422


class TestSetDoctorAvailability:
    def test_replaces_existing(self, client):
        token = doctor_token(client)
        set_availability(client, token, [{'day_of_week': 0, 'start_time': '09:00', 'end_time': '17:00'}])
        set_availability(client, token, [{'day_of_week': 2, 'start_time': '08:00', 'end_time': '12:00'}])
        windows = get_availability(client, token).get_json()['availability']
        assert [w['day_of_week'] for w in windows] == [2]

    def test_empty_list_clears_all(self, client):
        token = doctor_token(client)
        set_availability(client, token, [{'day_of_week': 0, 'start_time': '09:00', 'end_time': '17:00'}])
        set_availability(client, token, [])
        assert get_availability(client, token).get_json()['availability'] == []

    def test_invalid_day_of_week_rejected(self, client):
        res = set_availability(client, doctor_token(client), [{'day_of_week': 7, 'start_time': '09:00', 'end_time': '12:00'}])
        assert res.status_code == 400
        assert 'Invalid day_of_week' in res.get_json()['error']

    def test_start_after_end_rejected(self, client):
        res = set_availability(client, doctor_token(client), [{'day_of_week': 0, 'start_time': '17:00', 'end_time': '09:00'}])
        assert res.status_code == 400
        assert 'before end time' in res.get_json()['error']

    def test_overlapping_windows_on_same_day_rejected(self, client):
        res = set_availability(client, doctor_token(client), [
            {'day_of_week': 0, 'start_time': '09:00', 'end_time': '12:00'},
            {'day_of_week': 0, 'start_time': '11:00', 'end_time': '14:00'},
        ])
        assert res.status_code == 400
        assert 'overlap' in res.get_json()['error']

    def test_adjacent_windows_and_same_hours_on_other_days_allowed(self, client):
        res = set_availability(client, doctor_token(client), [
            {'day_of_week': 0, 'start_time': '09:00', 'end_time': '12:00'},
            {'day_of_week': 0, 'start_time': '12:00', 'end_time': '14:00'},
            {'day_of_week': 1, 'start_time': '09:00', 'end_time': '12:00'},
        ])
        assert res.status_code == 200

    def test_malformed_time_rejected(self, client):
        res = set_availability(client, doctor_token(client), [{'day_of_week': 0, 'start_time': '9:00', 'end_time': '12:00'}])
        assert res.status_code == 400
        assert 'HH:MM' in res.get_json()['error']

    def test_missing_time_rejected(self, client):
        assert set_availability(client, doctor_token(client), [{'day_of_week': 0}]).status_code == 400

    def test_time_off_half_hour_rejected(self, client):
        res = set_availability(client, doctor_token(client), [{'day_of_week': 0, 'start_time': '09:15', 'end_time': '12:00'}])
        assert res.status_code == 400
        assert '30-minute' in res.get_json()['error']

    def test_clients_cannot_set_availability(self, client):
        assert set_availability(client, client_token(client), []).status_code == 403

    def test_requires_auth(self, client):
        assert set_availability(client, 'badtoken', []).status_code == 422


class TestAvailableSlots:
    def test_no_availability_returns_no_slots(self, client):
        doctor_token(client)
        res = get_slots(client, client_token(client), first_doctor_id(client), next_monday())
        assert res.status_code == 200
        assert res.get_json()['slots'] == []

    def test_availability_generates_30min_slots(self, client):
        _, token, doctor_id, monday = monday_9_to_11(client)
        assert get_slots(client, token, doctor_id, monday).get_json()['slots'] == ['09:00', '09:30', '10:00', '10:30']

    def test_booked_slot_excluded(self, client):
        _, token, doctor_id, monday = monday_9_to_11(client)
        book_9am(client, token, doctor_id, monday)
        slots = get_slots(client, token, doctor_id, monday).get_json()['slots']
        assert '09:00' not in slots
        assert '09:30' in slots

    def test_declined_appointment_frees_slot(self, client):
        doctor, token, doctor_id, monday = monday_9_to_11(client)
        set_status(client, doctor, book_9am(client, token, doctor_id, monday), 'declined')
        assert '09:00' in get_slots(client, token, doctor_id, monday).get_json()['slots']

    def test_own_appointment_can_be_excluded_when_editing(self, client):
        _, token, doctor_id, monday = monday_9_to_11(client)
        appt_id = book_9am(client, token, doctor_id, monday)
        slots = get_slots(client, token, doctor_id, monday, exclude_appointment_id=appt_id).get_json()['slots']
        assert '09:00' in slots

    def test_other_clients_appointment_cannot_be_excluded(self, client):
        _, token, doctor_id, monday = monday_9_to_11(client)
        appt_id = book_9am(client, token, doctor_id, monday)
        other = second_client_token(client)
        slots = get_slots(client, other, doctor_id, monday, exclude_appointment_id=appt_id).get_json()['slots']
        assert '09:00' not in slots

    def test_past_date_has_no_slots(self, client):
        _, token, doctor_id, _ = monday_9_to_11(client)
        assert get_slots(client, token, doctor_id, '2000-01-03').get_json()['slots'] == []  # a Monday

    def test_unknown_doctor_returns_404(self, client):
        assert get_slots(client, client_token(client), 9999, next_monday()).status_code == 404

    def test_missing_date_returns_400(self, client):
        doctor_token(client)
        res = client.get(f'/doctors/{first_doctor_id(client)}/availableSlots', headers=auth_headers(client_token(client)))
        assert res.status_code == 400

    def test_invalid_date_format_returns_400(self, client):
        doctor_token(client)
        assert get_slots(client, client_token(client), first_doctor_id(client), '01-12-2099').status_code == 400
