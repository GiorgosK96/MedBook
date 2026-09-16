from helpers import (FUTURE_DATE, auth_headers, book, client_token, doctor_token, first_appointment,
                     second_client_token, set_full_week_availability, set_status, setup_booking, setup_users)

PAST_DATE = '2000-01-01'


class TestAddAppointment:
    def test_create_appointment_success(self, client):
        _, token, doctor_id = setup_users(client)
        res = book(client, token, doctor_id)
        assert res.status_code == 201
        assert res.get_json()['message'] == 'Appointment created successfully'

    def test_requires_auth(self, client):
        assert book(client, 'badtoken', 1).status_code == 422

    def test_doctors_cannot_book(self, client):
        doctor, _, doctor_id = setup_users(client)
        assert book(client, doctor, doctor_id).status_code == 403

    def test_past_date_rejected(self, client):
        _, token, doctor_id = setup_users(client)
        res = book(client, token, doctor_id, date=PAST_DATE)
        assert res.status_code == 400
        assert 'past' in res.get_json()['error']

    def test_invalid_date_format_rejected(self, client):
        _, token, doctor_id = setup_users(client)
        assert book(client, token, doctor_id, date='01-12-2099').status_code == 400

    def test_missing_times_rejected(self, client):
        _, token, doctor_id = setup_users(client)
        res = book(client, token, doctor_id, time_from=None, time_to=None)
        assert res.status_code == 400
        assert 'format' in res.get_json()['error']

    def test_end_before_start_rejected(self, client):
        _, token, doctor_id = setup_users(client)
        res = book(client, token, doctor_id, time_from='10:30', time_to='10:00')
        assert res.status_code == 400
        assert 'after' in res.get_json()['error']

    def test_unknown_doctor_rejected(self, client):
        _, token, _ = setup_users(client)
        res = book(client, token, 9999)
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Doctor not found'

    def test_time_outside_availability_rejected(self, client):
        _, token, doctor_id = setup_users(client)
        res = book(client, token, doctor_id, time_from='18:00', time_to='18:30')
        assert res.status_code == 400
        assert 'not available' in res.get_json()['error']

    def test_booking_running_past_end_of_availability_rejected(self, client):
        _, token, doctor_id = setup_users(client)
        res = book(client, token, doctor_id, time_from='17:30', time_to='18:30')
        assert res.status_code == 400
        assert 'not available' in res.get_json()['error']

    def test_time_not_on_slot_boundary_rejected(self, client):
        _, token, doctor_id = setup_users(client)
        res = book(client, token, doctor_id, time_from='10:15', time_to='10:45')
        assert res.status_code == 400
        assert '30-minute' in res.get_json()['error']

    def test_doctor_overlap_rejected(self, client):
        _, token, doctor_id = setup_users(client)
        book(client, token, doctor_id)
        res = book(client, second_client_token(client), doctor_id)
        assert res.status_code == 400
        assert 'Doctor already has' in res.get_json()['error']

    def test_partial_overlap_rejected(self, client):
        _, token, doctor_id = setup_users(client)
        book(client, token, doctor_id, time_from='10:00', time_to='11:00')
        res = book(client, second_client_token(client), doctor_id, time_from='10:30', time_to='11:30')
        assert res.status_code == 400

    def test_client_overlap_rejected(self, client):
        _, token, doctor_id = setup_users(client)
        book(client, token, doctor_id)
        set_full_week_availability(client, doctor_token(client, email='doc2@test.com', username='docuser2'))
        doctor2_id = next(d['id'] for d in client.get('/doctors').get_json()['doctors'] if d['id'] != doctor_id)
        res = book(client, token, doctor2_id)
        assert res.status_code == 400
        assert 'another appointment' in res.get_json()['error']


class TestShowAppointments:
    def test_empty_list(self, client):
        res = client.get('/ShowAppointment', headers=auth_headers(client_token(client)))
        assert res.status_code == 200
        assert res.get_json()['appointments'] == []

    def test_returns_created(self, client):
        _, token, _, _ = setup_booking(client)
        res = client.get('/ShowAppointment', headers=auth_headers(token))
        assert res.status_code == 200
        appointments = res.get_json()['appointments']
        assert len(appointments) == 1
        assert appointments[0]['date'] == FUTURE_DATE
        assert appointments[0]['status'] == 'pending'

    def test_requires_auth(self, client):
        assert client.get('/ShowAppointment', headers=auth_headers('badtoken')).status_code == 422

    def test_client_only_sees_own_appointments(self, client):
        setup_booking(client)
        res = client.get('/ShowAppointment', headers=auth_headers(second_client_token(client)))
        assert res.get_json()['appointments'] == []


