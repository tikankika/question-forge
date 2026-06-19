"""
Decision Logger for Step 1.

Logs every teacher decision to logs/step1_decisions.jsonl.
JSONL format (one JSON object per line) for easy analysis.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from ..utils.timestamp import get_timestamp


def _append_decision(project_path: Path, entry: Dict[str, Any]) -> None:
    """Append one entry to logs/step1_decisions.jsonl, creating logs/ if needed."""
    logs_dir = Path(project_path) / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "step1_decisions.jsonl"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def log_decision(
    project_path: Path,
    session_id: str,
    question_id: str,
    issue_type: str,
    issue_description: str,
    line_number: Optional[int],
    ai_suggestion: Dict[str, Any],
    teacher_decision: str,
    applied_fix: Optional[Dict[str, Any]],
    teacher_note: Optional[str] = None,
    pattern_id: Optional[str] = None,
    time_spent_seconds: Optional[float] = None
) -> None:
    """
    Log a teacher decision to step1_decisions.jsonl.

    Args:
        project_path: Path to project directory
        session_id: Current session ID
        question_id: Question being fixed (e.g., "Q007")
        issue_type: Type of structural issue
        issue_description: Human-readable description
        line_number: Line number in file (if known)
        ai_suggestion: The AI's suggested fix
        teacher_decision: "accept_ai", "modify", "manual", "skip", "delete"
        applied_fix: The fix that was actually applied
        teacher_note: Optional note from teacher
        pattern_id: Pattern that was used/updated
        time_spent_seconds: Time teacher spent on decision
    """
    entry = {
        "timestamp": get_timestamp(),
        "session_id": session_id,
        "question_id": question_id,
        "issue_type": issue_type,
        "issue_description": issue_description,
        "line_number": line_number,
        "ai_suggestion": ai_suggestion,
        "teacher_decision": teacher_decision,
        "applied_fix": applied_fix,
        "teacher_note": teacher_note,
        "pattern_id": pattern_id,
        "time_spent_seconds": time_spent_seconds
    }
    _append_decision(project_path, entry)


def log_session_start(
    project_path: Path,
    session_id: str,
    source_file: str,
    total_questions: int,
    detected_format: str
) -> None:
    """Log session start event."""
    entry = {
        "timestamp": get_timestamp(),
        "session_id": session_id,
        "event": "session_start",
        "source_file": source_file,
        "total_questions": total_questions,
        "detected_format": detected_format
    }
    _append_decision(project_path, entry)


def log_session_complete(
    project_path: Path,
    session_id: str,
    status: str,
    questions_completed: int,
    questions_skipped: int,
    questions_deleted: int,
    issues_fixed: int,
    patterns_updated: int
) -> None:
    """Log session completion event."""
    entry = {
        "timestamp": get_timestamp(),
        "session_id": session_id,
        "event": "session_complete",
        "status": status,
        "result": {
            "questions_completed": questions_completed,
            "questions_skipped": questions_skipped,
            "questions_deleted": questions_deleted,
            "issues_fixed": issues_fixed,
            "patterns_updated": patterns_updated
        }
    }
    _append_decision(project_path, entry)


def log_navigation(
    project_path: Path,
    session_id: str,
    from_question: str,
    to_question: str,
    direction: str
) -> None:
    """Log navigation between questions."""
    entry = {
        "timestamp": get_timestamp(),
        "session_id": session_id,
        "event": "navigate",
        "from_question": from_question,
        "to_question": to_question,
        "direction": direction
    }
    _append_decision(project_path, entry)
