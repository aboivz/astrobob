"""
Test script to verify the new skill format generation.
"""

from datetime import datetime, timezone
from pathlib import Path
import sys
import io

# Set UTF-8 encoding for stdout on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from astrobob.models import MemoryDocument, Provenance
from astrobob.skills_export.renderer import render_skill, generate_description


def create_test_memory() -> MemoryDocument:
    """Create a test procedural memory."""
    return MemoryDocument(
        id="01KRQK0387V92FZCFJBD6PHY3T",
        memory_type="procedural",
        content="""FastAPI Endpoint Conventions for E-Commerce Platform:

1. Endpoint Structure:
   - Base path: /api/{resource}/{action}
   - Use plural nouns: /products, /orders
   - Use descriptive actions: /search, /filter

2. Implementation Pattern:
   - Use Pydantic models for request/response validation
   - Async route handlers (async def)
   - Query parameters for filters
   - Consistent response structure with 'total' and 'results' fields

3. Models:
   - Clear naming: Product, ProductSearchResponse
   - Include timestamps: created_at
   - Appropriate types: float for prices, bool for flags

4. Mock Data:
   - Store in module-level constants (e.g., MOCK_PRODUCTS)
   - Include realistic sample data
   - Cover different scenarios

5. Tech Stack:
   - FastAPI 0.104.1 with async routes
   - Pydantic v2 for validation
   - Uvicorn for ASGI server""",
        project="astrobob_demo",
        tags=["fastapi", "api", "conventions", "endpoints"],
        importance=5,
        confidence=1.0,
        scope="project",
        source="bob",
        provenance=Provenance(
            derived_from=["01ABC123", "01DEF456"],
            session_id="session_001",
            bob_skill_used="code-review"
        ),
        created_at=datetime(2026, 5, 16, 5, 8, 58, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 16, 5, 8, 58, tzinfo=timezone.utc),
        last_accessed_at=datetime(2026, 5, 16, 5, 15, 16, tzinfo=timezone.utc),
        access_count=2,
        success_count=0,
    )


def test_description_generation():
    """Test the description generation function."""
    print("=" * 80)
    print("Testing description generation...")
    print("=" * 80)
    
    memory = create_test_memory()
    description = generate_description(memory)
    
    print(f"\nGenerated description:")
    print(f"  {description}")
    print(f"\nLength: {len(description)} characters")
    
    # Verify it's not too long
    assert len(description) <= 150, f"Description too long: {len(description)} chars"
    
    # Verify it's not empty
    assert description, "Description is empty"
    
    print("\n✓ Description generation test passed")


def test_skill_rendering():
    """Test the full skill rendering."""
    print("\n" + "=" * 80)
    print("Testing skill rendering...")
    print("=" * 80)
    
    memory = create_test_memory()
    slug, content = render_skill(memory)
    
    print(f"\nGenerated slug: {slug}")
    print(f"\nGenerated content preview (first 500 chars):")
    print("-" * 80)
    print(content[:500])
    print("-" * 80)
    
    # Verify YAML front matter
    assert content.startswith("---\n"), "Content should start with YAML front matter"
    assert "name: " in content[:100], "YAML should contain 'name' field"
    assert "description: " in content[:200], "YAML should contain 'description' field"
    
    # Verify the content structure
    lines = content.split('\n')
    yaml_end_count = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            yaml_end_count += 1
            if yaml_end_count == 2:
                # Check that content starts after second ---
                assert i < 10, "YAML front matter should be within first 10 lines"
                break
    
    assert yaml_end_count >= 2, "Should have closing --- for YAML front matter"
    
    # Verify metadata section exists
    assert "## Metadata" in content, "Should have Metadata section"
    assert "Memory ID" in content, "Should include Memory ID in metadata"
    assert "Importance" in content, "Should include Importance in metadata"
    
    print("\n✓ Skill rendering test passed")
    
    return slug, content


def test_yaml_validity():
    """Test that the YAML front matter is valid."""
    print("\n" + "=" * 80)
    print("Testing YAML validity...")
    print("=" * 80)
    
    try:
        import yaml
    except ImportError:
        print("\n⚠ PyYAML not installed, skipping YAML validation")
        return
    
    memory = create_test_memory()
    slug, content = render_skill(memory)
    
    # Extract YAML front matter
    lines = content.split('\n')
    yaml_lines = []
    in_yaml = False
    yaml_end_count = 0
    
    for line in lines:
        if line.strip() == "---":
            yaml_end_count += 1
            if yaml_end_count == 1:
                in_yaml = True
                continue
            elif yaml_end_count == 2:
                break
        if in_yaml:
            yaml_lines.append(line)
    
    yaml_content = '\n'.join(yaml_lines)
    print(f"\nExtracted YAML:")
    print("-" * 80)
    print(yaml_content)
    print("-" * 80)
    
    # Parse YAML
    try:
        parsed = yaml.safe_load(yaml_content)
        print(f"\nParsed YAML:")
        print(f"  name: {parsed.get('name')}")
        print(f"  description: {parsed.get('description')}")
        
        # Verify required fields
        assert 'name' in parsed, "YAML must have 'name' field"
        assert 'description' in parsed, "YAML must have 'description' field"
        assert parsed['name'] == slug, f"Name should match slug: {parsed['name']} != {slug}"
        
        print("\n✓ YAML validity test passed")
    except yaml.YAMLError as e:
        print(f"\n✗ YAML parsing failed: {e}")
        raise


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("SKILL FORMAT TESTS")
    print("=" * 80)
    
    try:
        test_description_generation()
        slug, content = test_skill_rendering()
        test_yaml_validity()
        
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        
        # Optionally write to file for manual inspection
        output_file = Path(__file__).parent.parent / "test_skill_output.md"
        output_file.write_text(content, encoding='utf-8')
        print(f"\nFull output written to: {output_file}")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()

# Made with Bob
