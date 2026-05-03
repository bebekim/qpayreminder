from __future__ import annotations

from dataclasses import replace

from qpayreminder.auth.entities import AuthAuditEvent, Membership, Organization, PasswordCredential, Session, User


class InMemoryAuthRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.user_ids_by_email: dict[str, str] = {}
        self.credentials_by_user_id: dict[str, PasswordCredential] = {}
        self.organizations: dict[str, Organization] = {}
        self.memberships: dict[str, Membership] = {}
        self.sessions: dict[str, Session] = {}
        self.audit_events: list[AuthAuditEvent] = []

    def add_user(self, user: User, credential: PasswordCredential) -> None:
        self.users[user.id] = user
        self.user_ids_by_email[user.email] = user.id
        self.credentials_by_user_id[user.id] = credential

    def user_by_email(self, email: str) -> User | None:
        user_id = self.user_ids_by_email.get(email)
        if user_id is None:
            return None
        return self.users.get(user_id)

    def add_organization(self, organization: Organization) -> None:
        self.organizations[organization.id] = organization

    def add_membership(self, membership: Membership) -> None:
        self.memberships[membership.id] = membership

    def add_session(self, session: Session) -> None:
        self.sessions[session.id] = session

    def add_audit_event(self, event: AuthAuditEvent) -> None:
        self.audit_events.append(event)

    def disable_user(self, user_id: str) -> None:
        self.users[user_id] = replace(self.users[user_id], disabled=True)

    def suspend_membership(self, membership_id: str) -> None:
        self.memberships[membership_id] = replace(self.memberships[membership_id], suspended=True)
