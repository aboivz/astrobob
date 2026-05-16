"""
MCP tool implementations for AstroBob.

Implements the 5 core tools that handle memory operations.
"""

from typing import Any, Literal, Optional
from datetime import datetime, timezone

from astrobob.astra.client import AstraClient
from astrobob.config import AstroBobConfig
from astrobob.core.store import MemoryStore
from astrobob.core.retriever import MemoryRetriever
from astrobob.core.reflector import MemoryReflector
from astrobob.models import create_memory, Provenance


class MemoryTools:
    """Implements all MCP tools for memory operations."""
    
    def __init__(self, config: AstroBobConfig):
        """
        Initialize memory tools.
        
        Args:
            config: AstroBob configuration
        """
        self.config = config
        self.client = AstraClient(config)
        self.database = self.client.get_database()
        self.store = MemoryStore(self.database)
        self.retriever = MemoryRetriever(self.client, self.store)
        self.reflector = MemoryReflector()
    
    async def remember(
        self,
        content: str,
        memory_type: Literal["semantic", "episodic", "procedural"],
        project: str,
        tags: Optional[list[str]] = None,
        importance: int = 3,
        source: Literal["bob", "bobshell", "wxo", "cli", "user"] = "bob",
    ) -> dict[str, Any]:
        """
        Store a new memory.
        
        Args:
            content: Memory content
            memory_type: Type of memory
            project: Project name
            tags: Optional tags
            importance: Importance level (1-5)
            source: Source creating the memory
            
        Returns:
            Result with memory ID and confirmation
        """
        try:
            # Create memory document
            memory = create_memory(
                memory_type=memory_type,
                project=project,
                content=content,
                tags=tags or [],
                importance=importance,
                source=source,
            )
            
            # Store in AstraDB
            memory_id = self.store.insert(memory)
            
            # Check if reflection should be suggested (for episodic memories)
            suggestion = None
            if memory_type == "episodic":
                # Get recent episode count for this project
                recent_episodes = self.retriever.recall_recent_episodes(
                    project=project,
                    limit=10,
                )
                recent_count = len(recent_episodes)
                
                suggestion = self.reflector.should_suggest_reflection(
                    memory,
                    recent_episode_count=recent_count,
                )
            
            result = {
                "success": True,
                "memory_id": memory_id,
                "memory_type": memory_type,
                "project": project,
                "importance": importance,
                "message": f"Stored {memory_type} memory: {content[:100]}..."
            }
            
            if suggestion:
                result["reflection_suggestion"] = {
                    "reason": suggestion.reason,
                    "suggested_importance": suggestion.suggested_importance,
                    "message": "Consider calling reflect() to create a procedural memory"
                }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to store memory: {e}"
            }
    
    async def recall(
        self,
        query: str,
        project: str,
        memory_types: Optional[list[Literal["semantic", "episodic", "procedural"]]] = None,
        tags: Optional[list[str]] = None,
        limit: int = 10,
        min_importance: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Search and retrieve memories.
        
        Args:
            query: Natural language search query
            project: Project to search
            memory_types: Specific types to search (None = auto-detect)
            tags: Filter by tags
            limit: Max results
            min_importance: Minimum importance level
            
        Returns:
            Search results with memories and scores
        """
        try:
            # Perform recall
            results = self.retriever.recall(
                query=query,
                project=project,
                memory_types=memory_types,
                tags=tags,
                limit=limit,
                min_importance=min_importance,
            )
            
            # Format results
            memories = []
            for memory, score in results:
                memories.append({
                    "id": memory.id,
                    "type": memory.memory_type,
                    "content": memory.content,
                    "summary": memory.summary,
                    "tags": memory.tags,
                    "importance": memory.importance,
                    "created_at": memory.created_at.isoformat(),
                    "score": round(score, 4),
                    "access_count": memory.access_count,
                    "success_count": memory.success_count,
                })
            
            return {
                "success": True,
                "query": query,
                "count": len(memories),
                "memories": memories,
                "message": f"Found {len(memories)} memories matching '{query}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to recall memories: {e}"
            }
    
    async def reflect(
        self,
        project: str,
        episode_ids: list[str],
        lesson: str,
        tags: Optional[list[str]] = None,
        importance: int = 4,
    ) -> dict[str, Any]:
        """
        Convert episodic memories to procedural knowledge.
        
        Args:
            project: Project name
            episode_ids: IDs of episodes to reflect on
            lesson: The procedural knowledge extracted
            tags: Tags for the procedural memory
            importance: Importance level (default 4)
            
        Returns:
            Result with new procedural memory ID
        """
        try:
            # Retrieve the episodes
            episodes = []
            for episode_id in episode_ids:
                memory = self.retriever.recall_by_id("episodic", episode_id)
                if memory:
                    episodes.append(memory)
            
            if not episodes:
                return {
                    "success": False,
                    "error": "No valid episodes found",
                    "message": "Could not retrieve any of the specified episodes"
                }
            
            # Extract keywords from episodes if tags not provided
            if not tags:
                tags = self.reflector.extract_lesson_keywords(episodes)
            
            # Create procedural memory with provenance
            provenance = Provenance(
                derived_from=episode_ids,
                session_id=None,
                tool_call_id=None,
            )
            
            procedural = create_memory(
                memory_type="procedural",
                project=project,
                content=lesson,
                tags=tags or [],
                importance=importance,
                source="bob",
                provenance=provenance,
            )
            
            # Store the procedural memory
            memory_id = self.store.insert(procedural)
            
            return {
                "success": True,
                "memory_id": memory_id,
                "memory_type": "procedural",
                "project": project,
                "importance": importance,
                "episode_count": len(episodes),
                "derived_from": episode_ids,
                "message": f"Created procedural memory from {len(episodes)} episodes"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create reflection: {e}"
            }
    
    async def forget(
        self,
        memory_type: Literal["semantic", "episodic", "procedural"],
        memory_id: str,
        reason: str = "No longer needed",
    ) -> dict[str, Any]:
        """
        Soft-delete a memory.
        
        Args:
            memory_type: Type of memory
            memory_id: Memory ID
            reason: Reason for deletion
            
        Returns:
            Confirmation of deletion
        """
        try:
            # Soft delete the memory
            self.store.soft_delete(memory_type, memory_id)
            
            return {
                "success": True,
                "memory_id": memory_id,
                "memory_type": memory_type,
                "reason": reason,
                "message": f"Soft-deleted {memory_type} memory {memory_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete memory: {e}"
            }
    
    async def audit_trail(
        self,
        memory_type: Literal["semantic", "episodic", "procedural"],
        memory_id: str,
    ) -> dict[str, Any]:
        """
        View memory provenance and history.
        
        Args:
            memory_type: Type of memory
            memory_id: Memory ID
            
        Returns:
            Detailed memory information including provenance
        """
        try:
            # Retrieve the memory
            memory = self.store.get(memory_type, memory_id)
            
            # Format provenance
            provenance_info = {
                "derived_from": memory.provenance.derived_from,
                "session_id": memory.provenance.session_id,
                "tool_call_id": memory.provenance.tool_call_id,
                "bob_skill_used": memory.provenance.bob_skill_used,
            }
            
            # Build audit trail
            audit = {
                "success": True,
                "memory_id": memory.id,
                "memory_type": memory.memory_type,
                "project": memory.project,
                "scope": memory.scope,
                "content": memory.content,
                "summary": memory.summary,
                "tags": memory.tags,
                "importance": memory.importance,
                "confidence": memory.confidence,
                "source": memory.source,
                "provenance": provenance_info,
                "supersedes": memory.supersedes,
                "created_at": memory.created_at.isoformat(),
                "updated_at": memory.updated_at.isoformat(),
                "deleted_at": memory.deleted_at.isoformat() if memory.deleted_at else None,
                "last_accessed_at": memory.last_accessed_at.isoformat() if memory.last_accessed_at else None,
                "access_count": memory.access_count,
                "success_count": memory.success_count,
                "exported_as_skill": memory.exported_as_skill,
                "exported_at": memory.exported_at.isoformat() if memory.exported_at else None,
            }
            
            return audit
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve audit trail: {e}"
            }

# Made with Bob
