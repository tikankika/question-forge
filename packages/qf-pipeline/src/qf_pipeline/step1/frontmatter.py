"""
YAML Frontmatter Management for Step 1.

Handles adding, updating, and removing YAML frontmatter from markdown files.
Frontmatter tracks session progress for resumability and Obsidian compatibility.
"""

import re
import yaml
from typing import Optional, Dict, Any

from ..utils.timestamp import get_timestamp


def create_progress_dict(
    session_id: str,
    total_questions: int,
    current_question: int = 1,
    current_question_id: str = "Q001",
    status: str = "in_progress",
    questions_completed: int = 0,
    questions_skipped: int = 0,
    questions_deleted: int = 0,
    issues_fixed: int = 0
) -> Dict[str, Any]:
    """Create a progress dictionary for frontmatter."""
    now = get_timestamp()
    return {
        "step1_progress": {
            "session_id": session_id,
            "total_questions": total_questions,
            "current_question": current_question,
            "current_question_id": current_question_id,
            "status": status,
            "started_at": now,
            "last_updated": now,
            "questions_completed": questions_completed,
            "questions_skipped": questions_skipped,
            "questions_deleted": questions_deleted,
            "issues_fixed": issues_fixed
        }
    }


def add_frontmatter(content: str, progress: Dict[str, Any]) -> str:
    """
    Add YAML frontmatter to content.

    Args:
        content: Markdown content without frontmatter
        progress: Progress dictionary to add

    Returns:
        Content with frontmatter prepended
    """
    # Check if frontmatter already exists
    if has_frontmatter(content):
        return update_frontmatter(content, progress)

    # Create YAML block
    yaml_content = yaml.dump(progress, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # Prepend frontmatter
    return f"---\n{yaml_content}---\n\n{content}"


def update_frontmatter(content: str, updates: Dict[str, Any]) -> str:
    """
    Update existing frontmatter with new values.

    Args:
        content: Markdown content with frontmatter
        updates: Dictionary of updates to merge

    Returns:
        Content with updated frontmatter
    """
    existing = parse_frontmatter(content)

    if existing is None:
        # No existing frontmatter, add new
        return add_frontmatter(content, updates)

    # Merge updates into existing
    if "step1_progress" in updates and "step1_progress" in existing:
        existing["step1_progress"].update(updates["step1_progress"])
        existing["step1_progress"]["last_updated"] = get_timestamp()
    else:
        existing.update(updates)

    # Remove old frontmatter and add updated
    content_without_fm = remove_frontmatter(content)
    return add_frontmatter(content_without_fm, existing)


def remove_frontmatter(content: str) -> str:
    """
    Remove YAML frontmatter from content.

    Args:
        content: Markdown content possibly with frontmatter

    Returns:
        Content without frontmatter
    """
    # Match frontmatter block: starts with ---, ends with ---
    pattern = r'^---\n.*?\n---\n+'
    result = re.sub(pattern, '', content, count=1, flags=re.DOTALL)
    return result.lstrip('\n')


def parse_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    """
    Parse YAML frontmatter from content.

    Args:
        content: Markdown content possibly with frontmatter

    Returns:
        Parsed frontmatter dict, or None if not found
    """
    # Match frontmatter block
    pattern = r'^---\n(.*?)\n---'
    match = re.match(pattern, content, flags=re.DOTALL)

    if not match:
        return None

    try:
        yaml_content = match.group(1)
        return yaml.safe_load(yaml_content)
    except yaml.YAMLError:
        return None


def has_frontmatter(content: str) -> bool:
    """Check if content has YAML frontmatter."""
    return content.startswith('---\n') and '\n---' in content[4:]


def get_content_without_frontmatter(content: str) -> str:
    """Get content body without frontmatter."""
    return remove_frontmatter(content)


def update_progress(
    content: str,
    current_question: Optional[int] = None,
    current_question_id: Optional[str] = None,
    questions_completed: Optional[int] = None,
    questions_skipped: Optional[int] = None,
    questions_deleted: Optional[int] = None,
    issues_fixed: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    """
    Convenience function to update specific progress fields.

    Args:
        content: Markdown content with frontmatter
        **kwargs: Fields to update

    Returns:
        Content with updated frontmatter
    """
    updates = {"step1_progress": {}}

    if current_question is not None:
        updates["step1_progress"]["current_question"] = current_question
    if current_question_id is not None:
        updates["step1_progress"]["current_question_id"] = current_question_id
    if questions_completed is not None:
        updates["step1_progress"]["questions_completed"] = questions_completed
    if questions_skipped is not None:
        updates["step1_progress"]["questions_skipped"] = questions_skipped
    if questions_deleted is not None:
        updates["step1_progress"]["questions_deleted"] = questions_deleted
    if issues_fixed is not None:
        updates["step1_progress"]["issues_fixed"] = issues_fixed
    if status is not None:
        updates["step1_progress"]["status"] = status

    if updates["step1_progress"]:
        return update_frontmatter(content, updates)

    return content
