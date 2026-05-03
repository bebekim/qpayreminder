import pytest

from qpayreminder.auth.service import AuthError, AuthService


def test_login_creates_fresh_session_and_audit_event(auth_service: AuthService):
    registered = auth_service.register_with_password(
        email="owner@example.com",
        password="correct horse battery staple",
        request_id="req-register",
    )

    logged_in = auth_service.login_with_password(
        email="OWNER@example.com",
        password="correct horse battery staple",
        request_id="req-login",
    )

    assert logged_in.session_id != registered.session_id
    assert logged_in.user.id == registered.user.id
    assert auth_service.resolve_session(logged_in.session_id, request_id="req-resolve").actor_id == registered.user.id
    assert auth_service.audit_events[-2].event_type == "auth.login.succeeded"


@pytest.mark.parametrize("email,password", [("missing@example.com", "wrong-password"), ("owner@example.com", "wrong-password")])
def test_login_returns_same_safe_error_for_missing_user_and_wrong_password(
    auth_service: AuthService,
    email: str,
    password: str,
):
    auth_service.register_with_password(
        email="owner@example.com",
        password="correct horse battery staple",
        request_id="req-register",
    )

    with pytest.raises(AuthError) as error:
        auth_service.login_with_password(email=email, password=password, request_id="req-login-failed")

    assert error.value.public_code == "invalid_credentials"
    assert auth_service.audit_events[-1].event_type == "auth.login.failed"


def test_login_rejects_disabled_user(auth_service: AuthService):
    registered = auth_service.register_with_password(
        email="owner@example.com",
        password="correct horse battery staple",
        request_id="req-register",
    )
    auth_service.disable_user(registered.user.id)

    with pytest.raises(AuthError) as error:
        auth_service.login_with_password(
            email="owner@example.com",
            password="correct horse battery staple",
            request_id="req-login-disabled",
        )

    assert error.value.public_code == "invalid_credentials"
