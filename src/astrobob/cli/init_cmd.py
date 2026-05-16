"""
AstroBob CLI - Init command.

Initializes AstroBob in a project by generating configuration files.
"""

import sys
import os
from pathlib import Path
import shutil
import typer
from rich.console import Console
from rich.panel import Panel
from jinja2 import Environment, FileSystemLoader, select_autoescape

from astrobob.config import get_config
from astrobob.errors import AstroBobError

# Create command
app = typer.Typer()
console = Console()


def get_templates_dir() -> Path:
    """Get the templates directory path."""
    # Templates are in src/astrobob/templates
    return Path(__file__).parent.parent / "templates"




@app.command()
def init(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files",
    ),
    bob_dir: Path = typer.Option(
        Path(".bob"),
        "--bob-dir",
        help="Bob configuration directory",
    ),
):
    """
    Initialize AstroBob in the current project.
    
    Creates:
    - .bob/mcp.json (MCP server configuration)
    - .bob/custom_modes.yaml (AstroBob Builder mode)
    - .bob/skills/ (3 SKILL.md files)
    - .env.example (environment template)
    
    Example:
      astrobob init
      astrobob init --force  # Overwrite existing files
    """
    console.print("\n[bold cyan]Initializing AstroBob...[/bold cyan]\n")
    
    # Get current directory
    project_dir = Path.cwd()
    console.print(f"Project directory: [cyan]{project_dir}[/cyan]")
    
    # Check if .bob directory exists
    if bob_dir.exists() and not force:
        console.print(f"\n[yellow]Warning: {bob_dir} already exists[/yellow]")
        console.print("Use --force to overwrite existing files")
        sys.exit(1)
    
    # Create directories
    bob_dir.mkdir(exist_ok=True)
    skills_dir = bob_dir / "skills"
    skills_dir.mkdir(exist_ok=True)
    
    # Create skill subdirectories
    (skills_dir / "astra-memory-engineer").mkdir(exist_ok=True)
    (skills_dir / "agent-reflector").mkdir(exist_ok=True)
    (skills_dir / "wxo-agent-builder").mkdir(exist_ok=True)
    (skills_dir / "learned").mkdir(exist_ok=True)
    
    console.print(f"\n[green]Created directories:[/green]")
    console.print(f"  {bob_dir}/")
    console.print(f"  {bob_dir}/skills/")
    console.print(f"  {bob_dir}/skills/astra-memory-engineer/")
    console.print(f"  {bob_dir}/skills/agent-reflector/")
    console.print(f"  {bob_dir}/skills/wxo-agent-builder/")
    console.print(f"  {bob_dir}/skills/learned/")
    
    # Setup Jinja2 environment
    templates_dir = get_templates_dir()
    
    # Get configuration values
    try:
        config = get_config()
        astra_endpoint = config.astra_db_api_endpoint
        astra_token = config.astra_db_application_token
    except AstroBobError:
        # No config yet, use placeholders
        astra_endpoint = "https://YOUR_DATABASE_ID-YOUR_REGION.apps.astra.datastax.com"
        astra_token = "AstraCS:YOUR_TOKEN_HERE"
    
    # Template context
    context = {
        "astra_endpoint": astra_endpoint,
        "astra_token": astra_token,
    }
    
    # Generate files
    files_created = []
    
    try:
        # 1. MCP configuration
        jinja_env = Environment(
            loader=FileSystemLoader(templates_dir / "bob"),
            autoescape=select_autoescape()
        )
        mcp_template = jinja_env.get_template("mcp.json.j2")
        mcp_content = mcp_template.render(context)
        
        mcp_file = bob_dir / "mcp.json"
        mcp_file.write_text(mcp_content, encoding="utf-8")
        files_created.append(str(mcp_file))
        
        # 2. Custom modes
        modes_template = jinja_env.get_template("custom_modes.yaml.j2")
        modes_content = modes_template.render(context)
        
        modes_file = bob_dir / "custom_modes.yaml"
        modes_file.write_text(modes_content, encoding="utf-8")
        files_created.append(str(modes_file))
        
        # 3. Skills (copy from templates)
        skills_source = templates_dir / "skills"
        
        # Copy astra-memory-engineer skill
        shutil.copy(
            skills_source / "astra-memory-engineer.md",
            skills_dir / "astra-memory-engineer" / "SKILL.md"
        )
        files_created.append(str(skills_dir / "astra-memory-engineer" / "SKILL.md"))
        
        # Copy agent-reflector skill
        shutil.copy(
            skills_source / "agent-reflector.md",
            skills_dir / "agent-reflector" / "SKILL.md"
        )
        files_created.append(str(skills_dir / "agent-reflector" / "SKILL.md"))
        
        # Copy wxo-agent-builder skill
        shutil.copy(
            skills_source / "wxo-agent-builder.md",
            skills_dir / "wxo-agent-builder" / "SKILL.md"
        )
        files_created.append(str(skills_dir / "wxo-agent-builder" / "SKILL.md"))
        
        # 4. .env.example
        env_example_source = templates_dir / ".env.example"
        env_example_dest = project_dir / ".env.example"
        
        if not env_example_dest.exists() or force:
            shutil.copy(env_example_source, env_example_dest)
            files_created.append(str(env_example_dest))
        
        # 5. Create README in learned skills directory
        learned_readme = skills_dir / "learned" / "README.md"
        learned_readme.write_text(
            "# Learned Skills\n\n"
            "This directory contains skills automatically generated from procedural memories.\n\n"
            "Use `astrobob skills sync` to export procedural memories as Bob skills.\n",
            encoding="utf-8"
        )
        files_created.append(str(learned_readme))
        
        # Success message
        console.print(f"\n[green]Successfully created {len(files_created)} files:[/green]")
        for file in files_created:
            console.print(f"  [cyan]{file}[/cyan]")
        
        # Next steps
        next_steps = Panel(
            "[bold]Next Steps:[/bold]\n\n"
            "1. Copy .env.example to .env and fill in your AstraDB credentials\n"
            "2. Run: [cyan]astrobob astra setup[/cyan] to create collections\n"
            "3. Start MCP server: [cyan]astrobob mcp serve[/cyan]\n"
            "4. Configure Bob to use the MCP server (see .bob/mcp.json)\n"
            "5. Enable the AstroBob Builder mode in Bob (see .bob/custom_modes.yaml)\n"
            "6. Start using memory-aware development!\n\n"
            "[dim]For more information, see the documentation.[/dim]",
            title="Setup Complete",
            border_style="green",
        )
        console.print(next_steps)
        console.print()
        
    except Exception as e:
        console.print(f"\n[red]Error during initialization: {e}[/red]")
        sys.exit(2)


# Made with Bob