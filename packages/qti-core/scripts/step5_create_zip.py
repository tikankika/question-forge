#!/usr/bin/env python3
"""
Step 5: Create QTI Package (ZIP)

Creates the final QTI package by generating imsmanifest.xml and zipping all files.

Usage:
    python scripts/step5_create_zip.py [options]

Options:
    --quiz-dir DIR          Quiz output directory (overrides metadata.json)
    --output-name NAME      Output ZIP filename (default: quiz_dir name)
    --no-keep-folder       Delete extracted folder after zipping
    -v, --verbose          Show detailed information

Exit codes:
    0 = Success
    1 = Packaging errors

Example:
    # Using metadata from previous steps (recommended):
    python scripts/step5_create_zip.py

    # Or specify paths manually:
    python scripts/step5_create_zip.py --quiz-dir output/quiz

    # Custom output name:
    python scripts/step5_create_zip.py --output-name my_final_quiz.zip
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.packager.qti_packager import QTIPackager


def load_metadata(workflow_dir: Path) -> dict:
    """Load workflow metadata from previous steps."""
    metadata_file = workflow_dir / "metadata.json"
    if not metadata_file.exists():
        return None

    with open(metadata_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_xml_metadata(workflow_dir: Path) -> dict:
    """Load XML metadata from step 4."""
    xml_file = workflow_dir / "xml_files.json"
    if not xml_file.exists():
        return None

    with open(xml_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_package_metadata(workflow_dir: Path, zip_path: str, folder_path: str):
    """Save package metadata."""
    metadata_file = workflow_dir / "package_info.json"

    metadata = {
        'step': 'step5_create_zip',
        'timestamp': datetime.now().isoformat(),
        'zip_path': zip_path,
        'folder_path': folder_path
    }

    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description='Step 5: Create QTI package (ZIP)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using metadata from previous steps (recommended):
  python scripts/step5_create_zip.py

  # Or specify paths manually:
  python scripts/step5_create_zip.py --quiz-dir output/quiz

  # Custom output name:
  python scripts/step5_create_zip.py --output-name evolution_test_final.zip

This is Step 5 (final step) of the QTI generation pipeline.
        """
    )

    parser.add_argument(
        '--quiz-dir',
        type=str,
        help='Quiz output directory (overrides metadata.json)'
    )

    parser.add_argument(
        '--output-name',
        type=str,
        help='Output ZIP filename (default: quiz_dir name + .zip)'
    )

    parser.add_argument(
        '--no-keep-folder',
        action='store_true',
        help='Delete extracted folder after creating ZIP (default: keep folder)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information'
    )

    args = parser.parse_args()

    # Print step info
    print("=" * 70)
    print("STEP 5: CREATE QTI PACKAGE (ZIP)")
    print("=" * 70)

    # Try to load metadata
    current_dir = Path.cwd()

    if args.quiz_dir:
        quiz_dir = Path(args.quiz_dir).resolve()
    else:
        # Search for .workflow in output directory
        output_dir = current_dir / "output"
        if output_dir.exists():
            workflow_dirs = list(output_dir.glob("*/.workflow"))
            if workflow_dirs:
                workflow_dir = workflow_dirs[0]
                quiz_dir = workflow_dir.parent
                if args.verbose:
                    print(f"Found workflow directory: {workflow_dir}")
            else:
                quiz_dir = None
        else:
            quiz_dir = None

    if not quiz_dir:
        print("✗ Error: No quiz directory found", file=sys.stderr)
        print("  Either run previous steps first, or use --quiz-dir", file=sys.stderr)
        sys.exit(1)

    if not quiz_dir.exists():
        print(f"✗ Error: Quiz directory not found: {quiz_dir}", file=sys.stderr)
        print("  Run previous steps first", file=sys.stderr)
        sys.exit(1)

    workflow_dir = quiz_dir / ".workflow"

    # Load metadata
    metadata = load_metadata(workflow_dir)
    xml_metadata = load_xml_metadata(workflow_dir)

    if not xml_metadata:
        print("✗ Error: No XML metadata found", file=sys.stderr)
        print("  Run step4_generate_xml.py first", file=sys.stderr)
        sys.exit(1)

    # Determine output filename
    if args.output_name:
        output_filename = args.output_name
    else:
        quiz_name = quiz_dir.name
        output_filename = f"{quiz_name}.zip"

    output_base = quiz_dir.parent

    print(f"Quiz directory: {quiz_dir}")
    print(f"Output name:    {output_filename}")
    print(f"Output base:    {output_base}")
    print()

    try:
        # Check that XML files exist
        xml_files = xml_metadata.get('xml_files', [])
        if not xml_files:
            print("✗ Error: No XML files found in metadata", file=sys.stderr)
            print("  Run step4_generate_xml.py first", file=sys.stderr)
            sys.exit(1)

        print(f"Found {len(xml_files)} XML files")

        # Verify files exist
        missing_files = []
        for xml_file in xml_files:
            xml_path = Path(xml_file['path'])
            if not xml_path.exists():
                missing_files.append(xml_file['filename'])

        if missing_files:
            print(f"✗ Error: Missing XML files:", file=sys.stderr)
            for filename in missing_files:
                print(f"  - {filename}", file=sys.stderr)
            sys.exit(1)

        print("✓ All XML files verified")
        print()

        # Prepare questions_xml format for packager
        # Note: We don't need to read XML content since files are already written
        # We just need to prepare manifest and create ZIP

        print("Creating QTI package...")

        # Read XML content for manifest generation
        questions_xml = []
        questions_metadata = []
        for xml_file in xml_files:
            with open(xml_file['path'], 'r', encoding='utf-8') as f:
                xml_content = f.read()
            questions_xml.append((xml_file['identifier'], xml_content))

            # Extract question metadata (includes tags, title, points, etc.)
            if 'metadata' in xml_file:
                questions_metadata.append(xml_file['metadata'])

        # Get quiz metadata and add questions list
        quiz_metadata = xml_metadata.get('quiz_metadata', {})
        quiz_metadata['questions'] = questions_metadata

        # Check for assessmentTest XML (Question Set)
        assessment_test_xml = None
        assessment_files = list(quiz_dir.glob("*-assessment.xml"))
        if assessment_files:
            assessment_file = assessment_files[0]
            print(f"✓ Hittade Question Set: {assessment_file.name}")
            with open(assessment_file, 'r', encoding='utf-8') as f:
                assessment_test_xml = f.read()
        else:
            if args.verbose:
                print("  Inget Question Set hittades - skapar vanligt quiz-paket")

        # Initialize packager
        packager = QTIPackager(output_dir=str(output_base))

        # Create package
        if args.verbose:
            print(f"  Generating imsmanifest.xml...")
            print(f"  Creating ZIP archive...")

        result = packager.create_package(
            questions_xml=questions_xml,
            metadata=quiz_metadata,
            output_filename=output_filename,
            keep_folder=not args.no_keep_folder,
            base_dir=str(output_base),
            assessment_test_xml=assessment_test_xml
        )

        print(f"✓ Package created successfully")
        print()

        # Move ZIP to parent directory (Struktur B: ZIP bredvid folder, inte inne i den)
        zip_path = Path(result['zip_path'])
        parent_dir = quiz_dir.parent

        if zip_path.exists() and zip_path.parent != parent_dir:
            import shutil
            new_zip_path = parent_dir / zip_path.name

            if args.verbose:
                print(f"Moving ZIP to parent directory...")
                print(f"  From: {zip_path}")
                print(f"  To:   {new_zip_path}")

            shutil.move(str(zip_path), str(new_zip_path))
            result['zip_path'] = str(new_zip_path)

            if args.verbose:
                print(f"✓ ZIP moved to parent directory")
                print()

        # Save metadata
        save_package_metadata(
            workflow_dir,
            result['zip_path'],
            result.get('folder_path', '')
        )

        if args.verbose:
            print(f"✓ Saved package metadata: {workflow_dir / 'package_info.json'}")
            print()

        # Print summary
        print("=" * 70)
        print("QTI PACKAGE COMPLETE")
        print("=" * 70)
        print(f"ZIP file:       {result['zip_path']}")
        if result.get('folder_path'):
            print(f"Folder:         {result['folder_path']}")
        print()

        # Print usage instructions
        print("=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("1. Upload the ZIP file to Inspera:")
        print(f"   {result['zip_path']}")
        print()
        print("2. In Inspera Question Bank:")
        print("   - Go to 'Import' → 'QTI 2.1'")
        print("   - Select the ZIP file")
        print("   - Review and confirm import")
        print()

        sys.exit(0)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
