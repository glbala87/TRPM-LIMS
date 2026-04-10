"""Top-level pytest fixtures shared across all test modules."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.fixture
def user(db):
    """A plain test user."""
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.org',
        password='testpass-change-me-12345',
    )


@pytest.fixture
def admin_user(db):
    """A superuser for tests that need admin access."""
    User = get_user_model()
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.org',
        password='adminpass-change-me-12345',
    )


@pytest.fixture
def api_client():
    """An unauthenticated DRF APIClient."""
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    """An APIClient pre-authenticated as `user`."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """An APIClient pre-authenticated as superuser."""
    api_client.force_authenticate(user=admin_user)
    return api_client
