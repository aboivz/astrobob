"""
AstroBob Memory Tool for WxO Agents

This module provides a Python wrapper around AstroBob's MCP tools
for use in WxO multi-agent systems.
"""

import os
import json
from typing import Optional, Literal
from datetime import datetime


class AstroBobMemoryTool:
    """
    Python wrapper for AstroBob memory operations.
    
    This tool can be used by WxO agents to interact with AstroBob's
    persistent memory system via MCP or direct Python calls.
    
    Usage:
        tool = AstroBobMemoryTool()
        
        # Store a memory
        memory_id = tool.remember(
            content="How to add MCP tool: ...",
            memory_type="procedural",
            project="my-project",
            tags=["mcp", "development"],
            importance=4
        )
        
        # Retrieve memories
        results = tool.recall(
            query="how to add MCP tool",
            project="my-project"
        )
        
        # Reflect on episodes
        procedure_id = tool.reflect(
            project="my-project",
            episode_ids=["id1", "id2"],
            lesson="Always test MCP tools with Inspector"
        )
    """
    
    def __init__(
        self,
        mcp_server_command: Optional[str] = None,
        use_direct_api: bool = False
    ):
        """
        Initialize the memory tool.
        
        Args:
            mcp_server_command: Command to start MCP server (default: "astrobob mcp")
            use_direct_api: If True, use direct Python API instead of MCP
        """
        self.mcp_server_command = mcp_server_command or "astrobob mcp"
        self.use_direct_api = use_direct_api
        
        if use_direct_api:
            self._init_direct_api()
    
    def _init_direct_api(self):
        """Initialize direct Python API access."""
        try:
            from astrobob.config import get_config
            from astrobob.astra import create_astra_client
            from astrobob.core.store import MemoryStore
            from astrobob.core.retriever import Retriever
            
            config = get_config()
            client = create_astra_client(config)
            db = client.get_database()
            
            self.store = MemoryStore(db)
            self.retriever = Retriever(db)
        except ImportError as e:
            raise RuntimeError(
                f"Direct API mode requires astrobob package: {e}"
            )
    
    def remember(
        self,
        content: str,
        memory_type: Literal["semantic", "episodic", "procedural"],
        project: str,
        tags: Optional[list[str]] = None,
        importance: int = 3,
        source: str = "wxo-agent",
        session_id: Optional[str] = None,
        agent_name: Optional[str] = None
    ) -> str:
        """
        Store a new memory.
        
        Args:
            content: Memory content (clear, actionable text)
            memory_type: Type of memory (semantic/episodic/procedural)
            project: Project name
            tags: List of tags for categorization
            importance: Importance level (1-5)
            source: Source identifier (default: "wxo-agent")
            session_id: Optional session ID for tracking
            agent_name: Name of the agent creating this memory
            
        Returns:
            Memory ID (ULID)
            
        Example:
            >>> tool.remember(
            ...     content="Project uses FastAPI 0.104 with async routes",
            ...     memory_type="semantic",
            ...     project="my-api",
            ...     tags=["fastapi", "architecture"],
            ...     importance=3,
            ...     agent_name="code-memory"
            ... )
            '01KRPAF...'
        """
        if self.use_direct_api:
            from astrobob.models import create_memory
            
            # Add agent name to tags if provided
            if agent_name and tags:
                tags = tags + [f"agent:{agent_name}"]
            elif agent_name:
                tags = [f"agent:{agent_name}"]
            
            memory = create_memory(
                memory_type=memory_type,
                content=content,
                project=project,
                tags=tags or [],
                importance=importance,
                source=source,
                session_id=session_id
            )
            
            return self.store.insert(memory)
        else:
            # Use MCP call (implementation depends on MCP client)
            return self._call_mcp_tool("remember", {
                "content": content,
                "memory_type": memory_type,
                "project": project,
                "tags": tags or [],
                "importance": importance,
                "source": source,
                "session_id": session_id
            })
    
    def recall(
        self,
        query: str,
        project: Optional[str] = None,
        memory_type: Optional[Literal["semantic", "episodic", "procedural"]] = None,
        tags: Optional[list[str]] = None,
        limit: int = 10
    ) -> list[dict]:
        """
        Search for relevant memories.
        
        Args:
            query: Search query (natural language)
            project: Filter by project name
            memory_type: Filter by memory type
            tags: Filter by tags
            limit: Maximum number of results
            
        Returns:
            List of memory documents with scores
            
        Example:
            >>> results = tool.recall(
            ...     query="how to add MCP tool",
            ...     project="astrobob",
            ...     memory_type="procedural",
            ...     limit=5
            ... )
            >>> for result in results:
            ...     print(f"{result['score']:.2f}: {result['content'][:50]}...")
        """
        if self.use_direct_api:
            results = self.retriever.search(
                query=query,
                project=project,
                memory_type=memory_type,
                tags=tags,
                limit=limit
            )
            
            # Convert to dict format
            return [
                {
                    "id": r.memory.id,
                    "content": r.memory.content,
                    "memory_type": r.memory.memory_type,
                    "project": r.memory.project,
                    "tags": r.memory.tags,
                    "importance": r.memory.importance,
                    "score": r.score,
                    "created_at": r.memory.created_at.isoformat()
                }
                for r in results
            ]
        else:
            return self._call_mcp_tool("recall", {
                "query": query,
                "project": project,
                "memory_type": memory_type,
                "tags": tags,
                "limit": limit
            })
    
    def reflect(
        self,
        project: str,
        episode_ids: list[str],
        lesson: str,
        tags: Optional[list[str]] = None,
        importance: int = 4,
        agent_name: Optional[str] = None
    ) -> str:
        """
        Create a procedural memory from multiple episodes.
        
        Args:
            project: Project name
            episode_ids: List of episode memory IDs to reflect on
            lesson: The distilled lesson/procedure
            tags: Tags for the procedural memory
            importance: Importance level (typically 4-5 for reflections)
            agent_name: Name of the agent creating this reflection
            
        Returns:
            Procedural memory ID
            
        Example:
            >>> procedure_id = tool.reflect(
            ...     project="my-api",
            ...     episode_ids=["01KRP...", "01KRQ..."],
            ...     lesson="When adding auth: 1)Check existing patterns 2)Test with Postman 3)Document endpoints",
            ...     tags=["auth", "api", "procedure"],
            ...     agent_name="supervisor"
            ... )
        """
        if self.use_direct_api:
            # Add agent name to tags if provided
            if agent_name and tags:
                tags = tags + [f"agent:{agent_name}"]
            elif agent_name:
                tags = [f"agent:{agent_name}"]
            
            from astrobob.models import create_memory, Provenance
            
            memory = create_memory(
                memory_type="procedural",
                content=lesson,
                project=project,
                tags=tags or [],
                importance=importance,
                source="wxo-agent",
                provenance=Provenance(derived_from=episode_ids)
            )
            
            return self.store.insert(memory)
        else:
            return self._call_mcp_tool("reflect", {
                "project": project,
                "episode_ids": episode_ids,
                "lesson": lesson,
                "tags": tags or [],
                "importance": importance
            })
    
    def audit_trail(self, memory_type: str, memory_id: str) -> dict:
        """
        Get the audit trail for a memory.
        
        Args:
            memory_type: Type of memory
            memory_id: Memory ID
            
        Returns:
            Audit information including provenance and access history
        """
        if self.use_direct_api:
            memory = self.store.get(memory_type, memory_id)
            return {
                "id": memory.id,
                "memory_type": memory.memory_type,
                "created_at": memory.created_at.isoformat(),
                "updated_at": memory.updated_at.isoformat(),
                "access_count": memory.access_count,
                "success_count": memory.success_count,
                "provenance": {
                    "derived_from": memory.provenance.derived_from,
                    "session_id": memory.provenance.session_id,
                    "tool_call_id": memory.provenance.tool_call_id,
                    "bob_skill_used": memory.provenance.bob_skill_used
                },
                "exported_as_skill": memory.exported_as_skill,
                "exported_at": memory.exported_at.isoformat() if memory.exported_at else None
            }
        else:
            return self._call_mcp_tool("audit_trail", {
                "memory_type": memory_type,
                "memory_id": memory_id
            })
    
    def _call_mcp_tool(self, tool_name: str, params: dict) -> any:
        """
        Call an MCP tool (placeholder implementation).
        
        In a real WxO integration, this would use the MCP client
        to communicate with the AstroBob MCP server.
        """
        # This is a placeholder - real implementation would use MCP client
        raise NotImplementedError(
            "MCP integration not implemented. Use use_direct_api=True for now."
        )


