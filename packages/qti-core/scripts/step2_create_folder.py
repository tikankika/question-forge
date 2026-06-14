#!/usr/bin/env python3
"""
Step 2: Create Output Folder Structure

Creates the output directory structure for QTI generation.
By default, uses the markdown filename as the quiz name.

Usage:
    python scripts/step2_create_folder.py <markdown_file> [options]

Options:
    --output-name NAME     Override quiz name (default: use markdown filename)
    --output-dir DIR       Output base directory (default: ./output)
    -v, --verbose         Show detailed information

Exit codes:
    0 = Success
    1 = Error (file not found, etc.)

Example:
    python scripts/step2_create_folder.py input/quiz.md
    python scripts/step2_create_folder.py input/quiz.md --output-name my_quiz
    python scripts/step2_create_folder.py input/quiz.md --output-dir ~/exports
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime


# Add project root to path
project_root = Path(__file__).parent.parent


def load_workflow_settings() -> dict:
    """Load workflow settings from .workflow_settings.json if it exists."""
    settings_file = project_root / ".workflow_settings.json"

    if not settings_file.exists():
        return None

    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('settings')
    except Exception as e:
        print(f"Warning: Could not load workflow settings: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Step 2: Create output folder structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/step2_create_folder.py quiz.md
  python scripts/step2_create_folder.py quiz.md --output-name evolution_test
  python scripts/step2_create_folder.py quiz.md --output-dir output

This is Step 2 of the QTI generation pipeline.
After folder creation, run step3_copy_resources.py.
        """
    )

    parser.add_argument(
        'markdown_file',
        nargs='?',
        type=str,
        help='Path to markdown quiz file (optional if .workflow_settings.json exists)'
    )

    parser.add_argument(
        '--output-name',
        type=str,
        help='Override quiz name (default: use markdown filename without extension)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output base directory (default: ./output)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information'
    )

    args = parser.parse_args()

    # Try to load from workflow settings if markdown_file not provided
    if not args.markdown_file:
        workflow_settings = load_workflow_settings()
        if not workflow_settings:
            print("✗ Error: No markdown file specified and no .workflow_settings.json found", file=sys.stderr)
            print("  Either provide markdown_file argument or run interactive_qti.py first", file=sys.stderr)
            sys.exit(1)

        # Use settings from workflow file
        markdown_file = workflow_settings['markdown_file']
        output_name = args.output_name if args.output_name else workflow_settings['output_name']
        output_dir = args.output_dir if args.output_dir != 'output' else workflow_settings['output_dir']

        if args.verbose:
            print("Loaded settings from .workflow_settings.json")
    else:
        # Use command-line arguments
        markdown_file = args.markdown_file
        output_name = args.output_name
        output_dir = args.output_dir

    # Check file exists
    markdown_path = Path(markdown_file).resolve()
    if not markdown_path.exists():
        print(f"✗ Error: File not found: {markdown_file}", file=sys.stderr)
        sys.exit(1)

    # Determine quiz name
    if output_name:
        quiz_name = output_name
        if args.verbose:
            print(f"Using specified quiz name: {quiz_name}")
    else:
        # Use markdown filename without extension
        quiz_name = markdown_path.stem
        if args.verbose:
            print(f"Using markdown filename as quiz name: {quiz_name}")

    # Determine output base directory
    output_base = Path(output_dir).resolve()

    # Print step info
    print("=" * 70)
    print("STEP 2: CREATE OUTPUT FOLDER STRUCTURE")
    print("=" * 70)
    print(f"Input file:     {markdown_path}")
    print(f"Quiz name:      {quiz_name}")
    print(f"Output base:    {output_base}")
    print()

    # Create directory structure
    quiz_dir = output_base / quiz_name
    resources_dir = quiz_dir / "resources"
    workflow_dir = quiz_dir / ".workflow"

    try:
        # Create directories
        quiz_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {quiz_dir}/")

        resources_dir.mkdir(exist_ok=True)
        print(f"✓ Created: {resources_dir}/")

        workflow_dir.mkdir(exist_ok=True)
        print(f"✓ Created: {workflow_dir}/ (workflow metadata)")
        print()

        # Save metadata for next steps
        metadata = {
            'step': 'step2_create_folder',
            'timestamp': datetime.now().isoformat(),
            'input_file': str(markdown_path),
            'quiz_name': quiz_name,
            'quiz_dir': str(quiz_dir),
            'resources_dir': str(resources_dir),
            'output_base': str(output_base)
        }

        metadata_file = workflow_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        if args.verbose:
            print(f"✓ Saved workflow metadata: {metadata_file}")
            print()

        # Print summary
        print("=" * 70)
        print("FOLDER STRUCTURE CREATED")
        print("=" * 70)
        print(f"Quiz directory: {quiz_dir}")
        print(f"Resources:      {resources_dir}")
        print(f"Metadata:       {metadata_file}")
        print()

        # Print next steps
        print("=" * 70)
        print("NEXT STEP")
        print("=" * 70)
        print("Run step 3 to copy and rename resources:")
        print(f"  python scripts/step3_copy_resources.py")
        print()
        print("(Step 3 will read metadata from .workflow/metadata.json automatically)")
        print()

        sys.exit(0)

    except Exception as e:
        print(f"✗ Error creating directories: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
