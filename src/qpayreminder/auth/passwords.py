from __future__ import annotations

from argon2 import PasswordHasher as Argon2PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from argon2.low_level import Type


class PasswordHasher:
    algorithm = "argon2id"

    def __init__(self) -> None:
        self._hasher = Argon2PasswordHasher(type=Type.ID)

    def hash_password(self, raw_password: str) -> str:
        return self._hasher.hash(raw_password)

    def verify_password(self, raw_password: str, encoded_hash: str) -> bool:
        try:
            return self._hasher.verify(encoded_hash, raw_password)
        except (InvalidHashError, VerifyMismatchError):
            return False

    def needs_rehash(self, encoded_hash: str) -> bool:
        return self._hasher.check_needs_rehash(encoded_hash)
