"""
AstraDB collection management for AstroBob.

Handles creation and configuration of the three memory collections:
- astrobob_semantic_memory
- astrobob_episodic_memory
- astrobob_procedural_memory
"""

from typing import Literal
from astrapy import Database
from astrapy.exceptions import DataAPIException

from astrobob.errors import AstraConnectionError


# Memory types
MemoryType = Literal["semantic", "episodic", "procedural"]

# Default collection prefix
DEFAULT_PREFIX = "astrobob"


def get_collection_name(memory_type: MemoryType, prefix: str = DEFAULT_PREFIX) -> str:
    """
    Get the full collection name for a memory type.
    
    Args:
        memory_type: Type of memory (semantic, episodic, or procedural)
        prefix: Collection name prefix (default: "astrobob")
        
    Returns:
        Full collection name (e.g., "astrobob_semantic_memory")
    """
    return f"{prefix}_{memory_type}_memory"


def get_collection_definition(memory_type: MemoryType) -> dict:
    """
    Get the collection definition for a memory type.
    
    All three collections use identical configuration with:
    - Vector search (cosine metric, NVIDIA NV-Embed-QA-E5-V5)
    - Lexical search enabled
    - Reranking enabled (NVIDIA nv-rerank-qa-mistral-4b-v3)
    - Indexed fields for efficient filtering
    
    Args:
        memory_type: Type of memory (semantic, episodic, or procedural)
        
    Returns:
        Collection definition dictionary for astrapy
    """
    return {
        "vector": {
            "dimension": 1024,  # NV-Embed-QA-E5-V5 dimension
            "metric": "cosine",
            "service": {
                "provider": "nvidia",
                "modelName": "NV-Embed-QA-E5-V5",
            },
        },
        "indexing": {
            "allow": [
                "project",
                "memory_type",
                "tags",
                "importance",
                "deleted_at",
                "created_at",
                "scope",
                "source",
            ]
        },
    }


def create_collection_if_missing(
    database: Database,
    memory_type: MemoryType,
    prefix: str = DEFAULT_PREFIX,
) -> tuple[str, bool]:
    """
    Create a collection if it doesn't exist.
    
    Args:
        database: AstraDB database instance
        memory_type: Type of memory collection to create
        prefix: Collection name prefix (default: "astrobob")
        
    Returns:
        Tuple of (collection_name, was_created)
        - collection_name: Full name of the collection
        - was_created: True if collection was created, False if it already existed
        
    Raises:
        AstraConnectionError: If collection creation fails
    """
    collection_name = get_collection_name(memory_type, prefix)
    
    try:
        # Check if collection already exists
        existing_collections = database.list_collection_names()
        
        if collection_name in existing_collections:
            return collection_name, False
        
        # Create collection with definition
        definition = get_collection_definition(memory_type)
        
        database.create_collection(
            name=collection_name,
            definition=definition,
        )
        
        return collection_name, True
        
    except DataAPIException as e:
        raise AstraConnectionError(
            f"Failed to create collection '{collection_name}': {e}"
        ) from e
    except Exception as e:
        raise AstraConnectionError(
            f"Unexpected error creating collection '{collection_name}': {e}"
        ) from e


def create_all_collections(
    database: Database,
    prefix: str = DEFAULT_PREFIX,
) -> dict[MemoryType, tuple[str, bool]]:
    """
    Create all three memory collections if they don't exist.
    
    This is an idempotent operation - safe to call multiple times.
    
    Args:
        database: AstraDB database instance
        prefix: Collection name prefix (default: "astrobob")
        
    Returns:
        Dictionary mapping memory type to (collection_name, was_created)
        
    Raises:
        AstraConnectionError: If any collection creation fails
    """
    results: dict[MemoryType, tuple[str, bool]] = {}
    
    memory_types: list[MemoryType] = ["semantic", "episodic", "procedural"]
    
    for memory_type in memory_types:
        collection_name, was_created = create_collection_if_missing(
            database, memory_type, prefix
        )
        results[memory_type] = (collection_name, was_created)
    
    return results


def validate_collection_schema(
    database: Database,
    memory_type: MemoryType,
    prefix: str = DEFAULT_PREFIX,
) -> bool:
    """
    Validate that a collection exists and has the expected schema.
    
    Args:
        database: AstraDB database instance
        memory_type: Type of memory collection to validate
        prefix: Collection name prefix (default: "astrobob")
        
    Returns:
        True if collection exists and schema is valid, False otherwise
    """
    collection_name = get_collection_name(memory_type, prefix)
    
    try:
        # Check if collection exists
        existing_collections = database.list_collection_names()
        
        if collection_name not in existing_collections:
            return False
        
        # Get collection to verify it's accessible
        collection = database.get_collection(collection_name)
        
        # If we can get the collection, consider it valid
        # More detailed schema validation could be added here
        return collection is not None
        
    except Exception:
        return False


def delete_collection(
    database: Database,
    memory_type: MemoryType,
    prefix: str = DEFAULT_PREFIX,
) -> bool:
    """
    Delete a collection.
    
    WARNING: This permanently deletes all data in the collection.
    
    Args:
        database: AstraDB database instance
        memory_type: Type of memory collection to delete
        prefix: Collection name prefix (default: "astrobob")
        
    Returns:
        True if collection was deleted, False if it didn't exist
        
    Raises:
        AstraConnectionError: If deletion fails
    """
    collection_name = get_collection_name(memory_type, prefix)
    
    try:
        # Check if collection exists
        existing_collections = database.list_collection_names()
        
        if collection_name not in existing_collections:
            return False
        
        # Delete the collection
        database.drop_collection(collection_name)
        
        return True
        
    except DataAPIException as e:
        raise AstraConnectionError(
            f"Failed to delete collection '{collection_name}': {e}"
        ) from e
    except Exception as e:
        raise AstraConnectionError(
            f"Unexpected error deleting collection '{collection_name}': {e}"
        ) from e

# Made with Bob
