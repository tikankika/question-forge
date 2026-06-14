"""Session management tools for qf-pipeline MCP.

Provides tools for creating and managing QF pipeline sessions.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.session_manager import SessionManager
from ..utils.url_fetcher import is_url, fetch_url_to_markdown

logger = logging.getLogger(__name__)

# Global session manager instance
_current_session: Optional[SessionManager] = None


def get_current_session() -> Optional[SessionManager]:
    """Get the current active session manager."""
    return _current_session


def set_current_session(session: Optional[SessionManager]) -> None:
    """Set the current active session manager."""
    global _current_session
    _current_session = session


async def start_session_tool(
    output_folder: str,
    source_file: Optional[str] = None,
    project_name: Optional[str] = None,
    entry_point: str = "pipeline",
    materials_folder: Optional[str] = None,
    initial_sources: Optional[List[Dict[str, Any]]] = None
) -> dict:
    """Start a new QF pipeline session.

    Creates project structure (RFC-013 v2.1):
        project_name/
        ├── materials/      ← Input (lectures, slides) - M1 reads
        ├── methodology/    ← Method guides (copied in Step 0)
        ├── preparation/    ← M1 + M2 output (foundation for questions)
        ├── questions/      ← Questions (M3 creates, M4/M5 edit)
        │   └── history/    ← Automatic backups per step
        ├── pipeline/       ← Step 1-3 working area
        │   └── history/    ← Backups
        ├── output/         ← Step 4 final output
        │   └── qti/        ← QTI packages (.zip)
        ├── logs/           ← Session logs (shared by both MCPs)
        ├── sources.yaml    ← Source tracking (updated by both MCPs)
        └── session.yaml    ← Session metadata

    Args:
        output_folder: Directory where project will be created
        source_file: Path to source file OR URL (required for m2/m3/m4/pipeline)
                    If URL is provided, content is fetched and saved as .md
        project_name: Optional project name (auto-generated if not provided)
        entry_point: One of "m1", "m2", "m3", "m4", "pipeline". Default: "pipeline"
        materials_folder: Path to folder with instructional materials (required for m1)
        initial_sources: Optional list of initial sources for sources.yaml
                        Each source should have: path, type (optional), location (optional)

    Returns:
        dict with success status, paths, and next_module
    """
    global _current_session

    # Check if source_file is a URL - if so, fetch it first
    fetched_from_url = None
    if source_file and is_url(source_file):
        logger.info(f"Detected URL as source_file: {source_file}")

        # Create temp directory for fetched file
        output_path = Path(output_folder).resolve()
        temp_materials = output_path / "_temp_fetched"

        success, message, local_path = await fetch_url_to_markdown(
            url=source_file,
            output_dir=temp_materials
        )

        if not success:
            return {
                "success": False,
                "error": {
                    "type": "url_fetch_error",
                    "message": f"Failed to fetch URL: {message}",
                    "url": source_file
                }
            }

        # Use the fetched file as source
        fetched_from_url = source_file
        source_file = str(local_path)
        logger.info(f"URL fetched to: {source_file}")

    manager = SessionManager()
    result = manager.create_session(
        output_folder=output_folder,
        source_file=source_file,
        project_name=project_name,
        entry_point=entry_point,
        materials_folder=materials_folder,
        initial_sources=initial_sources
    )

    if result.get("success"):
        _current_session = manager

        # Add URL info to result if fetched from URL
        if fetched_from_url:
            result["fetched_from_url"] = fetched_from_url
            result["message"] = (
                f"URL fetched and session started. "
                f"Source: {fetched_from_url}"
            )

            # Clean up temp directory
            try:
                temp_materials = Path(output_folder).resolve() / "_temp_fetched"
                if temp_materials.exists():
                    import shutil
                    shutil.rmtree(temp_materials)
            except Exception as e:
                logger.warning(f"Could not clean up temp dir: {e}")

    return result


async def get_session_status_tool(session_id: Optional[str] = None) -> dict:
    """Get status of current or specified session.

    Args:
        session_id: Optional session ID (uses current session if None)

    Returns:
        dict with session status and paths
    """
    if _current_session:
        return _current_session.get_status()

    return {
        "active": False,
        "message": "No active session. Use start_session to begin."
    }


async def end_session_tool(session_id: Optional[str] = None) -> dict:
    """End current session.

    Args:
        session_id: Optional session ID (uses current session if None)

    Returns:
        dict with session summary
    """
    global _current_session

    if not _current_session:
        return {
            "success": False,
            "error": {
                "type": "no_session",
                "message": "No active session to end"
            }
        }

    result = _current_session.end_session()
    _current_session = None
    return result


async def load_session_tool(project_path: str) -> dict:
    """Load an existing session from project path.

    Args:
        project_path: Path to existing project directory

    Returns:
        dict with loaded session info
    """
    global _current_session

    try:
        manager = SessionManager.load_from_path(project_path)
        _current_session = manager
        return {
            "success": True,
            **manager.get_status(),
            "message": f"Session loaded from {project_path}"
        }
    except FileNotFoundError as e:
        return {
            "success": False,
            "error": {
                "type": "session_not_found",
                "message": str(e)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": type(e).__name__,
                "message": str(e)
            }
        }
