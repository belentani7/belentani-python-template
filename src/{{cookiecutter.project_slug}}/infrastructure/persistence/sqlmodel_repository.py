from __future__ import annotations
from typing import Generic, TypeVar, Optional, List
from sqlmodel import SQLModel, Session, select
from sqlalchemy.exc import IntegrityError

from {{cookiecutter.project_slug}}.domain.entities import Entity, EntityId, RepositoryPort

T = TypeVar("T", bound=Entity)
M = TypeVar("M", bound=SQLModel)


class SQLModelRepository(Generic[T, M], RepositoryPort[T]):
    def __init__(self, session: Session, model: type[M], entity_mapper):
        self.session = session
        self.model = model
        self.entity_mapper = entity_mapper  # callable: M -> T

    async def add(self, entity: T) -> None:
        db_model = self.entity_mapper.to_model(entity)
        self.session.add(db_model)
        try:
            self.session.commit()
            self.session.refresh(db_model)
            entity.id = EntityId(db_model.id) if hasattr(db_model, "id") else entity.id
        except IntegrityError:
            self.session.rollback()
            raise

    async def get(self, id: EntityId[T]) -> Optional[T]:
        db_model = self.session.get(self.model, id.value)
        if not db_model:
            return None
        return self.entity_mapper.to_entity(db_model)

    async def list(self, *, limit: int = 100, offset: int = 0) -> List[T]:
        statement = select(self.model).offset(offset).limit(limit)
        db_models = self.session.exec(statement).all()
        return [self.entity_mapper.to_entity(m) for m in db_models]

    async def remove(self, id: EntityId[T]) -> bool:
        db_model = self.session.get(self.model, id.value)
        if not db_model:
            return False
        self.session.delete(db_model)
        self.session.commit()
        return True

    async def exists(self, id: EntityId[T]) -> bool:
        return self.session.get(self.model, id.value) is not None;
