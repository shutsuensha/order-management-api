import pytest
from rest_framework.test import APIClient

from users.models import User


@pytest.mark.django_db
def test_registration_is_public():
    response = APIClient().post(
        "/api/users/",
        {
            "username": "new-user",
            "email": "new-user@example.com",
            "age": 25,
            "password": "StrongPassword123!",
        },
        format="json",
    )

    assert response.status_code == 201
    user = User.objects.get(username="new-user")
    assert user.check_password("StrongPassword123!")
    assert "password" not in response.data


@pytest.mark.django_db
def test_user_list_is_admin_only():
    User.objects.create_user(
        username="regular-user",
        email="regular@example.com",
        password="StrongPassword123!",
        age=25,
    )

    response = APIClient().get("/api/users/")

    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_admin_can_manage_users():
    admin = User.objects.create_user(
        username="admin-user",
        email="admin@example.com",
        password="StrongPassword123!",
        age=30,
        is_staff=True,
    )
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.get("/api/users/")

    assert response.status_code == 200
