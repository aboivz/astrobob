"""
Integration tests for AstroBob with live AstraDB.

These tests require:
- RUN_INTEGRATION=1 environment variable
- Valid ASTRA_DB_API_ENDPOINT and ASTRA_DB_APPLICATION_TOKEN

Run with: RUN_INTEGRATION=1 pytest tests/integration/test_astra_live.py -v
"""

import os
import pytest
from datetime import datetime, timezone

from astrobob.config import get_config
from astrobob.astra.client import create_astra_client
from astrobob.astra.collections import create_all_collections, get_collection_name
from astrobob.core.store import MemoryStore
from astrobob.models import create_memory, MemoryDocument


# Skip all tests if RUN_INTEGRATION is not set
pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION") != "1",
    reason="Integration tests require RUN_INTEGRATION=1"
)


@pytest.fixture(scope="module")
def config():
    """Get configuration for tests."""
    return get_config()


@pytest.fixture(scope="module")
def astra_client(config):
    """Create AstraDB client."""
    return create_astra_client(config)


@pytest.fixture(scope="module")
def setup_collections(astra_client):
    """Ensure test collections exist."""
    db = astra_client.get_database()
    results = create_all_collections(db, prefix="astrobob_test")
    yield results
    # Cleanup is optional - collections can persist for debugging


@pytest.fixture
def memory_store(astra_client, setup_collections):
    """Create memory store for tests."""
    return MemoryStore(astra_client, collection_prefix="astrobob_test")


@pytest.fixture
def test_project():
    """Generate unique test project name."""
    return f"test_integration_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"


def test_full_lifecycle(memory_store, test_project):
    """
    Test complete memory lifecycle:
    1. Create semantic memory
    2. Create episodic memory
    3. Recall memories
    4. Create procedural from episodic (reflect)
    5. Soft delete
    6. Verify deletion
    """
    # Step 1: Create semantic memory
    semantic = create_memory(
        memory_type="semantic",
        project=test_project,
        content="FastAPI is a modern Python web framework",
        tags=["python", "fastapi", "web"],
        importance=4
    )
    
    semantic_id = memory_store.insert(semantic)
    assert semantic_id == semantic.id
    
    # Step 2: Create episodic memory
    episodic = create_memory(
        memory_type="episodic",
        project=test_project,
        content="Fixed authentication bug by adding token refresh logic",
        tags=["bug", "auth", "fix"],
        importance=3
    )
    
    episodic_id = memory_store.insert(episodic)
    assert episodic_id == episodic.id
    
    # Step 3: Recall memories
    retrieved_semantic = memory_store.get("semantic", semantic_id)
    assert retrieved_semantic.id == semantic_id
    assert retrieved_semantic.content == semantic.content
    assert retrieved_semantic.project == test_project
    
    retrieved_episodic = memory_store.get("episodic", episodic_id)
    assert retrieved_episodic.id == episodic_id
    assert retrieved_episodic.content == episodic.content
    
    # Step 4: Create procedural memory (simulating reflection)
    procedural = create_memory(
        memory_type="procedural",
        project=test_project,
        content="When fixing auth bugs: 1) Check token expiry, 2) Add refresh logic, 3) Test edge cases",
        tags=["procedure", "auth", "debugging"],
        importance=5
    )
    # Set provenance to show it was derived from episodic
    procedural.provenance.derived_from = [episodic_id]
    
    procedural_id = memory_store.insert(procedural)
    assert procedural_id == procedural.id
    
    # Step 5: List procedural memories
    procedural_list = memory_store.list_procedural(test_project, min_importance=4)
    assert len(procedural_list) >= 1
    assert any(m.id == procedural_id for m in procedural_list)
    
    # Step 6: Soft delete episodic memory
    memory_store.soft_delete("episodic", episodic_id)
    
    # Step 7: Verify deletion (should still exist but marked deleted)
    deleted_memory = memory_store.get("episodic", episodic_id)
    assert deleted_memory.deleted_at is not None
    
    # Step 8: Update access count
    memory_store.update_access(semantic_id)
    updated_semantic = memory_store.get("semantic", semantic_id)
    assert updated_semantic.access_count == 1
    assert updated_semantic.last_accessed_at is not None


