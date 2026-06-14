"""Wrapper for ResourceManager from QTI-Generator-for-Inspera.

Provides clean functions for handling media resources (images, PDFs, etc.)
referenced in quiz questions.
"""

from pathlib import Path
from typing import List, Optional

from .errors import ResourceError

# Import from QTI-Generator (path configured in __init__.py)
from src.generator.resource_manager import ResourceManager, ResourceIssue


def validate_resources(
    input_file: str,
    questions: List[dict],
    media_dir: Optional[str] = None,
    strict: bool = False,
) -> dict:
    """Validate media resources referenced in questions.

    Args:
        input_file: Path to the markdown file (for relative path resolution).
        questions: List of parsed question dictionaries.
        media_dir: Optional media directory path. Auto-detects if None.
        strict: If True, treat warnings as errors.

    Returns:
        Dictionary with:
        {
            'valid': bool,           # True if no errors (or warnings in strict mode)
            'issues': [
                {
                    'level': str,           # 'ERROR', 'WARNING', 'INFO'
                    'resource_path': str,   # Path to the resource
                    'question_id': str,     # Question identifier
                    'message': str,         # Issue description
                    'fix_suggestion': str   # Optional fix suggestion
                },
                ...
            ],
            'error_count': int,
            'warning_count': int
        }

    Raises:
        ResourceError: If validation process fails.
    """
    try:
        rm = ResourceManager(
            input_file=Path(input_file),
            output_dir=Path("."),  # Not used for validation
            media_dir=Path(media_dir) if media_dir else None,
            strict=strict,
        )

        issues = rm.validate_resources(questions)

        error_count = sum(1 for i in issues if i.level == "ERROR")
        warning_count = sum(1 for i in issues if i.level == "WARNING")

        # In strict mode, warnings also count as invalid
        is_valid = error_count == 0 and (not strict or warning_count == 0)

        return {
            "valid": is_valid,
            "issues": [
                {
                    "level": i.level,
                    "resource_path": i.resource_path,
                    "question_id": i.question_id,
                    "message": i.message,
                    "fix_suggestion": i.fix_suggestion,
                }
                for i in issues
            ],
            "error_count": error_count,
            "warning_count": warning_count,
        }
    except Exception as e:
        raise ResourceError(f"Resource validation failed: {e}", source_error=e)


def prepare_output_structure(
    input_file: str,
    output_dir: str,
    quiz_name: str,
    media_dir: Optional[str] = None,
) -> dict:
    """Prepare output directory structure for QTI package.

    Args:
        input_file: Path to the markdown file.
        output_dir: Path to output directory.
        quiz_name: Name for the quiz (used for folder naming).
        media_dir: Optional media directory path.

    Returns:
        Dictionary with:
        {
            'quiz_dir': str,    # Path to created quiz directory
            'success': bool
        }

    Raises:
        ResourceError: If directory creation fails.
    """
    try:
        rm = ResourceManager(
            input_file=Path(input_file),
            output_dir=Path(output_dir),
            media_dir=Path(media_dir) if media_dir else None,
        )

        quiz_dir = rm.prepare_output_structure(quiz_name)

        return {
            "quiz_dir": str(quiz_dir),
            "success": True,
        }
    except Exception as e:
        raise ResourceError(f"Failed to prepare output structure: {e}", source_error=e)


def copy_resources(
    input_file: str,
    output_dir: str,
    questions: List[dict],
    media_dir: Optional[str] = None,
) -> dict:
    """Copy media resources to output directory with question ID prefixes.

    Args:
        input_file: Path to the markdown file.
        output_dir: Path to output directory.
        questions: List of parsed question dictionaries.
        media_dir: Optional media directory path.

    Returns:
        Dictionary with:
        {
            'copied': {original_name: renamed_name, ...},
            'count': int,
            'success': bool
        }

    Raises:
        ResourceError: If copying fails.
    """
    try:
        rm = ResourceManager(
            input_file=Path(input_file),
            output_dir=Path(output_dir),
            media_dir=Path(media_dir) if media_dir else None,
        )

        copied = rm.copy_resources(questions, Path(output_dir))

        return {
            "copied": copied,
            "count": len(copied),
            "success": True,
        }
    except Exception as e:
        raise ResourceError(f"Failed to copy resources: {e}", source_error=e)


def get_supported_formats() -> List[str]:
    """Get list of supported media file formats.

    Returns:
        List of supported file extensions (e.g., ['.png', '.jpg', ...])
    """
    return list(ResourceManager.SUPPORTED_FORMATS)


def get_max_file_size_mb() -> int:
    """Get maximum file size limit in MB (Inspera limit).

    Returns:
        Maximum file size in megabytes.
    """
    return ResourceManager.MAX_FILE_SIZE_MB
