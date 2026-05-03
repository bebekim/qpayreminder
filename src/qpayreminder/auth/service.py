from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from email_validator import EmailNotValidError, validate_email

from qpayreminder.auth.entities import (
    ActorContext,
    AuthAuditEvent,
    AuthResult,
    AuthStrength,
    Membership,
    Organization,
    PasswordCredential,
    Session,
    User,
)
from qpayreminder.auth.passwords import PasswordHasher
from qpayreminder.auth.policy import MIN_PASSWORD_LENGTH
from qpayreminder.auth.permissions import permissions_for_role
from qpayreminder.auth.repositories import InMemoryAuthRepository


class AuthError(Exception):
    def __init__(self, public_code: str) -> None:
        self.public_code = public_code
        super().__init__(public_code)


class AuthService:
    def __init__(
        self,
        *,
        repository: InMemoryAuthRepository | None = None,
        password_hasher: PasswordHasher | None = None,
        session_ttl: timedelta = timedelta(days=14),
    ) -> None:
        self.repository = repository or InMemoryAuthRepository()
        self.password_hasher = password_hasher or PasswordHasher()
        self.session_ttl = session_ttl

    @classmethod
    def in_memory(cls) -> AuthService:
        return cls(repository=InMemoryAuthRepository())

    @property
    def users(self) -> dict[str, User]:
        return self.repository.users

    @property
    def sessions(self) -> dict[str, Session]:
        return self.repository.sessions

    @property
    def audit_events(self) -> list[AuthAuditEvent]:
        return self.repository.audit_events

    def register_with_password(self, *, email: str, password: str, request_id: str) -> AuthResult:
        normalized_email = self._normalize_email(email)
        self._validate_password(password)
        if self.repository.user_by_email(normalized_email) is not None:
            raise AuthError("email_unavailable")

        user = User(id=self._new_id("user"), email=normalized_email)
        credential = PasswordCredential(user_id=user.id, password_hash=self.password_hasher.hash_password(password))
        organization = Organization(id=self._new_id("org"), name=normalized_email)
        membership = Membership(
            id=self._new_id("membership"),
            user_id=user.id,
            organization_id=organization.id,
            role="owner",
        )
        session = self._new_session(user_id=user.id, membership_id=membership.id)

        self.repository.add_user(user, credential)
        self.repository.add_organization(organization)
        self.repository.add_membership(membership)
        self.repository.add_session(session)
        self._audit("auth.registered", request_id=request_id, user_id=user.id, session_id=session.id)
        self._audit("auth.login.succeeded", request_id=request_id, user_id=user.id, session_id=session.id)
        return AuthResult(user=user, organization=organization, membership=membership, session_id=session.id)

    def login_with_password(self, *, email: str, password: str, request_id: str) -> AuthResult:
        try:
            normalized_email = self._normalize_email(email)
        except AuthError:
            self._audit("auth.login.failed", request_id=request_id)
            raise AuthError("invalid_credentials") from None

        user = self.repository.user_by_email(normalized_email)
        if user is None or user.disabled:
            self._audit("auth.login.failed", request_id=request_id, user_id=user.id if user else None)
            raise AuthError("invalid_credentials")

        credential = self.repository.credentials_by_user_id[user.id]
        if not self.password_hasher.verify_password(password, credential.password_hash):
            self._audit("auth.login.failed", request_id=request_id, user_id=user.id)
            raise AuthError("invalid_credentials")

        membership = self._active_membership_for_user(user.id)
        session = self._new_session(user_id=user.id, membership_id=membership.id)
        self.repository.add_session(session)
        self._audit("auth.login.succeeded", request_id=request_id, user_id=user.id, session_id=session.id)
        organization = self.repository.organizations[membership.organization_id]
        return AuthResult(user=user, organization=organization, membership=membership, session_id=session.id)

    def resolve_session(self, session_id: str, *, request_id: str) -> ActorContext:
        session = self.sessions.get(session_id)
        if not session_id or " " in session_id or session is None:
            raise AuthError("invalid_session")
        if session.revoked_at is not None or session.expires_at <= datetime.now(UTC):
            raise AuthError("invalid_session")

        user = self.repository.users.get(session.user_id)
        membership = self.repository.memberships.get(session.membership_id)
        if user is None or user.disabled or membership is None or membership.suspended:
            raise AuthError("invalid_session")

        actor = ActorContext(
            actor_id=user.id,
            organization_id=membership.organization_id,
            membership_id=membership.id,
            role=membership.role,
            permissions=permissions_for_role(membership.role),
            auth_channel="web",
            auth_method="password",
            auth_strength=AuthStrength(level="password", mfa_satisfied=False),
            session_id=session.id,
            request_id=request_id,
        )
        self._audit("auth.session.resolved", request_id=request_id, user_id=user.id, session_id=session.id)
        return actor

    def logout(self, session_id: str, *, request_id: str) -> None:
        session = self.sessions.get(session_id)
        if session is None:
            return
        self.sessions[session_id] = replace(session, revoked_at=datetime.now(UTC))
        self._audit("auth.logout.succeeded", request_id=request_id, user_id=session.user_id, session_id=session.id)

    def change_password(self, *, user_id: str, current_password: str, new_password: str, request_id: str) -> None:
        credential = self.repository.credentials_by_user_id[user_id]
        if not self.password_hasher.verify_password(current_password, credential.password_hash):
            raise AuthError("invalid_credentials")
        self._validate_password(new_password)
        self.repository.credentials_by_user_id[user_id] = PasswordCredential(
            user_id=user_id,
            password_hash=self.password_hasher.hash_password(new_password),
        )
        now = datetime.now(UTC)
        for session_id, session in list(self.sessions.items()):
            if session.user_id == user_id:
                self.sessions[session_id] = replace(session, revoked_at=now)
        self._audit("auth.password.changed", request_id=request_id, user_id=user_id)

    def disable_user(self, user_id: str) -> None:
        self.repository.disable_user(user_id)

    def suspend_membership(self, membership_id: str) -> None:
        self.repository.suspend_membership(membership_id)

    def _normalize_email(self, email: str) -> str:
        if not email:
            raise AuthError("invalid_email")
        try:
            validated = validate_email(email, check_deliverability=False)
        except EmailNotValidError as exc:
            raise AuthError("invalid_email") from exc
        return validated.normalized.lower()

    def _validate_password(self, password: str) -> None:
        if len(password) < MIN_PASSWORD_LENGTH or password != password.strip():
            raise AuthError("weak_password")

    def _new_session(self, *, user_id: str, membership_id: str) -> Session:
        return Session(
            id=self._new_id("session"),
            user_id=user_id,
            membership_id=membership_id,
            expires_at=datetime.now(UTC) + self.session_ttl,
        )

    def _active_membership_for_user(self, user_id: str) -> Membership:
        for membership in self.repository.memberships.values():
            if membership.user_id == user_id and not membership.suspended:
                return membership
        raise AuthError("invalid_credentials")

    def _audit(self, event_type: str, *, request_id: str, user_id: str | None = None, session_id: str | None = None) -> None:
        self.repository.add_audit_event(
            AuthAuditEvent(event_type=event_type, request_id=request_id, user_id=user_id, session_id=session_id)
        )

    def _new_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex}"
