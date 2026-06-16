#!/usr/bin/env python3
"""
QTI Generator for Inspera - CLI Tool

Convert markdown quiz files to QTI 2.2 packages for Inspera import.
"""

import argparse
import sys
from pathlib import Path

from src.parser import MarkdownQuizParser
from src.generator import XMLGenerator
from src.packager import QTIPackager
from src.error_handler import ParsingError, ErrorSuggester
from src.generator.resource_manager import (
    ResourceManager,
    has_errors,
    has_warnings,
    print_issues
)
import re
import os
from typing import Dict


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
    def replace_image(match):
        alt = match.group(1)
        original_path = match.group(2)
        # Extract just the filename to match resource_mapping keys
        basename = os.path.basename(original_path)
        # Use renamed path if available, otherwise keep original
        renamed = resource_mapping.get(basename, basename)
        return f'![{alt}]({renamed})'

    # Replace markdown image syntax: ![alt](path)
    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, text)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Convert markdown quiz to QTI 2.2 package for Inspera',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  qti-gen quiz.md output.zip
  qti-gen quiz.md -o EX_COURSE_quiz.zip

  # With language and images
  qti-gen quiz.md --language sv --output swedish_quiz.zip
  qti-gen quiz.md quiz.zip --images ./images/

  # Validate markdown before generating
  qti-gen quiz.md --validate-only

  # Validate resources only (pre-flight check for images)
  qti-gen quiz.md --validate-resources

  # Strict mode - treat warnings as errors
  qti-gen quiz.md output.zip --strict

  # Organized export structure (recommended)
  qti-gen quiz.md "Export QTI to Inspera/my_quiz.zip" --language sv

  # Result: output/Export QTI to Inspera/my_quiz.zip + output/my_quiz/ folder

Output Structure:
  All files are created in the 'output/' directory:
  - ZIP file: output/[path-you-specified].zip
  - Extracted folder: output/[quiz-name]/
  - Images (if any): output/[quiz-name]/resources/

