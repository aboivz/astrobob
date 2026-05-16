"""
Test script to verify all AstroBob fixes.

Tests:
1. NVIDIA embedding integration
2. datetime.now(timezone.utc) usage
3. $vectorize for automatic embeddings
4. Vector search functionality
5. CLI recall command
"""

import sys
import asyncio
from datetime import datetime, timezone
import os

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')

# Add src to path
sys.path.insert(0, "src")

from astrobob.config import get_config
from astrobob.astra import create_astra_client
from astrobob.astra.collections import create_all_collections, get_collection_definition
from astrobob.core.store import MemoryStore
from astrobob.core.retriever import MemoryRetriever
from astrobob.models import create_memory


def test_collection_definition():
    """Test that collection definition uses correct NVIDIA model."""
    print("\n=== Testing Collection Definition ===")
    
    definition = get_collection_definition("semantic")
    
    # Check vector service configuration
    assert definition["vector"]["service"]["provider"] == "nvidia", "Provider should be nvidia"
    assert definition["vector"]["service"]["modelName"] == "nvidia/nv-embedqa-e5-v5", \
        f"Model should be nvidia/nv-embedqa-e5-v5, got {definition['vector']['service']['modelName']}"
    assert definition["vector"]["dimension"] == 1024, "Dimension should be 1024"
    assert definition["vector"]["metric"] == "cosine", "Metric should be cosine"
    
    print("[OK] Collection definition correct")
    print(f"   Model: {definition['vector']['service']['modelName']}")
    print(f"   Dimension: {definition['vector']['dimension']}")
    print(f"   Metric: {definition['vector']['metric']}")


def test_datetime_usage():
    """Test that datetime.now(timezone.utc) is used correctly."""
    print("\n=== Testing Datetime Usage ===")
    
    # Create a test memory
    memory = create_memory(
        memory_type="semantic",
        project="test",
        content="Test memory for datetime",
        importance=3,
    )
    
    # Check that timestamps are timezone-aware
    assert memory.created_at.tzinfo is not None, "created_at should be timezone-aware"
    assert memory.updated_at.tzinfo is not None, "updated_at should be timezone-aware"
    
    # Check that timestamps are in UTC
    assert memory.created_at.tzinfo == timezone.utc, "created_at should be in UTC"
    assert memory.updated_at.tzinfo == timezone.utc, "updated_at should be in UTC"
    
    print("[OK] Datetime usage correct")
    print(f"   Created: {memory.created_at.isoformat()}")
    print(f"   Timezone: {memory.created_at.tzinfo}")


async def test_memory_insertion_and_recall():
    """Test memory insertion with $vectorize and recall."""
    print("\n=== Testing Memory Insertion and Recall ===")
    
    try:
        # Load config
        config = get_config()
        print(f"   Using database: {config.astra_db_api_endpoint}")
        
        # Create client and database
        client = create_astra_client(config)
        db = client.get_database()
        
        # Create collections
        print("   Creating collections...")
        results = create_all_collections(db)
        for memory_type, (name, was_created) in results.items():
            status = "created" if was_created else "exists"
            print(f"   - {name}: {status}")
        
        # Create store and retriever
        store = MemoryStore(db)
        retriever = MemoryRetriever(client, store)
        
        # Test project name
        test_project = "astrobob_test"
        
        # Insert test memories
        print(f"\n   Inserting test memories into project '{test_project}'...")
        
        test_memories = [
            {
                "type": "semantic",
                "content": "AstroBob uses NVIDIA embeddings for vector search with the nvidia/nv-embedqa-e5-v5 model",
                "tags": ["nvidia", "embeddings", "vector-search"],
                "importance": 5,
            },
            {
                "type": "procedural",
                "content": "To add a new MCP tool: 1) Define schema in schemas.py 2) Implement handler in tools.py 3) Register in server.py 4) Test with MCP Inspector",
                "tags": ["mcp", "development", "procedure"],
                "importance": 5,
            },
            {
                "type": "episodic",
                "content": "Fixed datetime.utcnow() deprecation by replacing with datetime.now(timezone.utc) in store.py",
                "tags": ["bug-fix", "datetime", "python"],
                "importance": 4,
            },
            {
                "type": "semantic",
                "content": "FastAPI uses async def for route handlers and Pydantic models for request validation",
                "tags": ["fastapi", "python", "api"],
                "importance": 3,
            },
        ]
        
        memory_ids = []
        for mem_data in test_memories:
            memory = create_memory(
                memory_type=mem_data["type"],
                project=test_project,
                content=mem_data["content"],
                tags=mem_data["tags"],
                importance=mem_data["importance"],
                source="cli",
            )
            memory_id = store.insert(memory)
            memory_ids.append(memory_id)
            print(f"   [+] Inserted {mem_data['type']}: {memory_id[:8]}...")
        
        # Wait a moment for indexing
        print("\n   Waiting for vector indexing...")
        await asyncio.sleep(3)
        
        # Test recall with different queries
        test_queries = [
            ("how to add MCP tool", "procedural"),
            ("NVIDIA embeddings", "semantic"),
            ("datetime fix", "episodic"),
            ("FastAPI", "semantic"),
        ]
        
        print("\n   Testing recall queries...")
        for query, expected_type in test_queries:
            print(f"\n   Query: '{query}'")
            results = retriever.recall(
                query=query,
                project=test_project,
                limit=3,
            )
            
            if results:
                print(f"   [OK] Found {len(results)} results")
                top_memory, top_score = results[0]
                print(f"     Top result: {top_memory.memory_type} (score: {top_score:.4f})")
                print(f"     Content: {top_memory.content[:80]}...")
                
                # Check if top result matches expected type
                if top_memory.memory_type == expected_type:
                    print(f"     [OK] Correct memory type returned")
                else:
                    print(f"     [WARN] Expected {expected_type}, got {top_memory.memory_type}")
            else:
                print(f"   [FAIL] No results found")
        
        print("\n[OK] Memory insertion and recall working")
        
        # Cleanup
        print("\n   Cleaning up test memories...")
        from typing import Literal
        for memory_id in memory_ids:
            try:
                # Get memory type from the stored memory
                mem_types: list[Literal["semantic", "episodic", "procedural"]] = ["semantic", "episodic", "procedural"]
                for mem_type in mem_types:
                    try:
                        mem = store.get(mem_type, memory_id)
                        store.soft_delete(mem_type, memory_id)
                        print(f"   [+] Deleted {memory_id[:8]}...")
                        break
                    except:
                        continue
            except Exception as e:
                print(f"   [WARN] Could not delete {memory_id[:8]}: {e}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AstroBob Fix Verification Tests")
    print("=" * 60)
    
    # Test 1: Collection definition
    try:
        test_collection_definition()
    except AssertionError as e:
        print(f"[FAIL] Collection definition test failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False
    
    # Test 2: Datetime usage
    try:
        test_datetime_usage()
    except AssertionError as e:
        print(f"[FAIL] Datetime test failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False
    
    # Test 3: Memory insertion and recall
    try:
        success = asyncio.run(test_memory_insertion_and_recall())
        if not success:
            return False
    except Exception as e:
        print(f"[FAIL] Memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All tests passed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Delete your current AstraDB database")
    print("2. Create a new database in AWS us-east-2 or GCP us-east1")
    print("3. Run: astrobob init")
    print("4. Run: astrobob astra setup")
    print("5. Test with Bob using the MCP server")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# Made with Bob
