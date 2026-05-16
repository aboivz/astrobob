"""
MCP tool schemas for AstroBob.

Defines the 5 core tools that Bob can use to interact with memory:
1. remember - Store new memories
2. recall - Search and retrieve memories
3. reflect - Convert episodic memories to procedural
4. forget - Soft-delete memories
5. audit_trail - View memory provenance and history
"""

from typing import Any

# Tool 1: remember
REMEMBER_TOOL = {
    "name": "remember",
    "description": """
Store a new memory in AstroBob's persistent memory system.

Use this when you:
- Learn a project convention or fact (semantic memory)
- Complete a task, fix a bug, or make a decision (episodic memory)
- Discover a reusable procedure or pattern (procedural memory)

Memory Types:
- semantic: Stable facts about the project (e.g., "Project uses FastAPI 0.104")
- episodic: Events that happened (e.g., "Fixed auth bug by adding token refresh")
- procedural: Reusable how-to knowledge (e.g., "To add MCP tool: 1) implement in core/...")

Importance Levels (1-5):
- 5: Critical patterns you'll reuse constantly
- 4: Important procedures or major decisions
- 3: Useful information (default)
- 2: Minor details
- 1: Trivial notes

Examples:
```
remember(
    content="Project uses FastAPI 0.104 with async routes and Pydantic v2 models",
    memory_type="semantic",
    project="astrobob",
    importance=3,
    tags=["fastapi", "architecture"]
)

remember(
    content="Fixed auth bug by implementing token refresh logic in middleware",
    memory_type="episodic",
    project="astrobob",
    importance=4,
    tags=["bug-fix", "auth"]
)

remember(
    content="To add MCP tool: 1) Define schema in schemas.py 2) Implement handler in tools.py 3) Register in server.py 4) Test with MCP Inspector",
    memory_type="procedural",
    project="astrobob",
    importance=5,
    tags=["mcp", "development", "procedure"]
)
```

Tips:
- Be specific and actionable in content
- Use importance 4-5 for patterns you'll reuse
- Add relevant tags for better retrieval
- Procedural memories should be step-by-step
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "The memory content (be specific and detailed)"
            },
            "memory_type": {
                "type": "string",
                "enum": ["semantic", "episodic", "procedural"],
                "description": "Type of memory to store"
            },
            "project": {
                "type": "string",
                "description": "Project name (e.g., 'astrobob')"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional tags for categorization",
                "default": []
            },
            "importance": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
                "description": "Importance level (1-5, default 3)",
                "default": 3
            },
            "source": {
                "type": "string",
                "enum": ["bob", "bobshell", "wxo", "cli", "user"],
                "description": "Source creating this memory",
                "default": "bob"
            }
        },
        "required": ["content", "memory_type", "project"]
    }
}

# Tool 2: recall
RECALL_TOOL = {
    "name": "recall",
    "description": """
Search and retrieve memories from AstroBob's persistent memory.

Use this to:
- Check if you've solved a similar problem before
- Retrieve project conventions before making changes
- Find procedures for common tasks
- Review past decisions and their outcomes

The system automatically:
- Routes queries to the right memory types based on intent
- Ranks results by relevance, importance, and recency
- Updates access tracking for retrieved memories

Query Intent Routing:
- "How to..." queries → procedural memories first
- "What is..." queries → semantic memories first
- "Last time..." queries → episodic memories first

Examples:
```
# Before adding a new feature
recall(
    query="how to add MCP tool",
    project="astrobob",
    limit=5
)

# Checking project conventions
recall(
    query="what testing framework does the project use",
    project="astrobob",
    memory_types=["semantic"]
)

# Finding past solutions
recall(
    query="how did we handle authentication errors",
    project="astrobob",
    tags=["auth", "error-handling"]
)

# Reviewing recent work
recall(
    query="what bugs were fixed last week",
    project="astrobob",
    memory_types=["episodic"],
    min_importance=3
)
```

Tips:
- Call recall() before starting non-trivial tasks
- Use natural language queries
- Filter by tags for specific topics
- Set min_importance to focus on key memories
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language search query"
            },
            "project": {
                "type": "string",
                "description": "Project to search within"
            },
            "memory_types": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["semantic", "episodic", "procedural"]
                },
                "description": "Specific memory types to search (optional, auto-detected from query)",
                "default": None
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by tags",
                "default": []
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
                "description": "Maximum results to return",
                "default": 10
            },
            "min_importance": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
                "description": "Minimum importance level",
                "default": None
            }
        },
        "required": ["query", "project"]
    }
}

