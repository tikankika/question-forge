#!/usr/bin/env python3
"""
Characterisation tests for MarkdownQuizParser.validate() required-header-field
validation (^type / ^identifier / ^points).

These lock the CURRENT behaviour (message + suggestion per branch) before the
table-driven refactor (parked refactor #2). They must stay green through the
refactor — they are the behaviour-preserving safety net, not new behaviour.

Each case isolates one field by keeping the other two valid, and asserts only on
errors whose `field` matches — so downstream parse/type errors do not interfere.
The CASES table below is itself the characterisation spec.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.parser.markdown_parser import MarkdownQuizParser  # noqa: E402


def make_md(
    type_line="^type multiple_choice_single",
    id_line="^identifier Q001",
    points_line="^points 1",
):
    """Build a single-question block; pass None to omit a field line."""
    lines = ["# Q001 Sample title"]
    for line in (type_line, id_line, points_line):
        if line is not None:
            lines.append(line)
    return "\n".join(lines) + "\n"


def field_errors(result, field):
    """(message, suggestion) pairs for errors on a given header field."""
    return [
        (e["message"], e["suggestion"])
        for e in result["errors"]
        if e.get("field") == field
    ]


# id → (make_md override, field, expected (message, suggestion) pairs)
CASES = [
    # ^type
    ("type_valid", {}, "type", []),
    ("type_colon", {"type_line": "^type: multiple_choice_single"}, "type", [(
        '^type has colon - QFMD v6.5 uses "^type value" not "^type: value"',
        "Remove the colon: ^type multiple_choice_single",
    )]),
    ("type_not_at_start", {"type_line": "prefix ^type multiple_choice_single"}, "type", [(
        "^type not at start of line - each metadata field must be on its own line",
        "Put ^type on its own line",
    )]),
    ("type_missing", {"type_line": None}, "type", [(
        "Missing ^type field",
        "Add: ^type multiple_choice_single (or other valid type)",
    )]),
    # ^identifier
    ("identifier_valid", {}, "identifier", []),
    ("identifier_colon", {"id_line": "^identifier: Q001"}, "identifier", [(
        '^identifier has colon - QFMD v6.5 uses "^identifier value" not "^identifier: value"',
        "Remove the colon: ^identifier Q001",
    )]),
    ("identifier_not_at_start", {"id_line": "prefix ^identifier Q001"}, "identifier", [(
        "^identifier not at start of line",
        "Put ^identifier on its own line",
    )]),
    ("identifier_missing", {"id_line": None}, "identifier", [(
        "Missing ^identifier field",
        "Add: ^identifier Q001",
    )]),
    # ^points
    ("points_valid", {}, "points", []),
    ("points_colon", {"points_line": "^points: 1"}, "points", [(
        '^points has colon - QFMD v6.5 uses "^points value" not "^points: value"',
        "Remove the colon: ^points 1",
    )]),
    ("points_not_at_start_or_invalid", {"points_line": "^points abc"}, "points", [(
        "^points not at start of line or invalid value",
        "Put ^points on its own line with integer value: ^points 1",
    )]),
    ("points_missing", {"points_line": None}, "points", [(
        "Missing ^points field",
        "Add: ^points 1",
    )]),
]


@pytest.mark.unit
@pytest.mark.parametrize(
    "overrides, field, expected",
    [pytest.param(o, f, e, id=cid) for cid, o, f, e in CASES],
)
def test_required_header_field_validation(overrides, field, expected):
    result = MarkdownQuizParser(make_md(**overrides)).validate()
    assert field_errors(result, field) == expected
