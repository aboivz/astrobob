"""
AstroBob CLI - Memory commands.

Commands for managing memories (CRUD operations).
"""

import sys
from typing import Optional, Literal
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
import json

from astrobob.config import get_config, ensure_config_or_exit
from astrobob.astra import create_astra_client
from astrobob.core import MemoryStore
from astrobob.models import create_memory, Provenance
from astrobob.errors import AstroBobError, MemoryNotFoundError

# Create command group
app = typer.Typer()
console = Console()


@app.command()
def remember(
    content: str = typer.Argument(..., help="Memory content"),
    memory_type: Literal["semantic", "episodic", "procedural"] = typer.Option(
        "semantic",
        "--type",
        "-t",
        help="Type of memory",
    ),
    project: str = typer.Option(
        "default",
        "--project",
        "-p",
        help="Project name",
    ),
    tags: list[str] = typer.Option(
        [],
        "--tag",
        help="Tags (can be specified multiple times)",
    ),
    importance: int = typer.Option(
        3,
        "--importance",
        "-i",
        min=1,
        max=5,
        help="Importance level (1-5)",
    ),
    source: Literal["bob", "bobshell", "wxo", "cli", "user"] = typer.Option(
        "cli",
        "--source",
        help="Source of the memory",
    ),
):
    """
    Store a new memory.
    
    Examples:
      astrobob memory remember "Project uses FastAPI 0.104" --type semantic --importance 4
      astrobob memory remember "Fixed auth bug" --type episodic --tag bug --tag auth
      astrobob memory remember "To add MCP tool: 1) Define schema..." --type procedural --importance 5
    """
    console.print("\n[bold cyan]Storing memory...[/bold cyan]\n")
    
    # Load configuration
    try:
        config = ensure_config_or_exit()
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    
    # Create store
    try:
        client = create_astra_client(config)
        db = client.get_database()
        store = MemoryStore(db)
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)
    
    # Create and insert memory
    try:
        memory = create_memory(
            memory_type=memory_type,
            project=project,
            content=content,
            tags=tags,
            importance=importance,
            source=source,
        )
        
        memory_id = store.insert(memory)
        
        console.print(f"[green]Memory stored successfully[/green]")
        console.print(f"  ID: [cyan]{memory_id}[/cyan]")
        console.print(f"  Type: {memory_type}")
        console.print(f"  Project: {project}")
        console.print(f"  Importance: {importance}/5")
        if tags:
            console.print(f"  Tags: {', '.join(tags)}")
        console.print()
        
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)


@app.command()
def forget(
    memory_id: str = typer.Argument(..., help="Memory ID to delete"),
    memory_type: Literal["semantic", "episodic", "procedural"] = typer.Option(
        ...,
        "--type",
        "-t",
        help="Type of memory",
    ),
    confirm: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt",
    ),
):
    """
    Soft delete a memory.
    
    Example:
      astrobob memory forget 01ABC123... --type semantic
    """
    if not confirm:
        confirmed = typer.confirm(
            f"Are you sure you want to delete {memory_type} memory {memory_id}?"
        )
        if not confirmed:
            console.print("[yellow]Cancelled[/yellow]")
            sys.exit(0)
    
    console.print("\n[bold cyan]Deleting memory...[/bold cyan]\n")
    
    # Load configuration
    try:
        config = ensure_config_or_exit()
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    
    # Create store
    try:
        client = create_astra_client(config)
        db = client.get_database()
        store = MemoryStore(db)
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)
    
    # Delete memory
    try:
        store.soft_delete(memory_type, memory_id)
        console.print(f"[green]Memory deleted successfully[/green]\n")
    except MemoryNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(3)
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)


