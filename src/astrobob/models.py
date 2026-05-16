"""Data models for AstroBob memory system."""

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from ulid import ULID


class Provenance(BaseModel):
    """Tracks the origin and lineage of a memory."""
    
    derived_from: list[str] = Field(
        default_factory=list,
        description="List of episode _ids this memory was derived from"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID when memory was created"
    )
    tool_call_id: Optional[str] = Field(
        default=None,
        description="MCP tool call ID that created this memory"
    )
    bob_skill_used: Optional[str] = Field(
        default=None,
        description="Bob skill that was active when creating this memory"
    )


class MemoryDocument(BaseModel):
    """
    Unified schema for all memory types (semantic, episodic, procedural).
    
    This uniform schema future-proofs for single-collection optimization
    while maintaining clear separation of memory types.
    
    Note: The 'id' field will be stored as '_id' in AstraDB.
    """
    
    model_config = ConfigDict(populate_by_name=True)
    
    # Identity
    id: str = Field(
        description="ULID identifier for this memory"
    )
    memory_type: Literal["semantic", "episodic", "procedural"] = Field(
        description="Type of memory: semantic (facts), episodic (events), procedural (how-to)"
    )
    project: str = Field(
        description="Project this memory belongs to"
    )
    scope: Literal["project", "user", "global"] = Field(
        default="project",
        description="Scope of memory visibility"
    )
    
    # Content
    content: str = Field(
        description="Main content of the memory (indexed via $vectorize)"
    )
    summary: Optional[str] = Field(
        default=None,
        description="Optional brief summary of the content"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorization and filtering"
    )
    importance: int = Field(
        ge=1,
        le=5,
        default=3,
        description="Importance level (1=low, 5=critical)"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        default=1.0,
        description="Confidence in the accuracy of this memory"
    )
    
    # Provenance
    source: Literal["bob", "bobshell", "wxo", "cli", "user"] = Field(
        default="cli",
        description="Source that created this memory"
    )
    provenance: Provenance = Field(
        default_factory=Provenance,
        description="Lineage and origin tracking"
    )
    supersedes: Optional[str] = Field(
        default=None,
        description="ID of memory this one supersedes/replaces"
    )
    
    # Lifecycle
    created_at: datetime = Field(
        description="When this memory was created"
    )
    updated_at: datetime = Field(
        description="When this memory was last updated"
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Soft delete timestamp (None = not deleted)"
    )
    last_accessed_at: Optional[datetime] = Field(
        default=None,
        description="When this memory was last accessed/retrieved"
    )
    access_count: int = Field(
        default=0,
        description="Number of times this memory has been accessed"
    )
    success_count: int = Field(
        default=0,
        description="Number of times this memory led to successful outcomes"
    )
    
    # Skill export (procedural only)
    exported_as_skill: Optional[str] = Field(
        default=None,
        description="Path to skill file if exported (procedural memories only)"
    )
    exported_at: Optional[datetime] = Field(
        default=None,
        description="When this memory was exported as a skill"
    )


def generate_ulid() -> str:
    """Generate a new ULID string."""
    return str(ULID())


def create_memory(
    memory_type: Literal["semantic", "episodic", "procedural"],
    project: str,
    content: str,
    *,
    summary: Optional[str] = None,
    tags: Optional[list[str]] = None,
    importance: int = 3,
    confidence: float = 1.0,
    source: Literal["bob", "bobshell", "wxo", "cli", "user"] = "cli",
    scope: Literal["project", "user", "global"] = "project",
    provenance: Optional[Provenance] = None,
    supersedes: Optional[str] = None,
) -> MemoryDocument:
    """
    Factory function to create a new memory document with proper defaults.
    
    Args:
        memory_type: Type of memory (semantic, episodic, procedural)
        project: Project name
        content: Main content of the memory
        summary: Optional brief summary
        tags: Optional list of tags
        importance: Importance level (1-5)
        confidence: Confidence level (0.0-1.0)
        source: Source that created this memory
        scope: Visibility scope
        provenance: Optional provenance information
        supersedes: Optional ID of memory this supersedes
        
    Returns:
        MemoryDocument instance ready to be stored
    """
    now = datetime.now(timezone.utc)
    
    return MemoryDocument(
        id=generate_ulid(),
        memory_type=memory_type,
        project=project,
        scope=scope,
        content=content,
        summary=summary,
        tags=tags or [],
        importance=importance,
        confidence=confidence,
        source=source,
        provenance=provenance or Provenance(),
        supersedes=supersedes,
        created_at=now,
        updated_at=now,
        deleted_at=None,
        last_accessed_at=None,
        access_count=0,
        success_count=0,
        exported_as_skill=None,
        exported_at=None,
    )

# Made with Bob
