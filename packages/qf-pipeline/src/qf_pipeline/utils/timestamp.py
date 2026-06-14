"""Shared timestamp utility."""

from datetime import datetime, timezone


def get_timestamp() -> str:
    """Get current timestamp in ISO 8601 format with Z suffix."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
