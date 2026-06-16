"""
Resource Manager for QTI Generator

Centralized resource management for QTI generation.
Handles validation, organisation, and copying of media resources (images, PDFs, etc.).

Features:
- Early resource validation before XML generation
- Auto-detection of media directories (resources/, images/, same dir)
- Nextcloud path support with tilde expansion
- Question ID prefix renaming for better organisation
- Clear error messages with fix suggestions

Author: QTI Generator Team
Created: 2025-11-10
Version: 1.0.0
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ResourceIssue:
    """
    Represents a resource validation issue.

    Attributes:
        level: Severity level ('ERROR', 'WARNING', 'INFO')
        resource_path: Path to the problematic resource
        question_id: Optional question identifier for context
        message: Human-readable error message
        fix_suggestion: Optional suggestion for fixing the issue
    """
    level: str
    resource_path: str
    question_id: Optional[str]
    message: str
    fix_suggestion: Optional[str] = None

    def __str__(self) -> str:
        """Format issue for display."""
        context = f" (Question: {self.question_id})" if self.question_id else ""
        suggestion = f"\n  → Fix: {self.fix_suggestion}" if self.fix_suggestion else ""
        return f"{self.level}: {self.message}{context}{suggestion}"


class ResourceManager:
    """
    Centralized resource management for QTI generation.

    Responsibilities:
    1. Validate resources before generation (existence, format, size)
    2. Prepare output directory structure early
    3. Copy resources with question ID prefix renaming
    4. Support multiple path formats (local, Nextcloud, absolute)
    5. Provide clear error messages with fix suggestions

    Usage:
        rm = ResourceManager(
            input_file="quiz.md",
            output_dir="output/",
            media_dir=None,  # Auto-detect
            strict=False
        )

        # Validate resources
        issues = rm.validate_resources(questions)
        if has_errors(issues):
            print_issues(issues)
            sys.exit(1)

        # Prepare structure and copy resources
        quiz_dir = rm.prepare_output_structure("quiz_name")
        copied = rm.copy_resources(questions, quiz_dir)
    """

    # Supported image formats (Inspera compatible)
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.svg', '.gif'}

    # Inspera file size limit (5 MB)
    MAX_FILE_SIZE_MB = 5

    def __init__(self,
                 input_file: Path,
                 output_dir: Path,
                 media_dir: Optional[Path] = None,
                 strict: bool = False):
        """
        Initialize ResourceManager.

        Args:
            input_file: Path to input markdown file (supports /path/to/... paths)
            output_dir: Path to output directory
            media_dir: Optional media directory (auto-detect if None)
            strict: If True, treat warnings as errors

        Examples:
            # Local workflow
            rm = ResourceManager("quiz.md", "output/")

            # Nextcloud workflow
            rm = ResourceManager(
                "/path/to/course/.../quiz.md",
                "/path/to/export/"
            )
        """
        # Expand tilde and resolve paths
        self.input_file = Path(input_file).expanduser().resolve()
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.strict = strict

        # Auto-detect media directory if not provided
        if media_dir:
            self.media_dir = Path(media_dir).expanduser().resolve()
        else:
            self.media_dir = self._auto_detect_media_dir()

        logger.info(f"ResourceManager initialised:")
        logger.info(f"  Input file: {self.input_file}")
        logger.info(f"  Output dir: {self.output_dir}")
        logger.info(f"  Media dir: {self.media_dir}")
        logger.info(f"  Strict mode: {self.strict}")

    def _auto_detect_media_dir(self) -> Path:
        """
        Auto-detect media directory using search order.

        Search order:
        1. ./resources/ (Nextcloud convention)
        2. ./images/ (common convention)
        3. Same directory as input file (fallback)

        Returns:
            Path to detected media directory

        Examples:
            # If input is /path/to/.../quiz.md
            # Searches:
            #   1. /path/to/.../resources/
            #   2. /path/to/.../images/
            #   3. /path/to/.../
        """
        candidates = [
            self.input_file.parent / "resources",
            self.input_file.parent / "images",
            self.input_file.parent
        ]

        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                logger.info(f"Auto-detected media directory: {candidate}")
                return candidate

        # Default fallback: same directory as input file
        fallback = self.input_file.parent
        logger.warning(f"No media directory found, using fallback: {fallback}")
        return fallback

    def validate_resources(self, questions: List[Dict]) -> List[ResourceIssue]:
        """
        Validate all resources referenced in questions.

        Validation checks:
        - File existence
        - File format (must be in SUPPORTED_FORMATS)
        - File size (must be < MAX_FILE_SIZE_MB)
        - Filename validity (no special characters, spaces)

        Args:
            questions: List of parsed question dictionaries

        Returns:
            List of ResourceIssue objects (errors, warnings, info)

        Example:
            issues = rm.validate_resources(questions)

            for issue in issues:
                if issue.level == 'ERROR':
                    print(f"❌ {issue}")
                elif issue.level == 'WARNING':
                    print(f"⚠️  {issue}")
        """
        issues = []
        seen_resources = set()  # Track to avoid duplicate checks

        logger.info(f"Validating resources for {len(questions)} questions...")

        for question in questions:
            question_id = question.get('identifier', 'UNKNOWN')
            resources = self._extract_resources(question)

            for resource_path in resources:
                # Skip if already validated
                if resource_path in seen_resources:
                    continue
                seen_resources.add(resource_path)

                full_path = (self.media_dir / resource_path).resolve()

                # Security: prevent path traversal outside media directory
                try:
                    full_path.relative_to(self.media_dir.resolve())
                except ValueError:
                    issues.append(ResourceIssue(
                        level='ERROR',
                        resource_path=resource_path,
                        question_id=question_id,
                        message=f"Path traversal blocked: {resource_path}",
                        fix_suggestion="Resource paths must not contain '../' or reference files outside the media directory"
                    ))
                    continue

                # Check 1: File existence
                if not full_path.exists():
                    issues.append(ResourceIssue(
                        level='ERROR',
                        resource_path=resource_path,
                        question_id=question_id,
                        message=f"Resource not found: {resource_path}",
                        fix_suggestion=f"Check media directory: {self.media_dir}\n"
                                     f"  Expected full path: {full_path}"
                    ))
                    continue  # Skip further checks if file doesn't exist

                # Check 2: File format validation
                file_ext = full_path.suffix.lower()
                if file_ext not in self.SUPPORTED_FORMATS:
                    level = 'ERROR' if self.strict else 'WARNING'
                    issues.append(ResourceIssue(
                        level=level,
                        resource_path=resource_path,
                        question_id=question_id,
                        message=f"Unsupported format: {file_ext}",
                        fix_suggestion=f"Convert to supported format: {', '.join(self.SUPPORTED_FORMATS)}\n"
                                     f"  Recommended: .png (best compatibility)"
                    ))

                # Check 3: File size validation (Inspera limit: 5MB)
                try:
                    size_bytes = full_path.stat().st_size
                    size_mb = size_bytes / (1024 * 1024)

                    if size_mb > self.MAX_FILE_SIZE_MB:
                        level = 'ERROR' if self.strict else 'WARNING'
                        issues.append(ResourceIssue(
                            level=level,
                            resource_path=resource_path,
                            question_id=question_id,
                            message=f"File too large: {size_mb:.2f}MB (limit: {self.MAX_FILE_SIZE_MB}MB)",
                            fix_suggestion="Compress image or reduce dimensions\n"
                                         f"  Tools: ImageOptim, TinyPNG, or Photoshop 'Save for Web'"
                        ))
                    elif size_mb > (self.MAX_FILE_SIZE_MB * 0.8):  # 80% of limit
                        issues.append(ResourceIssue(
                            level='INFO',
                            resource_path=resource_path,
                            question_id=question_id,
                            message=f"File approaching size limit: {size_mb:.2f}MB",
                            fix_suggestion="Consider compressing to ensure fast loading"
                        ))
                except OSError as e:
                    issues.append(ResourceIssue(
                        level='WARNING',
                        resource_path=resource_path,
                        question_id=question_id,
                        message=f"Cannot read file size: {e}",
                        fix_suggestion="Check file permissions"
                    ))

                # Check 4: Filename validation (REMOVED - automatic sanitization handles this)
                # Filenames are automatically sanitized during copy_resources()
                # - Spaces → underscores
                # - Swedish/Nordic chars → transliterated (å→a, ä→a, ö→o)
                # - French chars → transliterated (é→e, ç→c, etc.)
                # - Special chars → removed
                # - Uppercase → lowercase
                # No need to warn about issues that are automatically fixed

        logger.info(f"Validation complete: {len(issues)} issues found")
        return issues

    def prepare_output_structure(self, quiz_name: str) -> Path:
        """
        Create output directory structure.

        Creates:
        - output/{quiz_name}/
        - output/{quiz_name}/resources/

        Args:
            quiz_name: Name of the quiz (used for directory name)

        Returns:
            Path to quiz output directory

        Example:
            quiz_dir = rm.prepare_output_structure("EXAMPLE_COURSE_Evolution_v8")
            # Creates: output/EXAMPLE_COURSE_Evolution_v8/
            #          output/EXAMPLE_COURSE_Evolution_v8/resources/
        """
        quiz_dir = self.output_dir / quiz_name
        resources_dir = quiz_dir / "resources"

        # Create directories (parents=True for nested paths, exist_ok=True to avoid errors)
        quiz_dir.mkdir(parents=True, exist_ok=True)
        resources_dir.mkdir(exist_ok=True)

        logger.info(f"Prepared output structure:")
        logger.info(f"  Quiz directory: {quiz_dir}")
        logger.info(f"  Resources directory: {resources_dir}")

        return quiz_dir

    def copy_resources(self, questions: List[Dict], quiz_dir: Path) -> Dict[str, str]:
        """
        Copy all resources to output directory with question ID prefix renaming.

        Naming convention:
            Original: virus_structure.png
            Question ID: HS_Q014
            Renamed: HS_Q014_virus_structure.png
            Format: {question_id}_{original_filename}

        Args:
            questions: List of parsed question dictionaries
            quiz_dir: Path to quiz output directory

        Returns:
            Mapping dictionary: original_path → renamed_filename

        Side effects:
            - Copies files to quiz_dir/resources/
            - Generates quiz_dir/resource_mapping.json

        Example:
            copied = rm.copy_resources(questions, quiz_dir)
            # copied = {
            #   "virus.png": "HS_Q014_virus.png",
            #   "bacteria.png": "GGM_Q005_bacteria.png"
            # }

            # Generated: quiz_dir/resource_mapping.json
        """
        import shutil
        import json

        resources_dir = quiz_dir / "resources"
        copied = {}

        logger.info(f"Copying resources for {len(questions)} questions...")

        for question in questions:
            question_id = question.get('identifier', 'UNKNOWN')
            resources = self._extract_resources(question)

            for resource_path in resources:
                # Skip if already copied
                if resource_path in copied:
                    continue

                src = (self.media_dir / resource_path).resolve()

                # Security: prevent path traversal outside media directory
                try:
                    src.relative_to(self.media_dir.resolve())
                except ValueError:
                    logger.error(f"Path traversal blocked: {resource_path}")
                    continue

                # Check if source file exists
                if not src.exists():
                    logger.warning(f"Resource not found, skipping: {resource_path}")
                    continue

                # Generate renamed filename with question ID prefix
                # Apply sanitization to remove problematic characters
                original_name = Path(resource_path).name
                sanitized_name = self.sanitize_filename(original_name)
                renamed_name = f"{question_id}_{sanitized_name}"
                dst = resources_dir / renamed_name

                # Log sanitization if filename changed
                if sanitized_name != original_name:
                    logger.info(f"Sanitized: {original_name} → {sanitized_name}")

                try:
                    # Copy file with metadata preservation
                    shutil.copy2(src, dst)
                    copied[resource_path] = renamed_name
                    logger.info(f"Copied: {resource_path} → {renamed_name}")
                except Exception as e:
                    logger.error(f"Failed to copy {resource_path}: {e}")

        # Save mapping to JSON file for reference
        mapping_file = quiz_dir / "resource_mapping.json"
        try:
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(copied, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved resource mapping: {mapping_file}")
        except Exception as e:
            logger.error(f"Failed to save mapping file: {e}")

        logger.info(f"Resource copying complete: {len(copied)} files copied")
        return copied

    def _extract_resources(self, question: Dict) -> List[str]:
        """
        Extract all resource paths from a question.

        Handles:
        - Images in question text (explicit 'image' field)
        - Hotspot background images
        - GraphicGapMatch background images
        - Match question images (stems/options)
        - Inline images in text (markdown ![](filename))
        - Images in feedback (all feedback types)

        Args:
            question: Parsed question dictionary

        Returns:
            List of unique resource file paths (relative to media_dir)

        Example:
            resources = rm._extract_resources(question)
            # returns: ["virus_structure.png", "bacteria_cell.png"]
        """
        import re

        resources = []

        # 1. Extract from explicit 'image' field
        # Used by: Hotspot, GraphicGapMatch, and questions with Image section
        if 'image' in question and question['image']:
            img = question['image']
            if isinstance(img, dict):
                # Fallback chain matches xml_generator.py:543
                path = img.get('path', img.get('file', ''))
                if path:
                    resources.append(path)
            elif isinstance(img, str):
                resources.append(img)

        # 2. Extract inline markdown images from question_text
        # Pattern: ![alt text](filename.png)
        if 'question_text' in question and question['question_text']:
            text = question['question_text']
            markdown_images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', text)
            for alt, path in markdown_images:
                if path:
                    resources.append(path)

        # 3. Extract images from feedback sections
        # Feedback can contain: general, correct, incorrect, option_specific
        if 'feedback' in question and question['feedback']:
            feedback = question['feedback']

            # Check text feedback types (general, correct, incorrect)
            for feedback_type in ['general', 'correct', 'incorrect']:
                if feedback_type in feedback and feedback[feedback_type]:
                    text = feedback[feedback_type]
                    markdown_images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', text)
                    for alt, path in markdown_images:
                        if path:
                            resources.append(path)

            # Check option-specific feedback (dict of option_id: feedback_text)
            if 'option_specific' in feedback and isinstance(feedback['option_specific'], dict):
                for option_id, feedback_text in feedback['option_specific'].items():
                    if feedback_text:
                        markdown_images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', feedback_text)
                        for alt, path in markdown_images:
                            if path:
                                resources.append(path)

        # 4. Extract images from Match question premises and responses
        # Match questions can have markdown images in left/right column text
        if 'premises' in question and question['premises']:
            for premise in question['premises']:
                if 'text' in premise and premise['text']:
                    markdown_images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', premise['text'])
                    for alt, path in markdown_images:
                        if path:
                            resources.append(path)

        if 'match_responses' in question and question['match_responses']:
            for response in question['match_responses']:
                if 'text' in response and response['text']:
                    markdown_images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', response['text'])
                    for alt, path in markdown_images:
                        if path:
                            resources.append(path)

        # 5. Remove duplicates and empty strings, preserve order
        seen = set()
        unique_resources = []
        for resource in resources:
            if resource and resource not in seen:
                seen.add(resource)
                unique_resources.append(resource)

        return unique_resources

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for cross-platform compatibility.

        Removes problematic characters that cause validation warnings,
        ensuring filenames work across all systems (Windows, macOS, Linux)
        and meet Inspera requirements.

        Rules applied:
        1. Transliterate Swedish/Nordic chars: å→a, ä→a, ö→o, ø→o
        2. Transliterate French chars: é→e, è→e, ç→c, etc.
        3. Convert to lowercase for consistency
        4. Replace spaces with underscores
        5. Remove special characters (keep only: a-z, 0-9, _, -, .)
        6. Collapse multiple underscores to single
        7. Trim underscores from start/end
        8. Preserve file extension

        Args:
            filename: Original filename to sanitize

        Returns:
            Sanitized filename safe for all platforms

        Examples:
            >>> sanitize_filename("Cellens_beståndsdelar.png")
            'cellens_bestansdelar.png'

            >>> sanitize_filename("Virus DNA struktur (v2).jpg")
            'virus_dna_struktur_v2.jpg'

            >>> sanitize_filename("Étude française.svg")
            'etude_francaise.svg'

            >>> sanitize_filename("perfect_name.png")
            'perfect_name.png'  # No changes needed
        """
        import re
        import os

        # Split filename into name and extension
        name, ext = os.path.splitext(filename)

        # Swedish/Nordic character transliteration
        # å, ä, ö, ø (Swedish, Danish, Norwegian)
        swedish_trans = str.maketrans('åäöøÅÄÖØ', 'aaooAAOO')
        name = name.translate(swedish_trans)

        # French character transliteration
        # é, è, ê, ë, ç, ù, û, ü, ô, à, â
        french_trans = str.maketrans(
            'éèêëçùûüôàâÉÈÊËÇÙÛÜÔÀÂ',
            'eeeecuuuoaaEEEECUUUOAA'
        )
        name = name.translate(french_trans)

        # Convert to lowercase for consistency
        name = name.lower()

        # Replace spaces with underscores
        name = name.replace(' ', '_')

        # Remove special characters
        # Keep only: letters (a-z), numbers (0-9), underscore (_), hyphen (-), dot (.)
        name = re.sub(r'[^a-z0-9_\-.]', '', name)

        # Collapse multiple underscores into single underscore
        name = re.sub(r'_+', '_', name)

        # Trim underscores from start and end
        name = name.strip('_')

        # Truncate long filenames to prevent issues
        # Max 50 chars for base name (leaves room for question_id prefix)
        # Total with prefix will be ~80 chars max (Windows/Inspera safe)
        MAX_BASE_LENGTH = 50
        if len(name) > MAX_BASE_LENGTH:
            original_length = len(name)
            name = name[:MAX_BASE_LENGTH].rstrip('_-')
            logger.warning(
                f"Truncated long filename from {original_length} to {MAX_BASE_LENGTH} chars"
            )

        # Reconstruct with lowercase extension
        return name + ext.lower()


