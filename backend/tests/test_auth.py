from helpers import get_token, login_client, login_doctor, register_client, register_doctor


class TestRegister:
    def test_register_client_success(self, client):
        res = register_client(client)
        assert res.status_code == 201
        assert res.get_json()['message'] == 'Account registered successfully'

    def test_register_doctor_success(self, client):
        res = register_doctor(client)
        assert res.status_code == 201
        assert res.get_json()['message'] == 'Doctor registered successfully'

    def test_duplicate_email_rejected(self, client):
        register_client(client)
        res = register_client(client, username='other_user')
        assert res.status_code == 400
        assert 'already registered' in res.get_json()['error']

    def test_duplicate_username_rejected(self, client):
        register_client(client)
        res = register_client(client, email='other@test.com')
        assert res.status_code == 400
        assert 'already registered' in res.get_json()['error']

    def test_doctor_without_specialization_rejected(self, client):
        res = register_doctor(client, specialization='')
        assert res.status_code == 400
        assert 'Specialization' in res.get_json()['error']

    def test_invalid_role_rejected(self, client):
        res = client.post('/register', json={'role': 'admin'})
        assert res.status_code == 400
        assert 'Invalid role' in res.get_json()['error']

    def test_blank_fields_rejected(self, client):
        res = register_client(client, full_name='   ', username='')
        assert res.status_code == 400
        error = res.get_json()['error']
        assert 'full_name' in error and 'username' in error

    def test_short_password_rejected(self, client):
        res = register_client(client, password='abc')
        assert res.status_code == 400
        assert '6 characters' in res.get_json()['error']

    def test_empty_body_rejected(self, client):
        assert client.post('/register').status_code == 400


class TestLogin:
    def test_client_login_success(self, client):
        register_client(client)
        res = login_client(client)
        assert res.status_code == 200
        data = res.get_json()
        assert get_token(res) is not None
        assert data['role'] == 'client'
        assert data['username'] == 'clientuser'
        assert 'specialization' not in data

    def test_doctor_login_success(self, client):
        register_doctor(client)
        res = login_doctor(client)
        assert res.status_code == 200
        data = res.get_json()
        assert get_token(res) is not None
        assert data['role'] == 'doctor'
        assert data['username'] == 'docuser'
        assert data['specialization'] == 'Cardiology'

    def test_wrong_password_rejected(self, client):
        register_client(client)
        res = login_client(client, password='wrongpassword')
        assert res.status_code == 401
        assert 'error' in res.get_json()

    def test_unknown_email_rejected(self, client):
        assert login_client(client, email='ghost@test.com').status_code == 401

    def test_missing_password_rejected(self, client):
        register_client(client)
        res = client.post('/login', json={'email': 'client@test.com', 'role': 'client'})
        assert res.status_code == 401

    def test_client_cannot_login_as_doctor(self, client):
        register_client(client)
        assert login_doctor(client, email='client@test.com').status_code == 401

    def test_doctor_cannot_login_as_client(self, client):
        register_doctor(client)
        assert login_client(client, email='doc@test.com').status_code == 401

    def test_invalid_role_rejected(self, client):
        res = client.post('/login', json={'email': 'anyone@test.com', 'password': 'pass123', 'role': 'superuser'})
        assert res.status_code == 400
        assert 'Invalid role' in res.get_json()['error']
