"""Quick test script to verify configuration loads correctly."""

from astrobob.config import get_config
from astrobob.errors import ConfigError

def main():
    try:
        config = get_config()
        print("[OK] Configuration loaded successfully!")
        print(f"   Endpoint: {config.astra_db_api_endpoint}")
        print(f"   Token: {config.astra_db_application_token[:20]}...")
        print(f"   Collection Prefix: {config.collection_prefix}")
        print(f"   Default Project: {config.default_project}")
    except ConfigError as e:
        print(f"[ERROR] Configuration Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

# Made with Bob
