import re
from typing import Any, Self

from pydantic import BaseModel, Field, EmailStr, field_validator


class AuthLoginIn(BaseModel):
    email: EmailStr
    password: str


class AuthSignUpIn(BaseModel):
    fullname: str = Field(max_length=255, min_length=5)
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("fullname")
    def validate_fullname(cls, value: str) -> Self:
        fullname_list = value.split(" ")

        if len(fullname_list) < 2:
            raise ValueError("Please enter both your first and last name.")

        return value.lower()

    @field_validator("email")
    def validate(cls, value: str) -> Self:
        return value.lower()

    @field_validator("password")
    def validate_password(cls, value: Any) -> Self:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value