def test_memory_insert_and_retrieve(memory_store, test_project):
    """Test basic insert and retrieve operations."""
    memory = create_memory(
        memory_type="semantic",
        project=test_project,
        content="Test memory for integration testing",
        importance=3
    )
    
    # Insert
    memory_id = memory_store.insert(memory)
    assert memory_id is not None
    
    # Retrieve
    retrieved = memory_store.get("semantic", memory_id)
    assert retrieved.id == memory_id
    assert retrieved.content == memory.content
    assert retrieved.project == test_project


def test_memory_with_tags(memory_store, test_project):
    """Test memory with multiple tags."""
    memory = create_memory(
        memory_type="episodic",
        project=test_project,
        content="Completed feature X with tests",
        tags=["feature", "testing", "completed"],
        importance=4
    )
    
    memory_id = memory_store.insert(memory)
    retrieved = memory_store.get("episodic", memory_id)
    
    assert set(retrieved.tags) == {"feature", "testing", "completed"}


def test_procedural_memory_export_marking(memory_store, test_project):
    """Test marking procedural memory as exported."""
    memory = create_memory(
        memory_type="procedural",
        project=test_project,
        content="How to deploy: 1) Build, 2) Test, 3) Deploy",
        importance=5
    )
    
    memory_id = memory_store.insert(memory)
    
    # Mark as exported
    skill_path = ".bob/skills/learned/deploy-procedure/SKILL.md"
    memory_store.mark_exported(memory_id, skill_path)
    
    # Verify
    retrieved = memory_store.get("procedural", memory_id)
    assert retrieved.exported_as_skill == skill_path
    assert retrieved.exported_at is not None


def test_list_procedural_with_importance_filter(memory_store, test_project):
    """Test listing procedural memories with importance filter."""
    # Create memories with different importance levels
    low_importance = create_memory(
        memory_type="procedural",
        project=test_project,
        content="Low importance procedure",
        importance=2
    )
    
    high_importance = create_memory(
        memory_type="procedural",
        project=test_project,
        content="High importance procedure",
        importance=5
    )
    
    memory_store.insert(low_importance)
    high_id = memory_store.insert(high_importance)
    
    # List with min_importance=4
    high_importance_list = memory_store.list_procedural(test_project, min_importance=4)
    
    # Should include high importance memory
    assert any(m.id == high_id for m in high_importance_list)
    
    # Should not include low importance memory
    assert not any(m.id == low_importance.id for m in high_importance_list)


def test_soft_delete_and_recovery(memory_store, test_project):
    """Test soft delete functionality."""
    memory = create_memory(
        memory_type="semantic",
        project=test_project,
        content="Memory to be deleted",
        importance=3
    )
    
    memory_id = memory_store.insert(memory)
    
    # Soft delete
    memory_store.soft_delete("semantic", memory_id)
    
    # Should still be retrievable
    deleted = memory_store.get("semantic", memory_id)
    assert deleted.id == memory_id
    assert deleted.deleted_at is not None


def test_access_tracking(memory_store, test_project):
    """Test access count and timestamp tracking."""
    memory = create_memory(
        memory_type="semantic",
        project=test_project,
        content="Memory for access tracking",
        importance=3
    )
    
    memory_id = memory_store.insert(memory)
    
    # Initial state
    initial = memory_store.get("semantic", memory_id)
    assert initial.access_count == 0
    assert initial.last_accessed_at is None
    
    # Update access
    memory_store.update_access(memory_id)
    
    # Check updated state
    updated = memory_store.get("semantic", memory_id)
    assert updated.access_count == 1
    assert updated.last_accessed_at is not None
    
    # Update again
    memory_store.update_access(memory_id)
    final = memory_store.get("semantic", memory_id)
    assert final.access_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

# Made with Bob
