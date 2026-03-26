import pytest
from helpers import register_client, register_doctor, login_client, login_doctor, auth_headers

FUTURE_DATE = '2099-12-01'
PAST_DATE = '2000-01-01'


def setup_users(client):
    register_doctor(client)
    res = login_doctor(client)
    doctor_id = res.get_json().get('id')

    register_client(client)
    token = login_client(client).get_json()['token']

    # Get the doctor's actual id from the /doctors endpoint
    doctors = client.get('/doctors').get_json()['doctors']
    doctor_id = doctors[0]['id']

    return token, doctor_id


def make_appointment(client, token, doctor_id, **overrides):
    payload = {
        'doctor_id': doctor_id,
        'date': FUTURE_DATE,
        'time_from': '10:00',
        'time_to': '10:30',
        'comments': 'Test appointment',
    }
    payload.update(overrides)
    return client.post('/AddAppointment', json=payload, headers=auth_headers(token))


# ===========================================================================
# Create appointment
# ===========================================================================

class TestAddAppointment:
    def test_create_appointment_success(self, client):
        token, doctor_id = setup_users(client)
        res = make_appointment(client, token, doctor_id)
        assert res.status_code == 201
        assert res.get_json()['message'] == 'Appointment created successfully'

    def test_create_appointment_requires_auth(self, client):
        register_doctor(client)
        doctors = client.get('/doctors').get_json()['doctors']
        res = make_appointment(client, 'badtoken', doctors[0]['id'])
        assert res.status_code == 422

    def test_create_appointment_in_past_rejected(self, client):
        token, doctor_id = setup_users(client)
        res = make_appointment(client, token, doctor_id, date=PAST_DATE)
        assert res.status_code == 400
        assert 'past' in res.get_json()['error'].lower()

    def test_create_appointment_invalid_date_format(self, client):
        token, doctor_id = setup_users(client)
        res = make_appointment(client, token, doctor_id, date='01-12-2099')
        assert res.status_code == 400

    def test_create_appointment_end_before_start_rejected(self, client):
        token, doctor_id = setup_users(client)
        res = make_appointment(client, token, doctor_id, time_from='10:30', time_to='10:00')
        assert res.status_code == 400
        assert 'after' in res.get_json()['error'].lower()

    def test_create_appointment_doctor_overlap_rejected(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        # Second client books the same doctor at the same time
        register_client(client, email='client2@test.com', username='client2')
        token2 = login_client(client, email='client2@test.com').get_json()['token']
        res = make_appointment(client, token2, doctor_id)
        assert res.status_code == 400
        assert 'doctor' in res.get_json()['error'].lower()

    def test_create_appointment_client_overlap_rejected(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        # Register a second doctor
        register_doctor(client, email='doc2@test.com', username='docuser2')
        doctors = client.get('/doctors').get_json()['doctors']
        doctor2_id = next(d['id'] for d in doctors if d['id'] != doctor_id)
        res = make_appointment(client, token, doctor2_id)
        assert res.status_code == 400
        assert 'another appointment' in res.get_json()['error'].lower()


# ===========================================================================
# List appointments
# ===========================================================================

class TestShowAppointments:
    def test_list_appointments_empty(self, client):
        register_client(client)
        token = login_client(client).get_json()['token']
        res = client.get('/ShowAppointment', headers=auth_headers(token))
        assert res.status_code == 200
        assert res.get_json()['appointments'] == []

    def test_list_appointments_returns_created(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        res = client.get('/ShowAppointment', headers=auth_headers(token))
        assert res.status_code == 200
        appointments = res.get_json()['appointments']
        assert len(appointments) == 1
        assert appointments[0]['date'] == FUTURE_DATE

    def test_list_appointments_requires_auth(self, client):
        res = client.get('/ShowAppointment', headers=auth_headers('badtoken'))
        assert res.status_code == 422

    def test_client_only_sees_own_appointments(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)

        register_client(client, email='client2@test.com', username='client2')
        token2 = login_client(client, email='client2@test.com').get_json()['token']

        res = client.get('/ShowAppointment', headers=auth_headers(token2))
        assert res.get_json()['appointments'] == []


# ===========================================================================
# Get single appointment
# ===========================================================================

class TestGetAppointment:
    def test_get_appointment_success(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = client.get('/ShowAppointment', headers=auth_headers(token)).get_json()['appointments'][0]['id']

        res = client.get(f'/ShowAppointment/{appt_id}', headers=auth_headers(token))
        assert res.status_code == 200
        data = res.get_json()
        assert data['id'] == appt_id
        assert 'doctor' in data

    def test_get_appointment_not_found(self, client):
        register_client(client)
        token = login_client(client).get_json()['token']
        res = client.get('/ShowAppointment/9999', headers=auth_headers(token))
        assert res.status_code == 404

    def test_get_appointment_other_client_blocked(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = client.get('/ShowAppointment', headers=auth_headers(token)).get_json()['appointments'][0]['id']

        register_client(client, email='client2@test.com', username='client2')
        token2 = login_client(client, email='client2@test.com').get_json()['token']

        res = client.get(f'/ShowAppointment/{appt_id}', headers=auth_headers(token2))
        assert res.status_code == 404


# ===========================================================================
# Update appointment
# ===========================================================================

class TestUpdateAppointment:
    def test_update_appointment_success(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = client.get('/ShowAppointment', headers=auth_headers(token)).get_json()['appointments'][0]['id']

        res = client.put(f'/UpdateAppointment/{appt_id}', json={
            'doctor_id': doctor_id,
            'date': FUTURE_DATE,
            'time_from': '11:00',
            'time_to': '11:30',
            'comments': 'Updated comment',
        }, headers=auth_headers(token))
        assert res.status_code == 200
        assert res.get_json()['message'] == 'Appointment updated successfully'

    def test_update_resets_status_to_pending(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = client.get('/ShowAppointment', headers=auth_headers(token)).get_json()['appointments'][0]['id']

        client.put(f'/UpdateAppointment/{appt_id}', json={
            'doctor_id': doctor_id,
            'date': FUTURE_DATE,
            'time_from': '11:00',
            'time_to': '11:30',
        }, headers=auth_headers(token))

        appt = client.get(f'/ShowAppointment/{appt_id}', headers=auth_headers(token)).get_json()
        assert appt['status'] == 'pending'

    def test_update_appointment_not_found(self, client):
        register_client(client)
        token = login_client(client).get_json()['token']
        res = client.put('/UpdateAppointment/9999', json={
            'date': FUTURE_DATE, 'time_from': '10:00', 'time_to': '10:30',
        }, headers=auth_headers(token))
        assert res.status_code == 404

    def test_update_appointment_to_past_rejected(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = client.get('/ShowAppointment', headers=auth_headers(token)).get_json()['appointments'][0]['id']

        res = client.put(f'/UpdateAppointment/{appt_id}', json={
            'doctor_id': doctor_id,
            'date': PAST_DATE,
            'time_from': '10:00',
            'time_to': '10:30',
        }, headers=auth_headers(token))
        assert res.status_code == 400
        assert 'past' in res.get_json()['error'].lower()


# ===========================================================================
# Delete appointment
# ===========================================================================

class TestDeleteAppointment:
    def test_delete_appointment_success(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = client.get('/ShowAppointment', headers=auth_headers(token)).get_json()['appointments'][0]['id']

        res = client.delete(f'/ShowAppointment/{appt_id}', headers=auth_headers(token))
        assert res.status_code == 202
        assert client.get('/ShowAppointment', headers=auth_headers(token)).get_json()['appointments'] == []

    def test_delete_appointment_not_found(self, client):
        register_client(client)
        token = login_client(client).get_json()['token']
        res = client.delete('/ShowAppointment/9999', headers=auth_headers(token))
        assert res.status_code == 404

    def test_delete_other_clients_appointment_blocked(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = client.get('/ShowAppointment', headers=auth_headers(token)).get_json()['appointments'][0]['id']

        register_client(client, email='client2@test.com', username='client2')
        token2 = login_client(client, email='client2@test.com').get_json()['token']

        res = client.delete(f'/ShowAppointment/{appt_id}', headers=auth_headers(token2))
        assert res.status_code == 404
