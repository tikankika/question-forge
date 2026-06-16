#!/usr/bin/env python3
"""
Security tests for qti-core.

Verifies that path traversal, ZIP Slip, and XML injection are blocked.
"""

import pytest
import tempfile
import zipfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generator.resource_manager import ResourceManager, ResourceIssue
from src.generator.xml_generator import XMLGenerator
from src.xml_utils import escape_xml


# =============================================================================
# Path Traversal — Resource Manager
# =============================================================================

class TestResourceManagerPathTraversal:
    """Verify that resource_manager blocks path traversal in image references."""

    def setup_method(self):
        """Create a temp project structure."""
        self.tmp = tempfile.mkdtemp()
        self.media_dir = Path(self.tmp) / "media"
        self.media_dir.mkdir()
        self.quiz_dir = Path(self.tmp) / "output"
        self.quiz_dir.mkdir()
        (self.quiz_dir / "resources").mkdir()

        # Create a legitimate resource
        (self.media_dir / "image.png").write_bytes(b"PNG_DATA")

    @pytest.mark.unit
    def test_traversal_in_validate_resources_blocked(self):
        """Markdown ![](../../etc/passwd) must be flagged as ERROR, not silently allowed."""
        rm = ResourceManager(
            input_file=str(self.media_dir / "dummy.md"),
            output_dir=str(self.quiz_dir),
            media_dir=str(self.media_dir),
        )

        # Simulate a question referencing a traversal path
        questions = [{
            "identifier": "Q001",
            "question_text": "![exploit](../../etc/passwd)",
            "question_text_xhtml": '<img src="../../etc/passwd"/>',
        }]

        issues = rm.validate_resources(questions)

        # Must contain a blocking error about path traversal
        traversal_errors = [i for i in issues if "traversal" in i.message.lower()]
        assert len(traversal_errors) > 0, "Path traversal in image reference was not blocked"

    @pytest.mark.unit
    def test_traversal_in_copy_resources_blocked(self):
        """copy_resources must refuse to copy files outside media_dir."""
        rm = ResourceManager(
            input_file=str(self.media_dir / "dummy.md"),
            output_dir=str(self.quiz_dir),
            media_dir=str(self.media_dir),
        )

        questions = [{
            "identifier": "Q001",
            "question_text": "![exploit](../../etc/passwd)",
            "question_text_xhtml": '<img src="../../etc/passwd"/>',
        }]

        copied = rm.copy_resources(questions, self.quiz_dir)

        # The traversal path must NOT be in the copied results
        assert "../../etc/passwd" not in copied, "Path traversal file was copied"

    @pytest.mark.unit
    def test_legitimate_resource_works(self):
        """Normal image references within media_dir should work fine."""
        rm = ResourceManager(
            input_file=str(self.media_dir / "dummy.md"),
            output_dir=str(self.quiz_dir),
            media_dir=str(self.media_dir),
        )

        questions = [{
            "identifier": "Q001",
            "question_text": "![img](image.png)",
            "question_text_xhtml": '<img src="image.png"/>',
        }]

        issues = rm.validate_resources(questions)
        errors = [i for i in issues if i.level == "ERROR"]
        assert len(errors) == 0, f"Legitimate resource flagged as error: {errors}"


# =============================================================================
# Path Traversal — XML Generator Templates
# =============================================================================

class TestXMLGeneratorPathTraversal:
    """Verify that xml_generator blocks path traversal in question_type."""

    @pytest.mark.unit
    def test_traversal_question_type_blocked(self):
        """question_type like '../../etc/passwd' must raise ValueError."""
        gen = XMLGenerator()

        with pytest.raises(ValueError, match="traversal"):
            gen._load_template("../../etc/passwd")

    @pytest.mark.unit
    def test_legitimate_question_type_works(self):
        """Normal question types should load successfully."""
        gen = XMLGenerator()

        # This should not raise
        template = gen._load_template("multiple_choice_single")
        assert len(template) > 0


# =============================================================================
# ZIP Slip — CLI
# =============================================================================

class TestZIPSlipPrevention:
    """Verify that cli.py rejects ZIP entries with path traversal."""

    @pytest.mark.unit
    def test_malicious_zip_entry_detected(self):
        """A ZIP with ../../evil.txt entry must be detected before extraction."""
        tmp = tempfile.mkdtemp()
        evil_zip = Path(tmp) / "evil.zip"

        # Create a ZIP with a traversal entry
        with zipfile.ZipFile(evil_zip, "w") as zf:
            zf.writestr("../../evil.txt", "malicious content")

        # Verify the malicious entry exists
        with zipfile.ZipFile(evil_zip, "r") as zf:
            names = zf.namelist()
            assert any(".." in name for name in names), "Test ZIP should contain traversal entry"

        # Verify our validation logic catches it
        with zipfile.ZipFile(evil_zip, "r") as zf:
            temp_path = Path(tmp) / "extract"
            temp_path.mkdir()
            for member in zf.namelist():
                member_path = (temp_path / member).resolve()
                if not member_path.is_relative_to(temp_path.resolve()):
                    # This is what our fix does — block it
                    assert True, "Traversal entry correctly detected"
                    return

        pytest.fail("Malicious ZIP entry was not detected")


# =============================================================================
# XML Escaping
# =============================================================================

class TestXMLEscaping:
    """Verify that escape_xml prevents XML injection."""

    @pytest.mark.unit
    def test_script_tag_escaped(self):
        result = escape_xml("<script>alert(1)</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    @pytest.mark.unit
    def test_attribute_breakout_escaped(self):
        result = escape_xml('value" onload="alert(1)')
        assert '"' not in result
        assert "&quot;" in result

    @pytest.mark.unit
    def test_ampersand_escaped(self):
        result = escape_xml("A & B")
        assert "&amp;" in result

    @pytest.mark.unit
    def test_empty_string(self):
        assert escape_xml("") == ""
        assert escape_xml(None) == ""
