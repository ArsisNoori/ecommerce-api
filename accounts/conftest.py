import pytest
from django.core.cache import cache
from rest_framework.test import APIClient
from accounts .models import User


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield


@pytest.fixture(autouse=True)
def fast_password_hasher(settings):
    settings.PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']


def make_client(user=None):
    client = APIClient()
    if user is not None:
        client.force_authenticate(user=user)
    return client

@pytest.fixture
def api_client():
    return make_client()


@pytest.fixture
def customer(db):
    return User.objects.create_user(
        username='test',
        email='test@gmail.com',
        password='pass12345'
    )

@pytest.fixture
def seller(db):
    return User.objects.create_user(username='seller1', password='pass12345', is_seller=True)


@pytest.fixture
def other_seller(db):
    return User.objects.create_user(username='seller2', password='pass12345', is_seller=True)


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(username='staff', password='pass12345', is_staff=True)

@pytest.fixture
def auth_client(customer):
    return make_client(customer)


@pytest.fixture
def seller_client(seller):
    return make_client(seller)

@pytest.fixture
def other_seller(other_seller):
    return make_client(other_seller)

@pytest.fixture
def staff_client(staff_user):
    return make_client(staff_user)





