from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int | None
    email: str
    hashed_password: str
    full_name: str | None
    is_active: bool
    created_at: datetime | None = None
