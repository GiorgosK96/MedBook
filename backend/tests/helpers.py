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
    """Extract the JWT from the Set-Cookie header returned by /login."""
    for cookie_header in response.headers.getlist('Set-Cookie'):
        for part in cookie_header.split(';'):
            part = part.strip()
            if part.startswith('access_token_cookie='):
                return part[len('access_token_cookie='):]
    return None


def auth_headers(token):
    return {'Authorization': f'Bearer {token}'}


def set_full_week_availability(client, doctor_token, start_time='08:00', end_time='18:00'):
    """Give a doctor the same working hours every day, so a booking on any date can succeed."""
    return client.put('/doctorAvailability', json={'availability': [
        {'day_of_week': day, 'start_time': start_time, 'end_time': end_time} for day in range(7)
    ]}, headers=auth_headers(doctor_token))
