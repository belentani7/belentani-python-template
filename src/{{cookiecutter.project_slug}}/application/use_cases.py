from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from {{cookiecutter.project_slug}}.domain.entities import EntityId, RepositoryPort, DomainEvent

T = TypeVar("T")

class UseCase(Protocol[T]):
    """Protocolo para casos de uso — entrada única, salida tipada."""
    async def execute(self, input: T) -> T: ...


@dataclass(frozen=True, slots=True)
class UseCaseInput:
    """Entrada base para casos de uso — inmutable."""
    pass


@dataclass(frozen=True, slots=True)
class UseCaseOutput:
    """Salida base para casos de uso — inmutable."""
    success: bool
    data: dict | None = None
    error: str | None = None


class EventPublisher(Protocol):
    """Publicador de eventos de dominio — implementación en infrastructure/."""
    async def publish(self, event: DomainEvent) -> None: ...


@dataclass(slots=True)
class BaseService:
    """Servicio base con acceso a repositorio y publicador de eventos."""
    repository: RepositoryPort
    event_publisher: EventPublisher | None = None

    async def _emit(self, event: DomainEvent) -> None:
        if self.event_publisher:
            await self.event_publisher.publish(event)
