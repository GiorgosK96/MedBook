from helpers import register_client, register_doctor, login_client, login_doctor, auth_headers

FUTURE_DATE = '2099-12-01'


def setup_users(client):
    register_doctor(client)
    doctor_token = login_doctor(client).get_json()['token']

    register_client(client)
    client_token = login_client(client).get_json()['token']

    doctors = client.get('/doctors').get_json()['doctors']
    doctor_id = doctors[0]['id']

    return doctor_token, client_token, doctor_id


def book_appointment(client, client_token, doctor_id, time_from='10:00', time_to='10:30'):
    return client.post('/AddAppointment', json={
        'doctor_id': doctor_id,
        'date': FUTURE_DATE,
        'time_from': time_from,
        'time_to': time_to,
        'comments': '',
    }, headers=auth_headers(client_token))


# ===========================================================================
# List doctor appointments
# ===========================================================================

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
        doctor_token = login_doctor(client).get_json()['token']

        res = client.get('/doctorAppointments', headers=auth_headers(doctor_token))
        assert res.status_code == 200
        assert res.get_json()['appointments'] == []

    def test_list_requires_auth(self, client):
        res = client.get('/doctorAppointments', headers=auth_headers('badtoken'))
        assert res.status_code == 422

    def test_doctor_only_sees_own_appointments(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)

        register_doctor(client, email='doc2@test.com', username='docuser2')
        doctor2_token = login_doctor(client, email='doc2@test.com').get_json()['token']

        res = client.get('/doctorAppointments', headers=auth_headers(doctor2_token))
        assert res.get_json()['appointments'] == []


# ===========================================================================
# Update appointment status (confirm / decline)
# ===========================================================================

class TestUpdateAppointmentStatus:
    def test_doctor_can_confirm_appointment(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        appt_id = client.get('/doctorAppointments', headers=auth_headers(doctor_token)).get_json()['appointments'][0]['id']

        res = client.patch(f'/doctorAppointments/{appt_id}/status',
                           json={'status': 'confirmed'},
                           headers=auth_headers(doctor_token))
        assert res.status_code == 200
        assert 'confirmed' in res.get_json()['message']

    def test_doctor_can_decline_appointment(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        appt_id = client.get('/doctorAppointments', headers=auth_headers(doctor_token)).get_json()['appointments'][0]['id']

        res = client.patch(f'/doctorAppointments/{appt_id}/status',
                           json={'status': 'declined'},
                           headers=auth_headers(doctor_token))
        assert res.status_code == 200
        assert 'declined' in res.get_json()['message']

    def test_invalid_status_rejected(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        appt_id = client.get('/doctorAppointments', headers=auth_headers(doctor_token)).get_json()['appointments'][0]['id']

        res = client.patch(f'/doctorAppointments/{appt_id}/status',
                           json={'status': 'maybe'},
                           headers=auth_headers(doctor_token))
        assert res.status_code == 400
        assert 'Invalid status' in res.get_json()['error']

    def test_status_update_not_found(self, client):
        register_doctor(client)
        doctor_token = login_doctor(client).get_json()['token']

        res = client.patch('/doctorAppointments/9999/status',
                           json={'status': 'confirmed'},
                           headers=auth_headers(doctor_token))
        assert res.status_code == 404

    def test_doctor_cannot_update_another_doctors_appointment(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        appt_id = client.get('/doctorAppointments', headers=auth_headers(doctor_token)).get_json()['appointments'][0]['id']

        register_doctor(client, email='doc2@test.com', username='docuser2')
        doctor2_token = login_doctor(client, email='doc2@test.com').get_json()['token']

        res = client.patch(f'/doctorAppointments/{appt_id}/status',
                           json={'status': 'confirmed'},
                           headers=auth_headers(doctor2_token))
        assert res.status_code == 404


# ===========================================================================
# Delete doctor appointment
# ===========================================================================

class TestDeleteDoctorAppointment:
    def test_doctor_can_delete_own_appointment(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        appt_id = client.get('/doctorAppointments', headers=auth_headers(doctor_token)).get_json()['appointments'][0]['id']

        res = client.delete(f'/doctorAppointments/{appt_id}', headers=auth_headers(doctor_token))
        assert res.status_code == 202
        assert client.get('/doctorAppointments', headers=auth_headers(doctor_token)).get_json()['appointments'] == []

    def test_delete_not_found(self, client):
        register_doctor(client)
        doctor_token = login_doctor(client).get_json()['token']

        res = client.delete('/doctorAppointments/9999', headers=auth_headers(doctor_token))
        assert res.status_code == 404

    def test_doctor_cannot_delete_another_doctors_appointment(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        appt_id = client.get('/doctorAppointments', headers=auth_headers(doctor_token)).get_json()['appointments'][0]['id']

        register_doctor(client, email='doc2@test.com', username='docuser2')
        doctor2_token = login_doctor(client, email='doc2@test.com').get_json()['token']

        res = client.delete(f'/doctorAppointments/{appt_id}', headers=auth_headers(doctor2_token))
        assert res.status_code == 404

    def test_declined_appointment_allows_rebooking(self, client):
        doctor_token, client_token, doctor_id = setup_users(client)
        book_appointment(client, client_token, doctor_id)
        appt_id = client.get('/doctorAppointments', headers=auth_headers(doctor_token)).get_json()['appointments'][0]['id']

        client.patch(f'/doctorAppointments/{appt_id}/status',
                     json={'status': 'declined'},
                     headers=auth_headers(doctor_token))

        res = book_appointment(client, client_token, doctor_id)
        assert res.status_code == 201