# Tool 3: reflect
REFLECT_TOOL = {
    "name": "reflect",
    "description": """
Convert episodic memories into reusable procedural knowledge.

Use this when you:
- Complete a multi-step task and want to remember the procedure
- Discover a pattern across multiple similar episodes
- Learn a lesson from successes or failures
- Want to codify tribal knowledge

Reflection Process:
1. Identify related episodic memories (recent tasks, bug fixes, decisions)
2. Extract the reusable pattern or procedure
3. Create a procedural memory with step-by-step instructions
4. Link back to source episodes for provenance

Examples:
```
# After successfully adding multiple MCP tools
reflect(
    project="astrobob",
    episode_ids=["01ABC123...", "01DEF456..."],
    lesson="To add MCP tool: 1) Define schema in schemas.py with detailed description 2) Implement handler in tools.py 3) Register in server.py 4) Test with MCP Inspector 5) Update documentation",
    tags=["mcp", "development", "procedure"],
    importance=5
)

# After fixing similar bugs multiple times
reflect(
    project="astrobob",
    episode_ids=["01GHI789..."],
    lesson="When AstraDB queries fail: 1) Check filter syntax 2) Verify collection exists 3) Validate field names match schema 4) Test with simpler query first",
    tags=["debugging", "astradb", "procedure"],
    importance=4
)
```

Tips:
- Reflect after completing significant tasks
- Make procedures specific and actionable
- Include context about when to use the procedure
- Set importance 4-5 for frequently-used procedures
- The system will suggest when reflection is appropriate
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "project": {
                "type": "string",
                "description": "Project name"
            },
            "episode_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "IDs of episodic memories to reflect on"
            },
            "lesson": {
                "type": "string",
                "description": "The procedural knowledge extracted (be specific and step-by-step)"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Tags for the procedural memory",
                "default": []
            },
            "importance": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
                "description": "Importance of this procedure (default 4)",
                "default": 4
            }
        },
        "required": ["project", "episode_ids", "lesson"]
    }
}

# Tool 4: forget
FORGET_TOOL = {
    "name": "forget",
    "description": """
Soft-delete a memory from AstroBob (marks as deleted, doesn't remove).

Use this when:
- Information becomes outdated or incorrect
- A procedure is superseded by a better one
- Episodic memories are no longer relevant
- You want to clean up low-value memories

Note: This is a soft delete - the memory is marked as deleted but not removed
from the database. This preserves audit trails and allows recovery if needed.

Examples:
```
# Remove outdated information
forget(
    memory_type="semantic",
    memory_id="01ABC123...",
    reason="Project migrated from FastAPI 0.104 to 0.110"
)

# Remove superseded procedure
forget(
    memory_type="procedural",
    memory_id="01DEF456...",
    reason="Replaced by improved procedure with better error handling"
)
```

Tips:
- Use sparingly - memories are valuable
- Provide a reason for audit purposes
- Consider updating instead of deleting
- Procedural memories can supersede each other
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "memory_type": {
                "type": "string",
                "enum": ["semantic", "episodic", "procedural"],
                "description": "Type of memory to delete"
            },
            "memory_id": {
                "type": "string",
                "description": "ID of the memory to delete"
            },
            "reason": {
                "type": "string",
                "description": "Reason for deletion (for audit trail)",
                "default": "No longer needed"
            }
        },
        "required": ["memory_type", "memory_id"]
    }
}

# Tool 5: audit_trail
AUDIT_TRAIL_TOOL = {
    "name": "audit_trail",
    "description": """
View the provenance and history of a memory.

Use this to:
- Understand where a memory came from
- See which episodes led to a procedural memory
- Check when a memory was last accessed
- Review the success rate of a procedure

Returns detailed information including:
- Creation and update timestamps
- Source (bob, cli, user, etc.)
- Provenance (derived from which episodes)
- Access count and last accessed time
- Success count (for procedural memories)
- Whether it supersedes another memory

Examples:
```
# Check provenance of a procedure
audit_trail(
    memory_type="procedural",
    memory_id="01ABC123..."
)

# Review an important decision
audit_trail(
    memory_type="episodic",
    memory_id="01DEF456..."
)
```

Tips:
- Use to understand memory lineage
- Helpful for debugging why certain memories are retrieved
- Shows the "story" behind procedural knowledge
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "memory_type": {
                "type": "string",
                "enum": ["semantic", "episodic", "procedural"],
                "description": "Type of memory"
            },
            "memory_id": {
                "type": "string",
                "description": "ID of the memory"
            }
        },
        "required": ["memory_type", "memory_id"]
    }
}

# Export all tools
ALL_TOOLS = [
    REMEMBER_TOOL,
    RECALL_TOOL,
    REFLECT_TOOL,
    FORGET_TOOL,
    AUDIT_TRAIL_TOOL,
]

# Made with Bob
