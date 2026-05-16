#!/usr/bin/env python3
"""
Reset/cleanup demo data from AstroBob.

This script removes all memories tagged with 'demo' from the AstroBob database.
Useful for cleaning up after demonstrations or testing.

Usage:
    python scripts/reset_demo.py
    python scripts/reset_demo.py --confirm  # Skip confirmation prompt
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import argparse
from typing import Literal, cast
from astrobob.config import get_config
from astrobob.astra.client import AstraClient
from astrobob.astra.collections import get_collection_name
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

MemoryType = Literal["semantic", "episodic", "procedural"]

console = Console()


def delete_demo_memories(database, collection_prefix: str, confirm: bool = False):
    """
    Delete all memories tagged with 'demo'.
    
    Args:
        database: AstraDB database instance
        collection_prefix: Prefix for collection names
        confirm: If True, skip confirmation prompt
        
    Returns:
        Total number of memories deleted
    """
    memory_types = ["semantic", "episodic", "procedural"]
    total_deleted = 0
    
    # Count memories first
    console.print("\n[bold]Scanning for demo memories...[/bold]\n")
    
    counts = {}
    for memory_type in memory_types:
        collection_name = get_collection_name(cast(MemoryType, memory_type), collection_prefix)
        collection = database.get_collection(collection_name)
        
        # Count documents with 'demo' tag
        try:
            # Use find with filter for demo tag
            cursor = collection.find({"tags": "demo"}, projection={"_id": 1})
            docs = list(cursor)
            count = len(docs)
            counts[memory_type] = count
            total_deleted += count
            
            if count > 0:
                console.print(f"  • {memory_type.capitalize()}: [yellow]{count}[/yellow] memories")
        except Exception as e:
            console.print(f"  [red]Error scanning {memory_type}: {e}[/red]")
            counts[memory_type] = 0
    
    if total_deleted == 0:
        console.print("\n[green]No demo memories found. Nothing to delete.[/green]\n")
        return 0
    
    console.print(f"\n[bold]Total demo memories found: [yellow]{total_deleted}[/yellow][/bold]\n")
    
    # Confirm deletion
    if not confirm:
        should_delete = Confirm.ask(
            "[bold red]Are you sure you want to delete these memories?[/bold red]",
            default=False
        )
        if not should_delete:
            console.print("\n[yellow]Deletion cancelled.[/yellow]\n")
            return 0
    
    # Delete memories
    console.print("\n[bold]Deleting demo memories...[/bold]\n")
    
    deleted_count = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for memory_type in memory_types:
            if counts[memory_type] == 0:
                continue
                
            task = progress.add_task(
                f"Deleting {memory_type} memories...",
                total=counts[memory_type]
            )
            
            collection_name = get_collection_name(cast(MemoryType, memory_type), collection_prefix)
            collection = database.get_collection(collection_name)
            
            try:
                # Delete all documents with 'demo' tag
                result = collection.delete_many({"tags": "demo"})
                deleted = result.deleted_count if hasattr(result, 'deleted_count') else counts[memory_type]
                deleted_count += deleted
                progress.update(task, completed=counts[memory_type])
            except Exception as e:
                console.print(f"  [red]Error deleting {memory_type} memories: {e}[/red]")
    
    return deleted_count


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Reset/cleanup demo data from AstroBob"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt"
    )
    parser.add_argument(
        "--project",
        default="astrobob-demo",
        help="Project name to filter (default: astrobob-demo)"
    )
    args = parser.parse_args()
    
    console.print("\n[bold cyan]AstroBob Demo Data Reset[/bold cyan]\n")
    
    try:
        # Load configuration
        console.print("[1/3] Loading configuration...")
        config = get_config()
        console.print("  ✓ Configuration loaded\n")
        
        # Connect to AstraDB
        console.print("[2/3] Connecting to AstraDB...")
        client = AstraClient(config)
        database = client.get_database()
        console.print("  ✓ Connected to AstraDB\n")
        
        # Delete demo memories
        console.print("[3/3] Processing deletion...")
        deleted_count = delete_demo_memories(
            database,
            config.collection_prefix,
            confirm=args.confirm
        )
        
        if deleted_count > 0:
            console.print(f"\n[bold green]✓ Successfully deleted {deleted_count} demo memories![/bold green]\n")
            console.print("[dim]To re-seed demo data: python scripts/seed_demo.py[/dim]\n")
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user[/yellow]\n")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
