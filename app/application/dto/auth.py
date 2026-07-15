from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RegisterUserInput:
    email: str
    password: str
    full_name: str | None = None


@dataclass(frozen=True)
class LoginInput:
    email: str
    password: str


@dataclass(frozen=True)
class AuthResult:
    user_id: int
    email: str
    full_name: str | None
    is_active: bool
    created_at: datetime
    access_token: str


@dataclass(frozen=True)
class UserOutput:
    id: int
    email: str
    full_name: str | None
    is_active: bool
    created_at: datetime
