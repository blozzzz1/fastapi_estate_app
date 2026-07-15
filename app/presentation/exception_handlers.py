from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DomainError,
    NotFoundError,
)


def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
    status_map: dict[type[DomainError], int] = {
        NotFoundError: 404,
        ConflictError: 400,
        AuthenticationError: 401,
        AuthorizationError: 403,
    }
    status_code = status_map.get(type(exc), 400)
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})
