import pytest
from django.conf import settings
from rest_framework.test import APIClient

from users.models import User
from users.serializers import ProfileSerializer


def test_profile_user_is_read_only():
    serializer = ProfileSerializer()

    assert serializer.fields["user"].read_only


def test_jwt_rotation_and_lifetime_settings():
    assert settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds() == 900
    assert settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].days == 7
    assert settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"] is True
    assert settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"] is True


@pytest.mark.django_db
def test_refresh_token_is_rotated_and_blacklisted():
    User.objects.create_user(
        username="jwt-user",
        email="jwt@example.com",
        password="StrongPassword123!",
        age=25,
    )
    client = APIClient()

    token_response = client.post(
        "/api/token/",
        {"username": "jwt-user", "password": "StrongPassword123!"},
        format="json",
    )
    assert token_response.status_code == 200
    old_refresh = token_response.data["refresh"]

    refresh_response = client.post(
        "/api/token/refresh/",
        {"refresh": old_refresh},
        format="json",
    )
    assert refresh_response.status_code == 200
    assert refresh_response.data["refresh"] != old_refresh

    reused_response = client.post(
        "/api/token/refresh/",
        {"refresh": old_refresh},
        format="json",
    )
    assert reused_response.status_code == 401


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
    assert "password" not in response.data["results"][0]


@pytest.mark.django_db
def test_user_can_view_and_edit_own_profile():
    user = User.objects.create_user(
        username="me-user",
        email="me@example.com",
        password="StrongPassword123!",
        age=25,
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/auth/me/")

    assert response.status_code == 200
    assert response.data["username"] == "me-user"
    assert response.data["profile"] is None

    response = client.patch(
        "/api/auth/me/",
        {
            "email": "updated@example.com",
            "profile": {"bio": "Updated bio"},
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["email"] == "updated@example.com"
    assert response.data["profile"]["bio"] == "Updated bio"
    user.refresh_from_db()
    assert user.email == "updated@example.com"
    assert user.profile.bio == "Updated bio"


@pytest.mark.django_db
def test_me_endpoint_requires_authentication():
    response = APIClient().get("/api/auth/me/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_user_can_change_password_securely():
    user = User.objects.create_user(
        username="password-user",
        email="password@example.com",
        password="OldPassword123!",
        age=25,
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/auth/change-password/",
        {
            "old_password": "OldPassword123!",
            "new_password": "NewPassword456!",
        },
        format="json",
    )

    assert response.status_code == 204
    user.refresh_from_db()
    assert user.check_password("NewPassword456!")
    assert not user.check_password("OldPassword123!")


@pytest.mark.django_db
def test_password_change_rejects_wrong_current_password():
    user = User.objects.create_user(
        username="wrong-password-user",
        email="wrong-password@example.com",
        password="OldPassword123!",
        age=25,
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/auth/change-password/",
        {
            "old_password": "WrongPassword123!",
            "new_password": "NewPassword456!",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "old_password" in response.data["error"]
