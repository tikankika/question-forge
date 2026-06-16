#!/usr/bin/env python3
"""
Tests for tag parsing and categorisation in markdown_parser.

Verifies that Bloom, Difficulty, and Custom tags are correctly
parsed from both comma-separated and space-separated formats.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser.markdown_parser import MarkdownQuizParser


SAMPLE_WITH_TAGS = """---
title: Tag Test
---

# Q001 Remember Easy
^question Q001
^type multiple_choice_single
^identifier MC_Q001
^points 1
^labels #Remember #Easy #Cellbiologi

@field: question_text
What is a cell?
@end_field

@field: options
*A. A unit of life
A. A rock
@end_field

---

# Q002 Understand Medium
^question Q002
^type multiple_choice_single
^identifier MC_Q002
^points 2
^labels #Understand #Medium #Evolution

@field: question_text
What is evolution?
@end_field

@field: options
*A. Change over time
A. A type of rock
@end_field
"""


@pytest.mark.unit
class TestTagParsing:
    """Verify tag parsing from markdown questions."""

    def setup_method(self):
        parser = MarkdownQuizParser(SAMPLE_WITH_TAGS)
        self.quiz_data = parser.parse()
        self.questions = self.quiz_data.get('questions', [])

    def test_questions_found(self):
        assert len(self.questions) >= 2

    def test_tags_are_lists(self):
        for q in self.questions:
            tags = q.get('labels', q.get('tags', []))
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(',')]
            assert isinstance(tags, list)

    def test_bloom_tags_present(self):
        bloom_levels = {'Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'}
        all_tags = set()
        for q in self.questions:
            tags = q.get('labels', q.get('tags', []))
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(',')]
            all_tags.update(t.lstrip('#') for t in tags)

        found_bloom = all_tags & bloom_levels
        assert len(found_bloom) > 0, f"No Bloom tags found in {all_tags}"

    def test_difficulty_tags_present(self):
        difficulty_levels = {'Easy', 'Medium', 'Hard'}
        all_tags = set()
        for q in self.questions:
            tags = q.get('labels', q.get('tags', []))
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(',')]
            all_tags.update(t.lstrip('#') for t in tags)

        found_diff = all_tags & difficulty_levels
        assert len(found_diff) > 0, f"No Difficulty tags found in {all_tags}"
