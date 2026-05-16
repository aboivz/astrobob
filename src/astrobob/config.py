"""Configuration management for AstroBob."""

import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from astrobob.errors import ConfigError


class AstroBobConfig(BaseSettings):
    """Configuration for AstroBob with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # AstraDB Configuration (Required)
    astra_db_api_endpoint: str = Field(
        ...,
        description="AstraDB API endpoint URL"
    )
    astra_db_application_token: str = Field(
        ...,
        description="AstraDB application token for authentication"
    )
    
    # Collection Configuration
    collection_prefix: str = Field(
        default="astrobob",
        description="Prefix for collection names"
    )
    
    # Project Configuration
    default_project: str = Field(
        default="default",
        description="Default project name for memories"
    )
    
    # Embedding Configuration
    embedding_provider: str = Field(
        default="nvidia",
        description="Embedding provider (nvidia)"
    )
    embedding_model: str = Field(
        default="NV-Embed-QA-E5-V5",
        description="Embedding model name"
    )
    
    # Reranking Configuration
    rerank_provider: str = Field(
        default="nvidia",
        description="Reranking provider (nvidia)"
    )
    rerank_model: str = Field(
        default="nv-rerank-qa-mistral-4b-v3",
        description="Reranking model name"
    )
    
    # Search Configuration
    default_search_limit: int = Field(
        default=10,
        description="Default number of results to return"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )


def load_config(env_file: Optional[Path] = None) -> AstroBobConfig:
    """
    Load configuration from environment variables and .env file.
    
    Args:
        env_file: Optional path to .env file. If None, searches for .env in current directory.
        
    Returns:
        AstroBobConfig instance
        
    Raises:
        ConfigError: If required configuration is missing or invalid
    """
    # Load .env file if it exists
    if env_file:
        if not env_file.exists():
            raise ConfigError(f".env file not found at: {env_file}")
        load_dotenv(env_file)
    else:
        # Try to load from current directory
        load_dotenv()
    
    try:
        config = AstroBobConfig()
        return config
    except Exception as e:
        # Provide helpful error message for missing required fields
        error_msg = str(e)
        if "astra_db_api_endpoint" in error_msg.lower():
            raise ConfigError(
                "Missing required environment variable: ASTRA_DB_API_ENDPOINT\n"
                "Please set it in your .env file or environment.\n"
                "Example: ASTRA_DB_API_ENDPOINT=https://your-db-id-region.apps.astra.datastax.com"
            ) from e
        elif "astra_db_application_token" in error_msg.lower():
            raise ConfigError(
                "Missing required environment variable: ASTRA_DB_APPLICATION_TOKEN\n"
                "Please set it in your .env file or environment.\n"
                "Get your token from: https://astra.datastax.com/settings/tokens"
            ) from e
        else:
            raise ConfigError(f"Configuration error: {error_msg}") from e


def validate_config(config: AstroBobConfig) -> None:
    """
    Validate configuration values.
    
    Args:
        config: Configuration to validate
        
    Raises:
        ConfigError: If configuration is invalid
    """
    # Validate endpoint format
    if not config.astra_db_api_endpoint.startswith("https://"):
        raise ConfigError(
            f"Invalid ASTRA_DB_API_ENDPOINT: {config.astra_db_api_endpoint}\n"
            "Endpoint must start with https://"
        )
    
    # Validate token is not empty
    if not config.astra_db_application_token.strip():
        raise ConfigError("ASTRA_DB_APPLICATION_TOKEN cannot be empty")
    
    # Validate token format (basic check)
    if len(config.astra_db_application_token) < 20:
        raise ConfigError(
            "ASTRA_DB_APPLICATION_TOKEN appears to be invalid (too short)\n"
            "Token should be a long string starting with 'AstraCS:...'"
        )


def get_config(env_file: Optional[Path] = None, validate: bool = True) -> AstroBobConfig:
    """
    Get validated configuration.
    
    Args:
        env_file: Optional path to .env file
        validate: Whether to validate configuration
        
    Returns:
        AstroBobConfig instance
        
    Raises:
        ConfigError: If configuration is missing or invalid
    """
    config = load_config(env_file)
    
    if validate:
        validate_config(config)
    
    return config


def ensure_config_or_exit() -> AstroBobConfig:
    """
    Load and validate configuration, exit with error code 1 if it fails.
    
    This is the main entry point for CLI commands that require configuration.
    
    Returns:
        AstroBobConfig instance
    """
    try:
        return get_config()
    except ConfigError as e:
        print(f"❌ Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)

# Made with Bob
