from qpayreminder.auth.fakes import fake_actor_context


def test_fake_actor_context_is_available_without_flask_or_network():
    actor = fake_actor_context(
        actor_id="user-test",
        organization_id="org-test",
        role="owner",
        permissions={"invoice:create"},
        request_id="req-test",
    )

    assert actor.actor_id == "user-test"
    assert actor.organization_id == "org-test"
    assert actor.role == "owner"
    assert actor.permissions == frozenset({"invoice:create"})
    assert actor.auth_channel == "test"
    assert actor.auth_method == "fake"
