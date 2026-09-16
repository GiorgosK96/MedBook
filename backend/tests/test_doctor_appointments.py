from helpers import FUTURE_DATE, auth_headers, book, client_token, doctor_token, set_status, setup_booking


def doctor_appointments(client, token):
    return client.get('/doctorAppointments', headers=auth_headers(token))


def other_doctor_token(client):
    return doctor_token(client, email='doc2@test.com', username='docuser2')


class TestGetDoctorAppointments:
    def test_returns_booked_appointment(self, client):
        doctor, _, _, _ = setup_booking(client)
        res = doctor_appointments(client, doctor)
        assert res.status_code == 200
        appointments = res.get_json()['appointments']
        assert len(appointments) == 1
        assert appointments[0]['date'] == FUTURE_DATE
        assert 'client' in appointments[0]

    def test_empty_list(self, client):
        res = doctor_appointments(client, doctor_token(client))
        assert res.status_code == 200
        assert res.get_json()['appointments'] == []

    def test_requires_auth(self, client):
        assert doctor_appointments(client, 'badtoken').status_code == 422

    def test_clients_cannot_list(self, client):
        assert doctor_appointments(client, client_token(client)).status_code == 403

    def test_doctor_only_sees_own_appointments(self, client):
        setup_booking(client)
        assert doctor_appointments(client, other_doctor_token(client)).get_json()['appointments'] == []

    def test_doctor_sees_client_cancellation(self, client):
        doctor, token, _, appt_id = setup_booking(client)
        client.delete(f'/ShowAppointment/{appt_id}', headers=auth_headers(token))
        assert doctor_appointments(client, doctor).get_json()['appointments'][0]['status'] == 'cancelled'


class TestUpdateAppointmentStatus:
    def test_doctor_can_confirm(self, client):
        doctor, _, _, appt_id = setup_booking(client)
        res = set_status(client, doctor, appt_id, 'confirmed')
        assert res.status_code == 200
        assert 'confirmed' in res.get_json()['message']

    def test_doctor_can_decline(self, client):
        doctor, _, _, appt_id = setup_booking(client)
        res = set_status(client, doctor, appt_id, 'declined')
        assert res.status_code == 200
        assert 'declined' in res.get_json()['message']

    def test_doctor_can_cancel_confirmed(self, client):
        doctor, _, _, appt_id = setup_booking(client)
        set_status(client, doctor, appt_id, 'confirmed')
        assert set_status(client, doctor, appt_id, 'cancelled').status_code == 200

    def test_pending_cannot_be_cancelled_by_doctor(self, client):
        doctor, _, _, appt_id = setup_booking(client)
        assert set_status(client, doctor, appt_id, 'cancelled').status_code == 409

    def test_declined_cannot_be_confirmed(self, client):
        doctor, _, _, appt_id = setup_booking(client)
        set_status(client, doctor, appt_id, 'declined')
        res = set_status(client, doctor, appt_id, 'confirmed')
        assert res.status_code == 409
        assert 'declined' in res.get_json()['error']

    def test_cancelled_cannot_be_revived(self, client):
        doctor, token, _, appt_id = setup_booking(client)
        client.delete(f'/ShowAppointment/{appt_id}', headers=auth_headers(token))
        assert set_status(client, doctor, appt_id, 'confirmed').status_code == 409

    def test_invalid_status_rejected(self, client):
        doctor, _, _, appt_id = setup_booking(client)
        res = set_status(client, doctor, appt_id, 'maybe')
        assert res.status_code == 400
        assert 'Invalid status' in res.get_json()['error']

    def test_not_found(self, client):
        assert set_status(client, doctor_token(client), 9999, 'confirmed').status_code == 404

    def test_client_cannot_change_status(self, client):
        _, token, _, appt_id = setup_booking(client)
        assert set_status(client, token, appt_id, 'confirmed').status_code == 403

    def test_doctor_cannot_update_another_doctors_appointment(self, client):
        _, _, _, appt_id = setup_booking(client)
        assert set_status(client, other_doctor_token(client), appt_id, 'confirmed').status_code == 404

    def test_declined_appointment_allows_rebooking(self, client):
        doctor, token, doctor_id, appt_id = setup_booking(client)
        set_status(client, doctor, appt_id, 'declined')
        assert book(client, token, doctor_id).status_code == 201
