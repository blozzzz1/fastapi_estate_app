from sqlalchemy.orm import Session

from app.domain.interfaces.unit_of_work import UnitOfWork
from app.infrastructure.repositories.property import SqlAlchemyPropertyRepository
from app.infrastructure.repositories.user import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        self._session = session
        self.users = SqlAlchemyUserRepository(session)
        self.properties = SqlAlchemyPropertyRepository(session)

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
