FUTURE_DATE = '2099-12-01'


def register_client(client, *, email='client@test.com', username='clientuser',
                    full_name='Test Client', password='pass123'):
    return client.post('/register', json={
        'full_name': full_name,
        'username': username,
        'email': email,
        'password': password,
        'role': 'client',
    })


def register_doctor(client, *, email='doc@test.com', username='docuser',
                    full_name='Dr. Smith', password='pass123',
                    specialization='Cardiology'):
    return client.post('/register', json={
        'full_name': full_name,
        'username': username,
        'email': email,
        'password': password,
        'role': 'doctor',
        'specialization': specialization,
    })


def login_client(client, email='client@test.com', password='pass123'):
    return client.post('/login', json={'email': email, 'password': password, 'role': 'client'})


def login_doctor(client, email='doc@test.com', password='pass123'):
    return client.post('/login', json={'email': email, 'password': password, 'role': 'doctor'})


def get_token(response):
    for header in response.headers.getlist('Set-Cookie'):
        if header.startswith('access_token_cookie='):
            return header.split(';')[0].split('=', 1)[1]
    return None


def auth_headers(token):
    return {'Authorization': f'Bearer {token}'}


def client_token(client, email='client@test.com', username='clientuser'):
    register_client(client, email=email, username=username)
    return get_token(login_client(client, email=email))


def second_client_token(client):
    return client_token(client, email='client2@test.com', username='client2')


def doctor_token(client, email='doc@test.com', username='docuser'):
    register_doctor(client, email=email, username=username)
    return get_token(login_doctor(client, email=email))


def first_doctor_id(client):
    return client.get('/doctors').get_json()['doctors'][0]['id']


def set_full_week_availability(client, token):
    return client.put('/doctorAvailability', json={'availability': [
        {'day_of_week': day, 'start_time': '08:00', 'end_time': '18:00'} for day in range(7)
    ]}, headers=auth_headers(token))


def setup_users(client):
    doctor = doctor_token(client)
    set_full_week_availability(client, doctor)
    return doctor, client_token(client), first_doctor_id(client)


def book(client, token, doctor_id, **overrides):
    payload = {'doctor_id': doctor_id, 'date': FUTURE_DATE, 'time_from': '10:00', 'time_to': '10:30', **overrides}
    return client.post('/AddAppointment', json=payload, headers=auth_headers(token))


def first_appointment(client, token):
    return client.get('/ShowAppointment', headers=auth_headers(token)).get_json()['appointments'][0]


def setup_booking(client):
    doctor, token, doctor_id = setup_users(client)
    book(client, token, doctor_id)
    return doctor, token, doctor_id, first_appointment(client, token)['id']


def set_status(client, token, appointment_id, status):
    return client.patch(f'/doctorAppointments/{appointment_id}/status',
                        json={'status': status}, headers=auth_headers(token))
