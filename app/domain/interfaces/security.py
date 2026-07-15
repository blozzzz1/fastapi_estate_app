from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        raise NotImplementedError


class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, subject: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def decode_access_token(self, token: str) -> str | None:
        raise NotImplementedError
