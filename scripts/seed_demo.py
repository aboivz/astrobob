#!/usr/bin/env python3
"""
Seed demo data for AstroBob demonstrations.

This script populates the AstroBob database with realistic demo memories
that showcase the system's capabilities. All demo memories are tagged with
'demo=true' for easy cleanup.

Usage:
    python scripts/seed_demo.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datetime import datetime, timezone, timedelta
from astrobob.config import get_config
from astrobob.core.store import MemoryStore
from astrobob.models import create_memory
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def create_demo_memories():
    """Create a comprehensive set of demo memories."""
    
    memories = []
    
    # Semantic Memories (Facts about the project)
    semantic_memories = [
        {
            "content": "AstroBob uses FastAPI 0.104 with async routes for the MCP server implementation",
            "importance": 4,
            "tags": ["demo", "architecture", "fastapi", "mcp"],
        },
        {
            "content": "The project uses Python 3.12+ with uv for package management and dependency resolution",
            "importance": 4,
            "tags": ["demo", "python", "tooling", "uv"],
        },
        {
            "content": "AstraDB Serverless is configured with hybrid search (vector + lexical) and NVIDIA reranking",
            "importance": 5,
            "tags": ["demo", "astradb", "search", "nvidia"],
        },
        {
            "content": "Memory ranking uses weighted formula: 55% rerank + 15% importance + 15% recency + 10% success - 5% staleness",
            "importance": 5,
            "tags": ["demo", "ranking", "algorithm"],
        },
        {
            "content": "Three memory types: semantic (facts), episodic (events), procedural (how-to guides)",
            "importance": 5,
            "tags": ["demo", "memory-types", "architecture"],
        },
        {
            "content": "MCP server provides 5 tools: remember, recall, reflect, forget, audit_trail",
            "importance": 4,
            "tags": ["demo", "mcp", "tools"],
        },
        {
            "content": "All memories use ULID for unique identifiers, generated client-side for consistency",
            "importance": 3,
            "tags": ["demo", "ulid", "identifiers"],
        },
        {
            "content": "Provenance tracking includes derived_from, session_id, tool_call_id, and bob_skill_used fields",
            "importance": 4,
            "tags": ["demo", "provenance", "tracking"],
        },
    ]
    
    for mem in semantic_memories:
        memories.append(create_memory(
            memory_type="semantic",
            project="astrobob-demo",
            content=mem["content"],
            importance=mem["importance"],
            tags=mem["tags"],
            source="cli",
        ))
    
    # Episodic Memories (Events that happened during development)
    episodic_memories = [
        {
            "content": "Fixed Pydantic v2 field naming issue by using 'id' instead of '_id', mapping at AstraDB layer",
            "importance": 3,
            "tags": ["demo", "bug-fix", "pydantic", "models"],
            "days_ago": 5,
        },
        {
            "content": "Implemented query routing in retriever.py - routes queries to appropriate collections based on keywords",
            "importance": 4,
            "tags": ["demo", "feature", "retriever", "routing"],
            "days_ago": 4,
        },
        {
            "content": "Added soft delete functionality to preserve audit trails while marking memories as deleted",
            "importance": 3,
            "tags": ["demo", "feature", "delete", "audit"],
            "days_ago": 3,
        },
        {
            "content": "Discovered that hybrid search with reranking significantly improves recall accuracy (92% vs 78%)",
            "importance": 5,
            "tags": ["demo", "discovery", "search", "performance"],
            "days_ago": 2,
        },
        {
            "content": "Completed integration tests with 7 comprehensive test cases covering full memory lifecycle",
            "importance": 4,
            "tags": ["demo", "testing", "integration", "milestone"],
            "days_ago": 1,
        },
        {
            "content": "Bob successfully used reflect() tool to create procedural memory from 3 episodic memories",
            "importance": 5,
            "tags": ["demo", "reflection", "bob", "success"],
            "days_ago": 1,
        },
        {
            "content": "Optimized ranking formula weights based on A/B testing with 500 queries",
            "importance": 4,
            "tags": ["demo", "optimization", "ranking", "testing"],
            "days_ago": 2,
        },
    ]
    
    for mem in episodic_memories:
        created_at = datetime.now(timezone.utc) - timedelta(days=mem["days_ago"])
        memory = create_memory(
            memory_type="episodic",
            project="astrobob-demo",
            content=mem["content"],
            importance=mem["importance"],
            tags=mem["tags"],
            source="cli",
        )
        memory.created_at = created_at
        memory.updated_at = created_at
        memories.append(memory)
    
    # Procedural Memories (How-to guides)
    procedural_memories = [
        {
            "content": """To add a new MCP tool:
