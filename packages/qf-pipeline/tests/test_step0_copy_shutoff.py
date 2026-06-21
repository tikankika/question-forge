"""Tests for step0_add_file copy-shutdown in shared course-vault mode.

ADR_qf_ts_material_flow Decision 5: in a course vault, a file already INSIDE the
vault is referenced in place (location:"in_place", no copy); a file OUTSIDE the
vault is copied as before (location:"local").
"""

import asyncio

import yaml

from qf_pipeline.tools.step0_tools import step0_add_file


def _make_vault(tmp_path):
    """Create a course vault + a nested QF project; return (course_root, project)."""
    course = tmp_path / "Courses" / "Biologi" / "BIOG200x"
    course.mkdir(parents=True)
    (course / "project_state.json").write_text("{}")
    project = course / "Exams" / "Formativa" / "q1"
    project.mkdir(parents=True)
    return course, project


def _read_sources(project):
    f = project / "sources.yaml"
    return yaml.safe_load(f.read_text()) if f.exists() else None


def test_in_vault_file_is_referenced_not_copied(tmp_path):
    course, project = _make_vault(tmp_path)
    material = course / "Material" / "Klart" / "foto.md"
    material.parent.mkdir(parents=True)
    material.write_text("# Photosynthesis")

    res = asyncio.run(step0_add_file(str(project), str(material), file_type="materials"))

    assert res["success"] is True
    assert res["file_added"]["location"] == "in_place"
    # not copied into the project
    assert not (project / "materials" / "foto.md").exists()
    # registered as an in-place reference, path points into the vault
    sources = _read_sources(project)
    entries = sources["sources"] if isinstance(sources, dict) else sources
    assert any(
        e.get("location") == "in_place" and e.get("path") == "Material/Klart/foto.md"
        for e in (entries if isinstance(entries, list) else [])
    )


def test_outside_file_is_copied_as_before(tmp_path):
    course, project = _make_vault(tmp_path)
    external = tmp_path / "Downloads" / "lecture.md"
    external.parent.mkdir(parents=True)
    external.write_text("external")

    res = asyncio.run(step0_add_file(str(project), str(external), file_type="materials"))

    assert res["success"] is True
    assert res["file_added"].get("location", "local") == "local"
    # copied into the project's materials/
    assert (project / "materials" / "lecture.md").exists()


def test_standalone_project_copies_as_before(tmp_path):
    project = tmp_path / "standalone"
    project.mkdir()
    src = tmp_path / "src.md"
    src.write_text("x")

    res = asyncio.run(step0_add_file(str(project), str(src), file_type="materials"))

    assert res["success"] is True
    assert (project / "materials" / "src.md").exists()
