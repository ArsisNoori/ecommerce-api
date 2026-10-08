import pytest
from rest_framework import status

REGISTER_URL = "/api/auth/register/"
PAYLOAD = {
    'username': 'arsis', 'email': 'new@gmail.com',
    'password': 'Str0ng-pass!123', 'password2': 'Str0ng-pass!123'
}

@pytest.mark.django_db
class TestRegister:
    def test_register_success(self,api_client):
        resp = api_client.post(REGISTER_URL, PAYLOAD)
        assert resp.status_code == status.HTTP_201_CREATED
        assert 'password' not in resp.data and 'password2' not in resp.data

    def test_password_hashed(self,api_client):
        from accounts.models import User
        api_client.post(REGISTER_URL, PAYLOAD)
        user = User.objects.get(username='arsis')
        assert user.password != PAYLOAD['password']
        assert user.check_password(PAYLOAD['password'])
    def test_default_is_not_seller(self,api_client):
        from accounts.models import User
        api_client.post(REGISTER_URL, PAYLOAD)
        assert User.objects.get(username='arsis').is_seller is False

    def test_password_mismatch(self,api_client):
        resp = api_client.post(REGISTER_URL, {**PAYLOAD, 'password': "different"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password2' in resp.data

    def test_weak_password_rejected(self,api_client):
        resp = api_client.post(REGISTER_URL, {
            **PAYLOAD, 'password': "12345678",
            "password2": "12345678"
            }
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in resp.data

    def test_duplicate_email(self,api_client, customer):
        resp = api_client.post(REGISTER_URL, {**PAYLOAD, 'email': "test@gmail.com"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in resp.data

    def test_duplicate_username_rejected(self,api_client, customer):
        resp = api_client.post(REGISTER_URL, {**PAYLOAD, 'username': 'test'})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestLoginLogout:
    def test_login_returns_tokens(self, api_client, customer):
        resp = api_client.post("/api/auth/token/", {"username": "test", "password":
            "pass12345"})
        assert resp.status_code == 200
        assert "access" in resp.data and "refresh" in resp.data

    def test_wrong_password(self, api_client, customer):
        resp = api_client.post("/api/auth/token/", {"username": "test", "password": "nope"})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_rotates_token(self, api_client, customer):
        tokens = api_client.post("/api/auth/token/", {"username": "test", "password":"pass12345"}).data
        resp = api_client.post("/api/auth/token/refresh/", {"refresh": tokens["refresh"]})
        assert resp.status_code == 200
        assert resp.data["refresh"] != tokens["refresh"]
        assert api_client.post("/api/auth/token/refresh/", {"refresh":tokens["refresh"]}).status_code == 401

    def test_access_token_authenticates(self, api_client, customer):
        token = api_client.post("/api/auth/token/", {"username": "test", "password":"pass12345"}).data
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token['access']}")
        assert api_client.get("/api/auth/me/").status_code == status.HTTP_200_OK

@pytest.mark.django_db
class TestProfile:
    def test_me_requires_auth(self, api_client):
        assert api_client.get("/api/auth/me/").status_code == 401

    def test_me_returns_profile(self, auth_client):
        resp = auth_client.get("/api/auth/me/")
        assert resp.status_code == 200
        assert resp.data["username"] == "test"

    def test_patch_update_phone(self, auth_client, customer):
        resp = auth_client.patch("/api/auth/me/", {"phone_number": "09120000000"})
        assert resp.status_code == 200
        customer.refresh_from_db()
        assert customer.phone_number == "09120000000"

    def test_cannot_promote_self_seller(self, auth_client, customer):
        auth_client.patch("/api/auth/me/", {"is_seller": True, 'is_staff': True})
        customer.refresh_from_db()
        assert customer.is_seller is False and customer.is_staff is False

    def test_cannot_other_users_email(self, auth_client, seller):
        seller.email = 'token@example.com'
        seller.save()
        resp = auth_client.patch("/api/auth/me/", {'email': 'token@example.com'})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestChangePassword:
    URL = '/api/auth/change_password/'

    def test_wrong_old_password(self, auth_client, customer):
        resp = auth_client.post(self.URL, {'old_password': "bad", "new_password": "newPassword12345"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_success_then_login_with_new_password(self, auth_client, api_client):
        resp = auth_client.post(self.URL, {'old_password': "pass12345", "new_password": "newPass12345"})
        assert resp.status_code == status.HTTP_200_OK
        login = api_client.post('/api/auth/token/', {'username': 'test', 'password': 'newPass12345'})
        assert login.status_code == status.HTTP_200_OK

    def test_weak_new_password(self, auth_client):
        resp = auth_client.post(self.URL, {'old_password': "pass12345", "new_password": "1234"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST














