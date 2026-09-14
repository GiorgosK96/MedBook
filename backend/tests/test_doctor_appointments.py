from helpers import (auth_headers, get_token, login_client, login_doctor, register_client,
                     register_doctor, set_full_week_availability)

FUTURE_DATE = '2099-12-01'


def setup_users(client):
    register_doctor(client)
    doctor_token = get_token(login_doctor(client))
    set_full_week_availability(client, doctor_token)

    register_client(client)
    client_token = get_token(login_client(client))

    doctor_id = client.get('/doctors').get_json()['doctors'][0]['id']
    return doctor_token, client_token, doctor_id


def book_appointment(client, client_token, doctor_id, time_from='10:00', time_to='10:30'):
    return client.post('/AddAppointment', json={
        'doctor_id': doctor_id,
        'date': FUTURE_DATE,
        'time_from': time_from,
        'time_to': time_to,
        'comments': '',
    }, headers=auth_headers(client_token))


def first_appointment_id(client, doctor_token):
    return client.get('/doctorAppointments', headers=auth_headers(doctor_token)).get_json()['appointments'][0]['id']


def set_status(client, token, appt_id, status):
    return client.patch(f'/doctorAppointments/{appt_id}/status', json={'status': status}, headers=auth_headers(token))


class TestGetDoctorAppointments:
    def test_list_returns_booked_appointment(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        res = client.get('/doctorAppointments', headers=auth_headers(doctor_token))
        assert res.status_code == 200
        appointments = res.get_json()['appointments']
        assert len(appointments) == 1
        assert appointments[0]['date'] == FUTURE_DATE
        assert 'client' in appointments[0]

    def test_list_empty_when_no_appointments(self, client):
        register_doctor(client)
        doctor_token = get_token(login_doctor(client))
        res = client.get('/doctorAppointments', headers=auth_headers(doctor_token))
        assert res.status_code == 200
        assert res.get_json()['appointments'] == []

    def test_list_requires_auth(self, client):
        res = client.get('/doctorAppointments', headers=auth_headers('badtoken'))
        assert res.status_code == 422

    def test_clients_cannot_list_doctor_appointments(self, client):
        _, client_token, _ = setup_users(client)
        res = client.get('/doctorAppointments', headers=auth_headers(client_token))
        assert res.status_code == 403

    def test_doctor_only_sees_own_appointments(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        register_doctor(client, email='doc2@test.com', username='docuser2')
        doctor2_token = get_token(login_doctor(client, email='doc2@test.com'))
        res = client.get('/doctorAppointments', headers=auth_headers(doctor2_token))
        assert res.get_json()['appointments'] == []

    def test_doctor_sees_client_cancellation(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        appt_id = first_appointment_id(client, doctor_token)
        client.delete(f'/ShowAppointment/{appt_id}', headers=auth_headers(client_token))
        appointments = client.get('/doctorAppointments', headers=auth_headers(doctor_token)).get_json()['appointments']
        assert appointments[0]['status'] == 'cancelled'


class TestUpdateAppointmentStatus:
    def test_doctor_can_confirm_appointment(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        res = set_status(client, doctor_token, first_appointment_id(client, doctor_token), 'confirmed')
        assert res.status_code == 200
        assert 'confirmed' in res.get_json()['message']

    def test_doctor_can_decline_appointment(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        res = set_status(client, doctor_token, first_appointment_id(client, doctor_token), 'declined')
        assert res.status_code == 200
        assert 'declined' in res.get_json()['message']

    def test_doctor_can_cancel_confirmed_appointment(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        appt_id = first_appointment_id(client, doctor_token)
        set_status(client, doctor_token, appt_id, 'confirmed')
        assert set_status(client, doctor_token, appt_id, 'cancelled').status_code == 200

    def test_pending_appointment_cannot_be_cancelled_by_doctor(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        res = set_status(client, doctor_token, first_appointment_id(client, doctor_token), 'cancelled')
        assert res.status_code == 409

    def test_declined_appointment_cannot_be_confirmed(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        appt_id = first_appointment_id(client, doctor_token)
        set_status(client, doctor_token, appt_id, 'declined')
        res = set_status(client, doctor_token, appt_id, 'confirmed')
        assert res.status_code == 409
        assert 'declined' in res.get_json()['error']

    def test_cancelled_appointment_cannot_be_revived(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        appt_id = first_appointment_id(client, doctor_token)
        client.delete(f'/ShowAppointment/{appt_id}', headers=auth_headers(client_token))
        assert set_status(client, doctor_token, appt_id, 'confirmed').status_code == 409

    def test_invalid_status_rejected(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        res = set_status(client, doctor_token, first_appointment_id(client, doctor_token), 'maybe')
        assert res.status_code == 400
        assert 'Invalid status' in res.get_json()['error']

    def test_status_update_not_found(self, client):
        register_doctor(client)
        doctor_token = get_token(login_doctor(client))
        assert set_status(client, doctor_token, 9999, 'confirmed').status_code == 404

    def test_client_cannot_change_status(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        res = set_status(client, client_token, first_appointment_id(client, doctor_token), 'confirmed')
        assert res.status_code == 403

    def test_doctor_cannot_update_another_doctors_appointment(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        appt_id = first_appointment_id(client, doctor_token)
        register_doctor(client, email='doc2@test.com', username='docuser2')
        doctor2_token = get_token(login_doctor(client, email='doc2@test.com'))
        assert set_status(client, doctor2_token, appt_id, 'confirmed').status_code == 404

    def test_declined_appointment_allows_rebooking(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        set_status(client, doctor_token, first_appointment_id(client, doctor_token), 'declined')
        res = book_appointment(client, client_token, doctor_id)
        assert res.status_code == 201
