"""Tests for the Python course-vault detector.

Mirrors the TypeScript detectCourseRoot (qf-scaffolding course_vault.ts). The
cross-language contract (ADR_qf_ts_material_flow Decision 5) is the RULE, not the
code: "walk up to the nearest project_state.json" — two implementations, one spec.
"""

import pytest

from qf_pipeline.utils.course_vault import detect_course_root


def _course(tmp_path, *segs):
    d = tmp_path.joinpath(*segs)
    d.mkdir(parents=True, exist_ok=True)
    return d


def test_finds_course_root_from_nested_project(tmp_path):
    course = _course(tmp_path, "Courses", "Biologi", "BIOG200x")
    (course / "project_state.json").write_text("{}")
    project = _course(tmp_path, "Courses", "Biologi", "BIOG200x", "Exams", "Formativa", "q1")
    assert detect_course_root(str(project)) == str(course)


def test_returns_none_standalone(tmp_path):
    project = _course(tmp_path, "standalone")
    (project / "session.yaml").write_text("session: {}")  # QF marker, not a course
    assert detect_course_root(str(project)) is None


def test_returns_project_itself_when_course_root(tmp_path):
    course = _course(tmp_path, "c")
    (course / "project_state.json").write_text("{}")
    assert detect_course_root(str(course)) == str(course)


def test_returns_nearest_ancestor(tmp_path):
    outer = _course(tmp_path, "outer")
    (outer / "project_state.json").write_text("{}")
    inner = _course(tmp_path, "outer", "inner")
    (inner / "project_state.json").write_text("{}")
    project = _course(tmp_path, "outer", "inner", "Exams", "q")
    assert detect_course_root(str(project)) == str(inner)


def test_respects_max_depth(tmp_path):
    course = _course(tmp_path, "a")
    (course / "project_state.json").write_text("{}")
    deep = _course(tmp_path, "a", "b", "c", "d", "e")
    assert detect_course_root(str(deep), max_depth=2) is None
    assert detect_course_root(str(deep), max_depth=8) == str(course)
