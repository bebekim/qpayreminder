import pytest

from qpayreminder.auth.service import AuthError, AuthService


def test_actor_context_contains_no_flask_session_or_current_user(auth_service: AuthService):
    registered = auth_service.register_with_password(
        email="owner@example.com",
        password="correct horse battery staple",
        request_id="req-register",
    )

    actor = auth_service.resolve_session(registered.session_id, request_id="req-resolve")

    assert actor.request_id == "req-resolve"
    assert actor.session_id == registered.session_id
    assert actor.role == "owner"
    assert actor.auth_strength.level == "password"
    assert not hasattr(actor, "current_user")
    assert not hasattr(actor, "flask_session")


def test_actor_resolution_fails_closed_for_suspended_membership(auth_service: AuthService):
    registered = auth_service.register_with_password(
        email="owner@example.com",
        password="correct horse battery staple",
        request_id="req-register",
    )
    auth_service.suspend_membership(registered.membership.id)

    with pytest.raises(AuthError) as error:
        auth_service.resolve_session(registered.session_id, request_id="req-resolve")

    assert error.value.public_code == "invalid_session"
