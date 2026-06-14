"""Tests for ensure_central_methodology (ADR-016).

The helper takes a workspace_root (where the snapshot lives), a source_dir
(the git-root methodology), and a repo_version. It copies on first run,
no-ops when versions match, surfaces update_available when local is older,
backs-up-and-overwrites on force_update, and refuses to clobber when local
is ahead.
"""

import json
from pathlib import Path

import pytest

from qf_pipeline.utils.methodology import ensure_central_methodology


def _make_source(tmp_path: Path) -> Path:
    """Build a minimal methodology/ tree (m1..m5 with one file each)."""
    src = tmp_path / "git-root" / "methodology"
    for module in ("m1", "m2", "m3", "m4", "m5"):
        (src / module).mkdir(parents=True)
        (src / module / "README.md").write_text(f"# {module}\n")
    return src


def test_creates_snapshot_when_missing(tmp_path):
    src = _make_source(tmp_path)
    ws = tmp_path / "nextcloud" / "QuestionForge"

    result = ensure_central_methodology(
        workspace_root=ws, source_dir=src, repo_version="0.1.0"
    )

    assert result["action"] == "created"
    assert (ws / "methodology" / "m1" / "README.md").exists()
    meta = json.loads((ws / "_meta" / "methodology_version.json").read_text())
    assert meta["version"] == "0.1.0"
    assert meta["from"].startswith("qf-pipeline")
    assert "copied_at" in meta


def test_unchanged_when_versions_match(tmp_path):
    src = _make_source(tmp_path)
    ws = tmp_path / "ws"
    ensure_central_methodology(workspace_root=ws, source_dir=src, repo_version="0.1.0")

    result = ensure_central_methodology(
        workspace_root=ws, source_dir=src, repo_version="0.1.0"
    )

    assert result["action"] == "unchanged"
    assert result["local_version"] == "0.1.0"


def test_update_available_when_local_older(tmp_path):
    src = _make_source(tmp_path)
    ws = tmp_path / "ws"
    ensure_central_methodology(workspace_root=ws, source_dir=src, repo_version="0.1.0")

    result = ensure_central_methodology(
        workspace_root=ws, source_dir=src, repo_version="0.2.0", force_update=False
    )

    assert result["action"] == "update_available"
    assert result["local_version"] == "0.1.0"
    assert result["repo_version"] == "0.2.0"
    # Snapshot untouched — still on old version
    meta = json.loads((ws / "_meta" / "methodology_version.json").read_text())
    assert meta["version"] == "0.1.0"


def test_force_update_backs_up_and_overwrites(tmp_path):
    src = _make_source(tmp_path)
    ws = tmp_path / "ws"
    ensure_central_methodology(workspace_root=ws, source_dir=src, repo_version="0.1.0")
    # Mutate snapshot so we can tell backup apart from new copy
    (ws / "methodology" / "m1" / "README.md").write_text("# LOCAL EDIT\n")

    result = ensure_central_methodology(
        workspace_root=ws, source_dir=src, repo_version="0.2.0", force_update=True
    )

    assert result["action"] == "updated"
    backup = Path(result["backup_path"])
    assert backup.exists() and backup.is_dir()
    assert (backup / "m1" / "README.md").read_text() == "# LOCAL EDIT\n"
    # Fresh snapshot is back to source content
    assert (ws / "methodology" / "m1" / "README.md").read_text() == "# m1\n"
    meta = json.loads((ws / "_meta" / "methodology_version.json").read_text())
    assert meta["version"] == "0.2.0"


def test_local_ahead_when_local_newer(tmp_path):
    src = _make_source(tmp_path)
    ws = tmp_path / "ws"
    ensure_central_methodology(workspace_root=ws, source_dir=src, repo_version="0.5.0")

    result = ensure_central_methodology(
        workspace_root=ws, source_dir=src, repo_version="0.2.0"
    )

    assert result["action"] == "local_ahead"
    # Snapshot untouched
    meta = json.loads((ws / "_meta" / "methodology_version.json").read_text())
    assert meta["version"] == "0.5.0"


def test_unchanged_when_no_version_file(tmp_path):
    src = _make_source(tmp_path)
    ws = tmp_path / "ws"
    (ws / "methodology").mkdir(parents=True)
    (ws / "methodology" / "hand-written.md").write_text("teacher edit\n")

    result = ensure_central_methodology(
        workspace_root=ws, source_dir=src, repo_version="0.1.0"
    )

    assert result["action"] == "unchanged"
    # Don't overwrite hand-created snapshot
    assert (ws / "methodology" / "hand-written.md").exists()


def test_workspace_root_defaults_to_env(tmp_path, monkeypatch):
    src = _make_source(tmp_path)
    default_ws = tmp_path / "from-env" / "QuestionForge"
    monkeypatch.setenv("QF_WORKSPACE", str(default_ws))

    result = ensure_central_methodology(source_dir=src, repo_version="0.1.0")

    assert result["action"] == "created"
    assert result["path"] == str(default_ws / "methodology")