@app.command()
def report(
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Filter by project (default: all projects)",
    ),
):
    """
    Show memory statistics and recent procedural memories.
    
    Example:
      astrobob memory report --project astrobob
    """
    console.print("\n[bold cyan]AstroBob Memory Report[/bold cyan]\n")
    
    # Load configuration
    try:
        config = ensure_config_or_exit()
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    
    # Create store
    try:
        client = create_astra_client(config)
        db = client.get_database()
        store = MemoryStore(db)
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)
    
    # Get counts
    try:
        semantic_count = store.count_memories("semantic", project=project)
        episodic_count = store.count_memories("episodic", project=project)
        procedural_count = store.count_memories("procedural", project=project)
        
        # Create counts table
        counts_table = Table(title="Memory Counts")
        counts_table.add_column("Type", style="cyan")
        counts_table.add_column("Count", justify="right", style="green")
        
        counts_table.add_row("Semantic", str(semantic_count))
        counts_table.add_row("Episodic", str(episodic_count))
        counts_table.add_row("Procedural", str(procedural_count))
        counts_table.add_row("[bold]Total[/bold]", f"[bold]{semantic_count + episodic_count + procedural_count}[/bold]")
        
        console.print(counts_table)
        console.print()
        
        # Show top procedural memories
        if procedural_count > 0:
            procedural_list = store.list_procedural(
                project=project or "default",
                min_importance=1,
                limit=5,
            )
            
            if procedural_list:
                console.print("[bold]Top Procedural Memories:[/bold]\n")
                
                for i, mem in enumerate(procedural_list, 1):
                    content_preview = mem.content[:80] + "..." if len(mem.content) > 80 else mem.content
                    panel = Panel(
                        f"[dim]{content_preview}[/dim]\n\n"
                        f"Importance: {mem.importance}/5 | "
                        f"Tags: {', '.join(mem.tags) if mem.tags else 'none'} | "
                        f"ID: [cyan]{mem.id}[/cyan]",
                        title=f"#{i}",
                        border_style="blue",
                    )
                    console.print(panel)
        
        console.print()
        
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)


@app.command()
def reflect(
    project: str = typer.Option(
        "default",
        "--project",
        "-p",
        help="Project name",
    ),
    episode_ids: list[str] = typer.Option(
        ...,
        "--episode-id",
        "-e",
        help="Episode IDs to reflect on (can be specified multiple times)",
    ),
    lesson: str = typer.Argument(..., help="The lesson learned (procedural knowledge)"),
    tags: list[str] = typer.Option(
        [],
        "--tag",
        help="Tags (can be specified multiple times)",
    ),
    importance: int = typer.Option(
        4,
        "--importance",
        "-i",
        min=1,
        max=5,
        help="Importance level (1-5)",
    ),
):
    """
    Create a procedural memory by reflecting on episodic memories.
    
    This distills lessons learned from past experiences into reusable knowledge.
    
    Example:
      astrobob memory reflect \
        --project astrobob \
        --episode-id 01ABC... --episode-id 01DEF... \
        "Always add tests when adding MCP tools" \
        --importance 4 \
        --tag testing --tag mcp
    """
    console.print("\n[bold cyan]Creating procedural memory from reflection...[/bold cyan]\n")
    
    # Load configuration
    try:
        config = ensure_config_or_exit()
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    
    # Create store
    try:
        client = create_astra_client(config)
        db = client.get_database()
        store = MemoryStore(db)
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)
    
    # Verify episode IDs exist
    try:
        console.print("[dim]Verifying episode IDs...[/dim]")
        for episode_id in episode_ids:
            try:
                store.get("episodic", episode_id)
            except MemoryNotFoundError:
                console.print(f"[red]Error: Episode not found: {episode_id}[/red]")
                sys.exit(3)
        
        console.print(f"[green]Found {len(episode_ids)} episode(s)[/green]\n")
        
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)
    
    # Create procedural memory
    try:
        memory = create_memory(
            memory_type="procedural",
            project=project,
            content=lesson,
            tags=tags,
            importance=importance,
            source="cli",
        )
        
        # Set provenance
        memory.provenance = Provenance(
            derived_from=episode_ids,
            session_id=None,
            tool_call_id=None,
            bob_skill_used=None,
        )
        
        memory_id = store.insert(memory)
        
        console.print(f"[green]Procedural memory created successfully[/green]")
        console.print(f"  ID: [cyan]{memory_id}[/cyan]")
        console.print(f"  Project: {project}")
        console.print(f"  Importance: {importance}/5")
        console.print(f"  Derived from: {len(episode_ids)} episode(s)")
        if tags:
            console.print(f"  Tags: {', '.join(tags)}")
        console.print()
        
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)


