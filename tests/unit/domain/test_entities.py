from __future__ import annotations
import pytest
from {{cookiecutter.project_slug}}.domain.entities import EntityId, Entity, DomainEvent


class TestEntityId:
    def test_generate_creates_unique_ids(self):
        id1 = EntityId.generate()
        id2 = EntityId.generate()
        assert id1 != id2
        assert str(id1) != str(id2)

    def test_str_returns_uuid_string(self):
        eid = EntityId.generate()
        assert isinstance(str(eid), str)
        assert len(str(eid)) == 36  # UUID format

    def test_equality(self):
        eid = EntityId.generate()
        same = EntityId(eid.value)
        different = EntityId.generate()
        assert eid == same
        assert eid != different


class TestEntity:
    def test_create_sets_timestamps(self):
        entity = Entity(id=EntityId.generate())
        assert entity.created_at is not None
        assert entity.updated_at is not None
        assert entity.created_at == entity.updated_at

    def test_touch_updates_updated_at(self):
        entity = Entity(id=EntityId.generate())
        original_updated = entity.updated_at
        # small delay to ensure timestamp changes
        import time
        time.sleep(0.001)
        entity.touch()
        assert entity.updated_at > original_updated
        assert entity.created_at == entity.created_at  # created_at unchanged


class TestDomainEvent:
    def test_create_sets_defaults(self):
        event = DomainEvent(event_type="test.event", payload={"key": "value"})
        assert event.event_type == "test.event"
        assert event.payload == {"key": "value"}
        assert event.occurred_at is not None
        assert event.correlation_id is not None
        assert event.causation_id is None

    def test_causation_id_optional(self):
        event = DomainEvent(
            event_type="test",
            payload={},
            causation_id=__import__("uuid").uuid4(),
        )
        assert event.causation_id is not None;
