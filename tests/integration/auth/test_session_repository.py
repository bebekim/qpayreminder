import pytest

from qpayreminder.auth.repositories import InMemoryAuthRepository
from qpayreminder.auth.service import AuthError, AuthService


def test_session_repository_persists_revocation_across_service_instances():
    repository = InMemoryAuthRepository()
    first_service = AuthService(repository=repository)
    registered = first_service.register_with_password(
        email="owner@example.com",
        password="correct horse battery staple",
        request_id="req-register",
    )

    second_service = AuthService(repository=repository)
    second_service.logout(registered.session_id, request_id="req-logout")

    with pytest.raises(AuthError):
        first_service.resolve_session(registered.session_id, request_id="req-resolve")
