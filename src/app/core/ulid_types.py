from typing import Any

import ulid
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from sqlalchemy import TypeDecorator, String


class ULID(str):
    def __init__(self, value: str) -> None:
        try:
            self._ulid = ulid.from_str(value)
        except ValueError:
            raise ValueError(f"Invalid ULID: {value}")

    def __str__(self) -> str:
        return str(self._ulid)

    def __repr__(self) -> str:
        return f"ULID({self._ulid})"

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __new__(cls, value: str, *args, **kwargs):
        try:
            ulid.from_str(value)
        except ValueError:
            raise ValueError(f"Invalid ULID: {value}")
        return super().__new__(cls, value)

    def __hash__(self) -> int:
        return hash(str(self))


class ULIDType:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, value: Any) -> ULID:
        if isinstance(value, ULID):
            return value
        if isinstance(value, str):
            return ULID(value)
        raise TypeError("Invalid type for ULID")


class ULIDTypeDB(TypeDecorator):
    impl = String(26)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)  # Works if value is ULID or ulid.ULID or str

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return ULID(value)  # returns your custom ULID class
