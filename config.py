"""CLI configuration - shared with API."""

import os


def get_api_url() -> str:
    """Get API base URL from environment or default."""
    return os.getenv("OPENMEDICA_API_URL", "http://localhost:8000/api/v1")


def get_docs_directory() -> str:
    """Get default documents directory."""
    return os.getenv("OPENMEDICA_DOCS_DIR", "./docs")
