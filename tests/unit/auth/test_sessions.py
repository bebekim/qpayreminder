from datetime import UTC, datetime, timedelta

import pytest

from qpayreminder.auth.service import AuthError, AuthService


def test_logout_revokes_current_session(auth_service: AuthService):
    registered = auth_service.register_with_password(
        email="owner@example.com",
        password="correct horse battery staple",
        request_id="req-register",
    )

    auth_service.logout(registered.session_id, request_id="req-logout")

    with pytest.raises(AuthError) as error:
        auth_service.resolve_session(registered.session_id, request_id="req-resolve")

    assert error.value.public_code == "invalid_session"


@pytest.mark.parametrize("session_id", ["", "not a session id", "unknown-session"])
def test_resolve_session_fails_closed_for_missing_malformed_or_unknown_session(
    auth_service: AuthService,
    session_id: str,
):
    with pytest.raises(AuthError) as error:
        auth_service.resolve_session(session_id, request_id="req-resolve")

    assert error.value.public_code == "invalid_session"


def test_expired_session_fails_closed(auth_service: AuthService):
    registered = auth_service.register_with_password(
        email="owner@example.com",
        password="correct horse battery staple",
        request_id="req-register",
    )
    auth_service.sessions[registered.session_id].expires_at = datetime.now(UTC) - timedelta(seconds=1)

    with pytest.raises(AuthError) as error:
        auth_service.resolve_session(registered.session_id, request_id="req-resolve")

    assert error.value.public_code == "invalid_session"


def test_password_change_revokes_existing_sessions(auth_service: AuthService):
    registered = auth_service.register_with_password(
        email="owner@example.com",
        password="correct horse battery staple",
        request_id="req-register",
    )

    auth_service.change_password(
        user_id=registered.user.id,
        current_password="correct horse battery staple",
        new_password="new correct horse battery staple",
        request_id="req-change-password",
    )

    with pytest.raises(AuthError):
        auth_service.resolve_session(registered.session_id, request_id="req-resolve")