The input markdown file should follow the QTI Generator markdown specification.
See docs/markdown_specification.md for details.
        """
    )

    parser.add_argument(
        'input',
        nargs='?',
        help='Input markdown quiz file'
    )

    parser.add_argument(
        'output',
        nargs='?',
        help='Output QTI package filename relative to output/ directory (default: quiz.zip). Can include subdirectories: "Export QTI to Inspera/my_quiz.zip"'
    )

    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Output QTI package filename (alternative syntax)'
    )

    parser.add_argument(
        '-l', '--language',
        default='en',
        help='Language code (default: en)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    parser.add_argument(
        '--inspect',
        metavar='PACKAGE',
        help='Inspect QTI package structure (shows tree view of ZIP contents)'
    )

    parser.add_argument(
        '--validate',
        metavar='PACKAGE',
        help='Validate QTI package structure'
    )

    parser.add_argument(
        '--no-keep-folder',
        action='store_true',
        help='Delete extracted folder after creating ZIP (keep ZIP only)'
    )

    parser.add_argument(
        '-i', '--images',
        dest='images_dir',
        help='Directory containing image files (default: same directory as input markdown file)'
    )

    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate the markdown format without generating QTI package'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat resource warnings as errors (strict validation mode for file formats, sizes, filenames)'
    )

    parser.add_argument(
        '--validate-resources',
        action='store_true',
        help='Only validate resources without generating QTI package (pre-flight check for images/files)'
    )

    args = parser.parse_args()

    # Handle inspect mode
    if args.inspect:
        packager = QTIPackager()
        try:
            tree = packager.get_package_tree(args.inspect)
            print(tree)
        except FileNotFoundError:
            print(f"Error: Package not found: {args.inspect}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error inspecting package: {e}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    # Handle validate mode
    if args.validate:
        try:
            import zipfile
            import tempfile
            import shutil

            # Extract package to temp directory
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(args.validate, 'r') as zipf:
                    # Security: validate all paths before extraction (ZIP Slip prevention)
                    temp_path = Path(temp_dir).resolve()
                    for member in zipf.namelist():
                        member_path = (temp_path / member).resolve()
                        if not member_path.is_relative_to(temp_path):
                            print(f"Blocked unsafe ZIP entry: {member}")
                            return 1
                    zipf.extractall(temp_dir)

                # Validate structure
                packager = QTIPackager()
                result = packager.validate_package(Path(temp_dir))

                if result['valid']:
                    print(f"✓ Package validation passed: {args.validate}")
                else:
                    print(f"✗ Package validation failed: {args.validate}")
                    for issue in result['issues']:
                        print(f"  ERROR: {issue}")

                if result['warnings']:
                    print("\nWarnings:")
                    for warning in result['warnings']:
                        print(f"  - {warning}")

                sys.exit(0 if result['valid'] else 1)

        except FileNotFoundError:
            print(f"Error: Package not found: {args.validate}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error validating package: {e}", file=sys.stderr)
            sys.exit(1)

    # Check that input file is provided for conversion
    if not args.input:
        print("Error: Input markdown file required (or use --inspect/--validate)", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # Validate input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Determine output filename - use input filename if not specified
    if args.output or args.output_file:
        output_file = args.output or args.output_file
    else:
        # Auto-generate from input filename (e.g., "quiz.md" → "quiz.zip")
        output_file = input_path.stem + '.zip'

    try:
        # Read markdown file
        if args.verbose:
            print(f"Reading markdown file: {input_path}")

        with open(input_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Validate if requested
        if args.validate_only or args.verbose:
            if args.verbose or args.validate_only:
                print("Validating markdown format...")

            # Add project root to path to import validate_mqg_format
            project_root = Path(__file__).parent.parent
            sys.path.insert(0, str(project_root))

            try:
                from validate_mqg_format import validate_content
                is_valid, issues = validate_content(markdown_content)

                if not is_valid:
                    print("\n✗ Validation failed with the following issues:\n")
                    error_count = 0
                    for issue in issues:
                        if issue.level == 'ERROR':
                            error_count += 1
                            print(f"  {'='*68}")
                            print(f"  ERROR #{error_count}: Question {issue.question_num} ({issue.question_id})")
                            print(f"  {'='*68}")
                            if issue.line_num:
                                print(f"  Line {issue.line_num}: {issue.message}")
                            else:
                                print(f"  {issue.message}")

                            # Add suggestions for common errors
                            if 'Invalid question type' in issue.message:
                                # Extract the invalid type from message
                                import re
                                match = re.search(r'"([^"]+)"', issue.message)
                                if match:
                                    invalid_type = match.group(1)
                                    suggestion = ErrorSuggester.suggest_question_type(invalid_type)
                                    if suggestion:
                                        print(f"\n  💡 Did you mean: {suggestion}?")
                                    print(f"\n  Valid types: multiple_choice_single, multiple_response,")
                                    print(f"               true_false, text_entry, inline_choice, match,")
                                    print(f"               hotspot, graphicgapmatch_v2, text_entry_graphic")

                            elif 'Missing @type' in issue.message:
                                print(f"\n  💡 Add after @question: line:")
                                print(f"     @type: multiple_choice_single")

                            elif 'Missing @identifier' in issue.message:
                                print(f"\n  💡 Add after @question: line:")
                                print(f"     @identifier: MC_Q{issue.question_num:03d}")

                            elif 'Missing @points' in issue.message:
                                print(f"\n  💡 Add after @question: line:")
                                print(f"     @points: 1")

                            elif 'Missing' in issue.message and 'section' in issue.message:
                                print(f"\n  💡 Check that all required @field: sections are present")
                                print(f"     for this question type")

                            print()  # Blank line between errors

                    if args.validate_only:
                        sys.exit(1)
                    else:
                        print("Continuing with generation despite validation errors...\n")
                else:
                    if args.validate_only or args.verbose:
                        print("✓ Validation passed - no issues found\n")

                    if args.validate_only:
                        sys.exit(0)

            except ImportError:
                if args.verbose:
                    print("  Warning: Could not import validate_mqg_format module")

        # Parse markdown
        if args.verbose:
            print("Parsing markdown content...")

        quiz_parser = MarkdownQuizParser(markdown_content)
        quiz_data = quiz_parser.parse()

        num_questions = len(quiz_data['questions'])
        if args.verbose:
            print(f"Found {num_questions} questions")

        if num_questions == 0:
            print("Warning: No questions found in markdown file", file=sys.stderr)
            sys.exit(1)

        # Initialize ResourceManager for resource validation and management
        # Determine media directory first
        if args.images_dir:
            media_dir = Path(args.images_dir)
            if not media_dir.exists():
                print(f"Warning: Images directory not found: {args.images_dir}", file=sys.stderr)
                media_dir = None
        else:
            # Auto-detect: use input file's parent directory
            media_dir = input_path.parent
            if args.verbose:
                print(f"Auto-detected images directory: {media_dir}")

        # Parse base directory from output path
        # This ensures ResourceManager and Packager use the same directory
        output_file_path = Path(output_file)
        if output_file_path.is_absolute():
            # Absolute path: extract parent directory
            # e.g., "/path/to/Nextcloud/quiz.zip" → "/path/to/Nextcloud/"
            output_base_dir = output_file_path.parent
        else:
            # Relative paths (including subdirs like "Export QTI to Inspera/quiz.zip")
            # use project's output/ directory
            project_root = Path(__file__).parent.parent
            output_base_dir = project_root / "output"

        resource_manager = ResourceManager(
            input_file=input_path,
            output_dir=output_base_dir,
            media_dir=media_dir,
            strict=args.strict  # Use CLI flag for strict validation mode
        )

        if args.verbose:
            print(f"ResourceManager initialised:")
            print(f"  Media directory: {resource_manager.media_dir}")

        # Validate resources BEFORE XML generation
        # This catches missing/invalid images early
        if args.verbose:
            print("Validating resources...")

        resource_issues = resource_manager.validate_resources(quiz_data['questions'])

        if resource_issues:
            print_issues(resource_issues, show_info=args.verbose)

            if has_errors(resource_issues):
                print("\n✗ Resource validation failed. Cannot proceed with generation.", file=sys.stderr)
                print("Fix the above errors and try again.\n", file=sys.stderr)
                sys.exit(1)

            if has_warnings(resource_issues):
                if args.strict:
                    print("\n✗ Resource validation failed in strict mode (warnings treated as errors).", file=sys.stderr)
                    print("Fix the above warnings or run without --strict flag.\n", file=sys.stderr)
                    sys.exit(1)
                else:
                    print("⚠️  Warnings found but continuing with generation...\n")
        else:
            if args.verbose:
                print("✓ All resources validated successfully")

        # Exit early if only validating resources (pre-flight check mode)
        if args.validate_resources:
            print("\n✓ Resource validation complete")
            if args.verbose:
                print("Exiting without generation (--validate-resources mode)")
            sys.exit(0)

        # Prepare output structure and copy resources BEFORE XML generation
        # Determine quiz name from output file
        quiz_name = Path(output_file).stem  # e.g., "quiz.zip" → "quiz"

        if args.verbose:
            print(f"Preparing output structure for: {quiz_name}")

        quiz_dir = resource_manager.prepare_output_structure(quiz_name)

        if args.verbose:
            print(f"Copying resources with question ID renaming...")

        resource_mapping = resource_manager.copy_resources(quiz_data['questions'], quiz_dir)

        if resource_mapping:
            if args.verbose:
                print(f"✓ Copied {len(resource_mapping)} resources")
                for original, renamed in resource_mapping.items():
                    print(f"    {original} → {renamed}")

            # Apply resource mapping to question data
            # This updates image paths to use renamed filenames (with question ID prefix + sanitization)
            for question in quiz_data['questions']:
                # 1. Handle explicit image field (hotspot, graphicgapmatch, text_entry_graphic)
                if 'image' in question and isinstance(question['image'], dict):
                    original_path = question['image'].get('path', '')
                    if original_path in resource_mapping:
                        question['image']['path'] = resource_mapping[original_path]
                        if args.verbose:
                            print(f"    Updated image path: {original_path} → {resource_mapping[original_path]}")

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
        else:
            if args.verbose:
                print("  No resources to copy")

        # Generate XML for each question
        if args.verbose:
            print("Generating QTI XML...")

        xml_generator = XMLGenerator()
        questions_xml = []

        for i, question in enumerate(quiz_data['questions'], 1):
            if args.verbose:
                print(f"  Generating question {i}/{num_questions}: {question.get('identifier', 'unknown')}")

            try:
                xml_content = xml_generator.generate_question(
                    question,
                    language=args.language
                )

                questions_xml.append((
                    question.get('identifier', f'Q{i:03d}'),
                    xml_content
                ))

            except Exception as e:
                # Enhanced error message with question context
                q_id = question.get('identifier', f'Q{i:03d}')
                q_type = question.get('type', 'unknown')
                q_title = question.get('title', 'Unknown Title')

                print(f"\n{'='*70}", file=sys.stderr)
                print(f"ERROR: Failed to generate question {i}/{num_questions}", file=sys.stderr)
                print(f"{'='*70}", file=sys.stderr)
                print(f"Question ID: {q_id}", file=sys.stderr)
                print(f"Question Type: {q_type}", file=sys.stderr)
                print(f"Title: {q_title}", file=sys.stderr)
                print(f"\nError Details: {str(e)}", file=sys.stderr)

                # Suggest fix based on question type
                if 'KeyError' in str(type(e).__name__):
                    print(f"\n💡 Suggestion: Missing required field for {q_type} questions.", file=sys.stderr)
                    print(f"   Check that all required sections are present in the markdown.", file=sys.stderr)

                print(f"{'='*70}\n", file=sys.stderr)

                if not args.verbose:
                    print("Run with --verbose for full traceback", file=sys.stderr)
                else:
                    import traceback
                    traceback.print_exc()

                sys.exit(1)

        # Package into QTI ZIP
        if args.verbose:
            print("Creating QTI package...")

        packager = QTIPackager()

        # Prepare metadata with questions for labels
        package_metadata = {
            'test_metadata': quiz_data['metadata'].get('test_metadata', {}),
            'questions': quiz_data['questions']  # Include full question metadata for labels
        }

        # NOTE: ResourceManager already copied resources to output_base_dir
        # Packager only handles XML generation and ZIP creation
        # Reuse the same output_base_dir that was calculated earlier (line 353)
        result = packager.create_package(
            questions_xml,
            package_metadata,
            output_file,
            keep_folder=not args.no_keep_folder,
            base_dir=str(output_base_dir)
        )

        # Display results
        print(f"\n✓ Successfully created QTI package:")
        if result['folder_path']:
            print(f"  Folder: {result['folder_path']}")
        print(f"  ZIP: {result['zip_path']}")
        print(f"  Questions: {num_questions}")
        print(f"  Language: {args.language}")

        if result['folder_path']:
            print(f"\n→ Browse package contents: {result['folder_path']}")
        print(f"→ Import ZIP into Inspera: {result['zip_path']}")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
