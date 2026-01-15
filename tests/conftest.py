import os
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _get_env_or_skip(var_name):
    """Get environment variable or skip test if not set."""
    value = os.getenv(var_name)
    if not value:
        pytest.skip(f"{var_name} not set in environment")
    return value


@pytest.fixture
def eclipse_credentials():
    """Return Eclipse API credentials from environment."""
    return {
        "usr": _get_env_or_skip("ECLIPSE_USER"),
        "pwd": _get_env_or_skip("ECLIPSE_PWD"),
    }


@pytest.fixture
def eclipse_client(eclipse_credentials):
    """Return authenticated EclipseAPI client."""
    from orionapi import EclipseAPI
    return EclipseAPI(**eclipse_credentials)


@pytest.fixture
def orion_credentials():
    """Return Orion API credentials from environment."""
    return {
        "usr": _get_env_or_skip("ORION_USER"),
        "pwd": _get_env_or_skip("ORION_PWD"),
    }


@pytest.fixture
def orion_client(orion_credentials):
    """Return authenticated OrionAPI client."""
    from orionapi import OrionAPI
    return OrionAPI(**orion_credentials)
