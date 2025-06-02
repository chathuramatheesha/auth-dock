from typing import Annotated

from argon2 import Type, PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash
from fastapi import Depends


class Argon2Hasher:
    def __init__(
        self,
        time_cost: int = 3,
        memory_cost: int = 64 * 1024,
        parallelism: int = 2,
        hash_len: int = 32,
        salt_len: int = 16,
        type_: Type = Type.ID,
    ) -> None:
        self._hasher = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=hash_len,
            salt_len=salt_len,
            type=type_,
        )

    async def hash(self, value: str) -> str:
        if not value or not isinstance(value, str):
            raise ValueError("Password must be a non-empty string.")

        return self._hasher.hash(value)

    async def verify(self, plain: str, hashed: str) -> bool:
        try:
            return self._hasher.verify(hashed, plain)
        except (VerifyMismatchError, VerificationError, InvalidHash):
            return False

    async def needs_rehash(self, hashed: str) -> bool:
        return self._hasher.check_needs_rehash(hashed)


async def __get_argon2_hasher() -> Argon2Hasher:
    return Argon2Hasher()


Argon2Dep = Annotated[Argon2Hasher, Depends(__get_argon2_hasher)]