# Convenience functions for WxO agents
def create_memory_tool(agent_name: str) -> AstroBobMemoryTool:
    """
    Create a memory tool configured for a specific agent.
    
    Args:
        agent_name: Name of the agent (used for tagging)
        
    Returns:
        Configured AstroBobMemoryTool instance
    """
    tool = AstroBobMemoryTool(use_direct_api=True)
    tool.agent_name = agent_name
    return tool


def remember_for_agent(
    agent_name: str,
    content: str,
    memory_type: Literal["semantic", "episodic", "procedural"],
    project: str,
    **kwargs
) -> str:
    """
    Convenience function to store a memory with agent tagging.
    
    Args:
        agent_name: Name of the creating agent
        content: Memory content
        memory_type: Type of memory
        project: Project name
        **kwargs: Additional arguments for remember()
        
    Returns:
        Memory ID
    """
    tool = create_memory_tool(agent_name)
    return tool.remember(
        content=content,
        memory_type=memory_type,
        project=project,
        agent_name=agent_name,
        **kwargs
    )


# Example usage for WxO agents
if __name__ == "__main__":
    # Example: Code Memory Agent storing a procedure
    tool = AstroBobMemoryTool(use_direct_api=True)
    
    # Store a procedural memory
    procedure_id = tool.remember(
        content="""How to Add MCP Tool to AstroBob:
        
1. Define tool schema in mcp_server/schemas.py
2. Implement handler in mcp_server/tools.py  
3. Register in mcp_server/server.py
4. Test with MCP Inspector
5. Add CLI command (optional)
6. Write unit tests""",
        memory_type="procedural",
        project="astrobob",
        tags=["mcp", "development", "scaffolding"],
        importance=5,
        agent_name="code-memory"
    )
    
    print(f"Stored procedure: {procedure_id}")
    
    # Search for related memories
    results = tool.recall(
        query="how to add MCP tool",
        project="astrobob",
        memory_type="procedural"
    )
    
    print(f"Found {len(results)} related memories")
    for result in results:
        print(f"  {result['score']:.2f}: {result['content'][:50]}...")

# Made with Bob
