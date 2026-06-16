#!/usr/bin/env python3
"""
Tests for src/error_handler.py module.

Tests error handling, suggestions, and fuzzy matching.
"""

import pytest
from src.error_handler import (
    ParsingError,
    ErrorSuggester,
    create_parsing_error
)


@pytest.mark.unit
def test_parsing_error_basic():
    """Test basic ParsingError creation."""
    error = ParsingError(
        message="Test error message",
        line_number=42,
        question_num=5,
        question_id="Q005"
    )

    error_str = str(error)
    assert "Test error message" in error_str
    assert "Line 42" in error_str
    assert "Question 5" in error_str
    assert "Q005" in error_str


@pytest.mark.unit
def test_parsing_error_with_suggestion():
    """Test ParsingError with suggestion."""
    error = ParsingError(
        message="Invalid field",
        suggestion="Try using 'field_name' instead"
    )

    error_str = str(error)
    assert "Invalid field" in error_str
    assert "💡 Suggestion:" in error_str
    assert "Try using 'field_name' instead" in error_str


@pytest.mark.unit
def test_parsing_error_expected_vs_found():
    """Test ParsingError with expected vs found comparison."""
    error = ParsingError(
        message="Format mismatch",
        expected="**Type:** multiple_choice_single",
        found="**Type**: multiple_choice"
    )

    error_str = str(error)
    assert "Expected:" in error_str
    assert "Found:" in error_str


@pytest.mark.unit
class TestErrorSuggester:
    """Tests for ErrorSuggester class."""

    def test_suggest_question_type_direct_match(self):
        """Test direct typo correction."""
        assert ErrorSuggester.suggest_question_type('multiple_choice') == 'multiple_choice_single'
        assert ErrorSuggester.suggest_question_type('multi_select') == 'multiple_response'
        assert ErrorSuggester.suggest_question_type('true_or_false') == 'true_false'

    def test_suggest_question_type_case_insensitive(self):
        """Test case-insensitive matching."""
        assert ErrorSuggester.suggest_question_type('MULTIPLE_CHOICE') == 'multiple_choice_single'
        assert ErrorSuggester.suggest_question_type('Multi_Choice') == 'multiple_choice_single'

    def test_suggest_question_type_fuzzy_match(self):
        """Test fuzzy matching for close typos."""
        # Close enough to match
        suggestion = ErrorSuggester.suggest_question_type('multiple_choise')  # typo in 'choice'
        assert suggestion == 'multiple_choice_single'

        suggestion = ErrorSuggester.suggest_question_type('true_fals')  # missing 'e'
        assert suggestion == 'true_false'

    def test_suggest_question_type_no_match(self):
        """Test that totally invalid types return None."""
        suggestion = ErrorSuggester.suggest_question_type('completely_invalid_xyz_123')
        assert suggestion is None

    def test_suggest_question_type_common_abbreviations(self):
        """Test common abbreviations."""
        assert ErrorSuggester.suggest_question_type('mcq') == 'multiple_choice_single'
        assert ErrorSuggester.suggest_question_type('tf') == 'true_false'
        assert ErrorSuggester.suggest_question_type('extended_text') == 'essay'

    def test_suggest_missing_section_multiple_choice(self):
        """Test suggestions for missing MC sections (v6.5 format)."""
        suggestion = ErrorSuggester.suggest_missing_section('multiple_choice_single', 'options')
        assert '@field: options' in suggestion
        assert 'A.' in suggestion

        suggestion = ErrorSuggester.suggest_missing_section('multiple_choice_single', 'answer')
        assert '@field: answer' in suggestion

    def test_suggest_missing_section_text_entry(self):
        """Test suggestions for text_entry sections (v6.5 format)."""
        suggestion = ErrorSuggester.suggest_missing_section('text_entry', 'blanks')
        assert '@field: blanks' in suggestion
        assert '@field: blank_1' in suggestion

    def test_suggest_missing_section_inline_choice(self):
        """Test suggestions for inline_choice sections (v6.5 format)."""
        suggestion = ErrorSuggester.suggest_missing_section('inline_choice', 'dropdown')
        assert '@field: dropdown' in suggestion

    def test_suggest_missing_section_match(self):
        """Test suggestions for match questions (v6.5 format)."""
        suggestion = ErrorSuggester.suggest_missing_section('match', 'pairs')
        assert '@field: pairs' in suggestion

    def test_suggest_invalid_metadata_type(self):
        """Test metadata suggestions for Type field (v6.5 format)."""
        suggestion = ErrorSuggester.suggest_invalid_metadata('Type')
        assert '@type:' in suggestion
        assert 'multiple_choice_single' in suggestion

    def test_suggest_invalid_metadata_identifier(self):
        """Test metadata suggestions for Identifier field (v6.5 format)."""
        suggestion = ErrorSuggester.suggest_invalid_metadata('Identifier')
        assert '@identifier:' in suggestion
        assert 'MC_Q001' in suggestion

    def test_suggest_invalid_metadata_points(self):
        """Test metadata suggestions for Points field (v6.5 format)."""
        suggestion = ErrorSuggester.suggest_invalid_metadata('Points')
        assert '@points:' in suggestion
        assert 'number' in suggestion.lower() or '2' in suggestion


@pytest.mark.unit
def test_create_parsing_error_auto_suggest():
    """Test create_parsing_error with auto-suggestion (v6.5 format)."""
    # Test Type field suggestion - uses v6.5 @type: format
    error = create_parsing_error(
        message="Missing @type field",
        line_num=10,
        question_num=2,
        question_id="Q002"
    )

    error_str = str(error)
    assert "Missing @type field" in error_str
    assert "💡 Suggestion:" in error_str
    assert "@type:" in error_str


@pytest.mark.unit
def test_create_parsing_error_no_auto_suggest():
    """Test create_parsing_error without auto-suggestion."""
    error = create_parsing_error(
        message="Custom error",
        auto_suggest=False
    )

    error_str = str(error)
    assert "Custom error" in error_str
    # Should not have automatic suggestion
    assert "💡" not in error_str or error_str.count("💡") == 0
