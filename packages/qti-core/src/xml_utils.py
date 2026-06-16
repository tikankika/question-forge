"""Shared XML utilities for qti-core."""


def escape_xml(text: str) -> str:
    """Escape special XML characters in text."""
    if not text:
        return ''
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))
