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


def auth_headers(token):
    return {'Authorization': f'Bearer {token}'}
