import pytest
from rest_framework import status

from accounts.models import Address

URL = '/api/addresses/'
PAYLOAD = {
    'title': 'office',
    'reverse_name': 'sara',
    'phone_number': '09120001111',
    'city': 'Shiraz',
    'postal_code': '7123456789',
    'full_address': 'Zand Blvd',
}


@pytest.mark.django_db
class TestAddress:
    def test_request_auth(self, api_client):
        assert api_client.get(URL).status_code == 401

    def test_address_becomes_default(self, auth_client):
        resp = auth_client.post(URL, PAYLOAD)
        assert resp.status_code == 201
        assert resp.data['is_default'] is True

    def test_new_default_replaces_old_default(self, auth_client, address):
        resp = auth_client.post(URL, {**PAYLOAD, 'is_default': True})
        assert resp.status_code == 201
        address.refresh_from_db()
        assert address.is_default is False
        assert Address.objects.filter(user=address.user, is_default=True).count() == 1

    def test_second_address_is_not_default_by_default(self, auth_client, address):
        resp = auth_client.post(URL, PAYLOAD)
        assert resp.data['is_default'] is False

    def test_list_shows_only_own_address(self, seller_client, address, auth_client):
        seller_client.post(URL, PAYLOAD)
        resp = auth_client.get(URL)
        assert resp.data['count'] == 1
        assert resp.data['results'][0]['id'] == address.id

    def test_cannot_access_other_address(self, seller_client, address):
        assert seller_client.get(f'{URL}{address.id}/').status_code == 404
        assert seller_client.delete(f'{URL}{address.id}/').status_code == 404

    def test_invalid_postal_code(self, auth_client):
        resp = auth_client.post(URL,{**PAYLOAD, 'postal_code': '1234'})
        assert resp.status_code == 400
        assert 'postal_code' in resp.data

    def test_invalid_phone_number(self, auth_client):
        resp = auth_client.post(URL,{**PAYLOAD, 'phone_number': 'abc'})
        assert resp.status_code == 400

    def test_update_and_delete(self, auth_client, address):
        assert auth_client.patch(f'{URL}{address.id}/', {'city':'Isfahan'}).status_code == 200
        address.refresh_from_db()
        assert address.city == 'Isfahan'
        assert auth_client.delete(f'{URL}{address.id}/').status_code == 204

    def test_user_field_cannot_be_spoofed(self, auth_client, seller, customer):
        resp = auth_client.post(URL,{**PAYLOAD, 'user': seller.id})
        assert resp.status_code == 201
        assert Address.objects.get(pk=resp.data['id']).user == customer