1. Implement the core logic in src/astrobob/core/store.py or appropriate module
2. Add tool definition to src/astrobob/mcp_server/schemas.py with detailed description
3. Implement tool handler in src/astrobob/mcp_server/tools.py
4. Register tool in server.py's tool list
5. Test with MCP Inspector to verify input/output schemas
6. Add unit tests in tests/unit/
7. Document in README.md MCP tools section""",
            "importance": 5,
            "tags": ["demo", "procedure", "mcp", "development"],
            "success_count": 3,
        },
        {
            "content": """To deploy AstroBob to production:
1. Run full test suite: uv run pytest tests/ -v
2. Verify all environment variables are set correctly
3. Run astrobob doctor to check system health
4. Build package: uv build
5. Deploy to staging environment first
6. Run smoke tests on staging
7. Monitor logs for 10 minutes
8. Deploy to production if staging is stable
9. Set up monitoring alerts for errors""",
            "importance": 5,
            "tags": ["demo", "procedure", "deployment", "production"],
            "success_count": 2,
        },
        {
            "content": """To debug memory retrieval issues:
1. Check AstraDB connection with astrobob doctor
2. Verify collection schemas match expected structure
3. Test query with astrobob memory recall --debug flag
4. Examine ranking scores in debug output
5. Check if memories exist with correct tags
6. Verify importance and recency weights are appropriate
7. Test with simpler queries to isolate issue
8. Review AstraDB Studio for raw data""",
            "importance": 4,
            "tags": ["demo", "procedure", "debugging", "troubleshooting"],
            "success_count": 5,
        },
        {
            "content": """To create a new Bob skill from procedural memory:
1. Ensure procedural memory has importance >= 4
2. Add detailed step-by-step content
3. Tag appropriately for discoverability
4. Run: astrobob skills sync --min-importance 4
5. Verify SKILL.md created in .bob/skills/learned/
6. Test skill by asking Bob to use it
7. Iterate on content based on Bob's usage
8. Mark successful uses to increase success_count""",
            "importance": 5,
            "tags": ["demo", "procedure", "skills", "bob"],
            "success_count": 4,
        },
        {
            "content": """To optimize memory search performance:
1. Use specific tags to narrow search scope
2. Prefer procedural memory type for how-to queries
3. Include key terms in query that match memory content
4. Set appropriate limit (default 10, max 50)
5. Review ranking scores to understand results
6. Update memory importance if consistently low-ranked
7. Use reflect() to consolidate related episodic memories
8. Archive old memories with low access_count""",
            "importance": 4,
            "tags": ["demo", "procedure", "optimization", "search"],
            "success_count": 6,
        },
    ]
    
    for mem in procedural_memories:
        memory = create_memory(
            memory_type="procedural",
            project="astrobob-demo",
            content=mem["content"],
            importance=mem["importance"],
            tags=mem["tags"],
            source="cli",
        )
        memory.success_count = mem["success_count"]
        memories.append(memory)
    
    return memories


def main():
    """Main execution function."""
    console.print("\n[bold cyan]AstroBob Demo Data Seeder[/bold cyan]\n")
    
    try:
        # Load configuration
        console.print("[1/3] Loading configuration...")
        config = get_config()
        console.print("  ✓ Configuration loaded\n")
        
        # Initialize store
        console.print("[2/3] Connecting to AstraDB...")
        from astrobob.astra.client import AstraClient
        client = AstraClient(config)
        database = client.get_database()
        store = MemoryStore(database, config.collection_prefix)
        console.print("  ✓ Connected to AstraDB\n")
        
        # Create demo memories
        console.print("[3/3] Creating demo memories...")
        memories = create_demo_memories()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Inserting memories...", total=len(memories))
            
            inserted_count = 0
            for memory in memories:
                try:
                    store.insert(memory)
                    inserted_count += 1
                    progress.update(task, advance=1)
                except Exception as e:
                    console.print(f"  [yellow]Warning: Failed to insert memory: {e}[/yellow]")
        
        console.print(f"\n[bold green]✓ Successfully seeded {inserted_count} demo memories![/bold green]\n")
        
        # Print summary
        console.print("[bold]Summary:[/bold]")
        console.print(f"  • Semantic memories: 8")
        console.print(f"  • Episodic memories: 7")
        console.print(f"  • Procedural memories: 5")
        console.print(f"  • Total: {inserted_count}")
        console.print(f"  • Project: astrobob-demo")
        console.print(f"  • Tag: demo (for easy cleanup)\n")
        
        console.print("[dim]To view memories: astrobob memory report --project astrobob-demo[/dim]")
        console.print("[dim]To clean up: python scripts/reset_demo.py[/dim]\n")
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
