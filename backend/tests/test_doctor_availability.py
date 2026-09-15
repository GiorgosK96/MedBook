from datetime import datetime, timedelta
from helpers import register_client, register_doctor, login_client, login_doctor, auth_headers, get_token


def next_weekday(weekday):
    today = datetime.now()
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')


def setup_doctor(client):
    register_doctor(client)
    token = get_token(login_doctor(client))
    doctors = client.get('/doctors').get_json()['doctors']
    doctor_id = doctors[0]['id']
    return token, doctor_id


def set_availability(client, token, slots):
    return client.put('/doctorAvailability', json={'availability': slots}, headers=auth_headers(token))


def monday_9_to_11(client):
    doctor_token, doctor_id = setup_doctor(client)
    set_availability(client, doctor_token, [{'day_of_week': 0, 'start_time': '09:00', 'end_time': '11:00'}])
    register_client(client)
    client_token = get_token(login_client(client))
    return doctor_token, client_token, doctor_id, next_weekday(0)


def get_slots(client, token, doctor_id, date, **params):
    query = '&'.join(f'{k}={v}' for k, v in {'date': date, **params}.items())
    return client.get(f'/doctors/{doctor_id}/availableSlots?{query}', headers=auth_headers(token))


class TestGetDoctorAvailability:
    def test_returns_empty_by_default(self, client):
        token, _ = setup_doctor(client)
        res = client.get('/doctorAvailability', headers=auth_headers(token))
        assert res.status_code == 200
        assert res.get_json()['availability'] == []

    def test_returns_saved_slots(self, client):
        token, _ = setup_doctor(client)
        set_availability(client, token, [{'day_of_week': 0, 'start_time': '09:00', 'end_time': '12:00'}])
        res = client.get('/doctorAvailability', headers=auth_headers(token))
        slots = res.get_json()['availability']
        assert len(slots) == 1
        assert slots[0]['day_of_week'] == 0
        assert slots[0]['start_time'] == '09:00'
        assert slots[0]['end_time'] == '12:00'

    def test_requires_auth(self, client):
        res = client.get('/doctorAvailability', headers=auth_headers('badtoken'))
        assert res.status_code == 422


class TestSetDoctorAvailability:
    def test_set_availability_success(self, client):
        token, _ = setup_doctor(client)
        res = set_availability(client, token, [
            {'day_of_week': 1, 'start_time': '08:00', 'end_time': '16:00'},
            {'day_of_week': 3, 'start_time': '10:00', 'end_time': '14:00'},
        ])
        assert res.status_code == 200
        assert res.get_json()['message'] == 'Availability updated successfully'

    def test_set_availability_replaces_existing(self, client):
        token, _ = setup_doctor(client)
        set_availability(client, token, [{'day_of_week': 0, 'start_time': '09:00', 'end_time': '17:00'}])
        set_availability(client, token, [{'day_of_week': 2, 'start_time': '08:00', 'end_time': '12:00'}])
        slots = client.get('/doctorAvailability', headers=auth_headers(token)).get_json()['availability']
        assert len(slots) == 1
        assert slots[0]['day_of_week'] == 2

    def test_set_availability_empty_clears_all(self, client):
        token, _ = setup_doctor(client)
        set_availability(client, token, [{'day_of_week': 0, 'start_time': '09:00', 'end_time': '17:00'}])
        set_availability(client, token, [])
        slots = client.get('/doctorAvailability', headers=auth_headers(token)).get_json()['availability']
        assert slots == []

    def test_invalid_day_of_week_rejected(self, client):
        token, _ = setup_doctor(client)
        res = set_availability(client, token, [{'day_of_week': 7, 'start_time': '09:00', 'end_time': '12:00'}])
        assert res.status_code == 400
        assert 'Invalid day_of_week' in res.get_json()['error']

    def test_start_after_end_rejected(self, client):
        token, _ = setup_doctor(client)
        res = set_availability(client, token, [{'day_of_week': 0, 'start_time': '17:00', 'end_time': '09:00'}])
        assert res.status_code == 400
        assert 'before end time' in res.get_json()['error']

    def test_overlapping_windows_on_same_day_rejected(self, client):
        token, _ = setup_doctor(client)
        res = set_availability(client, token, [
            {'day_of_week': 0, 'start_time': '09:00', 'end_time': '12:00'},
            {'day_of_week': 0, 'start_time': '11:00', 'end_time': '14:00'},
        ])
        assert res.status_code == 400
        assert 'overlap' in res.get_json()['error']

    def test_adjacent_windows_and_same_hours_on_other_days_allowed(self, client):
        token, _ = setup_doctor(client)
        res = set_availability(client, token, [
            {'day_of_week': 0, 'start_time': '09:00', 'end_time': '12:00'},
            {'day_of_week': 0, 'start_time': '12:00', 'end_time': '14:00'},
            {'day_of_week': 1, 'start_time': '09:00', 'end_time': '12:00'},
        ])
        assert res.status_code == 200

    def test_malformed_time_rejected(self, client):
        token, _ = setup_doctor(client)
        res = set_availability(client, token, [{'day_of_week': 0, 'start_time': '9:00', 'end_time': '12:00'}])
        assert res.status_code == 400
        assert 'HH:MM' in res.get_json()['error']

    def test_missing_time_rejected_without_server_error(self, client):
        token, _ = setup_doctor(client)
        res = set_availability(client, token, [{'day_of_week': 0}])
        assert res.status_code == 400

    def test_time_off_half_hour_rejected(self, client):
        token, _ = setup_doctor(client)
        res = set_availability(client, token, [{'day_of_week': 0, 'start_time': '09:15', 'end_time': '12:00'}])
        assert res.status_code == 400
        assert '30-minute' in res.get_json()['error']

    def test_clients_cannot_set_availability(self, client):
        register_client(client)
        token = get_token(login_client(client))
        res = set_availability(client, token, [])
        assert res.status_code == 403

    def test_requires_auth(self, client):
        res = client.put('/doctorAvailability',
                         json={'availability': [{'day_of_week': 0, 'start_time': '09:00', 'end_time': '17:00'}]},
                         headers=auth_headers('badtoken'))
        assert res.status_code == 422


