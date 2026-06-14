"""Tests for qf-pipeline wrappers.

These tests verify that the wrappers correctly interface with QTI-Generator-for-Inspera.
"""

import pytest
from pathlib import Path
import tempfile
import os

# Sample markdown content for testing
SAMPLE_MARKDOWN = '''---
test_metadata:
  title: Test Quiz
  description: A test quiz for validation
---

# Q001 Sample Multiple Choice Question
^question Q001
^type multiple_choice_single
^identifier MC_Q001
^points 1

@field: question_text
What is 2 + 2?
@end_field

@field: options
*A. 3
A. 4
A. 5
A. 6
@end_field

@field: feedback
@@field: general_feedback
The answer is 4.
@@end_field
@end_field
'''

SAMPLE_QUESTION_ONLY = '''# Q001 Test Question
^question Q001
^type multiple_choice_single
^identifier MC_TEST
^points 1

@field: question_text
Test question text
@end_field

@field: options
*A. Correct
A. Wrong
@end_field
'''


class TestParser:
    """Tests for parser wrapper."""

    def test_parse_markdown_returns_dict(self):
        """parse_markdown should return a dictionary."""
        from qf_pipeline.wrappers import parse_markdown

        result = parse_markdown(SAMPLE_MARKDOWN)
        assert isinstance(result, dict)

    def test_parse_markdown_has_questions(self):
        """parse_markdown should extract questions."""
        from qf_pipeline.wrappers import parse_markdown

        result = parse_markdown(SAMPLE_MARKDOWN)
        assert "questions" in result
        assert len(result["questions"]) >= 1

    def test_parse_markdown_has_metadata(self):
        """parse_markdown should extract metadata."""
        from qf_pipeline.wrappers import parse_markdown

        result = parse_markdown(SAMPLE_MARKDOWN)
        assert "metadata" in result

    def test_parse_question_single(self):
        """parse_question should return a single question dict."""
        from qf_pipeline.wrappers import parse_question

        result = parse_question(SAMPLE_QUESTION_ONLY)
        assert result is not None
        assert isinstance(result, dict)

    def test_parse_file_not_found(self):
        """parse_file should raise ParsingError for missing file."""
        from qf_pipeline.wrappers import parse_file, ParsingError

        with pytest.raises(ParsingError):
            parse_file("/nonexistent/path/to/file.md")


class TestGenerator:
    """Tests for generator wrapper."""

    def test_get_supported_types(self):
        """get_supported_types should return a list."""
        from qf_pipeline.wrappers import get_supported_types

        types = get_supported_types()
        assert isinstance(types, list)
        assert "multiple_choice_single" in types
        assert "multiple_response" in types
        assert len(types) >= 10

    # NOTE: get_generator, generate_xml, generate_all_xml were removed
    # in the /simplify review (archived wrappers cleanup). Use subprocess
    # to call qti-core scripts instead (RFC-012).


class TestValidator:
    """Tests for validator wrapper."""

    def test_validate_markdown_returns_dict(self):
        """validate_markdown should return validation result dict."""
        from qf_pipeline.wrappers import validate_markdown

        result = validate_markdown(SAMPLE_MARKDOWN)
        assert isinstance(result, dict)
        assert "valid" in result
        assert "issues" in result

    def test_validate_markdown_issues_format(self):
        """validate_markdown issues should have expected fields."""
        from qf_pipeline.wrappers import validate_markdown

        result = validate_markdown(SAMPLE_MARKDOWN)
        for issue in result.get("issues", []):
            assert "level" in issue
            assert "message" in issue


    # NOTE: TestPackager and TestResources removed — these tested
    # create_qti_package, get_supported_formats, get_max_file_size_mb,
    # validate_resources which were removed in /simplify (archived wrappers).

class TestResources:
    """Tests for resources error types."""

    def test_resource_error_inheritance(self):
        """ResourceError should inherit from WrapperError."""
        from qf_pipeline.wrappers import WrapperError, ResourceError

        assert issubclass(ResourceError, WrapperError)


class TestErrors:
    """Tests for error classes."""

    def test_wrapper_error_to_dict(self):
        """WrapperError should convert to dict."""
        from qf_pipeline.wrappers import WrapperError

        err = WrapperError("Test error", source_error=ValueError("source"))
        d = err.to_dict()
        assert d["error"] == "WrapperError"
        assert d["message"] == "Test error"
        assert "source" in d

    def test_error_inheritance(self):
        """Custom errors should inherit from WrapperError."""
        from qf_pipeline.wrappers import (
            WrapperError,
            ParsingError,
            GenerationError,
            PackagingError,
            ResourceError,
        )

        assert issubclass(ParsingError, WrapperError)
        assert issubclass(GenerationError, WrapperError)
        assert issubclass(PackagingError, WrapperError)
        assert issubclass(ResourceError, WrapperError)
