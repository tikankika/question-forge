"""Project configuration utilities.

Reads project folder configuration (mqg_folders.json) from qti-core or environment.
"""

import json
import os
from pathlib import Path
from typing import List

# Import QTI_GENERATOR_PATH from wrappers
from ..wrappers import QTI_GENERATOR_PATH


class ConfigError(Exception):
    """Configuration-related errors."""
    pass


def _is_listable_md(f: Path) -> bool:
    """Whether a markdown file should be listed (skip hidden, README, _archive)."""
    return (
        not f.name.startswith('.')
        and 'README' not in f.name
        and '_archive' not in str(f)
    )


def get_config_path() -> Path:
    """Get path to mqg_folders.json configuration.

    Priority:
        1. QF_PROJECTS_CONFIG environment variable
        2. QTI-Generator default location

    Returns:
        Path to configuration file.

    Raises:
        ConfigError: If no valid configuration found.
    """
    # 1. Check environment variable
    env_path = os.environ.get("QF_PROJECTS_CONFIG")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path

    # 2. Fall back to QTI-Generator location
    qti_config = QTI_GENERATOR_PATH / "config" / "mqg_folders.json"
    if qti_config.exists():
        return qti_config

    # 3. No config found
    raise ConfigError(
        "No project configuration found. Either:\n"
        "  1. Set QF_PROJECTS_CONFIG environment variable, or\n"
        "  2. Ensure QTI-Generator config exists at:\n"
        f"     {qti_config}"
    )


def load_config() -> dict:
    """Load project configuration."""
    config_path = get_config_path()

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {config_path}: {e}")
    except Exception as e:
        raise ConfigError(f"Failed to read {config_path}: {e}")


def list_projects(include_files: bool = False) -> dict:
    """List configured project folders with status.

    Args:
        include_files: If True, count markdown files in each folder.

    Returns:
        Dictionary with projects, default_output_dir, count, config_path.
    """
    config_path = get_config_path()
    config = load_config()

    projects = []
    for i, folder in enumerate(config.get('folders', []), 1):
        path = Path(folder['path']).expanduser()
        exists = path.exists()

        project = {
            'index': i,
            'name': folder['name'],
            'path': str(path),
            'exists': exists,
            'language': folder.get('default_language', 'sv'),
            'description': folder.get('description', ''),
        }

        if include_files and exists:
            md_files = [f for f in path.rglob("*.md") if _is_listable_md(f)]
            project['md_file_count'] = len(md_files)

        projects.append(project)

    return {
        'projects': projects,
        'default_output_dir': config.get('default_output_dir'),
        'count': len(projects),
        'config_path': str(config_path)
    }


def get_project_files(project_path: str) -> List[dict]:
    """List markdown files in a project folder."""
    path = Path(project_path).expanduser()
    if not path.exists():
        return []

    files = []
    for md_file in path.rglob("*.md"):
        if not _is_listable_md(md_file):
            continue

        files.append({
            'path': str(md_file),
            'relative_path': str(md_file.relative_to(path)),
            'name': md_file.name,
            'mtime': md_file.stat().st_mtime
        })

    files.sort(key=lambda x: x['relative_path'])
    return files
