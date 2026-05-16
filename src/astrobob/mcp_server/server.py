"""
MCP server for AstroBob.

Exposes memory tools via Model Context Protocol for use by Bob and other MCP clients.
"""

import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from astrobob.config import load_config
from astrobob.mcp_server.schemas import ALL_TOOLS
from astrobob.mcp_server.tools import MemoryTools


# Create MCP server instance
app = Server("astrobob")

# Global tools instance (initialized on startup)
tools: MemoryTools | None = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name=tool["name"],
            description=tool["description"],
            inputSchema=tool["inputSchema"],
        )
        for tool in ALL_TOOLS
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Handle tool calls from MCP clients.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        Tool result as TextContent
    """
    global tools
    
    if tools is None:
        return [TextContent(
            type="text",
            text="Error: Server not initialized. Please restart the server."
        )]
    
    try:
        # Route to appropriate tool handler
        if name == "remember":
            result = await tools.remember(
                content=arguments["content"],
                memory_type=arguments["memory_type"],
                project=arguments["project"],
                tags=arguments.get("tags"),
                importance=arguments.get("importance", 3),
                source=arguments.get("source", "bob"),
            )
        
        elif name == "recall":
            result = await tools.recall(
                query=arguments["query"],
                project=arguments["project"],
                memory_types=arguments.get("memory_types"),
                tags=arguments.get("tags"),
                limit=arguments.get("limit", 10),
                min_importance=arguments.get("min_importance"),
            )
        
        elif name == "reflect":
            result = await tools.reflect(
                project=arguments["project"],
                episode_ids=arguments["episode_ids"],
                lesson=arguments["lesson"],
                tags=arguments.get("tags"),
                importance=arguments.get("importance", 4),
            )
        
        elif name == "forget":
            result = await tools.forget(
                memory_type=arguments["memory_type"],
                memory_id=arguments["memory_id"],
                reason=arguments.get("reason", "No longer needed"),
            )
        
        elif name == "audit_trail":
            result = await tools.audit_trail(
                memory_type=arguments["memory_type"],
                memory_id=arguments["memory_id"],
            )
        
        else:
            result = {
                "success": False,
                "error": f"Unknown tool: {name}"
            }
        
        # Format result as text
        import json
        result_text = json.dumps(result, indent=2)
        
        return [TextContent(
            type="text",
            text=result_text
        )]
        
    except Exception as e:
        import traceback
        error_text = f"Error executing {name}: {e}\n\n{traceback.format_exc()}"
        return [TextContent(
            type="text",
            text=error_text
        )]


async def run_stdio_server():
    """Run the MCP server using STDIO transport."""
    global tools
    
    # Load configuration
    config = load_config()
    
    # Initialize tools
    tools = MemoryTools(config)
    
    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Main entry point for MCP server."""
    asyncio.run(run_stdio_server())


if __name__ == "__main__":
    main()

# Made with Bob