@app.command()
def audit(
    memory_id: str = typer.Argument(..., help="Memory ID"),
    memory_type: Literal["semantic", "episodic", "procedural"] = typer.Option(
        ...,
        "--type",
        "-t",
        help="Type of memory",
    ),
):
    """
    Show the audit trail for a memory.
    
    Displays complete provenance, access history, and lifecycle information.
    
    Example:
      astrobob memory audit 01ABC123... --type procedural
    """
    console.print("\n[bold cyan]Memory Audit Trail[/bold cyan]\n")
    
    # Load configuration
    try:
        config = ensure_config_or_exit()
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    
    # Create store
    try:
        client = create_astra_client(config)
        db = client.get_database()
        store = MemoryStore(db)
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)
    
    # Get memory
    try:
        memory = store.get(memory_type, memory_id)
        
        # Basic info
        info_table = Table(title="Memory Information")
        info_table.add_column("Field", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("ID", memory.id)
        info_table.add_row("Type", memory.memory_type)
        info_table.add_row("Project", memory.project)
        info_table.add_row("Scope", memory.scope)
        info_table.add_row("Importance", f"{memory.importance}/5")
        info_table.add_row("Confidence", f"{memory.confidence:.2f}")
        info_table.add_row("Source", memory.source)
        
        if memory.tags:
            info_table.add_row("Tags", ", ".join(memory.tags))
        
        console.print(info_table)
        console.print()
        
        # Content
        content_panel = Panel(
            memory.content,
            title="Content",
            border_style="blue",
        )
        console.print(content_panel)
        console.print()
        
        # Provenance
        if memory.provenance.derived_from or memory.provenance.session_id:
            prov_table = Table(title="Provenance")
            prov_table.add_column("Field", style="cyan")
            prov_table.add_column("Value", style="white")
            
            if memory.provenance.derived_from:
                prov_table.add_row(
                    "Derived From",
                    f"{len(memory.provenance.derived_from)} episode(s)"
                )
                for i, episode_id in enumerate(memory.provenance.derived_from, 1):
                    prov_table.add_row(f"  Episode {i}", episode_id)
            
            if memory.provenance.session_id:
                prov_table.add_row("Session ID", memory.provenance.session_id)
            
            if memory.provenance.tool_call_id:
                prov_table.add_row("Tool Call ID", memory.provenance.tool_call_id)
            
            if memory.provenance.bob_skill_used:
                prov_table.add_row("Bob Skill Used", memory.provenance.bob_skill_used)
            
            console.print(prov_table)
            console.print()
        
        # Lifecycle
        lifecycle_table = Table(title="Lifecycle")
        lifecycle_table.add_column("Field", style="cyan")
        lifecycle_table.add_column("Value", style="white")
        
        lifecycle_table.add_row("Created", memory.created_at.isoformat())
        lifecycle_table.add_row("Updated", memory.updated_at.isoformat())
        
        if memory.last_accessed_at:
            lifecycle_table.add_row("Last Accessed", memory.last_accessed_at.isoformat())
        
        lifecycle_table.add_row("Access Count", str(memory.access_count))
        lifecycle_table.add_row("Success Count", str(memory.success_count))
        
        if memory.deleted_at:
            lifecycle_table.add_row("Deleted", memory.deleted_at.isoformat())
        
        if memory.supersedes:
            lifecycle_table.add_row("Supersedes", memory.supersedes)
        
        console.print(lifecycle_table)
        console.print()
        
        # Skill export info (procedural only)
        if memory.memory_type == "procedural" and memory.exported_as_skill:
            export_table = Table(title="Skill Export")
            export_table.add_column("Field", style="cyan")
            export_table.add_column("Value", style="white")
            
            export_table.add_row("Exported As", memory.exported_as_skill)
            if memory.exported_at:
                export_table.add_row("Exported At", memory.exported_at.isoformat())
            
            console.print(export_table)
            console.print()
        
    except MemoryNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(3)
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)


