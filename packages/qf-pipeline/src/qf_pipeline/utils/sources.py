"""Sources management for qf-pipeline.

Handles sources.yaml - a shared file updated by both qf-pipeline and qf-scaffolding.
Uses file locking for thread-safe writes.
"""

import fcntl
import yaml
from pathlib import Path
from typing import Any, Dict, List

from .timestamp import get_timestamp


def generate_source_id(existing_count: int) -> str:
    """Generate sequential source ID.

    Args:
        existing_count: Number of existing sources

    Returns:
        Sequential ID like src001, src002, etc.
    """
    return f"src{existing_count + 1:03d}"


def create_empty_sources_yaml(
    project_path: Path,
    created_by: str = "qf-pipeline:step0_start"
) -> Path:
    """Create empty sources.yaml with metadata.

    Args:
        project_path: Project directory
        created_by: Tool identifier that created the file

    Returns:
        Path to created sources.yaml
    """
    sources_file = project_path / "sources.yaml"

    data = {
        "metadata": {
            "created_at": get_timestamp(),
            "created_by": created_by,
            "last_updated": get_timestamp(),
            "last_updated_by": created_by,
        },
        "sources": []
    }

    with open(sources_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

    return sources_file


def update_sources_yaml(
    project_path: Path,
    new_sources: List[Dict[str, Any]],
    updated_by: str = "qf-pipeline",
    append: bool = True
) -> Dict[str, Any]:
    """Update sources.yaml thread-safe.

    Args:
        project_path: Project directory
        new_sources: List of new sources to add. Each source should have:
            - path: str (required) - path to source file
            - type: str (optional) - type of source (lecture_transcript, etc)
            - location: str (optional) - where file is stored (nextcloud, local, etc)
            - metadata: dict (optional) - additional metadata
        updated_by: Tool identifier (e.g., "qf-pipeline:step0_start")
        append: True=add to existing, False=replace all

    Returns:
        dict with success status and updated sources count
    """
    sources_file = project_path / "sources.yaml"

    # Create if doesn't exist
    if not sources_file.exists():
        create_empty_sources_yaml(project_path, created_by=updated_by)

    try:
        with open(sources_file, 'r+', encoding='utf-8') as f:
            # Lock file for thread-safety
            fcntl.flock(f, fcntl.LOCK_EX)

            try:
                data = yaml.safe_load(f) or {}

                # Ensure structure exists
                if "metadata" not in data:
                    data["metadata"] = {
                        "created_at": get_timestamp(),
                        "created_by": updated_by,
                    }
                if "sources" not in data:
                    data["sources"] = []

                # Process new sources
                existing_count = len(data["sources"])
                processed_sources = []
                for idx, source in enumerate(new_sources):
                    processed = {
                        "id": source.get("id") or generate_source_id(existing_count + idx),
                        "path": source["path"],
                        "location": source.get("location", "local"),
                        "type": source.get("type", "unknown"),
                        "added_at": get_timestamp(),
                        "added_by": updated_by,
                    }

                    # Add optional metadata
                    if "metadata" in source:
                        processed["metadata"] = source["metadata"]
                    if "discovered_in" in source:
                        processed["discovered_in"] = source["discovered_in"]
                    if "referenced_in" in source:
                        processed["referenced_in"] = source["referenced_in"]

                    processed_sources.append(processed)

                # Update sources list
                if append:
                    data["sources"].extend(processed_sources)
                else:
                    data["sources"] = processed_sources

                # Update metadata
                data["metadata"]["last_updated"] = get_timestamp()
                data["metadata"]["last_updated_by"] = updated_by

                # Write back
                f.seek(0)
                f.truncate()
                yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

                return {
                    "success": True,
                    "sources_added": len(processed_sources),
                    "total_sources": len(data["sources"]),
                }
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def read_sources_yaml(project_path: Path) -> Dict[str, Any]:
    """Read sources.yaml.

    Args:
        project_path: Project directory

    Returns:
        dict with sources data or error
    """
    sources_file = project_path / "sources.yaml"

    if not sources_file.exists():
        return {
            "success": False,
            "error": "sources.yaml not found",
            "sources": []
        }

    try:
        with open(sources_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        return {
            "success": True,
            "metadata": data.get("metadata", {}),
            "sources": data.get("sources", []),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "sources": []
        }
