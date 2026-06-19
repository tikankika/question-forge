"""Regression tests for two latent bugs found during the /simplify review.

Both branches could not run before the fix:

1. ``pipeline_router.handle_pipeline_route`` imported ``Step3AutoFixer`` from
   ``step3_autofix`` where the class is actually named ``Step3AutoFix`` — the
   ``file_path``-only branch raised ``ImportError``.
2. ``session_manager.SessionManager.create_session`` generated a timestamp-based
   project name with ``datetime.now()`` but the module never imported
   ``datetime`` — the auto-naming branch raised ``NameError``.
"""

import re

import pytest

import qf_pipeline.utils.session_manager as sm
from qf_pipeline.tools.pipeline_router import handle_pipeline_route


@pytest.mark.asyncio
async def test_pipeline_route_resolves_step3_class_from_file_path(tmp_path):
    """The file_path-only branch must resolve the real Step3AutoFix class."""
    md = tmp_path / "questions.md"
    md.write_text(
        "# Q001\n"
        "^type multiple_choice_single\n"
        "^identifier Q001\n"
        "^points 1\n",
        encoding="utf-8",
    )

    # Before the fix this raised ImportError (Step3AutoFixer does not exist).
    result = await handle_pipeline_route({"file_path": str(md)})

    assert "route" in result


def test_create_session_setup_generates_timestamp_name(tmp_path, monkeypatch):
    """The setup entry point auto-names the project via datetime (was NameError)."""
    # Isolate the central-methodology copy, which writes outside tmp_path.
    monkeypatch.setattr(
        sm,
        "ensure_central_methodology",
        lambda: {"action": "skipped", "message": "test", "files_copied": 0},
    )

    manager = sm.SessionManager()

    # Before the fix this raised NameError (datetime not imported).
    result = manager.create_session(output_folder=str(tmp_path), entry_point="setup")

    assert result["success"], result
    name = re.sub(r".*/", "", result["project_path"])
    assert re.fullmatch(r"project_\d{8}_\d{6}", name), name