class TestGetAppointment:
    def test_success(self, client):
        _, token, _, appt_id = setup_booking(client)
        res = client.get(f'/ShowAppointment/{appt_id}', headers=auth_headers(token))
        assert res.status_code == 200
        assert res.get_json()['id'] == appt_id

    def test_not_found(self, client):
        res = client.get('/ShowAppointment/9999', headers=auth_headers(client_token(client)))
        assert res.status_code == 404

    def test_other_client_blocked(self, client):
        _, _, _, appt_id = setup_booking(client)
        res = client.get(f'/ShowAppointment/{appt_id}', headers=auth_headers(second_client_token(client)))
        assert res.status_code == 404


class TestUpdateAppointment:
    def update(self, client, token, appt_id, doctor_id, **overrides):
        payload = {'doctor_id': doctor_id, 'date': FUTURE_DATE, 'time_from': '11:00', 'time_to': '11:30', **overrides}
        return client.put(f'/UpdateAppointment/{appt_id}', json=payload, headers=auth_headers(token))

    def test_success(self, client):
        _, token, doctor_id, appt_id = setup_booking(client)
        res = self.update(client, token, appt_id, doctor_id, comments='Updated comment')
        assert res.status_code == 200
        assert res.get_json()['message'] == 'Appointment updated successfully'
        updated = first_appointment(client, token)
        assert (updated['time_from'], updated['comments']) == ('11:00', 'Updated comment')

    def test_appointment_does_not_overlap_with_itself(self, client):
        _, token, doctor_id, appt_id = setup_booking(client)
        res = self.update(client, token, appt_id, doctor_id, time_from='10:00', time_to='11:00')
        assert res.status_code == 200

    def test_not_found(self, client):
        assert self.update(client, client_token(client), 9999, 1).status_code == 404

    def test_other_client_cannot_update(self, client):
        _, _, doctor_id, appt_id = setup_booking(client)
        assert self.update(client, second_client_token(client), appt_id, doctor_id).status_code == 404

    def test_past_date_rejected(self, client):
        _, token, doctor_id, appt_id = setup_booking(client)
        res = self.update(client, token, appt_id, doctor_id, date=PAST_DATE)
        assert res.status_code == 400
        assert 'past' in res.get_json()['error']

    def test_outside_availability_rejected(self, client):
        _, token, doctor_id, appt_id = setup_booking(client)
        res = self.update(client, token, appt_id, doctor_id, time_from='07:00', time_to='07:30')
        assert res.status_code == 400
        assert 'not available' in res.get_json()['error']

    def test_confirmed_appointment_cannot_be_edited(self, client):
        doctor, token, doctor_id, appt_id = setup_booking(client)
        set_status(client, doctor, appt_id, 'confirmed')
        assert self.update(client, token, appt_id, doctor_id).status_code == 409
        assert first_appointment(client, token)['time_from'] == '10:00'


class TestCancelAppointment:
    def cancel(self, client, token, appt_id):
        return client.delete(f'/ShowAppointment/{appt_id}', headers=auth_headers(token))

    def test_cancel_keeps_appointment_with_cancelled_status(self, client):
        _, token, _, appt_id = setup_booking(client)
        assert self.cancel(client, token, appt_id).status_code == 200
        assert first_appointment(client, token)['status'] == 'cancelled'

    def test_confirmed_appointment_can_be_cancelled(self, client):
        doctor, token, _, appt_id = setup_booking(client)
        set_status(client, doctor, appt_id, 'confirmed')
        assert self.cancel(client, token, appt_id).status_code == 200

    def test_declined_appointment_cannot_be_cancelled(self, client):
        doctor, token, _, appt_id = setup_booking(client)
        set_status(client, doctor, appt_id, 'declined')
        assert self.cancel(client, token, appt_id).status_code == 409

    def test_cancelling_twice_rejected(self, client):
        _, token, _, appt_id = setup_booking(client)
        self.cancel(client, token, appt_id)
        assert self.cancel(client, token, appt_id).status_code == 409

    def test_cancelled_slot_can_be_rebooked(self, client):
        _, token, doctor_id, appt_id = setup_booking(client)
        self.cancel(client, token, appt_id)
        assert book(client, second_client_token(client), doctor_id).status_code == 201

    def test_not_found(self, client):
        assert self.cancel(client, client_token(client), 9999).status_code == 404

    def test_other_client_blocked(self, client):
        _, token, _, appt_id = setup_booking(client)
        assert self.cancel(client, second_client_token(client), appt_id).status_code == 404
        assert first_appointment(client, token)['status'] == 'pending'
