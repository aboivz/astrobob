"""
Test script for skills sync functionality.

Tests the complete workflow:
1. Create a procedural memory
2. Run skills sync (dry-run)
3. Run skills sync (actual)
4. Verify SKILL.md file created
5. Check that memory is marked as exported
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from astrobob.config import get_config
from astrobob.astra import create_astra_client
from astrobob.core.store import MemoryStore
from astrobob.models import create_memory
from astrobob.skills_export.renderer import render_skill, write_skill_file

def main():
    print("=" * 60)
    print("Testing Skills Export System")
    print("=" * 60)
    
    # Get config and setup
    print("\n[1/6] Loading configuration...")
    config = get_config()
    client = create_astra_client(config)
    db = client.get_database()
    store = MemoryStore(db)
    print("[OK] Configuration loaded")
    
    # Create a test procedural memory
    print("\n[2/6] Creating test procedural memory...")
    memory = create_memory(
        memory_type="procedural",
        content="""How to Add a New MCP Tool to AstroBob

This is a step-by-step procedure for adding a new MCP tool:

1. **Define the tool schema** in `src/astrobob/mcp_server/schemas.py`
   - Add tool name, description, and input schema
   - Include examples in the description
   - Make sure description is verbose (Bob reads this)

2. **Implement the tool handler** in `src/astrobob/mcp_server/tools.py`
   - Create async function with proper error handling
   - Use MemoryStore for database operations
   - Return JSON-formatted response

3. **Register the tool** in `src/astrobob/mcp_server/server.py`
   - Add to tools list in FastMCP server
   - Test with MCP Inspector

4. **Add CLI command** (optional) in `src/astrobob/cli/memory_cmd.py`
   - Mirror the MCP tool functionality
   - Add rich formatting for output

5. **Write tests** in `tests/unit/test_mcp_tools.py`
   - Test input validation
   - Test success cases
   - Test error handling

Success rate: 100% when following these steps.""",
        project="astrobob",
        tags=["mcp", "development", "scaffolding"],
        importance=5,
        source="cli",
    )
    
    memory_id = store.insert(memory)
    print(f"[OK] Created procedural memory: {memory_id}")
    
    # Test renderer
    print("\n[3/6] Testing skill renderer...")
    retrieved = store.get("procedural", memory_id)
    slug, content = render_skill(retrieved)
    print(f"[OK] Rendered skill with slug: {slug}")
    print(f"  Content length: {len(content)} characters")
    print(f"  First line: {content.split(chr(10))[0]}")
    
    # Test dry-run write
    print("\n[4/6] Testing dry-run write...")
    output_dir = Path("test-skills-output")
    skill_path = write_skill_file(
        base_dir=output_dir,
        slug=slug,
        content=content,
        dry_run=True
    )
    print(f"[OK] Would write to: {skill_path}")
    
    # Test actual write
    print("\n[5/6] Testing actual write...")
    skill_path = write_skill_file(
        base_dir=output_dir,
        slug=slug,
        content=content,
        dry_run=False
    )
    print(f"[OK] Wrote skill to: {skill_path}")
    
    # Verify file exists
    if skill_path.exists():
        file_size = skill_path.stat().st_size
        print(f"  File size: {file_size} bytes")
        print(f"  File exists and is readable")
    else:
        print("  [ERROR] File not created!")
        return 1
    
    # Test mark_exported
    print("\n[6/6] Testing mark_exported...")
    store.mark_exported(memory_id, str(skill_path))
    
    # Verify it was marked
    updated = store.get("procedural", memory_id)
    if updated.exported_as_skill:
        print(f"[OK] Memory marked as exported to: {updated.exported_as_skill}")
        print(f"  Exported at: {updated.exported_at}")
    else:
        print("  [ERROR] Memory not marked as exported!")
        return 1
    
    # Cleanup
    print("\n[Cleanup] Removing test data...")
    store.soft_delete("procedural", memory_id)
    print("[OK] Deleted test memory")
    
    # Remove test output directory
    import shutil
    if output_dir.exists():
        shutil.rmtree(output_dir)
        print(f"[OK] Removed test directory: {output_dir}")
    
    print("\n" + "=" * 60)
    print("[OK] All tests passed!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
