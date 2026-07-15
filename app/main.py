from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.domain.exceptions import DomainError
from app.infrastructure.database.session import init_db
from app.presentation.exception_handlers import domain_error_handler
from app.presentation.routers import auth, properties

init_db()

app = FastAPI(
    title="Real Estate API",
    description="CRUD API for real estate listings with search filters and JWT cookie auth",
    version="1.0.0",
)

app.add_exception_handler(DomainError, domain_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(properties.router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
