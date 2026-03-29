import pytest
from helpers import register_client, register_doctor, login_client, login_doctor


# ===========================================================================
# Registration
# ===========================================================================

class TestRegisterClient:
    def test_register_client_success(self, client):
        res = register_client(client)
        assert res.status_code == 201
        assert res.get_json()['message'] == 'Account registered successfully'

    def test_register_client_duplicate_email(self, client):
        register_client(client)
        res = register_client(client, username='other_user')  # same email, different username
        assert res.status_code == 400
        assert 'error' in res.get_json()

    def test_register_client_duplicate_username(self, client):
        register_client(client)
        res = register_client(client, email='other@test.com')  # same username, different email
        assert res.status_code == 400
        assert 'error' in res.get_json()


class TestRegisterDoctor:
    def test_register_doctor_success(self, client):
        res = register_doctor(client)
        assert res.status_code == 201
        assert res.get_json()['message'] == 'Doctor registered successfully'

    def test_register_doctor_missing_specialization(self, client):
        res = client.post('/register', json={
            'full_name': 'Dr. No Spec',
            'username': 'nospec',
            'email': 'nospec@test.com',
            'password': 'pass123',
            'role': 'doctor',
            # specialization intentionally omitted
        })
        assert res.status_code == 400
        assert 'Specialization' in res.get_json()['error']

    def test_register_doctor_duplicate_email(self, client):
        register_doctor(client)
        res = register_doctor(client, username='docuser2')  # same email
        assert res.status_code == 400

    def test_register_doctor_duplicate_username(self, client):
        register_doctor(client)
        res = register_doctor(client, email='other_doc@test.com')  # same username
        assert res.status_code == 400


class TestRegisterInvalidRole:
    def test_register_invalid_role_returns_400(self, client):
        res = client.post('/register', json={
            'full_name': 'Nobody',
            'username': 'nobody',
            'email': 'nobody@test.com',
            'password': 'pass123',
            'role': 'admin',
        })
        assert res.status_code == 400
        assert 'Invalid role' in res.get_json()['error']


# ===========================================================================
# Login
# ===========================================================================

class TestLoginClient:
    def test_login_client_success(self, client):
        register_client(client)
        res = login_client(client)
        assert res.status_code == 200
        data = res.get_json()
        assert 'token' in data
        assert data['role'] == 'client'
        assert data['username'] == 'clientuser'
        # specialization should NOT be present for clients
        assert 'specialization' not in data

    def test_login_client_wrong_password(self, client):
        register_client(client)
        res = client.post('/login', json={
            'email': 'client@test.com',
            'password': 'wrongpassword',
            'role': 'client',
        })
        assert res.status_code == 401
        assert 'error' in res.get_json()

    def test_login_client_nonexistent_email(self, client):
        res = client.post('/login', json={
            'email': 'ghost@test.com',
            'password': 'pass123',
            'role': 'client',
        })
        assert res.status_code == 401

    def test_login_client_with_doctor_role_returns_401(self, client):
        register_client(client)
        res = client.post('/login', json={
            'email': 'client@test.com',
            'password': 'pass123',
            'role': 'doctor',
        })
        assert res.status_code == 401


class TestLoginDoctor:
    def test_login_doctor_success(self, client):
        register_doctor(client)
        res = login_doctor(client)
        assert res.status_code == 200
        data = res.get_json()
        assert 'token' in data
        assert data['role'] == 'doctor'
        assert data['username'] == 'docuser'
        assert data['specialization'] == 'Cardiology'

    def test_login_doctor_wrong_password(self, client):
        register_doctor(client)
        res = client.post('/login', json={
            'email': 'doc@test.com',
            'password': 'wrongpassword',
            'role': 'doctor',
        })
        assert res.status_code == 401

    def test_login_doctor_with_client_role_returns_401(self, client):
        register_doctor(client)
        res = client.post('/login', json={
            'email': 'doc@test.com',
            'password': 'pass123',
            'role': 'client',
        })
        assert res.status_code == 401


class TestLoginInvalidRole:
    def test_login_invalid_role_returns_400(self, client):
        res = client.post('/login', json={
            'email': 'anyone@test.com',
            'password': 'pass123',
            'role': 'superuser',
        })
        assert res.status_code == 400
        assert 'Invalid role' in res.get_json()['error']
