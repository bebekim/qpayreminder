import pytest

from qpayreminder.auth.service import AuthService


@pytest.fixture
def auth_service() -> AuthService:
    return AuthService.in_memory()