# Module-level helper functions

def has_errors(issues: List[ResourceIssue]) -> bool:
    """Check if any issues are ERROR level."""
    return any(issue.level == 'ERROR' for issue in issues)


def has_warnings(issues: List[ResourceIssue]) -> bool:
    """Check if any issues are WARNING level."""
    return any(issue.level == 'WARNING' for issue in issues)


def print_issues(issues: List[ResourceIssue], show_info: bool = False) -> None:
    """
    Print validation issues in a user-friendly format.

    Args:
        issues: List of ResourceIssue objects
        show_info: If True, also show INFO level messages
    """
    if not issues:
        print("✓ No validation issues found")
        return

    error_count = sum(1 for i in issues if i.level == 'ERROR')
    warning_count = sum(1 for i in issues if i.level == 'WARNING')
    info_count = sum(1 for i in issues if i.level == 'INFO')

    print(f"\n{'='*70}")
    print("RESOURCE VALIDATION REPORT")
    print(f"{'='*70}")
    print(f"Errors: {error_count}, Warnings: {warning_count}, Info: {info_count}\n")

    for issue in issues:
        if issue.level == 'ERROR':
            print(f"❌ {issue}\n")
        elif issue.level == 'WARNING':
            print(f"⚠️  {issue}\n")
        elif show_info and issue.level == 'INFO':
            print(f"ℹ️  {issue}\n")

    print(f"{'='*70}\n")
