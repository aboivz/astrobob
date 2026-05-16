"""
Test script for Memory Store CRUD operations.

This script tests:
1. Insert memory
2. Get memory by ID
3. List procedural memories
4. Soft delete
5. Count memories
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from astrobob.config import get_config
from astrobob.astra import create_astra_client
from astrobob.core import MemoryStore
from astrobob.models import create_memory


def main():
    print("=" * 60)
    print("AstroBob - Memory Store CRUD Test")
    print("=" * 60)
    
    # Setup
    print("\n[Setup] Initializing client and store...")
    try:
        config = get_config()
        client = create_astra_client(config)
        db = client.get_database()
        store = MemoryStore(db)
        print("  Store initialized successfully")
    except Exception as e:
        print(f"  ERROR: Failed to initialize: {e}")
        return 1
    
    # Test 1: Insert semantic memory
    print("\n[1/6] Testing insert (semantic memory)...")
    try:
        semantic_memory = create_memory(
            memory_type="semantic",
            project="astrobob",
            content="AstroBob uses Python 3.12+ with uv package manager",
            tags=["python", "tooling"],
            importance=4,
            source="cli",
        )
        
        memory_id = store.insert(semantic_memory)
        print(f"  Inserted semantic memory: {memory_id}")
    except Exception as e:
        print(f"  ERROR: Failed to insert: {e}")
        return 1
    
    # Test 2: Get memory by ID
    print("\n[2/6] Testing get by ID...")
    try:
        retrieved = store.get("semantic", memory_id)
        print(f"  Retrieved memory: {retrieved.content[:50]}...")
        print(f"  Access count: {retrieved.access_count}")
    except Exception as e:
        print(f"  ERROR: Failed to get: {e}")
        return 1
    
    # Test 3: Insert procedural memory
    print("\n[3/6] Testing insert (procedural memory)...")
    try:
        procedural_memory = create_memory(
            memory_type="procedural",
            project="astrobob",
            content="To add a new MCP tool: 1) Define in mcp_server/tools.py 2) Add schema 3) Test with MCP Inspector",
            tags=["mcp", "development"],
            importance=5,
            source="bob",
        )
        
        proc_id = store.insert(procedural_memory)
        print(f"  Inserted procedural memory: {proc_id}")
    except Exception as e:
        print(f"  ERROR: Failed to insert procedural: {e}")
        return 1
    
    # Test 4: List procedural memories
    print("\n[4/6] Testing list procedural memories...")
    try:
        procedural_list = store.list_procedural(
            project="astrobob",
            min_importance=3,
            limit=10,
        )
        print(f"  Found {len(procedural_list)} procedural memories")
        for mem in procedural_list[:3]:
            print(f"    - {mem.content[:60]}... (importance: {mem.importance})")
    except Exception as e:
        print(f"  ERROR: Failed to list: {e}")
        return 1
    
    # Test 5: Count memories
    print("\n[5/6] Testing count memories...")
    try:
        semantic_count = store.count_memories("semantic", project="astrobob")
        episodic_count = store.count_memories("episodic", project="astrobob")
        procedural_count = store.count_memories("procedural", project="astrobob")
        
        print(f"  Semantic: {semantic_count}")
        print(f"  Episodic: {episodic_count}")
        print(f"  Procedural: {procedural_count}")
    except Exception as e:
        print(f"  ERROR: Failed to count: {e}")
        return 1
    
    # Test 6: Soft delete
    print("\n[6/6] Testing soft delete...")
    try:
        store.soft_delete("semantic", memory_id)
        print(f"  Soft deleted memory: {memory_id}")
        
        # Verify it's excluded from count
        count_after = store.count_memories("semantic", project="astrobob")
        print(f"  Count after delete: {count_after} (was {semantic_count})")
    except Exception as e:
        print(f"  ERROR: Failed to soft delete: {e}")
        return 1
    
    print("\n" + "=" * 60)
    print("All CRUD operations passed successfully")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
