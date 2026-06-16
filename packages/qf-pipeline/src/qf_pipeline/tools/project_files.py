"""
Project file tools for qf-pipeline MCP.

General-purpose file read/write within project directory.
Allows Claude to access ANY file within the project, not just
specific folders like materials/ or questions/.

Security: Only allows access within project_path (no path traversal)

Mirrors the TypeScript implementation in qf-scaffolding.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import os


def is_path_within_project(project_path: str, target_path: str) -> bool:
    """
    Validate that the resolved path is within project_path (prevent path traversal).

    Args:
        project_path: The root project directory
        target_path: The target path to validate

    Returns:
        True if target_path is within project_path, False otherwise
    """
    try:
        # Resolve to absolute paths
        project_resolved = Path(project_path).resolve()
        target_resolved = Path(target_path).resolve()

        # Check if target is relative to project
        target_resolved.relative_to(project_resolved)

        # Also check it's not the same as project_path
        if target_resolved == project_resolved:
            return False

        return True
    except ValueError:
        # relative_to() raises ValueError if not relative
        return False


async def read_project_file(
    project_path: str,
    relative_path: str
) -> Dict[str, Any]:
    """
    Read any file within the project directory.

    Args:
        project_path: Root project directory
        relative_path: Path relative to project_path, e.g. "output/questions.md"

    Returns:
        Dict with success status, content, and metadata
    """
    # Build full path
    full_path = Path(project_path) / relative_path

    # Security: Ensure path is within project
    if not is_path_within_project(project_path, str(full_path)):
        return {
            "success": False,
            "error": f"Security error: Path \"{relative_path}\" resolves outside project directory."
        }

    try:
        # Check if file exists
        if not full_path.exists():
            return {
                "success": False,
                "relative_path": relative_path,
                "error": f"File not found: {relative_path}"
            }

        # Check if it's a directory
        if full_path.is_dir():
            return {
                "success": False,
                "relative_path": relative_path,
                "error": f"Path is a directory, not a file: {relative_path}"
            }

        # Read file content
        content = full_path.read_text(encoding='utf-8')
        stats = full_path.stat()

        return {
            "success": True,
            "file_path": str(full_path),
            "relative_path": relative_path,
            "content": content,
            "size_bytes": stats.st_size
        }

    except Exception as e:
        return {
            "success": False,
            "relative_path": relative_path,
            "error": f"Failed to read file: {str(e)}"
        }


async def write_project_file(
    project_path: str,
    relative_path: str,
    content: str,
    create_dirs: bool = True,
    overwrite: bool = True
) -> Dict[str, Any]:
    """
    Write any file within the project directory.

    Args:
        project_path: Root project directory
        relative_path: Path relative to project_path
        content: Content to write
        create_dirs: Create parent directories if needed (default: True)
        overwrite: Overwrite if file exists (default: True)

    Returns:
        Dict with success status and metadata
    """
    # Build full path
    full_path = Path(project_path) / relative_path

    # Security: Ensure path is within project
    if not is_path_within_project(project_path, str(full_path)):
        return {
            "success": False,
            "error": f"Security error: Path \"{relative_path}\" resolves outside project directory."
        }

    try:
        # Check if file exists and overwrite is False
        if full_path.exists() and not overwrite:
            return {
                "success": False,
                "relative_path": relative_path,
                "error": f"File already exists: {relative_path}. Set overwrite=true to replace."
            }

        # Create parent directories if needed
        parent_dir = full_path.parent
        created_dirs = False

        if not parent_dir.exists():
            if create_dirs:
                parent_dir.mkdir(parents=True, exist_ok=True)
                created_dirs = True
            else:
                return {
                    "success": False,
                    "relative_path": relative_path,
                    "error": f"Parent directory does not exist: {parent_dir.name}. Set create_dirs=true to create."
                }

        # Write file
        full_path.write_text(content, encoding='utf-8')
        bytes_written = len(content.encode('utf-8'))

        return {
            "success": True,
            "file_path": str(full_path),
            "relative_path": relative_path,
            "bytes_written": bytes_written,
            "created_dirs": created_dirs
        }

    except Exception as e:
        return {
            "success": False,
            "relative_path": relative_path,
            "error": f"Failed to write file: {str(e)}"
        }


# Tool registration info for documentation
PROJECT_FILE_TOOLS = [
    {
        "name": "read_project_file",
        "description": "Read any file within a project directory. Security: prevents path traversal outside project.",
        "parameters": {
            "project_path": {"type": "string", "description": "Root project directory"},
            "relative_path": {"type": "string", "description": "Path relative to project_path, e.g. 'output/questions.md'"}
        }
    },
    {
        "name": "write_project_file",
        "description": "Write any file within a project directory. Creates parent dirs by default. Security: prevents path traversal.",
        "parameters": {
            "project_path": {"type": "string", "description": "Root project directory"},
            "relative_path": {"type": "string", "description": "Path relative to project_path"},
            "content": {"type": "string", "description": "Content to write"},
            "create_dirs": {"type": "boolean", "description": "Create parent directories if needed (default: true)", "optional": True},
            "overwrite": {"type": "boolean", "description": "Overwrite if file exists (default: true)", "optional": True}
        }
    }
]
