from qpayreminder.auth.passwords import PasswordHasher


def test_hash_password_uses_argon2id_and_never_returns_plaintext():
    hasher = PasswordHasher()

    encoded = hasher.hash_password("correct horse battery staple")

    assert encoded.startswith("$argon2id$")
    assert "correct horse battery staple" not in encoded
    assert hasher.verify_password("correct horse battery staple", encoded)


def test_verify_password_rejects_wrong_password():
    hasher = PasswordHasher()
    encoded = hasher.hash_password("correct horse battery staple")

    assert not hasher.verify_password("wrong horse battery staple", encoded)


def test_hash_parameters_are_versioned_for_migration_checks():
    hasher = PasswordHasher()
    encoded = hasher.hash_password("correct horse battery staple")

    assert hasher.needs_rehash(encoded) is False
    assert hasher.algorithm == "argon2id"
