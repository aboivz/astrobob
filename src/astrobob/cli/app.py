"""
AstroBob CLI - Main application entry point.

Provides command-line interface for managing AstroBob memories.
"""

import sys
import typer
from rich.console import Console

from astrobob.cli import astra_cmd, memory_cmd, mcp_cmd, init_cmd, skills_cmd, doctor_cmd

# Create main app
app = typer.Typer(
    name="astrobob",
    help="Memory-powered agent toolkit for IBM Bob",
    add_completion=False,
)

# Create console for rich output
console = Console()

# Add command groups
app.add_typer(astra_cmd.app, name="astra", help="AstraDB setup and management")
app.add_typer(memory_cmd.app, name="memory", help="Memory operations (CRUD)")
app.add_typer(mcp_cmd.app, name="mcp", help="MCP server management")
app.add_typer(skills_cmd.app, name="skills", help="Export procedural memories as Bob skills")

# Add init and doctor as direct commands (not groups)
app.command(name="init", help="Initialize AstroBob in a project")(init_cmd.init)
app.command(name="doctor", help="Run system health checks")(doctor_cmd.run)


@app.command()
def version():
    """Show AstroBob version."""
    console.print("[bold cyan]AstroBob[/bold cyan] version [green]0.1.0[/green]")


def main():
    """Main entry point for the CLI."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
