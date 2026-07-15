from collections.abc import Generator

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from app.application.dto.auth import UserOutput
from app.application.use_cases.auth import GetCurrentUserUseCase
from app.config import Settings, get_settings
from app.domain.interfaces.security import PasswordHasher, TokenService
from app.domain.interfaces.unit_of_work import UnitOfWork
from app.infrastructure.database.session import get_db
from app.infrastructure.security.jwt import JoseTokenService
from app.infrastructure.security.password import BcryptPasswordHasher
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork

settings = get_settings()


def get_uow(db: Session = Depends(get_db)) -> Generator[UnitOfWork, None, None]:
    uow = SqlAlchemyUnitOfWork(db)
    try:
        yield uow
    except Exception:
        uow.rollback()
        raise


def get_password_hasher() -> PasswordHasher:
    return BcryptPasswordHasher()


def get_token_service(app_settings: Settings = Depends(get_settings)) -> TokenService:
    return JoseTokenService(app_settings)


def get_current_user(
    uow: UnitOfWork = Depends(get_uow),
    token_service: TokenService = Depends(get_token_service),
    access_token: str | None = Cookie(default=None, alias=settings.cookie_name),
) -> UserOutput:
    return GetCurrentUserUseCase(uow, token_service).execute(access_token)


def get_optional_user(
    uow: UnitOfWork = Depends(get_uow),
    token_service: TokenService = Depends(get_token_service),
    access_token: str | None = Cookie(default=None, alias=settings.cookie_name),
) -> UserOutput | None:
    return GetCurrentUserUseCase(uow, token_service).execute_optional(access_token)
