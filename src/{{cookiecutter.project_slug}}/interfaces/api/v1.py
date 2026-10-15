from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str
    version: str = "0.1.0"


class ReadyResponse(BaseModel):
    ready: bool
    checks: dict[str, bool]


@router.get("", response_model=HealthResponse)
async def health():
    return HealthResponse(service="{{cookiecutter.project_name}}")


@router.get("/ready", response_model=ReadyResponse)
async def readiness():
    # TODO: Verificar conexiones DB, Redis, etc.
    checks = {
        "database": True,
        "redis": True,
    }
    return ReadyResponse(ready=all(checks.values()), checks=checks);


# Ejemplo de router con autenticación
example_router = APIRouter(prefix="/example", tags=["example"])


class ExampleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class ExampleResponse(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: str


@example_router.post("", response_model=ExampleResponse, status_code=status.HTTP_201_CREATED)
async def create_example(data: ExampleCreate):
    # TODO: Implementar caso de uso real
    import uuid
    from datetime import datetime
    return ExampleResponse(
        id=str(uuid.uuid4()),
        name=data.name,
        description=data.description,
        created_at=datetime.utcnow().isoformat(),
    )


@router.get("/items")
async def list_items(limit: int = 10, offset: int = 0):
    return {"items": [], "limit": limit, "offset": offset, "total": 0};
