#!/usr/bin/env python3
"""
Step 1: Validate Markdown Format

Validates a markdown quiz file against QFMD v6.5 format requirements.
This ensures the file is correctly formatted before proceeding with QTI generation.

Usage:
    python scripts/step1_validate.py <markdown_file> [--verbose]

Exit codes:
    0 = Valid (ready for next step)
    1 = Validation errors found
    2 = File not found or other error

Example:
    python scripts/step1_validate.py input/quiz.md
    python scripts/step1_validate.py input/quiz.md --verbose
"""

import sys
import argparse
from pathlib import Path

# Add project root to path to import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from validate_mqg_format import validate_markdown_file


def main():
    parser = argparse.ArgumentParser(
        description='Step 1: Validate markdown quiz file format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/step1_validate.py quiz.md
  python scripts/step1_validate.py quiz.md --verbose

This is Step 1 of the QTI generation pipeline.
After validation passes, run step2_create_folder.py.
        """
    )

    parser.add_argument(
        'markdown_file',
        type=str,
        help='Path to markdown quiz file'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed validation information'
    )

    args = parser.parse_args()

    # Check file exists
    markdown_path = Path(args.markdown_file)
    if not markdown_path.exists():
        print(f"✗ Error: File not found: {args.markdown_file}", file=sys.stderr)
        sys.exit(2)

    # Print step info
    print("=" * 70)
    print("STEP 1: VALIDATE MARKDOWN FORMAT")
    print("=" * 70)
    print(f"Input file: {markdown_path}")
    print()

    # Validate using existing validator
    report = validate_markdown_file(markdown_path, verbose=args.verbose)

    # Print report
    report.print_report()

    # Print next steps
    if report.is_valid():
        print()
        print("=" * 70)
        print("NEXT STEP")
        print("=" * 70)
        print("Run step 2 to create output folder:")
        print(f"  python scripts/step2_create_folder.py {args.markdown_file}")
        print()

    # Exit with appropriate code
    sys.exit(0 if report.is_valid() else 1)


if __name__ == '__main__':
    main()
