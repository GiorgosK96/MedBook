from helpers import (auth_headers, get_token, login_client, login_doctor, register_client,
                     register_doctor, set_full_week_availability)

FUTURE_DATE = '2099-12-01'
PAST_DATE = '2000-01-01'


def setup_users(client):
    """Register a doctor who works 08:00-18:00 every day, plus a logged-in client."""
    register_doctor(client)
    set_full_week_availability(client, get_token(login_doctor(client)))

    register_client(client)
    token = get_token(login_client(client))

    doctor_id = client.get('/doctors').get_json()['doctors'][0]['id']
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


def first_appointment(client, token):
    return client.get('/ShowAppointment', headers=auth_headers(token)).get_json()['appointments'][0]


def second_client_token(client):
    register_client(client, email='client2@test.com', username='client2')
    return get_token(login_client(client, email='client2@test.com'))


def set_status_as_doctor(client, appointment_id, status):
    token = get_token(login_doctor(client))
    return client.patch(f'/doctorAppointments/{appointment_id}/status',
                        json={'status': status}, headers=auth_headers(token))


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

    def test_doctors_cannot_book(self, client):
        _, doctor_id = setup_users(client)
        doctor_token = get_token(login_doctor(client))
        res = make_appointment(client, doctor_token, doctor_id)
        assert res.status_code == 403

    def test_create_appointment_in_past_rejected(self, client):
        token, doctor_id = setup_users(client)
        res = make_appointment(client, token, doctor_id, date=PAST_DATE)
        assert res.status_code == 400
        assert 'past' in res.get_json()['error'].lower()

    def test_create_appointment_invalid_date_format(self, client):
        token, doctor_id = setup_users(client)
        res = make_appointment(client, token, doctor_id, date='01-12-2099')
        assert res.status_code == 400

    def test_create_appointment_missing_times_rejected(self, client):
        token, doctor_id = setup_users(client)
        res = make_appointment(client, token, doctor_id, time_from=None, time_to=None)
        assert res.status_code == 400
        assert 'format' in res.get_json()['error']

    def test_create_appointment_end_before_start_rejected(self, client):
        token, doctor_id = setup_users(client)
        res = make_appointment(client, token, doctor_id, time_from='10:30', time_to='10:00')
        assert res.status_code == 400
        assert 'after' in res.get_json()['error'].lower()

    def test_unknown_doctor_rejected(self, client):
        token, _ = setup_users(client)
        res = make_appointment(client, token, 9999)
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Doctor not found'

    def test_time_outside_doctor_availability_rejected(self, client):
        token, doctor_id = setup_users(client)
        res = make_appointment(client, token, doctor_id, time_from='18:00', time_to='18:30')
        assert res.status_code == 400
        assert 'not available' in res.get_json()['error']

    def test_booking_running_past_end_of_availability_rejected(self, client):
        token, doctor_id = setup_users(client)
        res = make_appointment(client, token, doctor_id, time_from='17:30', time_to='18:30')
        assert res.status_code == 400
        assert 'not available' in res.get_json()['error']

    def test_time_not_on_slot_boundary_rejected(self, client):
        token, doctor_id = setup_users(client)
        res = make_appointment(client, token, doctor_id, time_from='10:15', time_to='10:45')
        assert res.status_code == 400
        assert '30-minute' in res.get_json()['error']

    def test_create_appointment_doctor_overlap_rejected(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        res = make_appointment(client, second_client_token(client), doctor_id)
        assert res.status_code == 400
        assert 'doctor' in res.get_json()['error'].lower()

    def test_partial_overlap_rejected(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id, time_from='10:00', time_to='11:00')
        res = make_appointment(client, second_client_token(client), doctor_id, time_from='10:30', time_to='11:30')
        assert res.status_code == 400

    def test_create_appointment_client_overlap_rejected(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        register_doctor(client, email='doc2@test.com', username='docuser2')
        set_full_week_availability(client, get_token(login_doctor(client, email='doc2@test.com')))
        doctors = client.get('/doctors').get_json()['doctors']
        doctor2_id = next(d['id'] for d in doctors if d['id'] != doctor_id)
        res = make_appointment(client, token, doctor2_id)
        assert res.status_code == 400
        assert 'another appointment' in res.get_json()['error'].lower()


class TestShowAppointments:
    def test_list_appointments_empty(self, client):
        register_client(client)
        token = get_token(login_client(client))
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
        assert appointments[0]['status'] == 'pending'

    def test_list_appointments_requires_auth(self, client):
        res = client.get('/ShowAppointment', headers=auth_headers('badtoken'))
        assert res.status_code == 422

    def test_client_only_sees_own_appointments(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        res = client.get('/ShowAppointment', headers=auth_headers(second_client_token(client)))
        assert res.get_json()['appointments'] == []


class TestGetAppointment:
    def test_get_appointment_success(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = first_appointment(client, token)['id']
        res = client.get(f'/ShowAppointment/{appt_id}', headers=auth_headers(token))
        assert res.status_code == 200
        data = res.get_json()
        assert data['id'] == appt_id
        assert 'doctor' in data

    def test_get_appointment_not_found(self, client):
        register_client(client)
        token = get_token(login_client(client))
        res = client.get('/ShowAppointment/9999', headers=auth_headers(token))
        assert res.status_code == 404

    def test_get_appointment_other_client_blocked(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = first_appointment(client, token)['id']
        res = client.get(f'/ShowAppointment/{appt_id}', headers=auth_headers(second_client_token(client)))
        assert res.status_code == 404


class TestUpdateAppointment:
    def update(self, client, token, appt_id, doctor_id, **overrides):
        payload = {'doctor_id': doctor_id, 'date': FUTURE_DATE, 'time_from': '11:00', 'time_to': '11:30'}
        payload.update(overrides)
        return client.put(f'/UpdateAppointment/{appt_id}', json=payload, headers=auth_headers(token))

    def test_update_appointment_success(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = first_appointment(client, token)['id']
        res = self.update(client, token, appt_id, doctor_id, comments='Updated comment')
        assert res.status_code == 200
        assert res.get_json()['message'] == 'Appointment updated successfully'
        updated = first_appointment(client, token)
        assert (updated['time_from'], updated['comments']) == ('11:00', 'Updated comment')

    def test_appointment_does_not_overlap_with_itself(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id, time_from='10:00', time_to='10:30')
        appt_id = first_appointment(client, token)['id']
        res = self.update(client, token, appt_id, doctor_id, time_from='10:00', time_to='11:00')
        assert res.status_code == 200

    def test_update_appointment_not_found(self, client):
        register_client(client)
        token = get_token(login_client(client))
        res = client.put('/UpdateAppointment/9999', json={
            'date': FUTURE_DATE, 'time_from': '10:00', 'time_to': '10:30',
        }, headers=auth_headers(token))
        assert res.status_code == 404

    def test_other_client_cannot_update(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = first_appointment(client, token)['id']
        res = self.update(client, second_client_token(client), appt_id, doctor_id)
        assert res.status_code == 404

    def test_update_appointment_to_past_rejected(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = first_appointment(client, token)['id']
        res = self.update(client, token, appt_id, doctor_id, date=PAST_DATE)
        assert res.status_code == 400
        assert 'past' in res.get_json()['error'].lower()

    def test_update_outside_availability_rejected(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = first_appointment(client, token)['id']
        res = self.update(client, token, appt_id, doctor_id, time_from='07:00', time_to='07:30')
        assert res.status_code == 400
        assert 'not available' in res.get_json()['error']

    def test_confirmed_appointment_cannot_be_edited(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = first_appointment(client, token)['id']
        set_status_as_doctor(client, appt_id, 'confirmed')
        res = self.update(client, token, appt_id, doctor_id)
        assert res.status_code == 409
        assert first_appointment(client, token)['time_from'] == '10:00'


class TestCancelAppointment:
    def cancel(self, client, token, appt_id):
        return client.delete(f'/ShowAppointment/{appt_id}', headers=auth_headers(token))

    def test_cancel_keeps_appointment_with_cancelled_status(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = first_appointment(client, token)['id']
        res = self.cancel(client, token, appt_id)
        assert res.status_code == 200
        assert first_appointment(client, token)['status'] == 'cancelled'

    def test_confirmed_appointment_can_be_cancelled(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = first_appointment(client, token)['id']
        set_status_as_doctor(client, appt_id, 'confirmed')
        assert self.cancel(client, token, appt_id).status_code == 200

    def test_declined_appointment_cannot_be_cancelled(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = first_appointment(client, token)['id']
        set_status_as_doctor(client, appt_id, 'declined')
        assert self.cancel(client, token, appt_id).status_code == 409

    def test_cancelling_twice_rejected(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = first_appointment(client, token)['id']
        self.cancel(client, token, appt_id)
        assert self.cancel(client, token, appt_id).status_code == 409

    def test_cancelled_slot_can_be_rebooked(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        self.cancel(client, token, first_appointment(client, token)['id'])
        res = make_appointment(client, second_client_token(client), doctor_id)
        assert res.status_code == 201

    def test_cancel_appointment_not_found(self, client):
        register_client(client)
        token = get_token(login_client(client))
        assert self.cancel(client, token, 9999).status_code == 404

    def test_cancel_other_clients_appointment_blocked(self, client):
        token, doctor_id = setup_users(client)
        make_appointment(client, token, doctor_id)
        appt_id = first_appointment(client, token)['id']
        assert self.cancel(client, second_client_token(client), appt_id).status_code == 404
        assert first_appointment(client, token)['status'] == 'pending'
