from __future__ import annotations

from collections.abc import Iterable

from qpayreminder.auth.entities import ActorContext, AuthStrength
from qpayreminder.auth.permissions import permissions_for_role


def fake_actor_context(
    *,
    actor_id: str = "user-test",
    organization_id: str = "org-test",
    membership_id: str = "membership-test",
    role: str = "owner",
    permissions: Iterable[str] | None = None,
    request_id: str = "req-test",
) -> ActorContext:
    return ActorContext(
        actor_id=actor_id,
        organization_id=organization_id,
        membership_id=membership_id,
        role=role,
        permissions=frozenset(permissions) if permissions is not None else permissions_for_role(role),
        auth_channel="test",
        auth_method="fake",
        auth_strength=AuthStrength(level="fake", mfa_satisfied=False),
        session_id=None,
        request_id=request_id,
    )
