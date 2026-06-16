#!/usr/bin/env python3
"""
Tests for parse_selection_input function.

Verifies comma-separated and 'or'-separated input parsing.
"""

import pytest
import re
from typing import List


def parse_selection_input(input_str: str) -> List[int]:
    """Parse user selection input supporting both comma and 'or' separators."""
    if not input_str:
        return []

    normalized = input_str.lower().strip()
    parts = re.split(r'\s*or\s*', normalized)

    if len(parts) == 1:
        parts = [p.strip() for p in normalized.split(',')]

    selected = []
    for part in parts:
        part = part.strip()
        if part.isdigit():
            selected.append(int(part))

    return selected


@pytest.mark.unit
class TestParseSelectionInput:

    def test_or_separator(self):
        assert parse_selection_input("1 or 2") == [1, 2]

    def test_comma_separator(self):
        assert parse_selection_input("1,2") == [1, 2]

    def test_case_insensitive_or(self):
        assert parse_selection_input("1 OR 2") == [1, 2]

    def test_no_spaces_around_or(self):
        assert parse_selection_input("1or2") == [1, 2]

    def test_multiple_values_or(self):
        assert parse_selection_input("1 or 2 or 3") == [1, 2, 3]

    def test_multiple_values_comma(self):
        assert parse_selection_input("1,2,3") == [1, 2, 3]

    def test_empty_input(self):
        assert parse_selection_input("") == []

    def test_invalid_input(self):
        assert parse_selection_input("xyz") == []

    def test_single_value(self):
        assert parse_selection_input("1") == [1]

    def test_whitespace(self):
        assert parse_selection_input("  1 or 2  ") == [1, 2]
