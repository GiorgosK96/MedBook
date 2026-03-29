from helpers import register_client, register_doctor, login_client, login_doctor, auth_headers


# ===========================================================================
# GET /account
# ===========================================================================

class TestGetAccount:
    def test_get_client_account(self, client):
        register_client(client)
        token = login_client(client).get_json()['token']

        res = client.get('/account?role=client', headers=auth_headers(token))
        assert res.status_code == 200
        data = res.get_json()
        assert data['username'] == 'clientuser'
        assert data['email'] == 'client@test.com'
        assert data['role'] == 'client'
        assert 'password' not in data

    def test_get_doctor_account(self, client):
        register_doctor(client)
        token = login_doctor(client).get_json()['token']

        res = client.get('/account?role=doctor', headers=auth_headers(token))
        assert res.status_code == 200
        data = res.get_json()
        assert data['username'] == 'docuser'
        assert data['specialization'] == 'Cardiology'
        assert data['role'] == 'doctor'
        assert 'password' not in data

    def test_get_account_invalid_role_returns_400(self, client):
        register_client(client)
        token = login_client(client).get_json()['token']

        res = client.get('/account?role=admin', headers=auth_headers(token))
        assert res.status_code == 400

    def test_get_account_requires_auth(self, client):
        res = client.get('/account?role=client', headers=auth_headers('badtoken'))
        assert res.status_code == 422


# ===========================================================================
# PUT /account — update name & email
# ===========================================================================

class TestUpdateAccountBasic:
    def test_client_update_full_name(self, client):
        register_client(client)
        token = login_client(client).get_json()['token']

        res = client.put('/account', json={
            'role': 'client',
            'full_name': 'Updated Name',
            'email': 'client@test.com',
        }, headers=auth_headers(token))
        assert res.status_code == 200
        assert res.get_json()['full_name'] == 'Updated Name'

    def test_client_update_email(self, client):
        register_client(client)
        token = login_client(client).get_json()['token']

        res = client.put('/account', json={
            'role': 'client',
            'full_name': 'Test Client',
            'email': 'new_email@test.com',
        }, headers=auth_headers(token))
        assert res.status_code == 200
        assert res.get_json()['email'] == 'new_email@test.com'

    def test_doctor_update_full_name(self, client):
        register_doctor(client)
        token = login_doctor(client).get_json()['token']

        res = client.put('/account', json={
            'role': 'doctor',
            'full_name': 'Dr. Updated',
            'email': 'doc@test.com',
        }, headers=auth_headers(token))
        assert res.status_code == 200
        assert res.get_json()['full_name'] == 'Dr. Updated'

    def test_update_email_duplicate_rejected(self, client):
        register_client(client)
        register_client(client, email='other@test.com', username='other')
        token = login_client(client).get_json()['token']

        res = client.put('/account', json={
            'role': 'client',
            'full_name': 'Test Client',
            'email': 'other@test.com',
        }, headers=auth_headers(token))
        assert res.status_code == 400
        assert 'Email already in use' in res.get_json()['error']

    def test_update_full_name_too_short_rejected(self, client):
        register_client(client)
        token = login_client(client).get_json()['token']

        res = client.put('/account', json={
            'role': 'client',
            'full_name': 'A',
            'email': 'client@test.com',
        }, headers=auth_headers(token))
        assert res.status_code == 400

    def test_update_account_requires_auth(self, client):
        res = client.put('/account', json={'role': 'client', 'full_name': 'X', 'email': 'x@x.com'},
                         headers=auth_headers('badtoken'))
        assert res.status_code == 422


# ===========================================================================
# PUT /account — password change
# ===========================================================================

class TestUpdateAccountPassword:
    def test_change_password_success(self, client):
        register_client(client)
        token = login_client(client).get_json()['token']

        res = client.put('/account', json={
            'role': 'client',
            'full_name': 'Test Client',
            'email': 'client@test.com',
            'current_password': 'pass123',
            'new_password': 'newpass456',
        }, headers=auth_headers(token))
        assert res.status_code == 200

        login_res = login_client(client, password='newpass456')
        assert login_res.status_code == 200

    def test_change_password_wrong_current_rejected(self, client):
        register_client(client)
        token = login_client(client).get_json()['token']

        res = client.put('/account', json={
            'role': 'client',
            'full_name': 'Test Client',
            'email': 'client@test.com',
            'current_password': 'wrongpass',
            'new_password': 'newpass456',
        }, headers=auth_headers(token))
        assert res.status_code == 400
        assert 'incorrect' in res.get_json()['error'].lower()

    def test_change_password_missing_current_rejected(self, client):
        register_client(client)
        token = login_client(client).get_json()['token']

        res = client.put('/account', json={
            'role': 'client',
            'full_name': 'Test Client',
            'email': 'client@test.com',
            'new_password': 'newpass456',
        }, headers=auth_headers(token))
        assert res.status_code == 400
        assert 'required' in res.get_json()['error'].lower()

    def test_change_password_too_short_rejected(self, client):
        register_client(client)
        token = login_client(client).get_json()['token']

        res = client.put('/account', json={
            'role': 'client',
            'full_name': 'Test Client',
            'email': 'client@test.com',
            'current_password': 'pass123',
            'new_password': 'abc',
        }, headers=auth_headers(token))
        assert res.status_code == 400
        assert '6 characters' in res.get_json()['error']
