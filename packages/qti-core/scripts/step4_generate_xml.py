#!/usr/bin/env python3
"""
Step 4: Generate QTI XML Files

Generates QTI XML files for each question in the markdown file.
Uses resource mapping from step 3 to update image paths.

Usage:
    python scripts/step4_generate_xml.py [options]

Options:
    --markdown-file FILE    Path to markdown file (overrides metadata.json)
    --quiz-dir DIR          Quiz output directory (overrides metadata.json)
    --language LANG         Question language code (default: en)
    -v, --verbose          Show detailed information

Exit codes:
    0 = Success
    1 = XML generation errors

Example:
    # Using metadata from previous steps (recommended):
    python scripts/step4_generate_xml.py

    # Or specify paths manually:
    python scripts/step4_generate_xml.py --markdown-file quiz.md --quiz-dir output/quiz

    # Swedish language:
    python scripts/step4_generate_xml.py --language sv
"""

import sys
import json
import argparse
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.parser.markdown_parser import MarkdownQuizParser
from src.generator.xml_generator import XMLGenerator


def load_metadata(workflow_dir: Path) -> dict:
    """Load workflow metadata from previous steps."""
    metadata_file = workflow_dir / "metadata.json"
    if not metadata_file.exists():
        return None

    with open(metadata_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_resource_mapping(workflow_dir: Path) -> dict:
    """Load resource mapping from step 3."""
    mapping_file = workflow_dir / "resource_mapping.json"
    if not mapping_file.exists():
        return {}

    with open(mapping_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('mapping', {})


def save_xml_metadata(workflow_dir: Path, xml_files: list, quiz_data: dict, assessment_test_xml: str = None):
    """Save XML metadata for next step."""
    metadata_file = workflow_dir / "xml_files.json"

    metadata = {
        'step': 'step4_generate_xml',
        'timestamp': datetime.now().isoformat(),
        'xml_count': len(xml_files),
        'xml_files': xml_files,
        'quiz_metadata': quiz_data.get('metadata', {}),
        'has_assessment_test': assessment_test_xml is not None
    }

    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def update_image_paths_in_text(text: str, resource_mapping: Dict[str, str]) -> str:
    """
    Replace original image filenames with renamed ones in markdown text.

    Handles markdown image syntax: ![alt](path)
    Updates paths to use ResourceManager's renamed files (with question ID prefix and sanitization).

    Args:
        text: Text containing markdown image references
        resource_mapping: Dict mapping original filenames to renamed filenames

    Returns:
        Text with updated image paths
    """
    # Create normalized mapping with basename keys for easy lookup
    basename_mapping = {os.path.basename(k): v for k, v in resource_mapping.items()}

    def replace_image(match):
        alt = match.group(1)
        original_path = match.group(2)
        # Extract just the filename to match resource_mapping keys
        basename = os.path.basename(original_path)
        # Use renamed path if available, otherwise keep original
        renamed = basename_mapping.get(basename, basename)
        return f'![{alt}](resources/{renamed})'

    # Replace markdown image syntax: ![alt](path)
    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, text)


def normalize_resource_path(path: str) -> str:
    """Strip resources/ prefix variants to get just the filename for mapping lookup."""
    for prefix in ['resources/', 'Resources/', './resources/', './Resources/']:
        if path.startswith(prefix):
            return path[len(prefix):]
    return path


def apply_resource_mapping(questions: list, resource_mapping: dict, verbose: bool = False):
    """
    Update question data with renamed resource paths.

    Args:
        questions: List of question dictionaries
        resource_mapping: Dict mapping original filenames to renamed filenames
        verbose: If True, print detailed updates
    """
    # Create normalized mapping (keys without resources/ prefix)
    normalized_mapping = {normalize_resource_path(k): v for k, v in resource_mapping.items()}

    for question in questions:
        # 1. Handle explicit image field (hotspot, graphicgapmatch, text_entry_graphic)
        if 'image' in question and isinstance(question['image'], dict):
            original_path = question['image'].get('path', '')
            # Normalize path for lookup
            lookup_key = normalize_resource_path(original_path)
            if lookup_key in normalized_mapping:
                # Set renamed path WITH resources/ prefix for QTI
                renamed = normalized_mapping[lookup_key]
                question['image']['path'] = f'resources/{renamed}'
                if verbose:
                    print(f"    Updated image path: {original_path} → resources/{renamed}")

        # 2. Handle inline markdown images in question_text
        if 'question_text' in question and question['question_text']:
            question['question_text'] = update_image_paths_in_text(
                question['question_text'], resource_mapping
            )

        # 3. Handle images in feedback
        if 'feedback' in question:
            for key in ['general', 'correct', 'incorrect', 'unanswered']:
                if key in question['feedback'] and question['feedback'][key]:
                    question['feedback'][key] = update_image_paths_in_text(
                        question['feedback'][key], resource_mapping
                    )

            # Option-specific feedback (for multiple choice questions)
            if 'option_specific' in question['feedback'] and question['feedback']['option_specific']:
                for option_id, feedback_text in question['feedback']['option_specific'].items():
                    if feedback_text:
                        question['feedback']['option_specific'][option_id] = update_image_paths_in_text(
                            feedback_text, resource_mapping
                        )

        # 4. Handle images in Match question premises/responses
        if 'premises' in question:
            for premise in question['premises']:
                if 'text' in premise and premise['text']:
                    premise['text'] = update_image_paths_in_text(
                        premise['text'], resource_mapping
                    )

        if 'match_responses' in question:
            for response in question['match_responses']:
                if 'text' in response and response['text']:
                    response['text'] = update_image_paths_in_text(
                        response['text'], resource_mapping
                    )


def main():
    parser = argparse.ArgumentParser(
        description='Step 4: Generate QTI XML files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using metadata from previous steps (recommended):
  python scripts/step4_generate_xml.py

  # Or specify paths manually:
  python scripts/step4_generate_xml.py --markdown-file quiz.md --quiz-dir output/quiz

  # Swedish language:
  python scripts/step4_generate_xml.py --language sv

This is Step 4 of the QTI generation pipeline.
After XML generation, run step5_create_zip.py.
        """
    )

    parser.add_argument(
        '--markdown-file',
        type=str,
        help='Path to markdown file (overrides metadata.json)'
    )

    parser.add_argument(
        '--quiz-dir',
        type=str,
        help='Quiz output directory (overrides metadata.json)'
    )

    parser.add_argument(
        '--language',
        type=str,
        default='en',
        help='Question language code (default: en)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information'
    )

    args = parser.parse_args()

    # Print step info
    print("=" * 70)
    print("STEP 4: GENERATE QTI XML FILES")
    print("=" * 70)

    # Try to load metadata
    current_dir = Path.cwd()

    if args.quiz_dir:
        workflow_dir = Path(args.quiz_dir) / ".workflow"
    else:
        # Search for .workflow in output directory
        output_dir = current_dir / "output"
        if output_dir.exists():
            workflow_dirs = list(output_dir.glob("*/.workflow"))
            if workflow_dirs:
                workflow_dir = workflow_dirs[0]
                if args.verbose:
                    print(f"Found workflow directory: {workflow_dir}")
            else:
                workflow_dir = None
        else:
            workflow_dir = None

    metadata = None
    if workflow_dir and workflow_dir.exists():
        metadata = load_metadata(workflow_dir)
        if args.verbose and metadata:
            print(f"✓ Loaded metadata from: {workflow_dir / 'metadata.json'}")

    # Determine paths
    if args.markdown_file:
        markdown_path = Path(args.markdown_file).resolve()
    elif metadata:
        markdown_path = Path(metadata['input_file'])
    else:
        print("✗ Error: No markdown file specified and no metadata found", file=sys.stderr)
        print("  Either run previous steps first, or use --markdown-file", file=sys.stderr)
        sys.exit(1)

    if args.quiz_dir:
        quiz_dir = Path(args.quiz_dir).resolve()
    elif metadata:
        quiz_dir = Path(metadata['quiz_dir'])
    else:
        print("✗ Error: No quiz directory specified and no metadata found", file=sys.stderr)
        print("  Either run previous steps first, or use --quiz-dir", file=sys.stderr)
        sys.exit(1)

    # Check paths exist
    if not markdown_path.exists():
        print(f"✗ Error: Markdown file not found: {markdown_path}", file=sys.stderr)
        sys.exit(1)

    if not quiz_dir.exists():
        print(f"✗ Error: Quiz directory not found: {quiz_dir}", file=sys.stderr)
        print("  Run step2_create_folder.py first", file=sys.stderr)
        sys.exit(1)

    workflow_dir = quiz_dir / ".workflow"

    print(f"Markdown file:  {markdown_path}")
    print(f"Quiz directory: {quiz_dir}")
    print(f"Language:       {args.language}")
    print()

    try:
        # Read and parse markdown
        if args.verbose:
            print("Reading markdown file...")

        with open(markdown_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        if args.verbose:
            print("Parsing markdown content...")

        parser = MarkdownQuizParser(markdown_content)
        quiz_data = parser.parse()

        num_questions = len(quiz_data['questions'])
        print(f"Found {num_questions} questions")
        print()

        # Load resource mapping from step 3
        resource_mapping = load_resource_mapping(workflow_dir)
        if resource_mapping:
            print(f"Loaded resource mapping with {len(resource_mapping)} entries")
            if args.verbose:
                print("Updating image paths in question data...")

            apply_resource_mapping(quiz_data['questions'], resource_mapping, args.verbose)
            print()

        # Generate XML for each question
        print("Generating QTI XML files...")
        xml_generator = XMLGenerator()
        xml_files = []

        for i, question in enumerate(quiz_data['questions'], 1):
            q_id = question.get('identifier', f'Q{i:03d}')

            if args.verbose:
                print(f"  [{i}/{num_questions}] Generating: {q_id}")

            try:
                xml_content = xml_generator.generate_question(
                    question,
                    language=args.language
                )

                # Save XML file
                xml_filename = f"{q_id}-item.xml"
                xml_path = quiz_dir / xml_filename

                with open(xml_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content)

                xml_files.append({
                    'identifier': q_id,
                    'filename': xml_filename,
                    'path': str(xml_path),
                    'metadata': question  # Include question metadata (tags, title, points, etc.)
                })

            except Exception as e:
                # Enhanced error message
                q_type = question.get('question_type', 'unknown')
                q_title = question.get('title', 'Unknown Title')

                print(f"\n{'='*70}", file=sys.stderr)
                print(f"✗ ERROR: Failed to generate question {i}/{num_questions}", file=sys.stderr)
                print(f"{'='*70}", file=sys.stderr)
                print(f"Question ID:   {q_id}", file=sys.stderr)
                print(f"Question Type: {q_type}", file=sys.stderr)
                print(f"Title:         {q_title}", file=sys.stderr)
                print(f"\nError Details: {str(e)}", file=sys.stderr)

                if 'KeyError' in str(type(e).__name__):
                    print(f"\n💡 Suggestion: Missing required field for {q_type} questions.", file=sys.stderr)
                    print(f"   Check that all required sections are present in the markdown.", file=sys.stderr)

                print(f"{'='*70}\n", file=sys.stderr)

                if args.verbose:
                    import traceback
                    traceback.print_exc()

                sys.exit(1)

        print(f"✓ Generated {len(xml_files)} XML files")
        print()

        # Generate assessmentTest if question_set is defined
        assessment_test_xml = None
        question_set_config = quiz_data.get('metadata', {}).get('question_set')
        if question_set_config:
            from src.generator.assessment_test_generator import generate_assessment_test
            print("Generating assessmentTest for Question Set...")
            assessment_test_xml = generate_assessment_test(quiz_data, language=args.language)
            if assessment_test_xml:
                test_meta = quiz_data.get('metadata', {}).get('test_metadata', {})
                test_identifier = test_meta.get('identifier', 'QUIZ_001')
                assessment_test_filename = f"ID_{test_identifier}-assessment.xml"
                assessment_test_path = quiz_dir / assessment_test_filename

                with open(assessment_test_path, 'w', encoding='utf-8') as f:
                    f.write(assessment_test_xml)
                print(f"✓ Generated assessmentTest: {assessment_test_filename}")
                print()

        # Save metadata for next step
        save_xml_metadata(workflow_dir, xml_files, quiz_data, assessment_test_xml=assessment_test_xml)
        if args.verbose:
            print(f"✓ Saved XML metadata: {workflow_dir / 'xml_files.json'}")
            print()

        # Print summary
        print("=" * 70)
        print("XML GENERATION COMPLETE")
        print("=" * 70)
        print(f"Output directory: {quiz_dir}")
        print(f"Generated files:  {len(xml_files)}")
        print()

        if args.verbose:
            print("Generated files:")
            for xml_file in xml_files:
                print(f"  • {xml_file['filename']}")
            print()

        # Print next steps
        print("=" * 70)
        print("NEXT STEP")
        print("=" * 70)
        print("Run step 5 to create QTI package (ZIP):")
        print(f"  python scripts/step5_create_zip.py")
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
