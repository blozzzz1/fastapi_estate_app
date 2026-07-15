from abc import ABC, abstractmethod

from app.domain.repositories.property import PropertyRepository
from app.domain.repositories.user import UserRepository


class UnitOfWork(ABC):
    users: UserRepository
    properties: PropertyRepository

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            self.rollback()
