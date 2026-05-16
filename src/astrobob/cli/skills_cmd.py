"""
Skills CLI commands for exporting procedural memories to Bob skills.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from astrobob.config import get_config
from astrobob.astra import create_astra_client
from astrobob.core.store import MemoryStore
from astrobob.skills_export.renderer import render_skill, write_skill_file
from astrobob.errors import AstroBobError

app = typer.Typer(help="Export procedural memories as Bob skills")
console = Console()


@app.command(name="sync")
def sync_skills(
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Project name (default: current directory name)"
    ),
    min_importance: int = typer.Option(
        4,
        "--min-importance",
        "-i",
        help="Minimum importance level (1-5) to export"
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory (default: .bob/skills/learned)"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be exported without writing files"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Re-export already exported memories"
    ),
) -> None:
    """
    Export procedural memories as Bob SKILL.md files.
    
    Queries procedural memories with importance >= min_importance,
    renders them as SKILL.md files, and writes to .bob/skills/learned/.
    
    Examples:
        astrobob skills sync
        astrobob skills sync --min-importance 5
        astrobob skills sync --dry-run
        astrobob skills sync --force  # Re-export all
    """
    try:
        # Determine project name
        if project is None:
            project = Path.cwd().name
        
        # Determine output directory
        if output_dir is None:
            output_dir = Path.cwd() / ".bob" / "skills" / "learned"
        
        # Validate min_importance
        if not 1 <= min_importance <= 5:
            console.print("[red]Error: min_importance must be between 1 and 5[/red]")
            raise typer.Exit(1)
        
        # Get config and database
        config = get_config()
        client = create_astra_client(config)
        db = client.get_database()
        store = MemoryStore(db)
        
        # Query procedural memories
        console.print(f"[cyan]Querying procedural memories for project '{project}'...[/cyan]")
        memories = store.list_procedural(
            project=project,
            min_importance=min_importance,
            limit=100,
            include_deleted=False,
        )
        
        if not memories:
            console.print(
                f"[yellow]No procedural memories found with importance >= {min_importance}[/yellow]"
            )
            console.print("\n[dim]Tip: Lower --min-importance or add more procedural memories[/dim]")
            return
        
        # Filter out already exported (unless --force)
        if not force:
            unexported = [m for m in memories if m.exported_as_skill is None]
            if len(unexported) < len(memories):
                console.print(
                    f"[dim]Skipping {len(memories) - len(unexported)} already exported "
                    f"(use --force to re-export)[/dim]"
                )
            memories = unexported
        
        if not memories:
            console.print("[yellow]All procedural memories already exported[/yellow]")
            console.print("\n[dim]Use --force to re-export[/dim]")
            return
        
        # Create results table
        table = Table(title=f"Exporting {len(memories)} Procedural Memories")
        table.add_column("Slug", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Importance", justify="center")
        table.add_column("Tags", style="dim")
        table.add_column("Status", justify="center")
        
        exported_count = 0
        errors = []
        
        # Process each memory
        for memory in memories:
            try:
                # Render skill
                slug, content = render_skill(memory)
                
                # Get title (first line of content)
                title = content.split('\n')[0].lstrip('# ').strip()
                if len(title) > 40:
                    title = title[:37] + "..."
                
                # Write file (or simulate)
                skill_path = write_skill_file(
                    base_dir=output_dir,
                    slug=slug,
                    content=content,
                    dry_run=dry_run,
                )
                
                # Mark as exported in database (unless dry run)
                if not dry_run:
                    store.mark_exported(
                        memory_id=memory.id,
                        skill_path=str(skill_path.relative_to(Path.cwd()))
                    )
                
                # Add to table
                status = "✓ Would export" if dry_run else "✓ Exported"
                table.add_row(
                    slug,
                    title,
                    "⭐" * memory.importance,
                    ", ".join(memory.tags[:3]) if memory.tags else "-",
                    f"[green]{status}[/green]"
                )
                
                exported_count += 1
                
            except Exception as e:
                errors.append((memory.id, str(e)))
                table.add_row(
                    "error",
                    f"Memory {memory.id[:8]}...",
                    "⭐" * memory.importance,
                    "-",
                    f"[red]✗ Error[/red]"
                )
        
        # Display results
        console.print()
        console.print(table)
        
        # Summary panel
        if dry_run:
            summary = f"[yellow]DRY RUN: Would export {exported_count} skills to:[/yellow]\n{output_dir}"
        else:
            summary = f"[green]✓ Exported {exported_count} skills to:[/green]\n{output_dir}"
        
        if errors:
            summary += f"\n\n[red]Errors: {len(errors)}[/red]"
            for memory_id, error in errors[:3]:  # Show first 3 errors
                summary += f"\n  • {memory_id[:8]}...: {error}"
        
        console.print()
        console.print(Panel(summary, title="Summary", border_style="cyan"))
        
        # Next steps
        if not dry_run and exported_count > 0:
            console.print()
            console.print("[dim]Next steps:[/dim]")
            console.print("  1. Review generated skills in .bob/skills/learned/")
            console.print("  2. Restart Bob to load new skills")
            console.print("  3. Bob will now have native access to these procedures")
        
    except AstroBobError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        if "--debug" in sys.argv:
            raise
        raise typer.Exit(2)


@app.command(name="list")
def list_skills(
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Skills directory (default: .bob/skills/learned)"
    ),
) -> None:
    """
    List all exported skills.
    
    Shows skills that have been exported to .bob/skills/learned/.
    
    Example:
        astrobob skills list
    """
    try:
        # Determine output directory
        if output_dir is None:
            output_dir = Path.cwd() / ".bob" / "skills" / "learned"
        
        if not output_dir.exists():
            console.print(f"[yellow]Skills directory not found: {output_dir}[/yellow]")
            console.print("\n[dim]Run 'astrobob skills sync' to export skills[/dim]")
            return
        
        # Find all SKILL.md files
        skill_files = list(output_dir.glob("*/SKILL.md"))
        
        if not skill_files:
            console.print(f"[yellow]No skills found in {output_dir}[/yellow]")
            console.print("\n[dim]Run 'astrobob skills sync' to export skills[/dim]")
            return
        
        # Create table
        table = Table(title=f"Exported Skills ({len(skill_files)})")
        table.add_column("Slug", style="cyan")
        table.add_column("Path", style="dim")
        table.add_column("Size", justify="right")
        
        for skill_file in sorted(skill_files):
            slug = skill_file.parent.name
            rel_path = skill_file.relative_to(Path.cwd())
            size = skill_file.stat().st_size
            
            # Format size
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f}KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f}MB"
            
            table.add_row(slug, str(rel_path), size_str)
        
        console.print()
        console.print(table)
        console.print()
        console.print(f"[dim]Skills directory: {output_dir}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

# Made with Bob
