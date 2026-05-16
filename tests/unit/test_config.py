"""Tests for configuration module."""

import os
import pytest
from pathlib import Path

from astrobob.config import load_config, validate_config, get_config
from astrobob.errors import ConfigError


def test_config_missing_endpoint(monkeypatch, tmp_path):
    """Test that missing ASTRA_DB_API_ENDPOINT raises ConfigError."""
    # Clear any existing env vars
    monkeypatch.delenv("ASTRA_DB_API_ENDPOINT", raising=False)
    monkeypatch.delenv("ASTRA_DB_APPLICATION_TOKEN", raising=False)
    # Change to temp directory to avoid loading .env
    monkeypatch.chdir(tmp_path)
    
    with pytest.raises(ConfigError) as exc_info:
        load_config()
    
    assert "ASTRA_DB_API_ENDPOINT" in str(exc_info.value)


def test_config_missing_token(monkeypatch, tmp_path):
    """Test that missing ASTRA_DB_APPLICATION_TOKEN raises ConfigError."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ASTRA_DB_API_ENDPOINT", "https://test.apps.astra.datastax.com")
    monkeypatch.delenv("ASTRA_DB_APPLICATION_TOKEN", raising=False)
    
    with pytest.raises(ConfigError) as exc_info:
        load_config()
    
    assert "ASTRA_DB_APPLICATION_TOKEN" in str(exc_info.value)


def test_config_valid(monkeypatch):
    """Test that valid configuration loads successfully."""
    monkeypatch.setenv("ASTRA_DB_API_ENDPOINT", "https://test-id-us-east-2.apps.astra.datastax.com")
    monkeypatch.setenv("ASTRA_DB_APPLICATION_TOKEN", "AstraCS:test-token-with-sufficient-length")
    
    config = load_config()
    
    assert config.astra_db_api_endpoint == "https://test-id-us-east-2.apps.astra.datastax.com"
    assert config.astra_db_application_token == "AstraCS:test-token-with-sufficient-length"
    assert config.collection_prefix == "astrobob"  # default value


def test_config_custom_values(monkeypatch):
    """Test that custom configuration values are loaded."""
    monkeypatch.setenv("ASTRA_DB_API_ENDPOINT", "https://test.apps.astra.datastax.com")
    monkeypatch.setenv("ASTRA_DB_APPLICATION_TOKEN", "AstraCS:test-token-with-sufficient-length")
    monkeypatch.setenv("COLLECTION_PREFIX", "custom_prefix")
    monkeypatch.setenv("DEFAULT_PROJECT", "my_project")
    
    config = load_config()
    
    assert config.collection_prefix == "custom_prefix"
    assert config.default_project == "my_project"


def test_validate_config_invalid_endpoint(monkeypatch):
    """Test that invalid endpoint format is caught."""
    monkeypatch.setenv("ASTRA_DB_API_ENDPOINT", "http://test.com")  # http instead of https
    monkeypatch.setenv("ASTRA_DB_APPLICATION_TOKEN", "AstraCS:test-token-with-sufficient-length")
    
    config = load_config()
    
    with pytest.raises(ConfigError) as exc_info:
        validate_config(config)
    
    assert "https://" in str(exc_info.value)


def test_validate_config_empty_token(monkeypatch):
    """Test that empty token is caught."""
    monkeypatch.setenv("ASTRA_DB_API_ENDPOINT", "https://test.apps.astra.datastax.com")
    monkeypatch.setenv("ASTRA_DB_APPLICATION_TOKEN", "   ")  # whitespace only
    
    config = load_config()
    
    with pytest.raises(ConfigError) as exc_info:
        validate_config(config)
    
    assert "cannot be empty" in str(exc_info.value)


def test_validate_config_short_token(monkeypatch):
    """Test that suspiciously short token is caught."""
    monkeypatch.setenv("ASTRA_DB_API_ENDPOINT", "https://test.apps.astra.datastax.com")
    monkeypatch.setenv("ASTRA_DB_APPLICATION_TOKEN", "short")
    
    config = load_config()
    
    with pytest.raises(ConfigError) as exc_info:
        validate_config(config)
    
    assert "too short" in str(exc_info.value)


def test_get_config_with_validation(monkeypatch):
    """Test get_config with validation enabled."""
    monkeypatch.setenv("ASTRA_DB_API_ENDPOINT", "https://test.apps.astra.datastax.com")
    monkeypatch.setenv("ASTRA_DB_APPLICATION_TOKEN", "AstraCS:test-token-with-sufficient-length")
    
    config = get_config(validate=True)
    
    assert config.astra_db_api_endpoint == "https://test.apps.astra.datastax.com"


def test_get_config_validation_fails(monkeypatch):
    """Test get_config fails when validation is enabled and config is invalid."""
    monkeypatch.setenv("ASTRA_DB_API_ENDPOINT", "http://test.com")  # invalid
    monkeypatch.setenv("ASTRA_DB_APPLICATION_TOKEN", "AstraCS:test-token-with-sufficient-length")
    
    with pytest.raises(ConfigError):
        get_config(validate=True)

# Made with Bob