class TestAvailableSlots:
    def test_no_availability_returns_empty_slots(self, client):
        _, doctor_id = setup_doctor(client)
        register_client(client)
        client_token = get_token(login_client(client))
        res = get_slots(client, client_token, doctor_id, next_weekday(0))
        assert res.status_code == 200
        assert res.get_json()['slots'] == []

    def test_availability_generates_30min_slots(self, client):
        _, client_token, doctor_id, monday = monday_9_to_11(client)
        slots = get_slots(client, client_token, doctor_id, monday).get_json()['slots']
        assert slots == ['09:00', '09:30', '10:00', '10:30']

    def test_booked_slot_excluded_from_available(self, client):
        _, client_token, doctor_id, monday = monday_9_to_11(client)
        client.post('/AddAppointment', json={
            'doctor_id': doctor_id, 'date': monday,
            'time_from': '09:00', 'time_to': '09:30',
        }, headers=auth_headers(client_token))
        slots = get_slots(client, client_token, doctor_id, monday).get_json()['slots']
        assert '09:00' not in slots
        assert '09:30' in slots

    def test_declined_appointment_slot_is_available(self, client):
        doctor_token, client_token, doctor_id, monday = monday_9_to_11(client)
        client.post('/AddAppointment', json={
            'doctor_id': doctor_id, 'date': monday,
            'time_from': '09:00', 'time_to': '09:30',
        }, headers=auth_headers(client_token))
        appt_id = client.get('/doctorAppointments', headers=auth_headers(doctor_token)).get_json()['appointments'][0]['id']
        client.patch(f'/doctorAppointments/{appt_id}/status',
                     json={'status': 'declined'}, headers=auth_headers(doctor_token))
        slots = get_slots(client, client_token, doctor_id, monday).get_json()['slots']
        assert '09:00' in slots

    def test_own_appointment_can_be_excluded_when_editing(self, client):
        _, client_token, doctor_id, monday = monday_9_to_11(client)
        client.post('/AddAppointment', json={
            'doctor_id': doctor_id, 'date': monday, 'time_from': '09:00', 'time_to': '09:30',
        }, headers=auth_headers(client_token))
        appt_id = client.get('/ShowAppointment', headers=auth_headers(client_token)).get_json()['appointments'][0]['id']
        slots = get_slots(client, client_token, doctor_id, monday, exclude_appointment_id=appt_id).get_json()['slots']
        assert '09:00' in slots

    def test_other_clients_appointment_cannot_be_excluded(self, client):
        _, client_token, doctor_id, monday = monday_9_to_11(client)
        client.post('/AddAppointment', json={
            'doctor_id': doctor_id, 'date': monday, 'time_from': '09:00', 'time_to': '09:30',
        }, headers=auth_headers(client_token))
        appt_id = client.get('/ShowAppointment', headers=auth_headers(client_token)).get_json()['appointments'][0]['id']
        register_client(client, email='client2@test.com', username='client2')
        other_token = get_token(login_client(client, email='client2@test.com'))
        slots = get_slots(client, other_token, doctor_id, monday, exclude_appointment_id=appt_id).get_json()['slots']
        assert '09:00' not in slots

    def test_past_date_has_no_slots(self, client):
        _, client_token, doctor_id, _ = monday_9_to_11(client)
        res = get_slots(client, client_token, doctor_id, '2000-01-03')  # a Monday
        assert res.get_json()['slots'] == []

    def test_unknown_doctor_returns_404(self, client):
        register_client(client)
        client_token = get_token(login_client(client))
        res = get_slots(client, client_token, 9999, next_weekday(0))
        assert res.status_code == 404

    def test_missing_date_param_returns_400(self, client):
        _, doctor_id = setup_doctor(client)
        register_client(client)
        client_token = get_token(login_client(client))
        res = client.get(f'/doctors/{doctor_id}/availableSlots', headers=auth_headers(client_token))
        assert res.status_code == 400

    def test_invalid_date_format_returns_400(self, client):
        _, doctor_id = setup_doctor(client)
        register_client(client)
        client_token = get_token(login_client(client))
        res = get_slots(client, client_token, doctor_id, '01-12-2099')
        assert res.status_code == 400
