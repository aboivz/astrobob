"""
Test script for AstraDB client and collections setup.

This script tests:
1. Connection to AstraDB
2. Collection creation
3. Basic operations
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from astrobob.config import get_config
from astrobob.astra import create_astra_client, create_all_collections


def main():
    print("=" * 60)
    print("AstroBob - AstraDB Connection Test")
    print("=" * 60)
    
    # Load configuration
    print("\n[1/4] Loading configuration...")
    try:
        config = get_config()
        print(f"  Endpoint: {config.astra_db_api_endpoint}")
        print(f"  Token: {config.astra_db_application_token[:20]}...")
        print("  Configuration loaded successfully")
    except Exception as e:
        print(f"  ERROR: Failed to load configuration: {e}")
        return 1
    
    # Create client
    print("\n[2/4] Creating AstraDB client...")
    try:
        client = create_astra_client(config)
        print("  Client created successfully")
    except Exception as e:
        print(f"  ERROR: Failed to create client: {e}")
        return 1
    
    # Test connection
    print("\n[3/4] Testing connection...")
    try:
        if client.test_connection():
            print("  Connection successful")
        else:
            print("  ERROR: Connection test failed")
            return 1
    except Exception as e:
        print(f"  ERROR: Connection test failed: {e}")
        return 1
    
    # Create collections
    print("\n[4/4] Creating collections...")
    try:
        db = client.get_database()
        results = create_all_collections(db)
        
        for memory_type, (collection_name, was_created) in results.items():
            status = "created" if was_created else "already exists"
            print(f"  {collection_name}: {status}")
        
        print("\n  All collections ready")
    except Exception as e:
        print(f"  ERROR: Failed to create collections: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # List all collections
    print("\n[Verification] Listing all collections in database:")
    try:
        db = client.get_database()
        collections = db.list_collection_names()
        for name in sorted(collections):
            if name.startswith("astrobob_"):
                print(f"  {name}")
    except Exception as e:
        print(f"  ERROR: Failed to list collections: {e}")
        return 1
    
    print("\n" + "=" * 60)
    print("All tests passed successfully")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
