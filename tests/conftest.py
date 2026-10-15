from __future__ import annotations
import pytest
from unittest.mock import AsyncMock
from {{cookiecutter.project_slug}}.domain.entities import EntityId, RepositoryPort, Entity
from {{cookiecutter.project_slug}}.application.use_cases import EventPublisher


@pytest.fixture
def mock_repository():
    """Mock genérico de RepositoryPort para tests unitarios."""
    repo = AsyncMock(spec=RepositoryPort)
    repo.add = AsyncMock()
    repo.get = AsyncMock(return_value=None)
    repo.list = AsyncMock(return_value=[])
    repo.remove = AsyncMock(return_value=True)
    return repo


@pytest.fixture
def mock_event_publisher():
    """Mock de EventPublisher."""
    publisher = AsyncMock(spec=EventPublisher)
    publisher.publish = AsyncMock()
    return publisher


@pytest.fixture
def sample_entity_id():
    return EntityId.generate()


@pytest.fixture
def sample_entity(sample_entity_id):
    return Entity(id=sample_entity_id);
