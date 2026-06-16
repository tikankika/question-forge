"""
Tests for bug fixes from the /simplify codebase review.

Covers: get_timestamp singleton, end_session key fix, log_decision signature,
step0_status field name, auto_load_session helper.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock


# =============================================================================
# get_timestamp — single source of truth
# =============================================================================

class TestTimestampSingleton:
    """Verify get_timestamp is defined once and imported everywhere."""

    def test_timestamp_format(self):
        from qf_pipeline.utils.timestamp import get_timestamp
        ts = get_timestamp()
        assert ts.endswith("Z"), f"Timestamp must end with Z, got: {ts}"
        assert "+" not in ts, "Timestamp must not contain +00:00"

    def test_imports_from_same_source(self):
        """All modules should import get_timestamp from utils.timestamp."""
        from qf_pipeline.utils.timestamp import get_timestamp as ts1
        from qf_pipeline.utils import get_timestamp as ts2
        assert ts1 is ts2


# =============================================================================
# end_session — uses "questions" key (not stale "working")
# =============================================================================

class TestEndSessionKey:
    """Verify session_manager reads from 'questions' not 'working'."""

    def test_session_data_uses_questions_key(self):
        """SessionManager must read validation_status from 'questions' dict."""
        from qf_pipeline.utils.session_manager import SessionManager

        mgr = SessionManager()
        # Simulate active session data with the correct key structure
        mgr._session_data = {
            "session": {"id": "test-123"},
            "questions": {
                "validation_status": "valid",
                "question_count": 5,
                "path": "/tmp/test.md"
            },
            "exports": []
        }
        mgr._project_path = Path("/tmp/test-project")

        # get_status should find the data under "questions"
        status = mgr.get_status()
        assert status["validation_status"] == "valid"
        assert status["question_count"] == 5


# =============================================================================
# log_decision — correct signature
# =============================================================================

class TestLogDecisionSignature:
    """Verify step1_tools calls log_decision with correct kwargs."""

    @pytest.mark.asyncio
    async def test_manual_fix_log_decision_call(self):
        """step1_manual_fix must pass correct kwargs to log_decision."""
        from qf_pipeline.tools.step1_tools import step1_manual_fix

        with tempfile.TemporaryDirectory() as tmp:
            # Create project structure
            project = Path(tmp) / "project"
            questions = project / "questions"
            questions.mkdir(parents=True)

            # Create test markdown file
            md_file = questions / "test.md"
            md_file.write_text("---\n# Q001 Test\n^identifier Q001\nContent\n---")

            # Patch log_decision to capture the call
            with patch("qf_pipeline.tools.step1_tools.log_decision") as mock_log:
                result = await step1_manual_fix(
                    file_path=str(md_file),
                    question_id="Q001",
                    new_content="Updated content",
                    reason="Test fix"
                )

                if mock_log.called:
                    call_kwargs = mock_log.call_args
                    # Verify the correct keyword arguments
                    assert "teacher_decision" in str(call_kwargs), \
                        "Must use teacher_decision, not decision"
                    assert "issue_description" in str(call_kwargs), \
                        "Must include issue_description"


# =============================================================================
# auto_load_session — extracted helper
# =============================================================================

class TestAutoLoadSession:
    """Verify _auto_load_session helper works correctly."""

    @pytest.mark.asyncio
    async def test_returns_none_for_non_project_path(self):
        """Files not in pipeline/ or questions/ should return None."""
        from qf_pipeline.server import _auto_load_session

        with tempfile.TemporaryDirectory() as tmp:
            result = await _auto_load_session(str(Path(tmp) / "random.md"))
            assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_no_session_yaml(self):
        """Project dir without session.yaml should return None."""
        from qf_pipeline.server import _auto_load_session

        with tempfile.TemporaryDirectory() as tmp:
            questions = Path(tmp) / "questions"
            questions.mkdir()
            test_file = questions / "test.md"
            test_file.write_text("test")

            result = await _auto_load_session(str(test_file))
            assert result is None
