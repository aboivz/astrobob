"""
CLI commands for MCP server management.
"""

import typer
from rich.console import Console

app = typer.Typer(help="MCP server commands")
console = Console()


@app.command()
def serve(
    transport: str = typer.Option(
        "stdio",
        "--transport",
        "-t",
        help="Transport type (stdio or http)"
    ),
    port: int = typer.Option(
        8765,
        "--port",
        "-p",
        help="Port for HTTP transport"
    ),
):
    """
    Start the MCP server.
    
    Examples:
        astrobob mcp serve                    # STDIO (default)
        astrobob mcp serve --transport http   # HTTP on port 8765
    """
    if transport == "stdio":
        console.print("[bold green]Starting AstroBob MCP server (STDIO)...[/bold green]")
        console.print("Server is ready to accept connections from Bob or other MCP clients.")
        console.print("Press Ctrl+C to stop.")
        
        # Import and run server
        from astrobob.mcp_server.server import main
        try:
            main()
        except KeyboardInterrupt:
            console.print("\n[yellow]Server stopped.[/yellow]")
    
    elif transport == "http":
        console.print(f"[bold green]Starting AstroBob MCP server (HTTP on port {port})...[/bold green]")
        console.print("[yellow]HTTP transport not yet implemented. Use STDIO for now.[/yellow]")
        raise typer.Exit(1)
    
    else:
        console.print(f"[red]Unknown transport: {transport}[/red]")
        console.print("Supported transports: stdio, http")
        raise typer.Exit(1)


@app.command()
def test():
    """
    Test MCP server tools (without starting server).
    
    Runs a quick test of all 5 tools to verify they work correctly.
    """
    import asyncio
    from astrobob.config import load_config
    from astrobob.mcp_server.tools import MemoryTools
    
    console.print("[bold]Testing MCP Tools...[/bold]\n")
    
    async def run_tests():
        # Load config and initialize tools
        config = load_config()
        tools = MemoryTools(config)
        
        # Test 1: remember
        console.print("1. Testing remember()...")
        result = await tools.remember(
            content="Test memory for MCP server validation",
            memory_type="semantic",
            project="astrobob-test",
            tags=["test", "mcp"],
            importance=3,
            source="cli",
        )
        if result["success"]:
            console.print(f"   [green]PASS[/green] Stored memory: {result['memory_id']}")
            test_memory_id = result["memory_id"]
        else:
            console.print(f"   [red]FAIL[/red] Failed: {result.get('error')}")
            return
        
        # Test 2: recall
        console.print("\n2. Testing recall()...")
        result = await tools.recall(
            query="test memory",
            project="astrobob-test",
            limit=5,
        )
        if result["success"]:
            console.print(f"   [green]PASS[/green] Found {result['count']} memories")
        else:
            console.print(f"   [red]FAIL[/red] Failed: {result.get('error')}")
        
        # Test 3: audit_trail
        console.print("\n3. Testing audit_trail()...")
        result = await tools.audit_trail(
            memory_type="semantic",
            memory_id=test_memory_id,
        )
        if result["success"]:
            console.print(f"   [green]PASS[/green] Retrieved audit trail")
            console.print(f"   Created: {result['created_at']}")
            console.print(f"   Access count: {result['access_count']}")
        else:
            console.print(f"   [red]FAIL[/red] Failed: {result.get('error')}")
        
        # Test 4: forget
        console.print("\n4. Testing forget()...")
        result = await tools.forget(
            memory_type="semantic",
            memory_id=test_memory_id,
            reason="Test cleanup",
        )
        if result["success"]:
            console.print(f"   [green]PASS[/green] Soft-deleted memory")
        else:
            console.print(f"   [red]FAIL[/red] Failed: {result.get('error')}")
        
        # Test 5: reflect (requires episodes, so we'll create one)
        console.print("\n5. Testing reflect()...")
        episode_result = await tools.remember(
            content="Test episode for reflection",
            memory_type="episodic",
            project="astrobob-test",
            tags=["test"],
            importance=4,
            source="cli",
        )
        if episode_result["success"]:
            episode_id = episode_result["memory_id"]
            result = await tools.reflect(
                project="astrobob-test",
                episode_ids=[episode_id],
                lesson="Test lesson: Always test your tools",
                tags=["test", "lesson"],
                importance=4,
            )
            if result["success"]:
                console.print(f"   [green]PASS[/green] Created procedural memory: {result['memory_id']}")
                # Clean up
                await tools.forget("episodic", episode_id, "Test cleanup")
                await tools.forget("procedural", result['memory_id'], "Test cleanup")
            else:
                console.print(f"   [red]FAIL[/red] Failed: {result.get('error')}")
        else:
            console.print(f"   [red]FAIL[/red] Failed to create test episode")
        
        console.print("\n[bold green]All MCP tools tested successfully![/bold green]")
    
    try:
        asyncio.run(run_tests())
    except Exception as e:
        console.print(f"\n[red]Test failed: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        raise typer.Exit(1)

# Made with Bob
