"""Methodology distribution for qf-pipeline.

ADR-016: central, not per-project. A single snapshot of the git-root
`methodology/` is copied to `<QF_WORKSPACE>/methodology/` so Desktop (and
the teacher in Finder/Obsidian) can read it — Desktop cannot read from the
git checkout. Version metadata in `<QF_WORKSPACE>/_meta/methodology_version.json`
lets us detect drift and back up local edits before overwriting.
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any, Dict, Optional

# Git-root methodology lives 5 levels above this file:
# utils/methodology.py → qf_pipeline → src → qf-pipeline → packages → <git-root>
_GIT_ROOT_METHODOLOGY = Path(__file__).resolve().parents[5] / "methodology"
# Generic default; override with the QF_WORKSPACE environment variable.
_DEFAULT_WORKSPACE = Path.home() / "QuestionForge"


def _resolve_workspace(workspace_root: Optional[Path]) -> Path:
    if workspace_root is not None:
        return Path(workspace_root)
    env = os.environ.get("QF_WORKSPACE")
    return Path(env) if env else _DEFAULT_WORKSPACE


def _resolve_repo_version(repo_version: Optional[str]) -> str:
    if repo_version is not None:
        return repo_version
    try:
        return metadata.version("qf-pipeline")
    except metadata.PackageNotFoundError:
        return "unknown"


def _parse_version(v: str) -> tuple[int, ...]:
    try:
        return tuple(int(p) for p in v.split("."))
    except ValueError:
        return (0,)


def _copy_tree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.rglob("*"):
        if not item.is_file():
            continue
        rel = item.relative_to(src)
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)


def _write_version_file(meta_dir: Path, version: str) -> None:
    meta_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": version,
        "copied_at": datetime.now(timezone.utc).isoformat(),
        "from": f"qf-pipeline@v{version}",
    }
    (meta_dir / "methodology_version.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )


def ensure_central_methodology(
    workspace_root: Optional[Path] = None,
    source_dir: Optional[Path] = None,
    repo_version: Optional[str] = None,
    force_update: bool = False,
) -> Dict[str, Any]:
    """Ensure the central methodology snapshot is in place.

    Returns a dict with `action` in {created, unchanged, update_available,
    local_ahead, updated, failed}, plus `path`, version fields, and
    `message`. On `updated`, includes `backup_path`.
    """
    ws = _resolve_workspace(workspace_root)
    src = Path(source_dir) if source_dir is not None else _GIT_ROOT_METHODOLOGY
    version = _resolve_repo_version(repo_version)

    methodology_dir = ws / "methodology"
    meta_dir = ws / "_meta"
    version_file = meta_dir / "methodology_version.json"

    if not src.exists():
        return {
            "action": "failed",
            "path": str(methodology_dir),
            "repo_version": version,
            "message": f"Source methodology not found: {src}",
        }

    if not methodology_dir.exists():
        try:
            _copy_tree(src, methodology_dir)
            _write_version_file(meta_dir, version)
            return {
                "action": "created",
                "path": str(methodology_dir),
                "repo_version": version,
                "message": f"Central methodology created at {ws} (v{version}).",
            }
        except OSError as exc:
            return {
                "action": "failed",
                "path": str(methodology_dir),
                "repo_version": version,
                "message": f"Failed to create central methodology: {exc}",
            }

    # Snapshot exists — inspect version.
    local_version: Optional[str] = None
    if version_file.exists():
        try:
            local_version = json.loads(version_file.read_text())["version"]
        except (json.JSONDecodeError, KeyError, OSError):
            local_version = None

    if local_version is None:
        return {
            "action": "unchanged",
            "path": str(methodology_dir),
            "repo_version": version,
            "message": (
                f"Central methodology at {ws} has no version metadata; "
                "treating as hand-maintained — no changes made."
            ),
        }

    if local_version == version:
        return {
            "action": "unchanged",
            "path": str(methodology_dir),
            "local_version": local_version,
            "repo_version": version,
            "message": f"Central methodology up to date (v{local_version}).",
        }

    if _parse_version(local_version) > _parse_version(version):
        return {
            "action": "local_ahead",
            "path": str(methodology_dir),
            "local_version": local_version,
            "repo_version": version,
            "message": (
                f"Central methodology v{local_version} is newer than "
                f"qf-pipeline v{version}; no changes made."
            ),
        }

    # local < repo
    if not force_update:
        return {
            "action": "update_available",
            "path": str(methodology_dir),
            "local_version": local_version,
            "repo_version": version,
            "message": (
                f"Central methodology v{local_version}; qf-pipeline ships "
                f"v{version}. Re-run with force_update=true to overwrite "
                "(a backup will be made)."
            ),
        }

    timestamp = (
        datetime.now(timezone.utc).isoformat().replace(":", "-").replace(".", "-")
    )
    backup_path = ws / f"methodology.backup-{timestamp}"
    try:
        methodology_dir.rename(backup_path)
        _copy_tree(src, methodology_dir)
        _write_version_file(meta_dir, version)
        return {
            "action": "updated",
            "path": str(methodology_dir),
            "local_version": local_version,
            "repo_version": version,
            "backup_path": str(backup_path),
            "message": (
                f"Central methodology updated v{local_version} → v{version}. "
                f"Previous version backed up to {backup_path}."
            ),
        }
    except OSError as exc:
        return {
            "action": "failed",
            "path": str(methodology_dir),
            "local_version": local_version,
            "repo_version": version,
            "message": f"Force-update failed during backup or copy: {exc}",
        }
