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


def generate_description(memory: MemoryDocument, max_length: int = 150) -> str:
    """
    Generate a concise description for the skill from memory content.
    
    The description should clearly indicate when to use this skill.
    It's used by Bob to determine skill relevance.
    
    Args:
        memory: Memory document
        max_length: Maximum length of description
        
    Returns:
        Description suitable for YAML front matter (without special chars that need quoting)
        
    Examples:
        >>> generate_description(memory_with_content("How to add MCP tool: ..."))
        'Add MCP tools following the standard implementation pattern'
    """
    # Get first line or first sentence
    content = memory.content.strip()
    first_line = content.split('\n')[0].strip()
    
    # Remove trailing colons (common in procedural memory titles)
    if first_line.endswith(':'):
        first_line = first_line[:-1]
    
    # Try to get first sentence if it's reasonable length
    if '.' in first_line and first_line.index('.') < max_length:
        description = first_line[:first_line.index('.')]
    else:
        description = first_line
    
    # Remove common procedural prefixes and make it more descriptive
    prefixes_map = {
        'How to ': '',
        'To ': '',
        'When ': 'Apply when ',
        'If ': 'Use if ',
        'Steps to ': '',
        'Procedure for ': '',
    }
    
    for prefix, replacement in prefixes_map.items():
        if description.startswith(prefix):
            description = replacement + description[len(prefix):]
            break
    
    # Ensure first letter is capitalized
    if description:
        description = description[0].upper() + description[1:]
    
    # Truncate if too long, at word boundary
    if len(description) > max_length:
        description = description[:max_length].rsplit(' ', 1)[0]
        if not description.endswith('.'):
            description += '...'
    
    # Fallback if empty
    if not description:
        # Try to create description from tags
        if memory.tags:
            description = f"Apply {', '.join(memory.tags[:3])} best practices"
        else:
            description = "Procedural knowledge learned from experience"
    
    return description


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
        '---\nname: add-mcp-tool\ndescription: Add MCP...'
    """
    if memory.memory_type != "procedural":
        raise ValueError(f"Can only render procedural memories, got {memory.memory_type}")
    
    # Generate slug from content
    slug = slugify(memory.content[:50])
    
    # Generate description for YAML front matter
    description = generate_description(memory)
    
    # Get Jinja2 environment
    env = get_jinja_env()
    template = env.get_template("learned_skill.md.j2")
    
    # Render template
    content = template.render(
        slug=slug,
        description=description,
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
