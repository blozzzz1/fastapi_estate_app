from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.repositories.user import UserRepository
from app.infrastructure.orm.mappers import user_to_entity
from app.infrastructure.orm.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, user_id: int) -> User | None:
        model = self._session.get(UserModel, user_id)
        return user_to_entity(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        model = self._session.query(UserModel).filter(UserModel.email == email).first()
        return user_to_entity(model) if model else None

    def add(self, user: User) -> User:
        model = UserModel(
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            is_active=user.is_active,
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return user_to_entity(model)
