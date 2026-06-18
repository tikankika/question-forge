"""Shared XML utilities for qti-core."""

import re


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


_UNSAFE_IDENTIFIER_CHARS = re.compile(r'[^A-Za-z0-9_-]')


def sanitize_identifier(raw: str, fallback: str = "ID") -> str:
    """Reduce an identifier to a safe token of ``[A-Za-z0-9_-]``.

    QTI identifiers (e.g. the ``^identifier`` field) flow unescaped into XML
    attributes and into output filenames. Restricting them to this charset
    prevents both XML injection (no ``< > " & '``) and path traversal (no
    ``/`` ``\\`` ``.``), and keeps the value identical across the item XML,
    the manifest ``href`` and the on-disk filename. Disallowed characters are
    replaced with ``_``; an empty result falls back to ``fallback``.
    """
    if not raw:
        return fallback
    cleaned = _UNSAFE_IDENTIFIER_CHARS.sub('_', raw.strip())
    return cleaned or fallback
