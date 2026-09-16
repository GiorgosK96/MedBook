from helpers import auth_headers, client_token, doctor_token, login_client, register_client


def update_account(client, token, **fields):
    payload = {'full_name': 'Test Client', 'email': 'client@test.com', **fields}
    return client.put('/account', json=payload, headers=auth_headers(token))


class TestGetAccount:
    def test_get_client_account(self, client):
        res = client.get('/account', headers=auth_headers(client_token(client)))
        assert res.status_code == 200
        data = res.get_json()
        assert data['username'] == 'clientuser'
        assert data['email'] == 'client@test.com'
        assert data['role'] == 'client'
        assert 'password' not in data

    def test_get_doctor_account(self, client):
        res = client.get('/account', headers=auth_headers(doctor_token(client)))
        assert res.status_code == 200
        data = res.get_json()
        assert data['username'] == 'docuser'
        assert data['specialization'] == 'Cardiology'
        assert data['role'] == 'doctor'
        assert 'password' not in data

    def test_role_derived_from_token_not_query_param(self, client):
        res = client.get('/account?role=client', headers=auth_headers(doctor_token(client)))
        assert res.status_code == 200
        assert res.get_json()['role'] == 'doctor'

    def test_requires_auth(self, client):
        assert client.get('/account', headers=auth_headers('badtoken')).status_code == 422


class TestUpdateAccount:
    def test_update_name_and_email(self, client):
        res = update_account(client, client_token(client), full_name='Updated Name', email='new@test.com')
        assert res.status_code == 200
        data = res.get_json()
        assert (data['full_name'], data['email']) == ('Updated Name', 'new@test.com')

    def test_duplicate_email_rejected(self, client):
        token = client_token(client)
        register_client(client, email='other@test.com', username='other')
        res = update_account(client, token, email='other@test.com')
        assert res.status_code == 400
        assert 'Email already in use' in res.get_json()['error']

    def test_short_full_name_rejected(self, client):
        assert update_account(client, client_token(client), full_name='A').status_code == 400

    def test_requires_auth(self, client):
        assert update_account(client, 'badtoken').status_code == 422


class TestChangePassword:
    def test_change_password_success(self, client):
        res = update_account(client, client_token(client), current_password='pass123', new_password='newpass456')
        assert res.status_code == 200
        assert login_client(client, password='newpass456').status_code == 200

    def test_wrong_current_password_rejected(self, client):
        res = update_account(client, client_token(client), current_password='wrongpass', new_password='newpass456')
        assert res.status_code == 400
        assert 'incorrect' in res.get_json()['error']

    def test_missing_current_password_rejected(self, client):
        res = update_account(client, client_token(client), new_password='newpass456')
        assert res.status_code == 400
        assert 'required' in res.get_json()['error']

    def test_short_new_password_rejected(self, client):
        res = update_account(client, client_token(client), current_password='pass123', new_password='abc')
        assert res.status_code == 400
        assert '6 characters' in res.get_json()['error']
