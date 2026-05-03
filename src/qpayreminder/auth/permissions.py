ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "owner": frozenset({"org:manage", "invoice:create", "invoice:read", "payment:read"}),
    "bookkeeper": frozenset({"invoice:create", "invoice:read", "payment:read"}),
    "viewer": frozenset({"invoice:read", "payment:read"}),
}


def permissions_for_role(role: str) -> frozenset[str]:
    return ROLE_PERMISSIONS.get(role, frozenset())
