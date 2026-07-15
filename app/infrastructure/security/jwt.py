from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.config import Settings
from app.domain.interfaces.security import TokenService


class JoseTokenService(TokenService):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def create_access_token(self, subject: str) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=self._settings.access_token_expire_minutes)
        payload = {"sub": subject, "exp": expire}
        return jwt.encode(payload, self._settings.secret_key, algorithm=self._settings.algorithm)

    def decode_access_token(self, token: str) -> str | None:
        try:
            payload = jwt.decode(
                token,
                self._settings.secret_key,
                algorithms=[self._settings.algorithm],
            )
            subject = payload.get("sub")
            return str(subject) if subject is not None else None
        except JWTError:
            return None
