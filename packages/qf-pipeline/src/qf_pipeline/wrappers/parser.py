"""Wrapper for MarkdownQuizParser from QTI-Generator-for-Inspera.

Provides clean functions for parsing markdown quiz content into structured data.
"""

from typing import Optional

from .errors import ParsingError

# Import from QTI-Generator (path configured in __init__.py)
from src.parser.markdown_parser import MarkdownQuizParser


def parse_markdown(content: str) -> dict:
    """Parse markdown content into structured data.

    Args:
        content: Full markdown content with YAML frontmatter and questions.

    Returns:
        Dictionary with structure:
        {
            'metadata': {...},      # Test-level config from YAML frontmatter
            'questions': [...]      # List of parsed question dicts
        }

    Raises:
        ParsingError: If parsing fails.
    """
    try:
        parser = MarkdownQuizParser(content)
        return parser.parse()
    except Exception as e:
        raise ParsingError(f"Failed to parse markdown: {e}", source_error=e)


def parse_question(content: str) -> Optional[dict]:
    """Parse a single question block.

    Args:
        content: Markdown content containing one question.

    Returns:
        Parsed question dict, or None if no question found.

    Raises:
        ParsingError: If parsing fails.
    """
    try:
        parser = MarkdownQuizParser(content)
        result = parser.parse()
        if result.get("questions"):
            return result["questions"][0]
        return None
    except Exception as e:
        raise ParsingError(f"Failed to parse question: {e}", source_error=e)


def parse_file(file_path: str) -> dict:
    """Parse a markdown file.

    Args:
        file_path: Path to the markdown file.

    Returns:
        Dictionary with metadata and questions.

    Raises:
        ParsingError: If file cannot be read or parsed.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return parse_markdown(content)
    except FileNotFoundError:
        raise ParsingError(f"File not found: {file_path}")
    except Exception as e:
        raise ParsingError(f"Failed to parse file {file_path}: {e}", source_error=e)
