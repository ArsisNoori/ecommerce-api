import pytest
from accounts.models import User

@pytest.mark.django_db
def test_user_defaults():
    user = User.objects.create_user(username='ali', email='', password='pass12345')
    assert user.is_seller is False
    assert user.phone_number == ''
    assert str(user) == 'ali'

def test_project_user_custom__user_model():
    assert User._meta.label == 'accounts.User'