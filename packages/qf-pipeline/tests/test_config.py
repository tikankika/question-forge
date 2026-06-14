"""Tests for utils/config.py"""

import pytest
from qf_pipeline.utils.config import list_projects, get_project_files, ConfigError


def test_list_projects_returns_dict():
    """list_projects should return dict with expected keys."""
    result = list_projects()
    assert 'projects' in result
    assert 'count' in result
    assert 'config_path' in result


def test_list_projects_includes_status():
    """Each project should have exists status."""
    result = list_projects()
    for p in result['projects']:
        assert 'exists' in p
        assert isinstance(p['exists'], bool)


def test_list_projects_with_files():
    """include_files should add md_file_count."""
    result = list_projects(include_files=True)
    for p in result['projects']:
        if p['exists']:
            assert 'md_file_count' in p
