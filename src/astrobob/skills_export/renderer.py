"""
Skills Export Renderer

Converts procedural memories from AstraDB into Bob-compatible SKILL.md files.
"""

import re
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from astrobob.models import MemoryDocument


def slugify(text: str, max_length: int = 50) -> str:
    """
    Convert text to a URL-safe slug.
    
    Args:
        text: Text to slugify
        max_length: Maximum length of slug
        
    Returns:
        Slugified text suitable for directory names
        
    Examples:
        >>> slugify("How to add MCP tool")
        'how-to-add-mcp-tool'
        >>> slugify("Fix auth bug (2024)")
        'fix-auth-bug-2024'
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters, keep alphanumeric and spaces
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    
    # Replace spaces and multiple hyphens with single hyphen
    text = re.sub(r'[\s-]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length].rsplit('-', 1)[0]
    
    return text or 'unnamed-skill'


def get_jinja_env() -> Environment:
    """
    Get Jinja2 environment configured for skills templates.
    
    Returns:
        Configured Jinja2 Environment
    """
    templates_dir = Path(__file__).parent / "templates"
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=False,  # Markdown doesn't need HTML escaping
        trim_blocks=True,
        lstrip_blocks=True,
    )


def generate_skill_title(memory: MemoryDocument) -> str:
    """
    Generate a human-readable title from memory content.
    
    Args:
        memory: Memory document
        
    Returns:
        Title for the skill
        
    Examples:
        >>> generate_skill_title(memory_with_content("How to add MCP tool: ..."))
        'How to Add MCP Tool'
    """
    # Take first line or first 60 chars
    first_line = memory.content.split('\n')[0]
    if len(first_line) > 60:
        first_line = first_line[:60].rsplit(' ', 1)[0] + '...'
    
    # Remove common prefixes
    for prefix in ['How to ', 'To ', 'When ', 'If ']:
        if first_line.startswith(prefix):
            first_line = prefix + first_line[len(prefix):].capitalize()
            break
    else:
        # Capitalize first letter
        first_line = first_line[0].upper() + first_line[1:] if first_line else 'Unnamed Skill'
    
    return first_line


def render_skill(memory: MemoryDocument) -> tuple[str, str]:
    """
    Convert procedural memory to SKILL.md content.
    
    Args:
        memory: Procedural memory document
        
    Returns:
        Tuple of (slug, rendered_markdown)
        
    Raises:
        ValueError: If memory is not procedural type
        
    Example:
        >>> slug, content = render_skill(procedural_memory)
        >>> print(slug)
        'add-mcp-tool'
        >>> print(content[:50])
        '# How to Add MCP Tool\n\n> **Auto-generated from...'
    """
    if memory.memory_type != "procedural":
        raise ValueError(f"Can only render procedural memories, got {memory.memory_type}")
    
    # Generate slug from content
    slug = slugify(memory.content[:50])
    
    # Generate title
    title = generate_skill_title(memory)
    
    # Get Jinja2 environment
    env = get_jinja_env()
    template = env.get_template("learned_skill.md.j2")
    
    # Render template
    content = template.render(
        title=title,
        slug=slug,
        memory_id=memory.id,
        content=memory.content,
        tags=memory.tags,
        importance=memory.importance,
        confidence=memory.confidence,
        project=memory.project,
        scope=memory.scope,
        source=memory.source,
        provenance=memory.provenance,
        supersedes=memory.supersedes,
        created_at=memory.created_at,
        updated_at=memory.updated_at,
        last_accessed_at=memory.last_accessed_at,
        access_count=memory.access_count,
        success_count=memory.success_count,
    )
    
    return slug, content


def get_skill_path(base_dir: Path, slug: str) -> Path:
    """
    Get the full path for a skill file.
    
    Args:
        base_dir: Base directory (usually .bob/skills/learned)
        slug: Skill slug
        
    Returns:
        Path to SKILL.md file
        
    Example:
        >>> get_skill_path(Path(".bob/skills/learned"), "add-mcp-tool")
        Path('.bob/skills/learned/add-mcp-tool/SKILL.md')
    """
    skill_dir = base_dir / slug
    return skill_dir / "SKILL.md"


def write_skill_file(
    base_dir: Path,
    slug: str,
    content: str,
    dry_run: bool = False
) -> Path:
    """
    Write skill content to file.
    
    Args:
        base_dir: Base directory (usually .bob/skills/learned)
        slug: Skill slug
        content: Rendered markdown content
        dry_run: If True, don't actually write file
        
    Returns:
        Path where file was (or would be) written
        
    Example:
        >>> path = write_skill_file(Path(".bob/skills/learned"), "add-mcp-tool", content)
        >>> print(path)
        .bob/skills/learned/add-mcp-tool/SKILL.md
    """
    skill_path = get_skill_path(base_dir, slug)
    
    if not dry_run:
        # Create directory if needed
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        skill_path.write_text(content, encoding='utf-8')
    
    return skill_path

# Made with Bob
