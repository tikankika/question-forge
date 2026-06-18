"""
QTI Packager

Creates IMS Content Package (ZIP) containing QTI XML files and manifest.
Follows Inspera's expected structure with resources/ subfolder for media files.
"""

import os
import zipfile
import re
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
from datetime import datetime

from ..xml_utils import escape_xml, sanitize_identifier

# Template mappings for question types (must match xml_generator.py)
TEMPLATE_MAPPINGS = {
    'fill_in_the_blank': 'text_entry',
    'matching': 'match',
    'gap_match': 'gapmatch'
}


class QTIPackager:
    """Package QTI XML files into importable ZIP."""

    def __init__(self, output_dir: str = None):
        """
        Initialize packager.

        Args:
            output_dir: Directory for temporary files and final package.
                       Defaults to 'output' in project root.
        """
        if output_dir is None:
            project_root = Path(__file__).parent.parent.parent
            output_dir = project_root / 'output'

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.media_files = []  # Track media files for manifest

    def create_package(
        self,
        questions_xml: List[tuple[str, str]],
        metadata: Dict[str, Any],
        output_filename: str,
        keep_folder: bool = True,
        base_dir: Optional[str] = None,
        assessment_test_xml: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create QTI package ZIP file and optionally keep extracted folder.

        Args:
            questions_xml: List of (identifier, xml_content) tuples
            metadata: Quiz metadata from frontmatter
            output_filename: Name for output ZIP file
            keep_folder: If True, keep extracted folder alongside ZIP (default: True)
            base_dir: Base directory for output. If None, uses self.output_dir (default: None)
            assessment_test_xml: Optional assessmentTest XML for Question Sets

        Returns:
            Dictionary with 'zip_path' and 'folder_path' (if kept)

        Note:
            Resource files should be pre-copied to the output directory by ResourceManager
            before calling this method. This packager only handles XML generation and ZIP creation.
        """
        # Reset media files tracking
        self.media_files = []

        # Determine base directory
        output_base = Path(base_dir) if base_dir is not None else self.output_dir

        # Create named directory for package contents (not temp)
        # Based on output filename: quiz.zip → quiz/
        # If output_filename includes directory (e.g., "Export QTI to Inspera/quiz.zip"),
        # preserve that structure for the extracted folder
        output_file_path = Path(output_filename)
        package_name = output_file_path.stem
        if output_file_path.parent != Path('.'):
            # Output path includes subdirectory, place folder in same location as ZIP
            package_dir = output_base / output_file_path.parent / package_name
        else:
            # Simple filename, place folder directly in base directory
            package_dir = output_base / package_name

        # Preserve existing directory if it exists (resources already copied by ResourceManager)
        # Otherwise create fresh directory structure
        package_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Create resources subfolder (Inspera requirement)
            # ResourceManager should have already populated this with media files
            resources_dir = package_dir / 'resources'
            resources_dir.mkdir(exist_ok=True)

            # Write question XML files
            self._write_question_files(package_dir, questions_xml)

            # Write assessmentTest XML if provided (for Question Sets)
            if assessment_test_xml:
                test_meta = metadata.get('test_metadata', {})
                test_identifier = sanitize_identifier(test_meta.get('identifier', 'QUIZ_001'))
                assessment_test_path = (package_dir / f'ID_{test_identifier}-assessment.xml').resolve()
                # Security: never write outside the package directory.
                try:
                    assessment_test_path.relative_to(package_dir.resolve())
                except ValueError:
                    raise ValueError("Refusing to write assessment file outside package directory")
                with open(assessment_test_path, 'w', encoding='utf-8') as f:
                    f.write(assessment_test_xml)

            # Generate and write manifest
            manifest_xml = self._generate_manifest(
                questions_xml, metadata, assessment_test_xml=assessment_test_xml
            )
            manifest_path = package_dir / 'imsmanifest.xml'
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(manifest_xml)

            # Validate package structure
            validation_result = self.validate_package(package_dir)
            if not validation_result['valid']:
                print(f"Warning: Package validation found issues:")
                for issue in validation_result['issues']:
                    print(f"  - {issue}")

            # Create ZIP package
            zip_path = output_base / output_filename
            self._create_zip(package_dir, zip_path)

            result = {
                'zip_path': str(zip_path),
                'folder_path': str(package_dir) if keep_folder else None
            }

            # Clean up folder only if not keeping it
            if not keep_folder:
                self._cleanup_temp_dir(package_dir)

            return result

        except Exception as e:
            # Clean up on error
            if package_dir.exists():
                self._cleanup_temp_dir(package_dir)
            raise e

    def _write_question_files(
        self,
        package_dir: Path,
        questions_xml: List[tuple[str, str]]
    ) -> None:
        """Write individual question XML files."""
        base = package_dir.resolve()
        for identifier, xml_content in questions_xml:
            filename = f'{sanitize_identifier(identifier)}-item.xml'
            filepath = (package_dir / filename).resolve()

            # Security: never write outside the package directory (defence in
            # depth — identifiers are already sanitised at parse time).
            try:
                filepath.relative_to(base)
            except ValueError:
                raise ValueError(
                    f"Refusing to write question file outside package directory: {filename!r}"
                )

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(xml_content)

    def _generate_manifest(
        self,
        questions_xml: List[tuple[str, str]],
        metadata: Dict[str, Any],
        assessment_test_xml: Optional[str] = None
    ) -> str:
        """Generate imsmanifest.xml for the package."""
        # Extract metadata
        test_meta = metadata.get('test_metadata', {})
        title = test_meta.get('title', 'Quiz')
        identifier = test_meta.get('identifier', 'QUIZ_001')

        # Detect media files from question XML
        all_media_files = self._detect_media_files(questions_xml)

        # Get questions metadata for labels
        questions = metadata.get('questions', [])

        # Generate resource entries
        resources = []
        for idx, (question_id, xml_content) in enumerate(questions_xml):
            # Find media files specific to this question
            question_media = set()
            for media_file in all_media_files:
                if media_file in xml_content:
                    question_media.add(media_file)

            # Build file references
            file_refs = [f'      <file href="{question_id}-item.xml"/>']

            # Add media file references
            for media_file in sorted(question_media):
                file_refs.append(f'      <file href="resources/{media_file}"/>')

            files_xml = '\n'.join(file_refs)

            # Get question metadata for labels
            question_meta = questions[idx] if idx < len(questions) else {}
            question_title = question_meta.get('title', f'Question {idx + 1}')

            # Generate labels section
            labels_xml = self._generate_labels(question_meta, test_meta)

            resource_xml = f'''    <resource identifier="{question_id}" type="imsqti_item_xmlv2p2" href="{question_id}-item.xml">
      <metadata>
        <imsmd:lom>
          <imsmd:general>
            <imsmd:identifier/>
            <imsmd:title>
              <imsmd:langstring xml:lang="en">{self._escape_xml(question_title)}</imsmd:langstring>
            </imsmd:title>
          </imsmd:general>
          <imsmd:classification>
            <imsmd:description>
              <imsmd:langstring>General info, metadata and labels</imsmd:langstring>
            </imsmd:description>
            <imsmd:taxonpath>
{labels_xml}
              <imsmd:taxon>
                <imsmd:id>contentItemId</imsmd:id>
                <imsmd:entry>
                  <imsmd:langstring>{question_id}</imsmd:langstring>
                </imsmd:entry>
              </imsmd:taxon>
              <imsmd:taxon>
                <imsmd:id>objectType</imsmd:id>
                <imsmd:entry>
                  <imsmd:langstring>content_question_qti2_{TEMPLATE_MAPPINGS.get(question_meta.get('question_type', 'multiple_choice_single'), question_meta.get('question_type', 'multiple_choice_single'))}</imsmd:langstring>
                </imsmd:entry>
              </imsmd:taxon>
            </imsmd:taxonpath>
          </imsmd:classification>
        </imsmd:lom>
      </metadata>
{files_xml}
    </resource>'''
            resources.append(resource_xml)

        # Add assessmentTest resource if provided (for Question Sets)
        if assessment_test_xml:
            assessment_test_filename = f'ID_{identifier}-assessment.xml'
            # Build item references for assessmentTest
            item_refs = '\n'.join([
                f'      <dependency identifierref="{q_id}"/>'
                for q_id, _ in questions_xml
            ])
            assessment_resource = f'''    <resource identifier="ID_{identifier}" type="imsqti_test_xmlv2p2" href="{assessment_test_filename}">
      <file href="{assessment_test_filename}"/>
{item_refs}
    </resource>'''
            resources.insert(0, assessment_resource)

        resources_xml = '\n'.join(resources)

        # Build complete manifest
        manifest = f'''<?xml version="1.0" encoding="UTF-8"?>
<manifest version="1.1" identifier="{identifier}_manifest"
          xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
          xmlns:imsmd="http://www.imsglobal.org/xsd/imsmd_v1p2"
          xmlns:imsqti="http://www.imsglobal.org/xsd/imsqti_v2p2"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/qti/qtiv2p2/qtiv2p2_imscpv1p2_v1p0.xsd
                              http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2p4.xsd
                              http://www.imsglobal.org/xsd/imsqti_v2p2 http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd">
  <metadata>
    <schema>QTI Package</schema>
    <schemaversion>2.2</schemaversion>
    <imsmd:lom>
      <imsmd:general>
        <imsmd:title>
          <imsmd:langstring xml:lang="en">{self._escape_xml(title)}</imsmd:langstring>
        </imsmd:title>
      </imsmd:general>
    </imsmd:lom>
  </metadata>
  <organizations/>
  <resources>
{resources_xml}
  </resources>
</manifest>'''

        return manifest

    def _create_zip(self, source_dir: Path, output_path: Path) -> None:
        """Create ZIP file from directory contents."""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    # Skip resource_mapping.json - it's for development reference only
                    if file_path.name == 'resource_mapping.json':
                        continue
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)

    def _cleanup_temp_dir(self, temp_dir: Path) -> None:
        """Remove temporary directory and its contents."""
        if temp_dir.exists():
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    file_path.unlink()

            # Remove empty directories
            for dir_path in sorted(temp_dir.rglob('*'), reverse=True):
                if dir_path.is_dir():
                    dir_path.rmdir()

            temp_dir.rmdir()

    def _detect_media_files(self, questions_xml: List[tuple[str, str]]) -> Set[str]:
        """
        Detect media file references in question XML.

        Args:
            questions_xml: List of (identifier, xml_content) tuples

        Returns:
            Set of media filenames referenced
        """
        media_files = set()

        for _, xml_content in questions_xml:
            # Find img src="resources/..." references
            img_pattern = r'<img[^>]+src="resources/([^"]+)"'
            for match in re.finditer(img_pattern, xml_content):
                media_files.add(match.group(1))

            # Find object data="resources/..." references
            obj_pattern = r'<object[^>]+data="resources/([^"]+)"'
            for match in re.finditer(obj_pattern, xml_content):
                media_files.add(match.group(1))

        return media_files


    def validate_package(self, package_dir: Path) -> Dict[str, Any]:
        """
        Validate package structure against Inspera requirements.

        Args:
            package_dir: Path to package directory

        Returns:
            Dictionary with validation results:
                - valid: bool
                - issues: List of issue descriptions
                - warnings: List of warning messages
        """
        issues = []
        warnings = []

        # Check imsmanifest.xml exists
        manifest_path = package_dir / 'imsmanifest.xml'
        if not manifest_path.exists():
            issues.append("Missing imsmanifest.xml")

        # Check resources/ folder exists
        resources_dir = package_dir / 'resources'
        if not resources_dir.exists():
            warnings.append("resources/ folder missing (okay if no media files)")
        elif not any(resources_dir.iterdir()):
            warnings.append("resources/ folder is empty")

        # Check for question XML files
        item_files = list(package_dir.glob('*-item.xml'))
        if not item_files:
            issues.append("No question XML files (*-item.xml) found")

        # Validate manifest if it exists
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_content = f.read()

            # Check each item file is referenced in manifest
            for item_file in item_files:
                if item_file.name not in manifest_content:
                    warnings.append(f"{item_file.name} not referenced in manifest")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def get_package_tree(self, package_path: str) -> str:
        """
        Get a tree view of package contents.

        Args:
            package_path: Path to ZIP package

        Returns:
            String representation of package structure
        """
        lines = []
        lines.append(f"\n{Path(package_path).name}/")

        with zipfile.ZipFile(package_path, 'r') as zipf:
            # Get all files sorted
            files = sorted(zipf.namelist())

            for i, filename in enumerate(files):
                is_last = (i == len(files) - 1)
                prefix = "└── " if is_last else "├── "

                # Get file size
                file_info = zipf.getinfo(filename)
                size = file_info.file_size

                # Format size
                if size < 1024:
                    size_str = f"{size}B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f}KB"
                else:
                    size_str = f"{size/(1024*1024):.1f}MB"

                lines.append(f"{prefix}{filename} ({size_str})")

        return '\n'.join(lines)

    def _generate_labels(
        self,
        question_meta: Dict[str, Any],
        test_meta: Dict[str, Any]
    ) -> str:
        """
        Generate label and custom metadata taxonomy entries for question metadata.

        Labels: Free-form tags (NO <imsmd:id>) from ^labels
        Custom Metadata: Structured field+value (WITH <imsmd:id>) from ^custom_metadata

        Args:
            question_meta: Question-level metadata
            test_meta: Test-level metadata

        Returns:
            XML string for taxon entries (labels + custom metadata)
        """
        labels = []

        # Add labels from the ^labels field (Inspera "Labels" - free-form tags)
        custom_labels = question_meta.get('labels', '')
        if custom_labels:
            if isinstance(custom_labels, str):
                # Split space-separated or comma-separated tags
                # Evolution format uses space-separated: #example_bio #evolution #mutation
                if ',' in custom_labels:
                    label_list = [label.strip() for label in custom_labels.split(',')]
                else:
                    label_list = [label.strip() for label in custom_labels.split()]
                for label in label_list:
                    if label:  # Skip empty strings
                        labels.append(label)
            elif isinstance(custom_labels, list):
                # Already a list
                labels.extend(custom_labels)

        # Remove duplicate labels (case-sensitive comparison)
        seen = set()
        unique_labels = []
        for label in labels:
            if label not in seen:
                seen.add(label)
                unique_labels.append(label)
        labels = unique_labels

        # Generate XML for each label (NO <imsmd:id>)
        taxon_entries = []
        for label in labels:
            taxon_xml = f'''              <imsmd:taxon>
                <imsmd:entry>
                  <imsmd:langstring>{self._escape_xml(label)}</imsmd:langstring>
                </imsmd:entry>
              </imsmd:taxon>'''
            taxon_entries.append(taxon_xml)

        # Generate custom metadata taxons (WITH <imsmd:id>)
        # Format: {field_name: [value1, value2, ...]}
        custom_metadata = question_meta.get('custom_metadata', {})
        for field_name, values in custom_metadata.items():
            for value in values:
                taxon_xml = f'''              <imsmd:taxon>
                <imsmd:id>{self._escape_xml(field_name)}</imsmd:id>
                <imsmd:entry>
                  <imsmd:langstring>{self._escape_xml(value)}</imsmd:langstring>
                </imsmd:entry>
              </imsmd:taxon>'''
                taxon_entries.append(taxon_xml)

        return '\n'.join(taxon_entries)

    def _escape_xml(self, text: str) -> str:
        """Escape special XML characters."""
        return escape_xml(text)
