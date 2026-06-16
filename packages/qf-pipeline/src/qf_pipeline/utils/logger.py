"""Pipeline logging utility.

Unified logging for QuestionForge (RFC-001).
All logs go to logs/session.jsonl (shared by qf-pipeline and qf-scaffolding).
"""

import fcntl
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# Schema version per RFC-001
SCHEMA_VERSION = 1


def _read_session_id(project_path: Path) -> str:
    """Read session_id from session.yaml.

    Args:
        project_path: Project directory containing session.yaml

    Returns:
        Session ID string, or "unknown" if not found
    """
    try:
        import yaml
        session_yaml = project_path / "session.yaml"
        if session_yaml.exists():
            data = yaml.safe_load(session_yaml.read_text())
            return data.get("session", {}).get("id", "unknown")
    except Exception:
        pass
    return "unknown"


def log_action(
    project_path: Path,
    step: str,
    message: str,
    data: dict = None,
    level: str = "info"
):
    """Log action to logs/session.jsonl (backward-compatible wrapper).

    This is a wrapper around log_event for backwards compatibility.
    Automatically reads session_id from session.yaml.

    Args:
        project_path: Project directory containing log files
        step: Tool/step name (e.g., "step0_start", "step2_validate")
        message: Human-readable message (becomes 'event' field)
        data: Optional structured data for JSON log
        level: Log level (debug, info, warn, error). Default: "info"
    """
    if project_path is None:
        return

    project_path = Path(project_path)

    # Auto-read session_id from session.yaml
    session_id = _read_session_id(project_path)

    # Filter out 'project_path' from data to avoid duplication
    safe_data = {k: v for k, v in (data or {}).items() if k != 'project_path'}

    log_event(
        project_path=project_path,
        session_id=session_id,
        tool=step,
        event=message,
        level=level,
        data=safe_data if safe_data else None
    )


def log_event(
    project_path: Path,
    session_id: str,
    tool: str,
    event: str,
    level: str = "info",
    data: Optional[Dict[str, Any]] = None,
    duration_ms: Optional[int] = None,
    parent_id: Optional[str] = None,
    mcp: str = "qf-pipeline"
) -> None:
    """Log event to logs/session.jsonl (RFC-001 compliant).

    This is the shared logging format used by both qf-pipeline and qf-scaffolding.
    Thread-safe with file locking.

    Args:
        project_path: Project directory
        session_id: UUID linking all events in a session
        tool: Tool name (e.g., "step0_start", "load_stage")
        event: Event type (e.g., "session_start", "tool_end")
        level: Log level (debug, info, warn, error). Default: "info"
        data: Optional structured data
        duration_ms: Optional operation duration in milliseconds
        parent_id: Optional parent event ID for hierarchical logging
        mcp: MCP name (default: "qf-pipeline")
    """
    if project_path is None:
        return

    project_path = Path(project_path)
    logs_dir = project_path / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Build log entry per RFC-001 schema
    log_entry = {
        "ts": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "v": SCHEMA_VERSION,
        "session_id": session_id,
        "mcp": mcp,
        "tool": tool,
        "event": event,
        "level": level,
    }

    # Add optional fields
    if data:
        log_entry["data"] = data
    if duration_ms is not None:
        log_entry["duration_ms"] = duration_ms
    if parent_id:
        log_entry["parent_id"] = parent_id

    # Append to session.jsonl (shared log) with file locking
    session_log = logs_dir / "session.jsonl"
    with open(session_log, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def get_session_state(project_path: Path) -> Dict[str, Any]:
    """Read session.jsonl and determine current state for resumption.

    Args:
        project_path: Project directory

    Returns:
        Dict with session state info
    """
    log_file = Path(project_path) / "logs" / "session.jsonl"

    if not log_file.exists():
        return {"status": "no_session", "events": 0}

    events = []
    try:
        with open(log_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
    except Exception as e:
        return {"status": "error", "error": str(e)}

    if not events:
        return {"status": "empty", "events": 0}

    # Find last completed stage/tool
    last_complete = None
    for e in reversed(events):
        if e.get("event") in ("stage_complete", "tool_end"):
            if e.get("data", {}).get("success", True):
                last_complete = e
                break

    # Count errors
    errors = [e for e in events if e.get("level") == "error"]

    return {
        "status": "resumable",
        "total_events": len(events),
        "last_activity": events[-1].get("ts") if events else None,
        "last_complete": last_complete,
        "error_count": len(errors),
        "errors": errors[-5:] if errors else []  # Last 5 errors
    }
