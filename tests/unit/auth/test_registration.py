import pytest

from qpayreminder.auth.policy import MIN_PASSWORD_LENGTH
from qpayreminder.auth.service import AuthError, AuthService


def test_register_creates_user_org_owner_membership_session_and_audit_event(auth_service: AuthService):
    result = auth_service.register_with_password(
        email="Owner@Example.COM",
        password="correct horse battery staple",
        request_id="req-register-1",
    )

    actor = auth_service.resolve_session(result.session_id, request_id="req-resolve-1")

    assert result.user.email == "owner@example.com"
    assert result.organization.name == "owner@example.com"
    assert result.membership.role == "owner"
    assert "org:manage" in actor.permissions
    assert actor.actor_id == result.user.id
    assert actor.organization_id == result.organization.id
    assert actor.membership_id == result.membership.id
    assert actor.auth_channel == "web"
    assert actor.auth_method == "password"
    assert actor.auth_strength.mfa_satisfied is False
    assert auth_service.audit_events[-1].event_type == "auth.session.resolved"


def test_register_rejects_duplicate_email_without_creating_second_user(auth_service: AuthService):
    auth_service.register_with_password(
        email="owner@example.com",
        password="correct horse battery staple",
        request_id="req-register-1",
    )

    with pytest.raises(AuthError) as error:
        auth_service.register_with_password(
            email="OWNER@example.com",
            password="correct horse battery staple",
            request_id="req-register-2",
        )

    assert error.value.public_code == "email_unavailable"
    assert len(auth_service.users) == 1


@pytest.mark.parametrize("email", ["", "not-an-email"])
def test_register_rejects_invalid_email(auth_service: AuthService, email: str):
    with pytest.raises(AuthError) as error:
        auth_service.register_with_password(
            email=email,
            password="correct horse battery staple",
            request_id="req-register-invalid-email",
        )

    assert error.value.public_code == "invalid_email"


@pytest.mark.parametrize("password", ["x" * (MIN_PASSWORD_LENGTH - 1), " leading-space-ok-but-too-short "])
def test_register_rejects_short_password(auth_service: AuthService, password: str):
    with pytest.raises(AuthError) as error:
        auth_service.register_with_password(
            email="owner@example.com",
            password=password,
            request_id="req-register-short-password",
        )

    assert error.value.public_code == "weak_password"
