#!/usr/bin/env python3
"""
Tests for filter logic in AssessmentTestGenerator.

Verifies: OR within categories, AND between categories.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generator.assessment_test_generator import AssessmentTestGenerator, SectionConfig


QUESTIONS = [
    {'identifier': 'Q001', 'title': 'Q1', 'tags': ['Remember', 'Easy', 'Cellbiologi'], 'points': 1},
    {'identifier': 'Q002', 'title': 'Q2', 'tags': ['Understand', 'Easy', 'Cellbiologi'], 'points': 1},
    {'identifier': 'Q003', 'title': 'Q3', 'tags': ['Remember', 'Medium', 'Evolution'], 'points': 2},
    {'identifier': 'Q004', 'title': 'Q4', 'tags': ['Apply', 'Hard', 'Cellbiologi'], 'points': 3},
    {'identifier': 'Q005', 'title': 'Q5', 'tags': ['Understand', 'Medium', 'Evolution'], 'points': 2},
]


@pytest.mark.unit
class TestFilterLogic:

    def setup_method(self):
        self.gen = AssessmentTestGenerator()

    def _ids(self, results):
        return [q['identifier'] for q in results]

    def test_single_bloom_filter(self):
        section = SectionConfig(name="T", filter_bloom=['Remember'])
        results = self.gen._filter_questions(QUESTIONS, section)
        assert self._ids(results) == ['Q001', 'Q003']

    def test_multiple_bloom_or(self):
        """OR within Bloom: Remember OR Understand."""
        section = SectionConfig(name="T", filter_bloom=['Remember', 'Understand'])
        results = self.gen._filter_questions(QUESTIONS, section)
        assert set(self._ids(results)) == {'Q001', 'Q002', 'Q003', 'Q005'}

    def test_bloom_and_difficulty(self):
        """AND between categories: (Remember OR Understand) AND Easy."""
        section = SectionConfig(name="T", filter_bloom=['Remember', 'Understand'], filter_difficulty=['Easy'])
        results = self.gen._filter_questions(QUESTIONS, section)
        assert set(self._ids(results)) == {'Q001', 'Q002'}

    def test_bloom_difficulty_and_custom(self):
        """AND across all three: Bloom AND Difficulty AND Custom."""
        section = SectionConfig(
            name="T",
            filter_bloom=['Remember', 'Understand'],
            filter_difficulty=['Easy'],
            filter_custom=['Cellbiologi']
        )
        results = self.gen._filter_questions(QUESTIONS, section)
        assert set(self._ids(results)) == {'Q001', 'Q002'}

    def test_points_filter(self):
        section = SectionConfig(name="T", filter_points=[1, 2])
        results = self.gen._filter_questions(QUESTIONS, section)
        assert set(self._ids(results)) == {'Q001', 'Q002', 'Q003', 'Q005'}

    def test_no_filters_returns_all(self):
        section = SectionConfig(name="T")
        results = self.gen._filter_questions(QUESTIONS, section)
        assert len(results) == 5
