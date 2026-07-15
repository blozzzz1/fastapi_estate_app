from app.application.dto.auth import AuthResult, LoginInput, RegisterUserInput, UserOutput
from app.domain.entities.user import User
from app.domain.exceptions import AuthenticationError, ConflictError
from app.domain.interfaces.security import PasswordHasher, TokenService
from app.domain.interfaces.unit_of_work import UnitOfWork


def _to_user_output(user: User) -> UserOutput:
    assert user.id is not None and user.created_at is not None
    return UserOutput(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
    )


def _to_auth_result(user: User, token: str) -> AuthResult:
    assert user.id is not None and user.created_at is not None
    return AuthResult(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
        access_token=token,
    )


class RegisterUserUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._uow = uow
        self._password_hasher = password_hasher
        self._token_service = token_service

    def execute(self, data: RegisterUserInput) -> AuthResult:
        if self._uow.users.get_by_email(data.email) is not None:
            raise ConflictError("Email already registered")

        user = User(
            id=None,
            email=data.email,
            hashed_password=self._password_hasher.hash(data.password),
            full_name=data.full_name,
            is_active=True,
        )
        created = self._uow.users.add(user)
        self._uow.commit()
        token = self._token_service.create_access_token(created.email)
        return _to_auth_result(created, token)


class LoginUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._uow = uow
        self._password_hasher = password_hasher
        self._token_service = token_service

    def execute(self, data: LoginInput) -> AuthResult:
        user = self._uow.users.get_by_email(data.email)
        if user is None or not self._password_hasher.verify(data.password, user.hashed_password):
            raise AuthenticationError("Incorrect email or password")
        if not user.is_active:
            raise AuthenticationError("Incorrect email or password")

        token = self._token_service.create_access_token(user.email)
        return _to_auth_result(user, token)


class GetCurrentUserUseCase:
    def __init__(self, uow: UnitOfWork, token_service: TokenService) -> None:
        self._uow = uow
        self._token_service = token_service

    def execute(self, token: str | None) -> UserOutput:
        if not token:
            raise AuthenticationError("Not authenticated")

        email = self._token_service.decode_access_token(token)
        if email is None:
            raise AuthenticationError("Not authenticated")

        user = self._uow.users.get_by_email(email)
        if user is None or not user.is_active:
            raise AuthenticationError("Not authenticated")

        return _to_user_output(user)

    def execute_optional(self, token: str | None) -> UserOutput | None:
        if not token:
            return None
        try:
            return self.execute(token)
        except AuthenticationError:
            return None