@app.command()
def recall(
    query: str = typer.Argument(..., help="Search query"),
    project: str = typer.Option(
        "default",
        "--project",
        "-p",
        help="Project to search",
    ),
    memory_types: list[str] = typer.Option(
        [],
        "--type",
        "-t",
        help="Memory types to search: semantic, episodic, or procedural (can be specified multiple times, default: all)",
    ),
    tags: list[str] = typer.Option(
        [],
        "--tag",
        help="Filter by tags (can be specified multiple times)",
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-l",
        help="Maximum number of results",
    ),
    min_importance: Optional[int] = typer.Option(
        None,
        "--min-importance",
        "-i",
        min=1,
        max=5,
        help="Minimum importance level (1-5)",
    ),
):
    """
    Search and retrieve memories.
    
    Uses natural language queries with automatic query intent routing.
    
    Examples:
      astrobob memory recall "how to add MCP tool" --project astrobob
      astrobob memory recall "API patterns" --type procedural --min-importance 4
      astrobob memory recall "authentication" --tag auth --tag security
    """
    console.print("\n[bold cyan]Searching memories...[/bold cyan]\n")
    
    # Validate memory types
    valid_types = {"semantic", "episodic", "procedural"}
    if memory_types:
        invalid_types = [t for t in memory_types if t not in valid_types]
        if invalid_types:
            console.print(f"[red]Error: Invalid memory type(s): {', '.join(invalid_types)}[/red]")
            console.print(f"[yellow]Valid types are: {', '.join(valid_types)}[/yellow]")
            sys.exit(1)
    
    # Load configuration
    try:
        config = ensure_config_or_exit()
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    
    # Create store and retriever
    try:
        client = create_astra_client(config)
        db = client.get_database()
        store = MemoryStore(db)
        
        # Import retriever here to avoid circular imports
        from astrobob.core.retriever import MemoryRetriever
        retriever = MemoryRetriever(client, store)
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)
    
    # Perform recall
    try:
        # Cast validated memory_types to proper Literal type
        from astrobob.core.retriever import MemoryType
        typed_memory_types: Optional[list[MemoryType]] = None
        if memory_types:
            typed_memory_types = [t for t in memory_types]  # type: ignore
        
        results = retriever.recall(
            query=query,
            project=project,
            memory_types=typed_memory_types,
            tags=tags if tags else None,
            limit=limit,
            min_importance=min_importance,
        )
        
        if not results:
            console.print(f"[yellow]No memories found matching '{query}'[/yellow]\n")
            return
        
        console.print(f"[green]Found {len(results)} memories:[/green]\n")
        
        # Create results table
        table = Table(title=f"Search Results for: {query}")
        table.add_column("#", style="dim", width=3)
        table.add_column("Type", style="cyan", width=10)
        table.add_column("Content", style="white")
        table.add_column("Score", justify="right", style="green", width=8)
        table.add_column("Importance", justify="center", style="yellow", width=10)
        table.add_column("Tags", style="blue")
        
        for i, (memory, score) in enumerate(results, 1):
            content_preview = memory.content[:80] + "..." if len(memory.content) > 80 else memory.content
            tags_str = ", ".join(memory.tags[:3]) if memory.tags else "-"
            if len(memory.tags) > 3:
                tags_str += f" +{len(memory.tags) - 3}"
            
            table.add_row(
                str(i),
                memory.memory_type,
                content_preview,
                f"{score:.4f}",
                f"{memory.importance}/5",
                tags_str,
            )
        
        console.print(table)
        console.print()
        
        # Show detailed view of top result
        if results:
            top_memory, top_score = results[0]
            console.print("[bold]Top Result Details:[/bold]\n")
            
            detail_panel = Panel(
                f"[bold]Content:[/bold]\n{top_memory.content}\n\n"
                f"[bold]ID:[/bold] [cyan]{top_memory.id}[/cyan]\n"
                f"[bold]Type:[/bold] {top_memory.memory_type}\n"
                f"[bold]Project:[/bold] {top_memory.project}\n"
                f"[bold]Importance:[/bold] {top_memory.importance}/5\n"
                f"[bold]Score:[/bold] {top_score:.4f}\n"
                f"[bold]Tags:[/bold] {', '.join(top_memory.tags) if top_memory.tags else 'none'}\n"
                f"[bold]Created:[/bold] {top_memory.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
                title="Top Match",
                border_style="green",
            )
            console.print(detail_panel)
        
        console.print()
        
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)


# Made with Bob
