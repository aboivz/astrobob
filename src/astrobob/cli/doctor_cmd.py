"""Doctor command for system health checks."""

import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from astrobob.config import get_config
from astrobob.errors import AstroBobError, ConfigError, AstraConnectionError
from astrobob.astra.client import create_astra_client
from astrobob.astra.collections import get_collection_name, MemoryType

app = typer.Typer(help="System health checks")
console = Console()


def check_env_vars() -> tuple[bool, str]:
    """Check if required environment variables are present."""
    try:
        config = get_config()
        if not config.astra_db_api_endpoint:
            return False, "ASTRA_DB_API_ENDPOINT not set"
        if not config.astra_db_application_token:
            return False, "ASTRA_DB_APPLICATION_TOKEN not set"
        return True, "All required environment variables present"
    except ConfigError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e}"


def check_astra_connectivity() -> tuple[bool, str]:
    """Check if AstraDB is reachable."""
    try:
        client = create_astra_client()
        if client.test_connection():
            return True, "Successfully connected to AstraDB"
        return False, "Failed to connect to AstraDB"
    except AstraConnectionError as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def check_collection_schemas() -> tuple[bool, str]:
    """Check if all required collections exist with correct schemas."""
    try:
        client = create_astra_client()
        db = client.get_database()
        collection_names = db.list_collection_names()
        
        # Define expected collections
        memory_types: list[MemoryType] = ["semantic", "episodic", "procedural"]
        expected_collections = [get_collection_name(mt) for mt in memory_types]
        
        missing = []
        for coll_name in expected_collections:
            if coll_name not in collection_names:
                missing.append(coll_name)
        
        if missing:
            return False, f"Missing collections: {', '.join(missing)}"
        
        # Check schema for each collection
        issues = []
        for coll_name in expected_collections:
            try:
                coll = db.get_collection(coll_name)
                # Try a simple find operation to verify collection is accessible
                # Don't use count_documents with upper_bound as it fails when count > upper_bound
                list(coll.find({}, limit=1))
            except Exception as e:
                issues.append(f"{coll_name}: {str(e)[:50]}")
        
        if issues:
            return False, f"Collection issues: {'; '.join(issues)}"
        
        return True, f"All {len(expected_collections)} collections present and accessible"
    except Exception as e:
        return False, f"Error checking collections: {e}"


def check_mcp_server() -> tuple[bool, str]:
    """Check if MCP server module is importable."""
    try:
        # Try importing the MCP server
        from astrobob.mcp_server import server  # noqa: F401
        return True, "MCP server module importable"
    except ImportError as e:
        return False, f"Import error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def check_bob_structure() -> tuple[bool, str]:
    """Check if .bob/ directory structure is valid."""
    try:
        bob_dir = Path.cwd() / ".bob"
        
        if not bob_dir.exists():
            return False, ".bob/ directory not found (run 'astrobob init')"
        
        required_files = [
            ".bob/mcp.json",
            ".bob/custom_modes.yaml",
        ]
        
        required_dirs = [
            ".bob/skills",
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (Path.cwd() / file_path).exists():
                missing_files.append(file_path)
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not (Path.cwd() / dir_path).exists():
                missing_dirs.append(dir_path)
        
        if missing_files or missing_dirs:
            missing = missing_files + missing_dirs
            return False, f"Missing: {', '.join(missing)}"
        
        # Check if skills directory has content
        skills_dir = Path.cwd() / ".bob" / "skills"
        skill_count = len(list(skills_dir.glob("*/SKILL.md")))
        
        return True, f".bob/ structure valid ({skill_count} skills found)"
    except Exception as e:
        return False, f"Error checking structure: {e}"


@app.command()
def run(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Run comprehensive system health checks.
    
    Validates:
    - Environment variables
    - AstraDB connectivity
    - Collection schemas
    - MCP server importability
    - .bob/ directory structure
    
    Exit codes:
    - 0: All checks passed
    - 1: One or more checks failed
    """
    console.print("\n[bold cyan]AstroBob System Health Check[/bold cyan]\n")
    
    checks = [
        ("Environment Variables", check_env_vars),
        ("AstraDB Connectivity", check_astra_connectivity),
        ("Collection Schemas", check_collection_schemas),
        ("MCP Server", check_mcp_server),
        (".bob/ Structure", check_bob_structure),
    ]
    
    results: list[tuple[str, bool, str]] = []
    all_passed = True
    
    for check_name, check_func in checks:
        console.print(f"Checking {check_name}...", end=" ")
        try:
            passed, message = check_func()
            results.append((check_name, passed, message))
            
            if passed:
                console.print("[green]PASS[/green]")
            else:
                console.print("[red]FAIL[/red]")
                all_passed = False
            
            if verbose or not passed:
                console.print(f"  [dim]{message}[/dim]")
        except Exception as e:
            results.append((check_name, False, f"Unexpected error: {e}"))
            console.print("[red]✗[/red]")
            console.print(f"  [dim red]Unexpected error: {e}[/dim red]")
            all_passed = False
    
    # Summary table
    console.print("\n[bold]Summary:[/bold]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Check", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Details", style="dim")
    
    for check_name, passed, message in results:
        status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        table.add_row(check_name, status, message)
    
    console.print(table)
    
    # Final verdict
    console.print()
    if all_passed:
        console.print("[bold green]All checks passed! System is healthy.[/bold green]\n")
        sys.exit(0)
    else:
        console.print("[bold red]Some checks failed. See details above.[/bold red]")
        console.print("[dim]Run with --verbose for more information.[/dim]\n")
        
        # Provide helpful suggestions
        failed_checks = [name for name, passed, _ in results if not passed]
        
        if "Environment Variables" in failed_checks:
            console.print("[yellow]Tip:[/yellow] Create a .env file with ASTRA_DB_API_ENDPOINT and ASTRA_DB_APPLICATION_TOKEN")
        
        if "AstraDB Connectivity" in failed_checks:
            console.print("[yellow]Tip:[/yellow] Verify your AstraDB credentials and network connectivity")
        
        if "Collection Schemas" in failed_checks:
            console.print("[yellow]Tip:[/yellow] Run 'astrobob astra setup' to create missing collections")
        
        if ".bob/ Structure" in failed_checks:
            console.print("[yellow]Tip:[/yellow] Run 'astrobob init' to set up the .bob/ directory")
        
        console.print()
        sys.exit(1)


if __name__ == "__main__":
    app()

# Made with Bob
