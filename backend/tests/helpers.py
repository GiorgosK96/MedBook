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
