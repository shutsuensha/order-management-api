import pytest
from django.conf import settings
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

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


def test_auth_throttle_rates_are_configured():
    assert settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["login"] == "5/minute"
    assert (
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["registration"] == "5/minute"
    )
    assert ScopedRateThrottle.scope_attr == "throttle_scope"


@pytest.mark.django_db
def test_refresh_token_is_rotated_and_blacklisted(user_factory):
    user_factory(
        username="jwt-user",
        email="jwt@example.com",
        password="StrongPassword123!",
    )
    client = APIClient()

    token_response = client.post(
        "/api/v1/token/",
        {"username": "jwt-user", "password": "StrongPassword123!"},
        format="json",
    )
    assert token_response.status_code == 200
    old_refresh = token_response.data["refresh"]

    refresh_response = client.post(
        "/api/v1/token/refresh/",
        {"refresh": old_refresh},
        format="json",
    )
    assert refresh_response.status_code == 200
    assert refresh_response.data["refresh"] != old_refresh

    reused_response = client.post(
        "/api/v1/token/refresh/",
        {"refresh": old_refresh},
        format="json",
    )
    assert reused_response.status_code == 401


@pytest.mark.django_db
def test_login_returns_access_and_refresh_tokens(user_factory):
    user_factory(username="login-user", password="StrongPassword123!")

    response = APIClient().post(
        "/api/v1/token/",
        {"username": "login-user", "password": "StrongPassword123!"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["access"]
    assert response.data["refresh"]


@pytest.mark.django_db
def test_login_rejects_invalid_password(user_factory):
    user_factory(username="invalid-login-user", password="StrongPassword123!")
    cache.clear()

    response = APIClient().post(
        "/api/v1/token/",
        {"username": "invalid-login-user", "password": "WrongPassword123!"},
        format="json",
    )

    assert response.status_code == 401
    assert response.data["code"] == "authentication_error"


@pytest.mark.django_db
def test_registration_is_public():
    response = APIClient().post(
        "/api/v1/users/",
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
def test_registration_rejects_weak_password():
    response = APIClient().post(
        "/api/v1/users/",
        {
            "username": "weak-password-user",
            "email": "weak-password@example.com",
            "age": 25,
            "password": "123",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "password" in response.data["fields"]


@pytest.mark.django_db
def test_user_list_is_admin_only(user_factory):
    user_factory(username="regular-user", email="regular@example.com")

    response = APIClient().get("/api/v1/users/")

    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_regular_user_cannot_manage_users(user_factory, authenticated_client):
    user = user_factory(username="regular-manager-user")
    response = authenticated_client(user).get("/api/v1/users/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_can_manage_users(user_factory, authenticated_client):
    admin = user_factory(
        username="admin-user", email="admin@example.com", age=30, is_staff=True
    )
    client = authenticated_client(admin)

    response = client.get("/api/v1/users/")

    assert response.status_code == 200
    assert "password" not in response.data["results"][0]


@pytest.mark.django_db
def test_user_can_view_and_edit_own_profile(user_factory, authenticated_client):
    user = user_factory(username="me-user", email="me@example.com")
    client = authenticated_client(user)

    response = client.get("/api/v1/auth/me/")

    assert response.status_code == 200
    assert response.data["username"] == "me-user"
    assert response.data["profile"] is None

    response = client.patch(
        "/api/v1/auth/me/",
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
    response = APIClient().get("/api/v1/auth/me/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_user_can_change_password_securely(user_factory, authenticated_client):
    user = user_factory(
        username="password-user",
        email="password@example.com",
        password="OldPassword123!",
    )
    client = authenticated_client(user)

    response = client.post(
        "/api/v1/auth/change-password/",
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
def test_password_change_rejects_wrong_current_password(
    user_factory, authenticated_client
):
    user = user_factory(
        username="wrong-password-user",
        email="wrong-password@example.com",
        password="OldPassword123!",
    )
    client = authenticated_client(user)

    response = client.post(
        "/api/v1/auth/change-password/",
        {
            "old_password": "WrongPassword123!",
            "new_password": "NewPassword456!",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "old_password" in response.data["fields"]
