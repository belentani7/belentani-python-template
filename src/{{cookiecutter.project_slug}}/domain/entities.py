from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, TypeVar, Generic

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class EntityId(Generic[T]):
    """Identificador tipado para entidades — evita mezclar IDs de tipos distintos."""
    value: uuid.UUID = field(default_factory=uuid.uuid4)

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def generate(cls) -> EntityId[T]:
        return cls(uuid.uuid4())


@dataclass(slots=True)
class Entity(Generic[T]):
    """Entidad base con ID tipado y timestamps."""
    id: EntityId[T]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def touch(self) -> None:
        """Actualiza updated_at — usar en mutaciones."""
        object.__setattr__(self, "updated_at", datetime.utcnow())


class RepositoryPort(Protocol[T]):
    """Puerto de persistencia — implementaciones en infrastructure/."""
    
    async def add(self, entity: T) -> None: ...
    async def get(self, id: EntityId[T]) -> T | None: ...
    async def list(self, *, limit: int = 100, offset: int = 0) -> list[T]: ...
    async def remove(self, id: EntityId[T]) -> bool: ...


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Evento de dominio base — inmutable, serializable."""
    event_type: str
    payload: dict
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    correlation_id: uuid.UUID = field(default_factory=uuid.uuid4)
    causation_id: uuid.UUID | None = None
