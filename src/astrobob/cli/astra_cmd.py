"""
AstraBob CLI - AstraDB commands.

Commands for setting up and managing AstraDB collections.
"""

import sys
import typer
from rich.console import Console
from rich.table import Table

from astrobob.config import get_config, ensure_config_or_exit
from astrobob.astra import create_astra_client, create_all_collections
from astrobob.errors import AstroBobError

# Create command group
app = typer.Typer()
console = Console()


@app.command()
def setup(
    prefix: str = typer.Option(
        "astrobob",
        "--prefix",
        help="Collection name prefix",
    ),
):
    """
    Setup AstraDB collections for AstroBob.
    
    Creates three collections if they don't exist:
    - {prefix}_semantic_memory
    - {prefix}_episodic_memory
    - {prefix}_procedural_memory
    
    This command is idempotent - safe to run multiple times.
    """
    console.print("\n[bold cyan]AstroBob - AstraDB Setup[/bold cyan]\n")
    
    # Load and validate configuration
    console.print("[1/3] Validating configuration...")
    try:
        config = ensure_config_or_exit()
        console.print("  [green]Configuration valid[/green]")
    except AstroBobError as e:
        console.print(f"  [red]ERROR: {e}[/red]")
        sys.exit(1)
    
    # Create client and test connection
    console.print("\n[2/3] Testing AstraDB connection...")
    try:
        client = create_astra_client(config)
        if not client.test_connection():
            console.print("  [red]ERROR: Connection test failed[/red]")
            sys.exit(2)
        console.print("  [green]Connection successful[/green]")
    except AstroBobError as e:
        console.print(f"  [red]ERROR: {e}[/red]")
        sys.exit(2)
    
    # Create collections
    console.print("\n[3/3] Creating collections...")
    try:
        db = client.get_database()
        results = create_all_collections(db, prefix=prefix)
        
        for memory_type, (collection_name, was_created) in results.items():
            if was_created:
                console.print(f"  [green]{collection_name}[/green] (created)")
            else:
                console.print(f"  [dim]{collection_name}[/dim] (already exists)")
        
        console.print("\n[bold green]Setup complete![/bold green]\n")
        sys.exit(0)
        
    except AstroBobError as e:
        console.print(f"  [red]✗ {e}[/red]")
        sys.exit(2)


@app.command()
def status(
    prefix: str = typer.Option(
        "astrobob",
        "--prefix",
        help="Collection name prefix",
    ),
):
    """
    Show status of AstraDB collections.
    
    Displays which collections exist and their document counts.
    """
    console.print("\n[bold cyan]AstroBob - AstraDB Status[/bold cyan]\n")
    
    # Load configuration
    try:
        config = ensure_config_or_exit()
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    
    # Create client
    try:
        client = create_astra_client(config)
        db = client.get_database()
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)
    
    # Get collection names
    from astrobob.astra.collections import get_collection_name, MemoryType
    from typing import cast
    
    memory_types: list[MemoryType] = ["semantic", "episodic", "procedural"]
    
    # Create status table
    table = Table(title="Collection Status")
    table.add_column("Collection", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Documents", justify="right")
    
    try:
        existing_collections = db.list_collection_names()
        
        for memory_type in memory_types:
            collection_name = get_collection_name(cast(MemoryType, memory_type), prefix)
            
            if collection_name in existing_collections:
                # Get document count
                collection = db.get_collection(collection_name)
                count = collection.count_documents(filter={}, upper_bound=10000)
                table.add_row(collection_name, "[green]Exists[/green]", str(count))
            else:
                table.add_row(collection_name, "[red]Missing[/red]", "-")
        
        console.print(table)
        console.print()
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)

# Made with Bob
