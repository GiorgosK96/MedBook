from datetime import datetime, timedelta
from helpers import register_client, register_doctor, login_client, login_doctor, auth_headers


def next_weekday(weekday):
    today = datetime.now()
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')


def setup_doctor(client):
    register_doctor(client)
    token = login_doctor(client).get_json()['token']
    doctors = client.get('/doctors').get_json()['doctors']
    doctor_id = doctors[0]['id']
    return token, doctor_id


def set_availability(client, token, slots):
    return client.put('/doctorAvailability', json={'availability': slots}, headers=auth_headers(token))


# ===========================================================================
# GET /doctorAvailability
# ===========================================================================

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


# ===========================================================================
# PUT /doctorAvailability
# ===========================================================================

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

    def test_requires_auth(self, client):
        res = client.put('/doctorAvailability',
                         json={'availability': [{'day_of_week': 0, 'start_time': '09:00', 'end_time': '17:00'}]},
                         headers=auth_headers('badtoken'))
        assert res.status_code == 422


# ===========================================================================
# GET /doctors/<id>/availableSlots
# ===========================================================================

class TestAvailableSlots:
    def test_no_availability_returns_empty_slots(self, client):
        register_doctor(client)
        login_doctor(client)
        doctors = client.get('/doctors').get_json()['doctors']
        doctor_id = doctors[0]['id']

        register_client(client)
        client_token = login_client(client).get_json()['token']

        monday = next_weekday(0)
        res = client.get(f'/doctors/{doctor_id}/availableSlots?date={monday}',
                         headers=auth_headers(client_token))
        assert res.status_code == 200
        assert res.get_json()['slots'] == []

    def test_availability_generates_30min_slots(self, client):
        doctor_token, doctor_id = setup_doctor(client)
        register_client(client)
        client_token = login_client(client).get_json()['token']

        monday = next_weekday(0)
        set_availability(client, doctor_token, [{'day_of_week': 0, 'start_time': '09:00', 'end_time': '11:00'}])

        res = client.get(f'/doctors/{doctor_id}/availableSlots?date={monday}',
                         headers=auth_headers(client_token))
        slots = res.get_json()['slots']
        assert '09:00' in slots
        assert '09:30' in slots
        assert '10:00' in slots
        assert '10:30' in slots
        assert len(slots) == 4

    def test_booked_slot_excluded_from_available(self, client):
        doctor_token, doctor_id = setup_doctor(client)
        register_client(client)
        client_token = login_client(client).get_json()['token']

        monday = next_weekday(0)
        set_availability(client, doctor_token, [{'day_of_week': 0, 'start_time': '09:00', 'end_time': '11:00'}])

        client.post('/AddAppointment', json={
            'doctor_id': doctor_id,
            'date': monday,
            'time_from': '09:00',
            'time_to': '09:30',
        }, headers=auth_headers(client_token))

        slots = client.get(f'/doctors/{doctor_id}/availableSlots?date={monday}',
                           headers=auth_headers(client_token)).get_json()['slots']
        assert '09:00' not in slots
        assert '09:30' in slots

    def test_declined_appointment_slot_is_available(self, client):
        doctor_token, doctor_id = setup_doctor(client)
        register_client(client)
        client_token = login_client(client).get_json()['token']

        monday = next_weekday(0)
        set_availability(client, doctor_token, [{'day_of_week': 0, 'start_time': '09:00', 'end_time': '11:00'}])

        client.post('/AddAppointment', json={
            'doctor_id': doctor_id,
            'date': monday,
            'time_from': '09:00',
            'time_to': '09:30',
        }, headers=auth_headers(client_token))

        appt_id = client.get('/doctorAppointments', headers=auth_headers(doctor_token)).get_json()['appointments'][0]['id']
        client.patch(f'/doctorAppointments/{appt_id}/status',
                     json={'status': 'declined'}, headers=auth_headers(doctor_token))

        slots = client.get(f'/doctors/{doctor_id}/availableSlots?date={monday}',
                           headers=auth_headers(client_token)).get_json()['slots']
        assert '09:00' in slots

    def test_missing_date_param_returns_400(self, client):
        doctor_token, doctor_id = setup_doctor(client)
        register_client(client)
        client_token = login_client(client).get_json()['token']

        res = client.get(f'/doctors/{doctor_id}/availableSlots', headers=auth_headers(client_token))
        assert res.status_code == 400

    def test_invalid_date_format_returns_400(self, client):
        doctor_token, doctor_id = setup_doctor(client)
        register_client(client)
        client_token = login_client(client).get_json()['token']

        res = client.get(f'/doctors/{doctor_id}/availableSlots?date=01-12-2099',
                         headers=auth_headers(client_token))
        assert res.status_code == 400
