"""Tests for data models."""

import pytest
from datetime import datetime

from astrobob.models import (
    MemoryDocument,
    Provenance,
    create_memory,
    generate_ulid,
)


def test_generate_ulid():
    """Test ULID generation."""
    ulid1 = generate_ulid()
    ulid2 = generate_ulid()
    
    # ULIDs should be strings
    assert isinstance(ulid1, str)
    assert isinstance(ulid2, str)
    
    # ULIDs should be 26 characters
    assert len(ulid1) == 26
    assert len(ulid2) == 26
    
    # ULIDs should be unique
    assert ulid1 != ulid2


def test_provenance_defaults():
    """Test Provenance model with defaults."""
    prov = Provenance()
    
    assert prov.derived_from == []
    assert prov.session_id is None
    assert prov.tool_call_id is None
    assert prov.bob_skill_used is None


def test_provenance_with_values():
    """Test Provenance model with values."""
    prov = Provenance(
        derived_from=["id1", "id2"],
        session_id="session-123",
        tool_call_id="call-456",
        bob_skill_used="code-architect"
    )
    
    assert prov.derived_from == ["id1", "id2"]
    assert prov.session_id == "session-123"
    assert prov.tool_call_id == "call-456"
    assert prov.bob_skill_used == "code-architect"


def test_memory_document_required_fields():
    """Test MemoryDocument with only required fields."""
    now = datetime.utcnow()
    
    memory = MemoryDocument(
        id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
        memory_type="semantic",
        project="test-project",
        content="Test content",
        created_at=now,
        updated_at=now,
    )
    
    assert memory.id == "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    assert memory.memory_type == "semantic"
    assert memory.project == "test-project"
    assert memory.content == "Test content"
    assert memory.scope == "project"  # default
    assert memory.importance == 3  # default
    assert memory.confidence == 1.0  # default
    assert memory.source == "cli"  # default
    assert memory.tags == []  # default
    assert memory.access_count == 0  # default


def test_memory_document_all_fields():
    """Test MemoryDocument with all fields."""
    now = datetime.utcnow()
    prov = Provenance(derived_from=["id1"])
    
    memory = MemoryDocument(
        id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
        memory_type="procedural",
        project="test-project",
        scope="user",
        content="How to do something",
        summary="Brief summary",
        tags=["tag1", "tag2"],
        importance=5,
        confidence=0.9,
        source="bob",
        provenance=prov,
        supersedes="old-id",
        created_at=now,
        updated_at=now,
        deleted_at=None,
        last_accessed_at=now,
        access_count=10,
        success_count=5,
        exported_as_skill=".bob/skills/test/SKILL.md",
        exported_at=now,
    )
    
    assert memory.memory_type == "procedural"
    assert memory.scope == "user"
    assert memory.summary == "Brief summary"
    assert memory.tags == ["tag1", "tag2"]
    assert memory.importance == 5
    assert memory.confidence == 0.9
    assert memory.source == "bob"
    assert memory.provenance.derived_from == ["id1"]
    assert memory.supersedes == "old-id"
    assert memory.access_count == 10
    assert memory.success_count == 5
    assert memory.exported_as_skill == ".bob/skills/test/SKILL.md"


def test_memory_document_invalid_memory_type():
    """Test that invalid memory_type raises validation error."""
    now = datetime.utcnow()
    
    with pytest.raises(ValueError):
        MemoryDocument(
            id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            memory_type="invalid",  # type: ignore
            project="test-project",
            content="Test content",
            created_at=now,
            updated_at=now,
        )


def test_memory_document_importance_bounds():
    """Test that importance must be between 1 and 5."""
    now = datetime.utcnow()
    
    # Too low
    with pytest.raises(ValueError):
        MemoryDocument(
            id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            memory_type="semantic",
            project="test-project",
            content="Test content",
            importance=0,
            created_at=now,
            updated_at=now,
        )
    
    # Too high
    with pytest.raises(ValueError):
        MemoryDocument(
            id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            memory_type="semantic",
            project="test-project",
            content="Test content",
            importance=6,
            created_at=now,
            updated_at=now,
        )
    
    # Valid bounds
    for importance in [1, 2, 3, 4, 5]:
        memory = MemoryDocument(
            id=f"id-{importance}",
            memory_type="semantic",
            project="test-project",
            content="Test content",
            importance=importance,
            created_at=now,
            updated_at=now,
        )
        assert memory.importance == importance


def test_memory_document_confidence_bounds():
    """Test that confidence must be between 0.0 and 1.0."""
    now = datetime.utcnow()
    
    # Too low
    with pytest.raises(ValueError):
        MemoryDocument(
            id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            memory_type="semantic",
            project="test-project",
            content="Test content",
            confidence=-0.1,
            created_at=now,
            updated_at=now,
        )
    
    # Too high
    with pytest.raises(ValueError):
        MemoryDocument(
            id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            memory_type="semantic",
            project="test-project",
            content="Test content",
            confidence=1.1,
            created_at=now,
            updated_at=now,
        )
    
    # Valid bounds
    for confidence in [0.0, 0.5, 1.0]:
        memory = MemoryDocument(
            id=f"id-{confidence}",
            memory_type="semantic",
            project="test-project",
            content="Test content",
            confidence=confidence,
            created_at=now,
            updated_at=now,
        )
        assert memory.confidence == confidence


def test_create_memory_minimal():
    """Test create_memory factory with minimal arguments."""
    memory = create_memory(
        memory_type="semantic",
        project="test-project",
        content="Test content"
    )
    
    assert memory.memory_type == "semantic"
    assert memory.project == "test-project"
    assert memory.content == "Test content"
    assert len(memory.id) == 26  # ULID
    assert memory.importance == 3  # default
    assert memory.confidence == 1.0  # default
    assert memory.source == "cli"  # default
    assert memory.scope == "project"  # default
    assert memory.tags == []
    assert memory.access_count == 0
    assert memory.success_count == 0
    assert isinstance(memory.created_at, datetime)
    assert isinstance(memory.updated_at, datetime)


def test_create_memory_full():
    """Test create_memory factory with all arguments."""
    prov = Provenance(session_id="session-123")
    
    memory = create_memory(
        memory_type="procedural",
        project="test-project",
        content="How to do something",
        summary="Brief summary",
        tags=["tag1", "tag2"],
        importance=5,
        confidence=0.9,
        source="bob",
        scope="user",
        provenance=prov,
        supersedes="old-id"
    )
    
    assert memory.memory_type == "procedural"
    assert memory.summary == "Brief summary"
    assert memory.tags == ["tag1", "tag2"]
    assert memory.importance == 5
    assert memory.confidence == 0.9
    assert memory.source == "bob"
    assert memory.scope == "user"
    assert memory.provenance.session_id == "session-123"
    assert memory.supersedes == "old-id"


def test_create_memory_generates_unique_ids():
    """Test that create_memory generates unique IDs."""
    memory1 = create_memory("semantic", "project", "content1")
    memory2 = create_memory("semantic", "project", "content2")
    
    assert memory1.id != memory2.id


def test_memory_document_json_serialization():
    """Test that MemoryDocument can be serialized to JSON."""
    memory = create_memory(
        memory_type="semantic",
        project="test-project",
        content="Test content",
        tags=["tag1"]
    )
    
    # Should be able to convert to dict
    data = memory.model_dump()
    assert isinstance(data, dict)
    assert data["memory_type"] == "semantic"
    assert data["content"] == "Test content"
    
    # Should be able to convert to JSON string
    json_str = memory.model_dump_json()
    assert isinstance(json_str, str)
    assert "semantic" in json_str

# Made with Bob
