from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    id: str
    email: str
    disabled: bool = False


@dataclass(frozen=True)
class PasswordCredential:
    user_id: str
    password_hash: str


@dataclass(frozen=True)
class Organization:
    id: str
    name: str


@dataclass(frozen=True)
class Membership:
    id: str
    user_id: str
    organization_id: str
    role: str
    suspended: bool = False


@dataclass
class Session:
    id: str
    user_id: str
    membership_id: str
    expires_at: datetime
    revoked_at: datetime | None = None


@dataclass(frozen=True)
class AuthStrength:
    level: str
    mfa_satisfied: bool = False


@dataclass(frozen=True)
class ActorContext:
    actor_id: str
    organization_id: str
    membership_id: str
    role: str
    permissions: frozenset[str]
    auth_channel: str
    auth_method: str
    auth_strength: AuthStrength
    session_id: str | None
    request_id: str


@dataclass(frozen=True)
class AuthAuditEvent:
    event_type: str
    request_id: str
    user_id: str | None = None
    session_id: str | None = None


@dataclass(frozen=True)
class AuthResult:
    user: User
    organization: Organization
    membership: Membership
    session_id: str
