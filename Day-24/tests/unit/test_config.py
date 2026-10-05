"""
Unit Tests: Environment Variables & Configuration
Validates Settings model constraints, default values, and security masking.
"""

import pytest
from pydantic import ValidationError
from app.core.config import Settings, get_settings


def test_default_settings_loading():
    """Verify that default settings instantiate without errors."""
    settings = get_settings()
    assert settings.APP_NAME is not None
    assert settings.APP_VERSION == "1.0.0"
    assert settings.PORT > 0
    assert len(settings.API_KEY) >= 8


def test_environment_validation():
    """Verify supported runtime environment values."""
    for env in ["development", "staging", "production", "test"]:
        s = Settings(ENVIRONMENT=env, API_KEY="valid-secure-key-for-test-342")
        assert s.ENVIRONMENT == env


def test_invalid_environment_raises_validation_error():
    """Verify that unsupported environment names raise ValidationError."""
    with pytest.raises(ValidationError):
        Settings(ENVIRONMENT="invalid_env_name")


def test_port_validation_range():
    """Verify that valid port numbers are accepted."""
    s1 = Settings(PORT=8000)
    assert s1.PORT == 8000
    s2 = Settings(PORT=443)
    assert s2.PORT == 443


def test_invalid_port_raises_validation_error():
    """Verify that out-of-range port numbers raise ValidationError."""
    with pytest.raises(ValidationError):
        Settings(PORT=0)
    with pytest.raises(ValidationError):
        Settings(PORT=70000)


def test_api_key_length_validation():
    """Verify that insecure short API keys or default keys in production raise ValidationError."""
    with pytest.raises(ValidationError):
        Settings(API_KEY="short")
    with pytest.raises(ValidationError):
        Settings(ENVIRONMENT="production", API_KEY="linkific-dev-local-test-key-2026")


def test_is_production_property():
    """Verify is_production evaluates correctly."""
    prod = Settings(ENVIRONMENT="production", API_KEY="prod-secure-custom-key-12345")
    assert prod.is_production is True
    dev = Settings(ENVIRONMENT="development")
    assert dev.is_production is False


def test_get_safe_dict_masks_api_key():
    """Verify get_safe_dict masks the secret API key."""
    settings = Settings(API_KEY="supersecretapikey12345")
    safe_dict = settings.get_safe_dict()
    assert "supersecretapikey12345" not in safe_dict["API_KEY"]
    assert "****" in safe_dict["API_KEY"]


def test_cors_origins_parsing():
    """Verify that CORS_ORIGINS parses list, json array string, and comma-separated string, stripping wildcards."""
    s_list = Settings(CORS_ORIGINS=["https://linkific.in"])
    assert s_list.CORS_ORIGINS == ["https://linkific.in"]

    s_str = Settings(CORS_ORIGINS="https://linkific.in, https://app.linkific.in, *")
    assert "https://linkific.in" in s_str.CORS_ORIGINS
    assert "https://app.linkific.in" in s_str.CORS_ORIGINS
    assert "*" not in s_str.CORS_ORIGINS
