"""
Memory Store - CRUD operations for AstroBob memories.

Provides high-level operations for storing and retrieving memories
from AstraDB collections.
"""

from datetime import datetime
from typing import Optional, Literal

from astrapy import Database
from astrapy.exceptions import DataAPIException

from astrobob.models import MemoryDocument, create_memory
from astrobob.errors import AstraConnectionError, MemoryNotFoundError
from astrobob.astra.collections import get_collection_name


class MemoryStore:
    """
    High-level interface for memory CRUD operations.
    
    Handles all interactions with AstraDB collections for storing,
    retrieving, updating, and deleting memories.
    """
    
    def __init__(self, database: Database, collection_prefix: str = "astrobob"):
        """
        Initialize the memory store.
        
        Args:
            database: AstraDB database instance
            collection_prefix: Prefix for collection names (default: "astrobob")
        """
        self.database = database
        self.collection_prefix = collection_prefix
    
    def _get_collection(self, memory_type: Literal["semantic", "episodic", "procedural"]):
        """Get collection for a memory type."""
        collection_name = get_collection_name(memory_type, self.collection_prefix)
        return self.database.get_collection(collection_name)
    
    def insert(self, memory: MemoryDocument) -> str:
        """
        Insert a new memory document.
        
        Args:
            memory: Memory document to insert
            
        Returns:
            The memory ID (ULID)
            
        Raises:
            AstraConnectionError: If insertion fails
        """
        try:
            collection = self._get_collection(memory.memory_type)
            
            # Convert to dict for insertion, mapping 'id' to '_id'
            doc = memory.model_dump(mode="json")
            doc["_id"] = doc.pop("id")  # AstraDB uses _id
            
            # Insert the document
            result = collection.insert_one(doc)
            
            return memory.id
            
        except DataAPIException as e:
            raise AstraConnectionError(
                f"Failed to insert memory: {e}"
            ) from e
        except Exception as e:
            raise AstraConnectionError(
                f"Unexpected error inserting memory: {e}"
            ) from e
    
    def get(
        self,
        memory_type: Literal["semantic", "episodic", "procedural"],
        memory_id: str
    ) -> MemoryDocument:
        """
        Get a memory by ID.
        
        Args:
            memory_type: Type of memory
            memory_id: Memory ID (ULID)
            
        Returns:
            Memory document
            
        Raises:
            MemoryNotFoundError: If memory doesn't exist
            AstraConnectionError: If retrieval fails
        """
        try:
            collection = self._get_collection(memory_type)
            
            # Find by _id
            doc = collection.find_one({"_id": memory_id})
            
            if doc is None:
                raise MemoryNotFoundError(
                    f"Memory not found: {memory_type}/{memory_id}"
                )
            
            # Map _id back to id for Pydantic
            doc["id"] = doc.pop("_id")
            
            # Update last_accessed_at and access_count
            self.update_access(memory_type, memory_id)
            
            return MemoryDocument(**doc)
            
        except MemoryNotFoundError:
            raise
        except DataAPIException as e:
            raise AstraConnectionError(
                f"Failed to get memory: {e}"
            ) from e
        except Exception as e:
            raise AstraConnectionError(
                f"Unexpected error getting memory: {e}"
            ) from e
    
    def list_procedural(
        self,
        project: str,
        min_importance: int = 1,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[MemoryDocument]:
        """
        List procedural memories for a project.
        
        Args:
            project: Project name
            min_importance: Minimum importance level (1-5)
            limit: Maximum number of results
            include_deleted: Whether to include soft-deleted memories
            
        Returns:
            List of procedural memory documents
            
        Raises:
            AstraConnectionError: If query fails
        """
        try:
            collection = self._get_collection("procedural")
            
            # Build filter
            filter_dict = {
                "project": project,
                "importance": {"$gte": min_importance},
            }
            
            if not include_deleted:
                filter_dict["deleted_at"] = None
            
            # Query with sort by importance (descending) and created_at (descending)
            cursor = collection.find(
                filter=filter_dict,
                sort={"importance": -1, "created_at": -1},
                limit=limit,
            )
            
            # Convert results
            results = []
            for doc in cursor:
                doc["id"] = doc.pop("_id")
                results.append(MemoryDocument(**doc))
            
            return results
            
        except DataAPIException as e:
            raise AstraConnectionError(
                f"Failed to list procedural memories: {e}"
            ) from e
        except Exception as e:
            raise AstraConnectionError(
                f"Unexpected error listing procedural memories: {e}"
            ) from e
    
    def soft_delete(
        self,
        memory_type: Literal["semantic", "episodic", "procedural"],
        memory_id: str
    ) -> None:
        """
        Soft delete a memory (sets deleted_at timestamp).
        
        Args:
            memory_type: Type of memory
            memory_id: Memory ID (ULID)
            
        Raises:
            MemoryNotFoundError: If memory doesn't exist
            AstraConnectionError: If deletion fails
        """
        try:
            collection = self._get_collection(memory_type)
            
            # Update with deleted_at timestamp
            result = collection.update_one(
                filter={"_id": memory_id},
                update={"$set": {"deleted_at": datetime.utcnow().isoformat()}},
            )
            
            if result.update_info["updatedExisting"] is False:
                raise MemoryNotFoundError(
                    f"Memory not found: {memory_type}/{memory_id}"
                )
            
        except MemoryNotFoundError:
            raise
        except DataAPIException as e:
            raise AstraConnectionError(
                f"Failed to soft delete memory: {e}"
            ) from e
        except Exception as e:
            raise AstraConnectionError(
                f"Unexpected error soft deleting memory: {e}"
            ) from e
    
    def mark_exported(
        self,
        memory_id: str,
        skill_path: str
    ) -> None:
        """
        Mark a procedural memory as exported to a skill.
        
        Args:
            memory_id: Memory ID (ULID)
            skill_path: Path to the exported skill file
            
        Raises:
            MemoryNotFoundError: If memory doesn't exist
            AstraConnectionError: If update fails
        """
        try:
            collection = self._get_collection("procedural")
            
            # Update with export info
            result = collection.update_one(
                filter={"_id": memory_id},
                update={
                    "$set": {
                        "exported_as_skill": skill_path,
                        "exported_at": datetime.utcnow().isoformat(),
                    }
                },
            )
            
            if result.update_info["updatedExisting"] is False:
                raise MemoryNotFoundError(
                    f"Procedural memory not found: {memory_id}"
                )
            
        except MemoryNotFoundError:
            raise
        except DataAPIException as e:
            raise AstraConnectionError(
                f"Failed to mark memory as exported: {e}"
            ) from e
        except Exception as e:
            raise AstraConnectionError(
                f"Unexpected error marking memory as exported: {e}"
            ) from e
    
    def update_access(
        self,
        memory_type: Literal["semantic", "episodic", "procedural"],
        memory_id: str
    ) -> None:
        """
        Update access tracking for a memory.
        
        Increments access_count and updates last_accessed_at.
        
        Args:
            memory_type: Type of memory
            memory_id: Memory ID (ULID)
            
        Raises:
            AstraConnectionError: If update fails
        """
        try:
            collection = self._get_collection(memory_type)
            
            # Update access tracking
            collection.update_one(
                filter={"_id": memory_id},
                update={
                    "$set": {"last_accessed_at": datetime.utcnow().isoformat()},
                    "$inc": {"access_count": 1},
                },
            )
            
        except DataAPIException as e:
            # Don't raise for access tracking failures - log and continue
            pass
        except Exception:
            # Don't raise for access tracking failures
            pass
    
    def increment_success_count(
        self,
        memory_type: Literal["semantic", "episodic", "procedural"],
        memory_id: str
    ) -> None:
        """
        Increment success count for a memory.
        
        Used to track how often a procedural memory leads to successful outcomes.
        
        Args:
            memory_type: Type of memory
            memory_id: Memory ID (ULID)
            
        Raises:
            AstraConnectionError: If update fails
        """
        try:
            collection = self._get_collection(memory_type)
            
            # Increment success count
            collection.update_one(
                filter={"_id": memory_id},
                update={"$inc": {"success_count": 1}},
            )
            
        except DataAPIException as e:
            raise AstraConnectionError(
                f"Failed to increment success count: {e}"
            ) from e
        except Exception as e:
            raise AstraConnectionError(
                f"Unexpected error incrementing success count: {e}"
            ) from e
    
    def count_memories(
        self,
        memory_type: Literal["semantic", "episodic", "procedural"],
        project: Optional[str] = None,
        include_deleted: bool = False,
    ) -> int:
        """
        Count memories in a collection.
        
        Args:
            memory_type: Type of memory
            project: Optional project filter
            include_deleted: Whether to include soft-deleted memories
            
        Returns:
            Count of matching memories
            
        Raises:
            AstraConnectionError: If count fails
        """
        try:
            collection = self._get_collection(memory_type)
            
            # Build filter
            filter_dict = {}
            if project:
                filter_dict["project"] = project
            if not include_deleted:
                filter_dict["deleted_at"] = None
            
            # Count documents
            count = collection.count_documents(filter=filter_dict, upper_bound=10000)
            
            return count
            
        except DataAPIException as e:
            raise AstraConnectionError(
                f"Failed to count memories: {e}"
            ) from e
        except Exception as e:
            raise AstraConnectionError(
                f"Unexpected error counting memories: {e}"
            ) from e

# Made with Bob
