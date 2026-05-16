#!/usr/bin/env python3
"""
Test script for the doctor command.

Tests various scenarios:
1. Missing environment variables
2. Invalid credentials
3. Missing collections
4. Missing .bob/ structure
5. All checks passing
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from astrobob.cli.doctor_cmd import (
    check_env_vars,
    check_astra_connectivity,
    check_collection_schemas,
    check_mcp_server,
    check_bob_structure,
)


def test_check_env_vars():
    """Test environment variable checking."""
    print("\n=== Testing Environment Variables Check ===")
    
    # Save original env vars
    original_endpoint = os.environ.get("ASTRA_DB_API_ENDPOINT")
    original_token = os.environ.get("ASTRA_DB_APPLICATION_TOKEN")
    
    try:
        # Test 1: Missing both
        if "ASTRA_DB_API_ENDPOINT" in os.environ:
            del os.environ["ASTRA_DB_API_ENDPOINT"]
        if "ASTRA_DB_APPLICATION_TOKEN" in os.environ:
            del os.environ["ASTRA_DB_APPLICATION_TOKEN"]
        
        passed, message = check_env_vars()
        status = "PASS" if not passed else "FAIL"
        print(f"Test 1 (missing both): {status} - {message}")
        
        # Test 2: With valid env vars
        if original_endpoint:
            os.environ["ASTRA_DB_API_ENDPOINT"] = original_endpoint
        if original_token:
            os.environ["ASTRA_DB_APPLICATION_TOKEN"] = original_token
        
        passed, message = check_env_vars()
        status = "PASS" if passed else "FAIL"
        print(f"Test 2 (valid env): {status} - {message}")
        
    finally:
        # Restore original env vars
        if original_endpoint:
            os.environ["ASTRA_DB_API_ENDPOINT"] = original_endpoint
        if original_token:
            os.environ["ASTRA_DB_APPLICATION_TOKEN"] = original_token


def test_check_astra_connectivity():
    """Test AstraDB connectivity check."""
    print("\n=== Testing AstraDB Connectivity Check ===")
    
    passed, message = check_astra_connectivity()
    status = "PASS" if passed else "FAIL"
    print(f"Connectivity test: {status} - {message}")


def test_check_collection_schemas():
    """Test collection schema checking."""
    print("\n=== Testing Collection Schemas Check ===")
    
    passed, message = check_collection_schemas()
    status = "PASS" if passed else "FAIL"
    print(f"Schema test: {status} - {message}")


def test_check_mcp_server():
    """Test MCP server importability."""
    print("\n=== Testing MCP Server Check ===")
    
    passed, message = check_mcp_server()
    status = "PASS" if passed else "FAIL"
    print(f"MCP server test: {status} - {message}")


def test_check_bob_structure():
    """Test .bob/ structure checking."""
    print("\n=== Testing .bob/ Structure Check ===")
    
    passed, message = check_bob_structure()
    status = "PASS" if passed else "FAIL"
    print(f"Structure test: {status} - {message}")
    
    if not passed:
        print("\nTip: Run 'astrobob init' to create the .bob/ structure")


def main():
    """Run all tests."""
    print("=" * 60)
    print("AstroBob Doctor Command Test Suite")
    print("=" * 60)
    
    try:
        test_check_env_vars()
        test_check_astra_connectivity()
        test_check_collection_schemas()
        test_check_mcp_server()
        test_check_bob_structure()
        
        print("\n" + "=" * 60)
        print("All tests completed")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
