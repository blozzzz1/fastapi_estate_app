from fastapi import APIRouter, Depends, Response, status

from app.application.dto.auth import LoginInput, RegisterUserInput
from app.application.use_cases.auth import LoginUseCase, RegisterUserUseCase
from app.config import Settings, get_settings
from app.domain.interfaces.security import PasswordHasher, TokenService
from app.domain.interfaces.unit_of_work import UnitOfWork
from app.presentation.dependencies import (
    get_current_user,
    get_password_hasher,
    get_token_service,
    get_uow,
)
from app.presentation.schemas import Message, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


def _clear_auth_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        key=settings.cookie_name,
        path="/",
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        httponly=True,
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreate,
    response: Response,
    uow: UnitOfWork = Depends(get_uow),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
    settings: Settings = Depends(get_settings),
) -> UserRead:
    result = RegisterUserUseCase(uow, password_hasher, token_service).execute(
        RegisterUserInput(email=payload.email, password=payload.password, full_name=payload.full_name)
    )
    _set_auth_cookie(response, result.access_token, settings)
    return UserRead(
        id=result.user_id,
        email=result.email,
        full_name=result.full_name,
        is_active=result.is_active,
        created_at=result.created_at,
    )


@router.post("/login", response_model=UserRead)
def login(
    payload: UserLogin,
    response: Response,
    uow: UnitOfWork = Depends(get_uow),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
    settings: Settings = Depends(get_settings),
) -> UserRead:
    result = LoginUseCase(uow, password_hasher, token_service).execute(
        LoginInput(email=payload.email, password=payload.password)
    )
    _set_auth_cookie(response, result.access_token, settings)
    return UserRead(
        id=result.user_id,
        email=result.email,
        full_name=result.full_name,
        is_active=result.is_active,
        created_at=result.created_at,
    )


@router.post("/logout", response_model=Message)
def logout(response: Response, settings: Settings = Depends(get_settings)) -> Message:
    _clear_auth_cookie(response, settings)
    return Message(message="Logged out")


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)) -> UserRead:
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
