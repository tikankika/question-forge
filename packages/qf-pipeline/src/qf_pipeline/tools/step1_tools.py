"""
Step 1: Minimal Safety Net

Vision A implementation - Step 1 is only used when:
1. Router returns STRUCTURAL errors that can't be auto-fixed
2. Step 3 fails to auto-fix
3. Unknown error types that need human decision

For most files: M5 → Step 2 → Step 3 → Step 4 (Step 1 skipped)

Date: 2026-01-28
Previous: 947 lines → Now: ~200 lines
"""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..step1.decision_logger import log_decision
from ..step1.frontmatter import add_frontmatter, remove_frontmatter, update_frontmatter


# =============================================================================
# Step 1 Minimal Tools
# =============================================================================

async def step1_review(
    file_path: str,
    errors: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Review structural errors that router sent to Step 1.

    Shows questions with errors and available actions.

    Args:
        file_path: Path to markdown file
        errors: Structural errors from pipeline_route (optional)

    Returns:
        Dict with questions, errors, and suggested actions
    """
    path = Path(file_path)
    if not path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    content = path.read_text(encoding='utf-8')

    # Parse questions (simple regex extraction)
    questions = _extract_questions(content)

    # Build review summary
    result = {
        "success": True,
        "file": str(path),
        "total_questions": len(questions),
        "questions_with_errors": [],
        "available_actions": [
            "step1_manual_fix(question_id, new_content) - Provide corrected content",
            "step1_delete(question_id) - Remove question from file",
            "step1_skip(question_id) - Skip for now, continue with others"
        ]
    }

    # Match errors to questions
    if errors:
        error_by_question = {}
        for err in errors:
            qid = err.get('question_id', 'unknown')
            if qid not in error_by_question:
                error_by_question[qid] = []
            error_by_question[qid].append(err)

        for qid, q_errors in error_by_question.items():
            result["questions_with_errors"].append({
                "question_id": qid,
                "errors": q_errors,
                "content_preview": _get_question_preview(questions.get(qid, ""))
            })

    return result


async def step1_manual_fix(
    file_path: str,
    question_id: str,
    new_content: str,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Apply manual fix when Step 3 auto-fix fails.

    Teacher provides the corrected question content.

    Args:
        file_path: Path to markdown file
        question_id: Question to fix (e.g., "Q001")
        new_content: Corrected question content
        reason: Optional reason for the fix

    Returns:
        Dict with success status and details
    """
    path = Path(file_path).resolve()

    # Security: verify file is within a project directory
    project_path = _get_project_path(path)
    if not project_path:
        return {"success": False, "error": "File must be within a project directory (pipeline/ or questions/ folder)"}

    if not path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    content = path.read_text(encoding='utf-8')

    # Find and replace question
    old_question = _find_question_by_id(content, question_id)
    if not old_question:
        return {"success": False, "error": f"Question not found: {question_id}"}

    # Replace content
    new_file_content = content.replace(old_question, new_content)

    # Save
    path.write_text(new_file_content, encoding='utf-8')

    # Log decision (project_path already resolved and validated above)
    if project_path:
        log_decision(
            project_path=project_path,
            session_id="manual",
            question_id=question_id,
            issue_type="manual_fix",
            issue_description=reason or "Manual fix applied",
            line_number=None,
            ai_suggestion={},
            teacher_decision="manual",
            applied_fix={"reason": reason, "content_length": len(new_content)},
        )

    return {
        "success": True,
        "question_id": question_id,
        "action": "manual_fix",
        "reason": reason,
        "file": str(path)
    }


async def step1_delete(
    file_path: str,
    question_id: str,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delete a question from the file.

    Use when question is unsalvageable or duplicate.

    Args:
        file_path: Path to markdown file
        question_id: Question to delete
        reason: Optional reason for deletion

    Returns:
        Dict with success status
    """
    path = Path(file_path).resolve()

    # Security: verify file is within a project directory
    project_path = _get_project_path(path)
    if not project_path:
        return {"success": False, "error": "File must be within a project directory (pipeline/ or questions/ folder)"}

    if not path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    content = path.read_text(encoding='utf-8')

    # Find question
    question = _find_question_by_id(content, question_id)
    if not question:
        return {"success": False, "error": f"Question not found: {question_id}"}

    # Remove question (including surrounding separators)
    new_content = _remove_question(content, question)

    # Save
    path.write_text(new_content, encoding='utf-8')

    # Log decision (project_path already resolved and validated above)
    if project_path:
        log_decision(
            project_path=project_path,
            session_id="manual",
            question_id=question_id,
            issue_type="deletion",
            issue_description=reason or "Question deleted",
            line_number=None,
            ai_suggestion={},
            teacher_decision="delete",
            applied_fix={"reason": reason},
        )

    return {
        "success": True,
        "question_id": question_id,
        "action": "deleted",
        "reason": reason,
        "file": str(path)
    }


async def step1_skip(
    question_id: str,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Skip a question for now.

    Question remains in file, move to next.

    Args:
        question_id: Question to skip
        reason: Optional reason for skipping

    Returns:
        Dict confirming skip
    """
    return {
        "success": True,
        "question_id": question_id,
        "action": "skipped",
        "reason": reason,
        "note": "Question unchanged, continue with others"
    }


# =============================================================================
# Helper Functions
# =============================================================================

def _extract_questions(content: str) -> Dict[str, str]:
    """Extract questions from markdown content."""
    questions = {}

    # Split by --- separators
    parts = re.split(r'\n---\n', content)

    for part in parts:
        # Find question ID (^identifier or in header)
        id_match = re.search(r'\^identifier\s+(\S+)', part)
        if not id_match:
            id_match = re.search(r'#.*?(Q\d+|[A-Z]+_[A-Z]+_Q\d+)', part)

        if id_match:
            qid = id_match.group(1)
            questions[qid] = part.strip()

    return questions


def _find_question_by_id(content: str, question_id: str) -> Optional[str]:
    """Find a specific question in content."""
    # Pattern to match question block
    pattern = rf'(---\n.*?\^identifier\s+{re.escape(question_id)}.*?(?=\n---|\Z))'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        return match.group(1)

    # Try alternative pattern (question ID in header)
    pattern = rf'(---\n.*?{re.escape(question_id)}.*?(?=\n---|\Z))'
    match = re.search(pattern, content, re.DOTALL)

    return match.group(1) if match else None


def _remove_question(content: str, question: str) -> str:
    """Remove question from content, cleaning up separators."""
    # Remove the question
    new_content = content.replace(question, '')

    # Clean up double separators
    new_content = re.sub(r'\n---\n\s*\n---\n', '\n---\n', new_content)

    # Clean up leading/trailing separators
    new_content = re.sub(r'^\s*---\s*\n', '', new_content)
    new_content = re.sub(r'\n---\s*$', '', new_content)

    return new_content.strip()


def _get_question_preview(content: str, max_lines: int = 5) -> str:
    """Get preview of question content."""
    lines = content.split('\n')[:max_lines]
    preview = '\n'.join(lines)
    if len(content.split('\n')) > max_lines:
        preview += '\n...'
    return preview


def _get_project_path(file_path: Path) -> Optional[Path]:
    """Derive project path from file location."""
    # If in pipeline/ or questions/, parent.parent is project
    if file_path.parent.name in ('pipeline', 'questions'):
        return file_path.parent.parent
    return None


