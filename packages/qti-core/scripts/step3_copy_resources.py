#!/usr/bin/env python3
"""
Step 3: Copy and Rename Resources

Validates and copies media resources (images, etc.) to the output directory.
Resources are renamed with question ID prefixes for organization.

Usage:
    python scripts/step3_copy_resources.py [options]

Options:
    --markdown-file FILE    Path to markdown file (overrides metadata.json)
    --quiz-dir DIR          Quiz output directory (overrides metadata.json)
    --media-dir DIR         Media directory (default: auto-detect)
    --strict                Treat warnings as errors
    -v, --verbose          Show detailed information

Exit codes:
    0 = Success
    1 = Resource validation errors found

Example:
    # Using metadata from step 2 (recommended):
    python scripts/step3_copy_resources.py

    # Or specify paths manually:
    python scripts/step3_copy_resources.py --markdown-file quiz.md --quiz-dir output/quiz
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.parser.markdown_parser import MarkdownQuizParser
from src.generator.resource_manager import ResourceManager, has_errors, has_warnings, print_issues


def load_metadata(workflow_dir: Path) -> dict:
    """Load workflow metadata from previous step."""
    metadata_file = workflow_dir / "metadata.json"
    if not metadata_file.exists():
        return None

    with open(metadata_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_resource_mapping(workflow_dir: Path, resource_mapping: dict):
    """Save resource mapping for next step."""
    mapping_file = workflow_dir / "resource_mapping.json"

    metadata = {
        'step': 'step3_copy_resources',
        'timestamp': datetime.now().isoformat(),
        'resource_count': len(resource_mapping),
        'mapping': resource_mapping
    }

    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description='Step 3: Copy and rename resources',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using metadata from step 2 (recommended):
  python scripts/step3_copy_resources.py

  # Or specify paths manually:
  python scripts/step3_copy_resources.py --markdown-file quiz.md --quiz-dir output/quiz

  # Strict mode (treat warnings as errors):
  python scripts/step3_copy_resources.py --strict

This is Step 3 of the QTI generation pipeline.
After resources are copied, run step4_generate_xml.py.
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
        '--media-dir',
        type=str,
        help='Media directory containing images (default: auto-detect)'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information'
    )

    args = parser.parse_args()

    # Print step info
    print("=" * 70)
    print("STEP 3: COPY AND RENAME RESOURCES")
    print("=" * 70)

    # Try to load metadata from step 2
    metadata = None
    current_dir = Path.cwd()

    # Look for .workflow directory in current directory or subdirectories
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

    if workflow_dir and workflow_dir.exists():
        metadata = load_metadata(workflow_dir)
        if args.verbose and metadata:
            print(f"✓ Loaded metadata from: {workflow_dir / 'metadata.json'}")

    # Determine paths (use CLI args or metadata)
    if args.markdown_file:
        markdown_path = Path(args.markdown_file).resolve()
    elif metadata:
        markdown_path = Path(metadata['input_file'])
    else:
        print("✗ Error: No markdown file specified and no metadata found", file=sys.stderr)
        print("  Either run step2_create_folder.py first, or use --markdown-file", file=sys.stderr)
        sys.exit(1)

    if args.quiz_dir:
        quiz_dir = Path(args.quiz_dir).resolve()
    elif metadata:
        quiz_dir = Path(metadata['quiz_dir'])
    else:
        print("✗ Error: No quiz directory specified and no metadata found", file=sys.stderr)
        print("  Either run step2_create_folder.py first, or use --quiz-dir", file=sys.stderr)
        sys.exit(1)

    # Check files exist
    if not markdown_path.exists():
        print(f"✗ Error: Markdown file not found: {markdown_path}", file=sys.stderr)
        sys.exit(1)

    if not quiz_dir.exists():
        print(f"✗ Error: Quiz directory not found: {quiz_dir}", file=sys.stderr)
        print("  Run step2_create_folder.py first", file=sys.stderr)
        sys.exit(1)

    resources_dir = quiz_dir / "resources"
    workflow_dir = quiz_dir / ".workflow"

    print(f"Markdown file:  {markdown_path}")
    print(f"Quiz directory: {quiz_dir}")
    print(f"Resources dir:  {resources_dir}")
    if args.media_dir:
        print(f"Media directory: {args.media_dir}")
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

        # Initialize ResourceManager
        if args.verbose:
            print("Initializing ResourceManager...")

        # Determine media directory
        if args.media_dir:
            media_dir = Path(args.media_dir)
        else:
            # Auto-detect: use markdown file's parent directory
            media_dir = markdown_path.parent

        output_base_dir = quiz_dir.parent

        resource_manager = ResourceManager(
            input_file=markdown_path,
            output_dir=output_base_dir,
            media_dir=media_dir,
            strict=args.strict
        )

        if args.verbose:
            print(f"  Media directory: {resource_manager.media_dir}")
            print()

        # Validate resources
        print("Validating resources...")
        resource_issues = resource_manager.validate_resources(quiz_data['questions'])

        if resource_issues:
            print()
            print_issues(resource_issues, show_info=args.verbose)
            print()

            if has_errors(resource_issues):
                print("✗ Resource validation failed. Cannot proceed.", file=sys.stderr)
                print("  Fix the above errors and try again.", file=sys.stderr)
                sys.exit(1)

            if has_warnings(resource_issues):
                if args.strict:
                    print("✗ Resource validation failed in strict mode (warnings treated as errors).", file=sys.stderr)
                    print("  Fix the above warnings or run without --strict flag.", file=sys.stderr)
                    sys.exit(1)
                else:
                    print("⚠️  Warnings found but continuing...")
                    print()
        else:
            print("✓ All resources validated successfully")
            print()

        # Copy resources with renaming
        print("Copying and renaming resources...")
        resource_mapping = resource_manager.copy_resources(quiz_data['questions'], quiz_dir)

        if resource_mapping:
            print(f"✓ Copied {len(resource_mapping)} resources:")
            print()

            for original, renamed in resource_mapping.items():
                print(f"  {original}")
                print(f"    → {renamed}")

            print()

            # Save resource mapping for next step
            save_resource_mapping(workflow_dir, resource_mapping)
            if args.verbose:
                print(f"✓ Saved resource mapping: {workflow_dir / 'resource_mapping.json'}")
                print()
        else:
            print("ℹ️  No resources to copy (no images in questions)")
            print()

            # Save empty mapping
            save_resource_mapping(workflow_dir, {})

        # Print summary
        print("=" * 70)
        print("RESOURCES COPIED SUCCESSFULLY")
        print("=" * 70)
        print(f"Resources directory: {resources_dir}")
        print(f"Copied files:        {len(resource_mapping)}")
        print()

        # Print next steps
        print("=" * 70)
        print("NEXT STEP")
        print("=" * 70)
        print("Run step 4 to generate QTI XML files:")
        print(f"  python scripts/step4_generate_xml.py")
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
