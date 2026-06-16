"""Wrapper for validate_mqg_format from QTI-Generator-for-Inspera.

Provides clean functions for validating markdown quiz format.
"""

from ..errors import ValidationError

# Import from QTI-Generator (path configured in __init__.py)
from validate_mqg_format import validate_content


def validate_markdown(content: str) -> dict:
    """Validate markdown content format.

    Args:
        content: Markdown content to validate.

    Returns:
        Dictionary with:
        {
            'valid': bool,
            'issues': [
                {
                    'level': str,           # 'ERROR', 'WARNING', 'INFO'
                    'question_num': int,    # Question number (1-indexed)
                    'question_id': str,     # Question identifier
                    'message': str,         # Issue description
                    'line_num': int         # Line number in source
                },
                ...
            ]
        }

    Raises:
        ValidationError: If validation process fails.
    """
    try:
        is_valid, issues = validate_content(content)

        return {
            "valid": is_valid,
            "issues": [
                {
                    "level": getattr(i, "level", "ERROR"),
                    "question_num": getattr(i, "question_num", None),
                    "question_id": getattr(i, "question_id", None),
                    "message": getattr(i, "message", str(i)),
                    "line_num": getattr(i, "line_num", None),
                }
                for i in issues
            ],
        }
    except Exception as e:
        raise ValidationError(f"Validation failed: {e}", source_error=e)


def validate_file(file_path: str) -> dict:
    """Validate a markdown file.

    Args:
        file_path: Path to the markdown file.

    Returns:
        Validation result dictionary.

    Raises:
        ValidationError: If file cannot be read or validation fails.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        result = validate_markdown(content)
        result["file_path"] = file_path
        return result
    except FileNotFoundError:
        raise ValidationError(f"File not found: {file_path}")
    except Exception as e:
        raise ValidationError(f"Failed to validate file {file_path}: {e}", source_error=e)


def get_error_count(validation_result: dict) -> dict:
    """Count issues by level from validation result.

    Args:
        validation_result: Result from validate_markdown().

    Returns:
        Dictionary with counts: {'errors': int, 'warnings': int, 'info': int}
    """
    issues = validation_result.get("issues", [])
    return {
        "errors": sum(1 for i in issues if i.get("level") == "ERROR"),
        "warnings": sum(1 for i in issues if i.get("level") == "WARNING"),
        "info": sum(1 for i in issues if i.get("level") == "INFO"),
    }
