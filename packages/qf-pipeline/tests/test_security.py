"""
Security tests for qf-pipeline.

Verifies path traversal prevention, SSRF blocking, and info disclosure fixes.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from qf_pipeline.utils.url_fetcher import is_url, _is_private_ip


# =============================================================================
# SSRF Prevention — url_fetcher
# =============================================================================

class TestSSRFPrevention:
    """Verify that url_fetcher blocks SSRF attacks."""

    @pytest.mark.unit
    def test_http_rejected(self):
        """Plain HTTP URLs must be rejected (HTTPS only)."""
        assert is_url("http://example.com") is False

    @pytest.mark.unit
    def test_https_accepted(self):
        """HTTPS URLs must be accepted."""
        assert is_url("https://example.com") is True

    @pytest.mark.unit
    def test_empty_string(self):
        assert is_url("") is False

    @pytest.mark.unit
    def test_not_url(self):
        assert is_url("/path/to/file") is False

    @pytest.mark.unit
    def test_private_ip_localhost(self):
        """localhost must be detected as private."""
        assert _is_private_ip("localhost") is True

    @pytest.mark.unit
    def test_private_ip_127(self):
        """127.0.0.1 must be detected as private."""
        assert _is_private_ip("127.0.0.1") is True

    @pytest.mark.unit
    def test_private_ip_192_168(self):
        """192.168.x.x must be detected as private."""
        assert _is_private_ip("192.168.1.1") is True

    @pytest.mark.unit
    def test_private_ip_10(self):
        """10.x.x.x must be detected as private."""
        assert _is_private_ip("10.0.0.1") is True

    @pytest.mark.unit
    def test_private_ip_169_254(self):
        """169.254.169.254 (AWS metadata) must be detected as private."""
        assert _is_private_ip("169.254.169.254") is True

    @pytest.mark.unit
    def test_public_ip_allowed(self):
        """A known public hostname should not be flagged as private."""
        # dns.google resolves to 8.8.8.8/8.8.4.4
        assert _is_private_ip("dns.google") is False

    @pytest.mark.unit
    def test_unresolvable_hostname_blocked(self):
        """Unresolvable hostnames must be blocked (fail-closed)."""
        assert _is_private_ip("this.hostname.definitely.does.not.exist.invalid") is True


# =============================================================================
# Path Traversal — step0_add_file
# =============================================================================

class TestStep0PathTraversal:
    """Verify that step0_add_file blocks path traversal in target_folder."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_target_folder_traversal_blocked(self):
        """target_folder='../../etc' must be rejected."""
        from qf_pipeline.tools.step0_tools import step0_add_file

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            (project / "questions").mkdir()

            # Create a source file
            source = Path(tmp) / "test.md"
            source.write_text("test content")

            result = await step0_add_file(
                project_path=str(project),
                file_path=str(source),
                target_folder="../../escape"
            )

            assert result.get("success") is not True, "Traversal target_folder was allowed"
            error = result.get("error", {})
            if isinstance(error, dict):
                assert "security" in error.get("type", "").lower() or "traversal" in error.get("message", "").lower()


# =============================================================================
# Path Traversal — step1 tools
# =============================================================================

class TestStep1PathTraversal:
    """Verify that step1_manual_fix and step1_delete require project context."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_manual_fix_outside_project_blocked(self):
        """file_path not in a project directory must be rejected."""
        from qf_pipeline.tools.step1_tools import step1_manual_fix

        with tempfile.TemporaryDirectory() as tmp:
            # Create a file NOT in a pipeline/ or questions/ subfolder
            orphan = Path(tmp) / "orphan.md"
            orphan.write_text("some content")

            result = await step1_manual_fix(
                file_path=str(orphan),
                question_id="Q001",
                new_content="new content"
            )

            assert result["success"] is False
            assert "project directory" in result.get("error", "").lower()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_delete_outside_project_blocked(self):
        """file_path not in a project directory must be rejected."""
        from qf_pipeline.tools.step1_tools import step1_delete

        with tempfile.TemporaryDirectory() as tmp:
            orphan = Path(tmp) / "orphan.md"
            orphan.write_text("some content")

            result = await step1_delete(
                file_path=str(orphan),
                question_id="Q001"
            )

            assert result["success"] is False
            assert "project directory" in result.get("error", "").lower()
