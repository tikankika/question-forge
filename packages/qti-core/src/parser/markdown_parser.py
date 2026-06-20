"""
Markdown Quiz Parser - v6.5 Format

Parses markdown files containing quiz questions in QFMD v6.5 format.
Extracts YAML frontmatter and individual question data.

v6.5 Format:
    # Q001 Title
    ^question Q001
    ^type multiple_choice_single
    ^identifier MC_Q001
    ^points 1
    ^labels #label1 #label2

    @field: question_text
    Content...
    @end_field

    @field: options
    ^Shuffle Yes
    A. Option 1
    B. Option 2
    @end_field

    @field: feedback

    @@field: general_feedback
    Content...
    @@end_field

    @@field: correct_feedback
    Content...
    @@end_field

    @end_field
"""

import os
import re
import yaml
import logging
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple

from ..xml_utils import escape_xml, sanitize_identifier

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RequiredField:
    """A required ^field header and the messages for each failure branch."""
    name: str
    value_pattern: str            # capture group, e.g. r"(\S+)" or r"(\d+)"
    not_at_start_message: str
    not_at_start_suggestion: str
    colon_suggestion: str
    missing_suggestion: str
    capture: bool = False         # if True, a successful match becomes the question id


# Required header fields, validated in order by MarkdownQuizParser.validate().
REQUIRED_HEADER_FIELDS = [
    RequiredField(
        name="type",
        value_pattern=r"(\S+)",
        not_at_start_message="^type not at start of line - each metadata field must be on its own line",
        not_at_start_suggestion="Put ^type on its own line",
        colon_suggestion="Remove the colon: ^type multiple_choice_single",
        missing_suggestion="Add: ^type multiple_choice_single (or other valid type)",
    ),
    RequiredField(
        name="identifier",
        value_pattern=r"(\S+)",
        not_at_start_message="^identifier not at start of line",
        not_at_start_suggestion="Put ^identifier on its own line",
        colon_suggestion="Remove the colon: ^identifier Q001",
        missing_suggestion="Add: ^identifier Q001",
        capture=True,
    ),
    RequiredField(
        name="points",
        value_pattern=r"(\d+)",
        not_at_start_message="^points not at start of line or invalid value",
        not_at_start_suggestion="Put ^points on its own line with integer value: ^points 1",
        colon_suggestion="Remove the colon: ^points 1",
        missing_suggestion="Add: ^points 1",
    ),
]


def check_required_field(
    field: RequiredField, header_section: str
) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    """Validate one required ^field in a question header.

    Returns (error, captured): `error` is an error dict (field/message/suggestion)
    or None when the field is present and well-formed; `captured` is the matched
    value when `field.capture` is set, else None.
    """
    match = re.search(rf'^\^{field.name}\s+{field.value_pattern}', header_section, re.MULTILINE)
    if match:
        return None, (match.group(1).strip() if field.capture else None)

    if re.search(rf'^\^{field.name}:', header_section, re.MULTILINE):
        message = f'^{field.name} has colon - QFMD v6.5 uses "^{field.name} value" not "^{field.name}: value"'
        suggestion = field.colon_suggestion
    elif re.search(rf'\^{field.name}', header_section):
        message = field.not_at_start_message
        suggestion = field.not_at_start_suggestion
    else:
        message = f'Missing ^{field.name} field'
        suggestion = field.missing_suggestion
    return {'field': field.name, 'message': message, 'suggestion': suggestion}, None


def validate_match_question_points(question_data: Dict) -> Tuple[bool, str, Optional[int]]:
    """
    Validate that match questions have correct point values.

    Args:
        question_data: Parsed question dictionary

    Returns:
        Tuple of (is_valid, error_message, corrected_points)
    """
    if question_data.get('question_type') != 'match':
        return True, "", None

    # Count premises
    premises = question_data.get('premises', [])
    premise_count = len(premises)

    # Get declared points
    declared_points = question_data.get('points', 1)

    # Check if points match premise count
    if declared_points != premise_count:
        return False, (
            f"Match question {question_data.get('identifier')} has "
            f"{premise_count} premises but Points: {declared_points}. "
            f"Should be Points: {premise_count}"
        ), premise_count

    return True, "", None


def validate_point_format(question_data: Dict) -> Tuple[bool, str, Optional[int]]:
    """
    Validate that points are integers, not floats.

    Args:
        question_data: Parsed question dictionary

    Returns:
        Tuple of (is_valid, warning_message, corrected_points)
    """
    points = question_data.get('points')

    if isinstance(points, float) and points == int(points):
        return False, (
            f"Question {question_data.get('identifier')} has "
            f"Points: {points} (float). Should be {int(points)} (integer)"
        ), int(points)

    return True, "", None


def parse_hashtag_list(value: str) -> List[str]:
    """Split a space-separated hashtag string (e.g. "#a #b") into bare tokens."""
    return [token.strip().lstrip('#') for token in value.split() if token.strip()]


class MarkdownQuizParser:
    """Parse markdown quiz files into structured data."""

    def __init__(self, markdown_content: str):
        """
        Initialize parser with markdown content.

        Args:
            markdown_content: Full markdown file content as string
        """
        self.content = markdown_content
        self.metadata = {}
        self.questions = []

    def parse(self) -> Dict[str, Any]:
        """
        Parse the markdown content and extract all data.

        Returns:
            Dictionary containing:
                - metadata: Test-level configuration
                - questions: List of parsed question dictionaries
        """
        self._extract_frontmatter()
        self._extract_questions()

        return {
            'metadata': self.metadata,
            'questions': self.questions
        }

    def validate(self) -> Dict[str, Any]:
        """
        Validate markdown content and collect ALL errors.

        Uses the SAME parsing logic as parse(), but collects errors
        instead of failing silently. This is the source of truth for
        validation - validate_mqg_format.py should call this method.

        Returns:
            Dictionary containing:
                - valid: bool - True if no errors
                - metadata: Test-level configuration
                - questions: List of successfully parsed questions
                - errors: List of error dicts with question_id, message, suggestion
        """
        errors = []

        # Extract frontmatter (same as parse)
        self._extract_frontmatter()

        # Get content after frontmatter/markers
        content = self.content

        # Remove YAML frontmatter if present
        if content.strip().startswith('---'):
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if match and ':' in match.group(1):
                content = content[match.end():]

        # Find ===QUESTIONS=== marker
        questions_marker = '===QUESTIONS==='
        if questions_marker in content:
            content = content.split(questions_marker, 1)[1]

        # Split by question headers
        question_pattern = r'\n(?=# Q\d+[A-Z]?\s)'
        blocks = re.split(question_pattern, content)

        # Filter to actual question blocks
        question_blocks = []
        for block in blocks:
            block = block.strip()
            if block and re.match(r'^# Q\d+[A-Z]?\s', block):
                question_blocks.append(block)

        # Validate each question block
        questions = []
        for idx, block in enumerate(question_blocks, 1):
            q_errors = []
            q_id = f'Q{idx:03d}'

            # Extract question ID from header
            header_match = re.match(r'^# (Q\d+[A-Z]?)\s', block)
            if header_match:
                q_id = header_match.group(1)

            # Get header section (before @field:)
            header_section = block.split('\n@field:')[0] if '\n@field:' in block else block

            # Validate required header fields (^type / ^identifier / ^points)
            # MUST be at start of line (v6.5: ^key value format, NO colon).
            for required in REQUIRED_HEADER_FIELDS:
                error, captured = check_required_field(required, header_section)
                if error:
                    q_errors.append(error)
                elif captured is not None:
                    q_id = captured

            # Add errors with question context
            for err in q_errors:
                errors.append({
                    'question_num': idx,
                    'question_id': q_id,
                    'field': err['field'],
                    'message': err['message'],
                    'suggestion': err['suggestion']
                })

            # Try to parse the question if no critical errors
            if not q_errors:
                try:
                    question_data = self._parse_question_block(block)
                    if question_data:
                        # Validate question-type-specific fields
                        type_errors = self._validate_question_type_fields(question_data, idx, q_id)
                        if type_errors:
                            for err in type_errors:
                                errors.append(err)
                        else:
                            questions.append(question_data)
                    else:
                        errors.append({
                            'question_num': idx,
                            'question_id': q_id,
                            'field': 'general',
                            'message': 'Question block could not be parsed',
                            'suggestion': 'Check that all required fields are present and correctly formatted'
                        })
                except Exception as e:
                    errors.append({
                        'question_num': idx,
                        'question_id': q_id,
                        'field': 'general',
                        'message': f'Parse error: {str(e)}',
                        'suggestion': 'Check question format against v6.5 specification'
                    })

        return {
            'valid': len(errors) == 0,
            'metadata': self.metadata,
            'questions': questions,
            'errors': errors,
            'total_questions': len(question_blocks),
            'parsed_questions': len(questions)
        }

    def _validate_question_type_fields(self, question_data: Dict[str, Any], q_num: int, q_id: str) -> List[Dict[str, Any]]:
        """
        Validate question-type-specific fields.

        This ensures that if validate() passes, export will work.
        Each question type has specific required fields that the XML generator expects.
        """
        errors = []
        q_type = question_data.get('question_type', '')

        def add_error(field: str, message: str, suggestion: str):
            errors.append({
                'question_num': q_num,
                'question_id': q_id,
                'field': field,
                'message': message,
                'suggestion': suggestion
            })

        # text_entry: requires blanks
        if q_type == 'text_entry':
            blanks = question_data.get('blanks', [])
            if not blanks:
                add_error(
                    'blanks',
                    'text_entry question requires blanks definition',
                    'Use @@field: blank_1 with ^Correct_Answers list. See tests/fixtures/v65/text_entry.md'
                )

        # text_entry_math: requires blanks
        elif q_type == 'text_entry_math':
            blanks = question_data.get('blanks', [])
            if not blanks:
                add_error(
                    'blanks',
                    'text_entry_math question requires blanks definition',
                    'Use @@field: blank_1 with ^Correct_Answers list'
                )

        # text_entry_numeric: requires blanks
        elif q_type == 'text_entry_numeric':
            blanks = question_data.get('blanks', [])
            if not blanks:
                add_error(
                    'blanks',
                    'text_entry_numeric question requires blanks definition',
                    'Use @@field: blank_1 with ^Correct_Answers list'
                )

        # inline_choice: requires inline_choices and correct_answers_dict
        elif q_type == 'inline_choice':
            inline_choices = question_data.get('inline_choices', {})
            correct_answers = question_data.get('correct_answers_dict', {})
            if not inline_choices:
                add_error(
                    'inline_choices',
                    'inline_choice question requires dropdown definitions',
                    'Use @field: dropdown_1 with options marked with * for correct. See tests/fixtures/v65/inline_choice.md'
                )
            elif not correct_answers:
                add_error(
                    'correct_answers_dict',
                    'inline_choice question requires correct answers marked',
                    'Mark correct options with * at the end: "- correct answer*"'
                )

        # multiple_choice_single: requires options and answer
        elif q_type == 'multiple_choice_single':
            options = question_data.get('options', [])
            answer = question_data.get('correct_answer') or question_data.get('answer')
            if not options:
                add_error(
                    'options',
                    'multiple_choice_single question requires options',
                    'Add @field: options with A), B), C), D) choices'
                )
            if not answer:
                add_error(
                    'answer',
                    'multiple_choice_single question requires correct answer',
                    'Add @field: answer with the correct letter (e.g., B)'
                )

        # multiple_response: requires options and correct_answers
        elif q_type == 'multiple_response':
            options = question_data.get('options', [])
            correct_answers = question_data.get('correct_answers', [])
            if not options:
                add_error(
                    'options',
                    'multiple_response question requires options',
                    'Add @field: options with [correct] markers or @field: correct_answers'
                )
            if not correct_answers:
                add_error(
                    'correct_answers',
                    'multiple_response question requires correct answers',
                    'Mark correct options with [correct] or add @field: correct_answers'
                )

        # true_false: requires answer
        elif q_type == 'true_false':
            answer = question_data.get('correct_answer') or question_data.get('answer')
            if not answer:
                add_error(
                    'answer',
                    'true_false question requires answer',
                    'Add @field: answer with True or False'
                )

        # match: requires pairs
        elif q_type == 'match':
            pairs = question_data.get('pairs', [])
            if not pairs:
                add_error(
                    'pairs',
                    'match question requires matching pairs',
                    'Add @field: pairs with left|right format'
                )

        # hotspot: requires image and hotspots
        elif q_type == 'hotspot':
            image = question_data.get('image')
            hotspots = question_data.get('hotspots', [])
            if not image:
                add_error(
                    'image',
                    'hotspot question requires image',
                    'Include an image in the question_text: ![alt](path/to/image.png)'
                )
            if not hotspots:
                add_error(
                    'hotspots',
                    'hotspot question requires hotspot definitions',
                    'Add @field: hotspots with coordinates'
                )

        # graphicgapmatch_v2: requires image and drop_zones
        elif q_type == 'graphicgapmatch_v2':
            image = question_data.get('image')
            drop_zones = question_data.get('drop_zones', [])
            if not image:
                add_error(
                    'image',
                    'graphicgapmatch question requires image',
                    'Include an image in the question_text'
                )
            if not drop_zones:
                add_error(
                    'drop_zones',
                    'graphicgapmatch question requires drop zones',
                    'Add @field: drop_zones with zone definitions'
                )

        # essay, text_area, audio_record: no special requirements (just question_text)
        # These types are more flexible

        return errors

    def _extract_frontmatter(self) -> None:
        """Extract and parse YAML frontmatter from markdown, or extract from markdown structure."""
        # Match YAML frontmatter between --- delimiters AT THE START OF FILE ONLY
        # \A ensures we match only at the absolute beginning of the string
        frontmatter_pattern = r'\A---\s*\n(.*?)\n---'
        match = re.search(frontmatter_pattern, self.content, re.DOTALL)

        if match:
            yaml_content = match.group(1)
            try:
                self.metadata = yaml.safe_load(yaml_content)
                logger.info("Successfully parsed YAML frontmatter")
            except yaml.YAMLError as e:
                logger.warning(f"Failed to parse YAML frontmatter: {e}. Extracting metadata from markdown structure.")
                self.metadata = self._extract_metadata_from_markdown()
        else:
            # No YAML frontmatter - extract metadata from markdown structure
            logger.warning("No YAML frontmatter found. Extracting metadata from markdown structure.")
            self.metadata = self._extract_metadata_from_markdown()

    def _extract_metadata_from_markdown(self) -> Dict[str, Any]:
        """
        Extract test metadata from markdown structure when YAML frontmatter is missing.

        Looks for patterns like:
        # Title
        **Course**: EX_COURSE
        **Module**: L1b
        etc.

        Returns:
            Dictionary with test_metadata structure
        """
        metadata = {
            'test_metadata': {
                'title': 'Untitled Assessment',
                'identifier': 'ASSESSMENT_001',
                'language': 'en',
                'duration': 120
            }
        }

        # Extract title from first H1 heading
        title_match = re.search(r'^#\s+(.+)$', self.content, re.MULTILINE)
        if title_match:
            metadata['test_metadata']['title'] = title_match.group(1).strip()

        # Extract before first question separator (---)
        header_section = self.content.split('\n---\n')[0] if '\n---\n' in self.content else self.content[:500]

        # Look for **Field**: Value patterns
        course_match = re.search(r'\*\*Course\*\*:\s*(.+?)(?=\n|$)', header_section)
        if course_match:
            course_text = course_match.group(1).strip()
            # Extract course code (e.g., "EX_COURSE - Emissions..." -> "EX_COURSE")
            course_code = re.match(r'([A-Z0-9]+)', course_text)
            if course_code:
                metadata['test_metadata']['identifier'] = f"{course_code.group(1)}_ASSESSMENT"

        # Extract module info
        module_match = re.search(r'\*\*Module\*\*:\s*(.+?)(?=\n|$)', header_section)
        if module_match:
            module_text = module_match.group(1).strip()
            # Append to identifier
            if metadata['test_metadata']['identifier'] != 'ASSESSMENT_001':
                module_code = re.match(r'([A-Za-z0-9]+)', module_text)
                if module_code:
                    metadata['test_metadata']['identifier'] += f"_{module_code.group(1)}"

        # Try to detect language from content
        # Simple heuristic: look for Swedish characters
        if any(char in self.content for char in ['å', 'ä', 'ö', 'Å', 'Ä', 'Ö']):
            metadata['test_metadata']['language'] = 'sv'

        return metadata

    def _extract_questions(self) -> None:
        """Extract individual questions from markdown content (v6.3 format)."""
        content = self.content

        # Remove YAML frontmatter if present at start
        if content.strip().startswith('---'):
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if match and ':' in match.group(1):
                content = content[match.end():]

        # Find ===QUESTIONS=== marker and skip document header
        questions_marker = '===QUESTIONS==='
        if questions_marker in content:
            content = content.split(questions_marker, 1)[1]

        # Split by question headers: # Q001, # Q002, etc.
        question_pattern = r'\n(?=# Q\d+[A-Z]?\s)'
        blocks = re.split(question_pattern, content)

        # Filter to actual question blocks
        question_blocks = []
        for block in blocks:
            block = block.strip()
            if block and re.match(r'^# Q\d+[A-Z]?\s', block):
                question_blocks.append(block)

        logger.info(f"Found {len(question_blocks)} questions...")

        for idx, block in enumerate(question_blocks, 1):
            try:
                question_data = self._parse_question_block(block)
                if question_data:
                    # Validate and auto-correct match question points
                    is_valid, error, corrected_points = validate_match_question_points(question_data)
                    if not is_valid:
                        logger.warning(error)
                        question_data['points'] = corrected_points
                        logger.info(f"  → Auto-corrected to Points: {corrected_points}")

                    # Validate and auto-correct point format (float vs int)
                    is_valid, warning, corrected_points = validate_point_format(question_data)
                    if not is_valid:
                        logger.warning(warning)
                        question_data['points'] = corrected_points
                        logger.info(f"  → Auto-corrected to Points: {corrected_points}")

                    self.questions.append(question_data)
                    logger.debug(f"Successfully parsed question {idx}: {question_data.get('identifier', 'UNKNOWN')}")
                else:
                    logger.warning(f"Question block {idx} could not be parsed")
            except Exception as e:
                logger.error(f"Failed to parse question block {idx}: {e}")
                continue

        logger.info(f"Successfully parsed {len(self.questions)} questions")

    def _parse_question_block(self, block: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single question block.

        Args:
            block: Markdown text for one question

        Returns:
            Dictionary with question data or None if parsing fails
        """
        question = {}

        # Extract title from first heading
        title_match = re.search(r'^#\s+(.+)$', block, re.MULTILINE)
        if title_match:
            question['title'] = title_match.group(1).strip()

        # Extract metadata fields (Type, Identifier, Points, etc.)
        metadata_fields = self._extract_metadata_fields(block)
        question.update(metadata_fields)

        # Extract sections (Question Text, Options, Answer, Feedback)
        question.update(self._extract_sections(block, metadata_fields))

        return question if question.get('identifier') else None

    def _extract_metadata_fields(self, block: str) -> Dict[str, Any]:
        """Extract ^ prefixed metadata fields from question block header (v6.5 format)."""
        fields = {}

        # Only extract metadata from header (before first @field: section)
        header_match = re.search(r'^(.*?)(?=\n@field:)', block, re.DOTALL)
        if not header_match:
            header_text = block
        else:
            header_text = header_match.group(1)

        # Extract title from # Q001 Title header
        title_match = re.match(r'^# Q\d+[A-Z]?\s+(.+)$', header_text, re.MULTILINE)
        if title_match:
            fields['title'] = title_match.group(1).strip()

        # Extract ^type (v6.5 format)
        type_match = re.search(r'^\^type\s+(.+)$', header_text, re.MULTILINE)
        if type_match:
            fields['question_type'] = type_match.group(1).strip()

        # Extract ^identifier (v6.5 format)
        # Sanitise at parse time: the identifier flows unescaped into XML
        # attributes (item + manifest) and into the output filename, so restrict
        # it to a safe token to prevent XML injection and path traversal.
        id_match = re.search(r'^\^identifier\s+(.+)$', header_text, re.MULTILINE)
        if id_match:
            fields['identifier'] = sanitize_identifier(id_match.group(1).strip())

        # Extract ^points (v6.5 format)
        points_match = re.search(r'^\^points\s+(.+)$', header_text, re.MULTILINE)
        if points_match:
            points_value = points_match.group(1).strip()
            if points_value.replace('.', '', 1).isdigit():
                points_float = float(points_value)
                if points_float == int(points_float):
                    fields['points'] = int(points_float)
                else:
                    fields['points'] = points_float
            else:
                fields['points'] = 1

        # Extract ^labels (v6.5 format) - Inspera "Labels" (free-form tags)
        labels_match = re.search(r'^\^labels\s+(.+)$', header_text, re.MULTILINE)
        if labels_match:
            label_value = labels_match.group(1).strip()
            # Space-separated: "#label1 #label2 #label3"
            fields['labels'] = parse_hashtag_list(label_value)

        # Extract ^tags and use as labels if ^labels not present
        # ^tags format: "#EXAMPLE_COURSE #topic1 #topic2 #Remember #Easy"
        tags_match = re.search(r'^\^tags\s+(.+)$', header_text, re.MULTILINE)
        if tags_match:
            tags_value = tags_match.group(1).strip()
            # Parse space-separated hashtags
            tags_list = parse_hashtag_list(tags_value)
            fields['tags'] = tags_list
            # If no ^labels field, use ^tags as labels for Inspera export
            if 'labels' not in fields:
                fields['labels'] = tags_list

        # Extract ^custom_metadata (v6.5 format)
        # Format: ^custom_metadata Field name: value OR ^custom_metadata Field name: v1, v2, v3
        custom_metadata_matches = re.findall(r'^\^custom_metadata\s+(.+)$', header_text, re.MULTILINE)
        if custom_metadata_matches:
            custom_metadata = {}
            for match in custom_metadata_matches:
                if ':' in match:
                    field_name, values_str = match.split(':', 1)
                    field_name = field_name.strip()
                    # Parse comma-separated values
                    values = [v.strip() for v in values_str.split(',') if v.strip()]
                    if field_name in custom_metadata:
                        custom_metadata[field_name].extend(values)
                    else:
                        custom_metadata[field_name] = values
            fields['custom_metadata'] = custom_metadata

        # Extract ^title (v6.5 format - if separate from header)
        title_field_match = re.search(r'^\^title\s+(.+)$', header_text, re.MULTILINE)
        if title_field_match:
            fields['title'] = title_field_match.group(1).strip()

        # Extract ^language (v6.5 format - optional)
        lang_match = re.search(r'^\^language\s+(.+)$', header_text, re.MULTILINE)
        if lang_match:
            fields['language'] = lang_match.group(1).strip()

        return fields

    def _extract_fields_v65(self, block: str) -> Dict[str, Any]:
        """
        Extract fields using v6.5 @field: / @end_field and @@field: / @@end_field markers.

        v6.5 format uses:
        - @field: / @end_field for top-level fields
        - @@field: / @@end_field for nested subfields (e.g., inside feedback)
        - ^Key Value for in-field metadata

        Returns a dict with field IDs and their content (which may include nested subfields).
        """
        field_contents = {}
        lines = block.split('\n')

        # Stack to track nested fields: [{field_id, content_lines, is_subfield}, ...]
        field_stack = []

        for line in lines:
            # Skip markdown header lines (###, ####) - they're for human readability only
            if re.match(r'^#{2,4}\s+', line):
                continue

            # Check for @@field: identifier (start of subfield - v6.5)
            subfield_match = re.match(r'^@@field:\s*(\w+)', line)
            if subfield_match:
                field_id = subfield_match.group(1)
                field_stack.append({'field_id': field_id, 'content': [], 'is_subfield': True})
                continue

            # Check for @@end_field (end of subfield - v6.5)
            if line.strip() == '@@end_field':
                if field_stack and field_stack[-1].get('is_subfield'):
                    completed = field_stack.pop()
                    content_str = '\n'.join(completed['content']).strip()
                    # Add subfield to parent field's content as structured data
                    if field_stack:
                        parent = field_stack[-1]
                        if 'subfields' not in parent:
                            parent['subfields'] = {}
                        parent['subfields'][completed['field_id']] = content_str
                    else:
                        # Orphan subfield - add directly
                        field_contents[completed['field_id']] = content_str
                continue

            # Check for @field: identifier (start of top-level field)
            field_match = re.match(r'^@field:\s*(\w+)', line)
            if field_match:
                field_id = field_match.group(1)
                field_stack.append({'field_id': field_id, 'content': [], 'is_subfield': False})
                continue

            # Check for @end_field (end of top-level field)
            if line.strip() == '@end_field':
                if field_stack and not field_stack[-1].get('is_subfield'):
                    completed = field_stack.pop()
                    content_str = '\n'.join(completed['content']).strip()

                    # If field has subfields, return structured data
                    if 'subfields' in completed:
                        field_contents[completed['field_id']] = completed['subfields']
                    else:
                        # Parse in-field ^metadata
                        field_contents[completed['field_id']] = self._parse_field_content_v65(content_str)
                continue

            # Add content to current field (if any)
            if field_stack:
                field_stack[-1]['content'].append(line)

        return field_contents

    def _parse_field_content_v65(self, content: str) -> Dict[str, Any]:
        """
        Parse field content with ^metadata lines (v6.5 format).

        Returns dict with 'content' and 'metadata' keys.
        """
        result = {'content': '', 'metadata': {}}
        lines = content.strip().split('\n')
        content_lines = []

        for line in lines:
            # ^Key Value or ^Key (followed by content)
            if line.startswith('^'):
                match = re.match(r'^\^(\w+)\s*(.*)$', line)
                if match:
                    key = match.group(1)
                    value = match.group(2).strip() if match.group(2) else True
                    result['metadata'][key] = value
            else:
                content_lines.append(line)

        result['content'] = '\n'.join(content_lines).strip()

        # If no metadata, just return the content string for simplicity
        if not result['metadata']:
            return result['content']

        return result

    def _get_field_content(self, field_value: Any) -> str:
        """
        Extract content string from v6.5 field value.

        v6.5 field values may be:
        - str: Plain content (no ^metadata)
        - dict with 'content' and 'metadata': Field with ^metadata lines
        - dict (subfields): Nested @@field: structure

        Returns the content string for parsing.
        """
        if isinstance(field_value, str):
            return field_value
        if isinstance(field_value, dict):
            if 'content' in field_value:
                return field_value['content']
            # Dict without 'content' is subfields - return empty
            return ''
        return str(field_value) if field_value else ''

    def _get_field_metadata(self, field_value: Any) -> Dict[str, Any]:
        """
        Extract metadata dict from v6.5 field value.

        Returns the ^metadata dict for fields with in-field metadata.
        """
        if isinstance(field_value, dict) and 'metadata' in field_value:
            return field_value['metadata']
        return {}

    def _extract_sections(self, block: str, metadata_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Extract major sections from question block (v6.5 format with @end_field and @@end_field markers)."""
        sections = {}

        # v6.5: Extract fields using @field: / @end_field and @@field: / @@end_field
        # Uses stack-based parsing to handle nested subfields
        field_contents = self._extract_fields_v65(block)

        # Map field IDs to expected output keys
        if 'question_text' in field_contents:
            sections['question_text'] = self._get_field_content(field_contents['question_text'])

        # Extract Options - handle both content and metadata (e.g., ^Shuffle)
        if 'options' in field_contents:
            options_content = self._get_field_content(field_contents['options'])
            sections['options'] = self._parse_options(options_content)
            # Extract ^Shuffle metadata if present
            options_metadata = self._get_field_metadata(field_contents['options'])
            if options_metadata.get('Shuffle', '').lower() == 'yes':
                sections['shuffle_options'] = True

        # Extract Answer (single letter for multiple_choice_single)
        if 'answer' in field_contents:
            answer_text = self._get_field_content(field_contents['answer']).strip()
            single_answer = re.search(r'^([A-Z])$', answer_text, re.MULTILINE)
            if single_answer:
                sections['correct_answer'] = single_answer.group(1)
            else:
                first_letter = re.search(r'([A-Z])', answer_text)
                if first_letter:
                    sections['correct_answer'] = first_letter.group(1)

        # Extract Correct Answers (comma-separated for multiple_response)
        if 'correct_answers' in field_contents:
            answer_text = self._get_field_content(field_contents['correct_answers']).strip()
            letters = re.findall(r'([A-Z])', answer_text)
            if letters:
                sections['correct_answers'] = letters

        # Extract Pairs (for match type) - format: "1. Premise -> Response"
        if 'pairs' in field_contents:
            pairs_content = self._get_field_content(field_contents['pairs'])
            result = self._parse_pairs_genai_format(pairs_content)
            sections['premises'] = result['premises']
            sections['match_responses'] = result['responses']

        # Extract Distractors (for match type)
        if 'distractors' in field_contents:
            distractor_content = self._get_field_content(field_contents['distractors'])
            distractor_lines = distractor_content.strip().split('\n')
            distractors = []
            for line in distractor_lines:
                line = line.strip()
                if line.startswith('- '):
                    distractors.append({'text': line[2:].strip()})
            if distractors:
                # Add distractors to match_responses
                if 'match_responses' not in sections:
                    sections['match_responses'] = []
                for i, d in enumerate(distractors):
                    sections['match_responses'].append({
                        'id': f'DISTRACTOR{i+1}',
                        'letter': f'D{i+1}',
                        'text': d['text']
                    })

        # Extract Scoring - handle ^metadata format
        if 'scoring' in field_contents:
            scoring_content = self._get_field_content(field_contents['scoring'])
            scoring_metadata = self._get_field_metadata(field_contents['scoring'])
            # If scoring has ^metadata, use that
            if scoring_metadata:
                sections['scoring'] = scoring_metadata
            else:
                sections['scoring'] = self._parse_scoring_section(scoring_content)

        # Extract Blanks - handle v6.5 @@field: blank_N subfields
        if 'blanks' in field_contents:
            blanks_data = field_contents['blanks']
            if isinstance(blanks_data, dict):
                # v6.5: blanks is a dict of @@field: blank_N subfields
                blanks = []
                for field_id, content in sorted(blanks_data.items()):
                    if field_id.startswith('blank_'):
                        blank_num = field_id.replace('blank_', '')
                        blank = self._parse_blank_v65(content, blank_num)
                        if blank:
                            blanks.append(blank)
                if blanks:
                    sections['blanks'] = blanks
            else:
                # Legacy: blanks is a string with ### Blank headers
                sections['blanks'] = self._parse_blanks_section(self._get_field_content(blanks_data))

        # Check for individual blank_N fields at top level
        blank_fields = {k: v for k, v in field_contents.items() if k.startswith('blank_')}
        if blank_fields and not sections.get('blanks'):
            blanks = []
            for field_id, content in sorted(blank_fields.items()):
                blank_num = field_id.replace('blank_', '')
                blank = self._parse_blank_v65(content, blank_num)
                if blank:
                    blanks.append(blank)
            if blanks:
                sections['blanks'] = blanks

        # Extract Dropdowns (for inline_choice)
        dropdown_fields = {k: v for k, v in field_contents.items() if k.startswith('dropdown_')}
        if dropdown_fields:
            choices = {}
            correct_answers = {}
            for field_id, field_value in dropdown_fields.items():
                dropdown_num = field_id.replace('dropdown_', '')
                # Get content string (field_value might be dict with 'content' and 'metadata')
                content_str = self._get_field_content(field_value)
                options, correct = self._parse_dropdown_content(content_str)
                choices[dropdown_num] = options
                # Also check metadata for ^Correct_Answer (v6.5 format)
                if not correct:
                    metadata = self._get_field_metadata(field_value)
                    if metadata.get('Correct_Answer'):
                        correct = metadata['Correct_Answer']
                if correct:
                    correct_answers[dropdown_num] = correct
            sections['inline_choices'] = choices
            if correct_answers:
                sections['correct_answers_dict'] = correct_answers

        # For graphic question types, extract image
        question_type = metadata_fields.get('question_type', '')
        if question_type in ['hotspot', 'graphicgapmatch_v2', 'text_entry_graphic'] and sections.get('question_text'):
            # Extract first image from question text
            image_match = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', sections['question_text'])
            if image_match:
                sections['image'] = {
                    'alt': image_match.group(1),
                    'path': image_match.group(2)
                }
                # Remove the image markdown from question text, keep only the text after it
                sections['question_text'] = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)\s*\n*', '', sections['question_text'], count=1).strip()

        # Extract Options
        options_match = re.search(
            r'##\s+Options\s*\n+(.*?)(?=\n##|\Z)',
            block,
            re.DOTALL
        )
        if options_match:
            sections['options'] = self._parse_options(options_match.group(1))

        # Extract Correct Answers (plural) - for multiple_response questions
        correct_answers_match = re.search(
            r'##\s+Correct Answers\s*\n+(.*?)(?=\n##|\Z)',
            block,
            re.DOTALL
        )
        if correct_answers_match:
            answer_text = correct_answers_match.group(1).strip()
            # Parse comma-separated letters: "A, B, D, E, G" -> ['A', 'B', 'D', 'E', 'G']
            letters = re.findall(r'([A-Z])', answer_text)
            if letters:
                sections['correct_answers'] = letters

        # Extract Answer (singular) - for single choice questions
        answer_match = re.search(
            r'##\s+Answer\s*\n+(.*?)(?=\n##|\Z)',
            block,
            re.DOTALL
        )
        if answer_match:
            answer_text = answer_match.group(1).strip()
            # Check if it's a match-type answer (contains →)
            if '→' in answer_text or '->' in answer_text:
                sections['match_pairings'] = self._parse_match_pairings(answer_text)
            else:
                # Check for comma-separated answers (e.g., "A, B, C" for multiple_response)
                if ',' in answer_text:
                    letters = [x.strip() for x in re.findall(r'([A-Z])', answer_text)]
                    if letters:
                        sections['correct_answers'] = letters
                else:
                    # Single letter answer for multiple choice
                    single_answer = re.search(r'^([A-Z])$', answer_text, re.MULTILINE)
                    if single_answer:
                        sections['correct_answer'] = single_answer.group(1)
                    else:
                        # Try to extract first letter if multi-line
                        first_letter = re.search(r'([A-Z])', answer_text)
                        if first_letter:
                            sections['correct_answer'] = first_letter.group(1)

        # Extract Image section (for image-based types)
        image_match = re.search(
            r'##\s+Image\s*\n+(.*?)(?=\n##|\Z)',
            block,
            re.DOTALL
        )
        if image_match:
            sections['image'] = self._parse_image_section(image_match.group(1))

        # Extract Hotspots section (for hotspot type)
        # Try "## Hotspots" first (old format)
        hotspots_match = re.search(
            r'##\s+Hotspots\s*\n+(.*?)(?=\n##|\Z)',
            block,
            re.DOTALL
        )
        if hotspots_match:
            sections['hotspots'] = self._parse_hotspots_section(hotspots_match.group(1))
        else:
            # Try "## Hotspot Definitions" (legacy hotspot format)
            hotspot_defs_match = re.search(
                r'##\s+Hotspot Definitions\s*\n+(.*?)(?=\n##\s+[^#]|\Z)',
                block,
                re.DOTALL
            )
            if hotspot_defs_match:
                sections['hotspots'] = self._parse_hotspot_definitions(hotspot_defs_match.group(1))

        # Also extract image data from markdown image syntax in question text for hotspot questions
        if metadata_fields.get('question_type') == 'hotspot' and not sections.get('image'):
            sections['image'] = self._extract_image_from_markdown(sections.get('question_text', ''))

        # Extract Draggable Items section (for graphicgapmatch_v2)
        if metadata_fields.get('question_type') == 'graphicgapmatch_v2':
            draggable_match = re.search(
                r'##\s+Draggable Items\s*\n+(.*?)(?=\n##\s+[^#]|\Z)',
                block,
                re.DOTALL
            )
            if draggable_match:
                sections['draggable_items'] = self._parse_draggable_items(draggable_match.group(1))

            # Extract Hotspot Zones section (for graphicgapmatch_v2)
            zones_match = re.search(
                r'##\s+Hotspot Zones\s*\n+(.*?)(?=\n##\s+[^#]|\Z)',
                block,
                re.DOTALL
            )
            if zones_match:
                sections['zones'] = self._parse_hotspot_zones(zones_match.group(1))

        # Extract Premises section (for match type)
        premises_match = re.search(
            r'##\s+Premises\s*(?:\(Left Column\))?\s*\n+(.*?)(?=\n##|\Z)',
            block,
            re.DOTALL
        )
        if premises_match:
            sections['premises'] = self._parse_premises_section(premises_match.group(1))

        # Extract Choices/Responses section (for match type)
        choices_match = re.search(
            r'##\s+(?:Choices|Responses)\s*(?:\(Right Column\))?\s*\n+(.*?)(?=\n##|\Z)',
            block,
            re.DOTALL
        )
        if choices_match:
            sections['match_responses'] = self._parse_match_responses_section(choices_match.group(1))

        # Extract Scoring section (for types with custom scoring)
        scoring_match = re.search(
            r'##\s+Scoring\s*\n+(.*?)(?=\n##|\Z)',
            block,
            re.DOTALL
        )
        if scoring_match:
            sections['scoring'] = self._parse_scoring_section(scoring_match.group(1))

        # Extract Blanks section (for text_entry type) - LEGACY FALLBACK
        # Only process if v6.4 @field: blanks didn't already extract blanks
        # Support multiple formats:
        # 1. ## Blanks with ### Blank N subsections
        # 2. Individual ## Blank N sections (legacy hotspot format)
        # 3. Simplified format: ### Correct Answer + ### Accepted Alternatives
        if not sections.get('blanks'):
            blanks_match = re.search(
                r'##\s+Blanks\s*\n+(.*?)(?=\n##|\Z)',
                block,
                re.DOTALL
            )
            if blanks_match:
                sections['blanks'] = self._parse_blanks_section(blanks_match.group(1))
            else:
                # Try to find individual ## Blank N sections (legacy hotspot format)
                individual_blanks = self._parse_individual_blanks(block)
                if individual_blanks:
                    sections['blanks'] = individual_blanks
                else:
                    # Try simplified format (### Correct Answer)
                    simplified_blanks = self._parse_simplified_blanks(block)
                    if simplified_blanks:
                        sections['blanks'] = simplified_blanks

        # Extract Editor Configuration section (for text_area type)
        editor_config_match = re.search(
            r'##\s+Editor Configuration\s*\n+(.*?)(?=\n##|\Z)',
            block,
            re.DOTALL
        )
        if editor_config_match:
            config_text = editor_config_match.group(1)
            # Extract individual configuration fields
            initial_lines_match = re.search(r'\*\*Initial lines\*\*:\s*(\d+)', config_text)
            if initial_lines_match:
                sections['initial_lines'] = int(initial_lines_match.group(1))

            field_width_match = re.search(r'\*\*Field width\*\*:\s*([^\n]+)', config_text)
            if field_width_match:
                sections['field_width'] = field_width_match.group(1).strip()

            show_word_count_match = re.search(r'\*\*Show word count\*\*:\s*(true|false)', config_text, re.IGNORECASE)
            if show_word_count_match:
                sections['show_word_count'] = show_word_count_match.group(1).lower() == 'true'

            editor_prompt_match = re.search(r'\*\*Editor prompt\*\*:\s*([^\n]+)', config_text)
            if editor_prompt_match:
                sections['editor_prompt'] = editor_prompt_match.group(1).strip()

        # Extract Correct Answer (singular) for fill_in_the_blank (Evolution format)
        correct_answer_match = re.search(
            r'##\s+Correct Answer\s*\n+([^\n]+)',
            block,
            re.MULTILINE
        )
        if correct_answer_match:
            sections['correct_answer_text'] = correct_answer_match.group(1).strip()

        # Extract Correct Answers (plural) with {{N}}: format for text_entry/inline_choice (Evolution format)
        correct_answers_match = re.search(
            r'##\s+Correct Answers\s*\n+(.*?)(?=\n##|\Z)',
            block,
            re.DOTALL
        )
        if correct_answers_match:
            sections['correct_answers_dict'] = self._parse_correct_answers_dict(correct_answers_match.group(1))

        # Extract Accepted Alternatives (Evolution format)
        alternatives_match = re.search(
            r'##\s+Accepted Alternatives\s*\n+(.*?)(?=\n##|\Z)',
            block,
            re.DOTALL
        )
        if alternatives_match:
            sections['accepted_alternatives'] = self._parse_accepted_alternatives(alternatives_match.group(1))

        # Extract Inline Choices (Evolution format) - LEGACY FALLBACK
        # Only process if v6.4 @field: dropdown_N didn't already extract inline_choices
        if not sections.get('inline_choices'):
            inline_choices_match = re.search(
                r'##\s+Inline Choices\s*\n+(.*?)(?=\n##|\Z)',
                block,
                re.DOTALL
            )
            if inline_choices_match:
                sections['inline_choices'] = self._parse_inline_choices(inline_choices_match.group(1))
            else:
                # Try alternative format with ## Dropdown N sections
                dropdown_data = self._parse_dropdown_format(block)
                if dropdown_data:
                    sections['inline_choices'] = dropdown_data['choices']
                    # Also extract correct answers for inline_choice questions
                    if 'correct_answers' in dropdown_data and dropdown_data['correct_answers']:
                        if 'correct_answers_dict' not in sections:
                            sections['correct_answers_dict'] = {}
                        sections['correct_answers_dict'].update(dropdown_data['correct_answers'])

        # Extract Matching Pairs (Evolution format)
        matching_pairs_match = re.search(
            r'##\s+Matching Pairs\s*\n+(.*?)(?=\n##|\Z)',
            block,
            re.DOTALL
        )
        if matching_pairs_match:
            result = self._parse_matching_pairs_evolution(matching_pairs_match.group(1))
            sections['premises'] = result['premises']
            sections['match_responses'] = result['responses']
        else:
            # Try alternative ## Pairs format (GenAI format: "1. Premise → Response")
            pairs_match = re.search(
                r'##\s+Pairs\s*\n+(.*?)(?=\n##|\Z)',
                block,
                re.DOTALL
            )
            if pairs_match:
                result = self._parse_pairs_genai_format(pairs_match.group(1))
                sections['premises'] = result['premises']
                sections['match_responses'] = result['responses']

        # Extract Correct Matches (Evolution format)
        correct_matches_match = re.search(
            r'##\s+Correct Matches\s*\n+(.*?)(?=\n##|\Z)',
            block,
            re.DOTALL
        )
        if correct_matches_match:
            sections['match_pairings'] = self._parse_correct_matches(correct_matches_match.group(1))

        # Extract Feedback sections
        sections['feedback'] = self._extract_feedback(block, metadata_fields.get('type', ''), field_contents)

        # Convert Evolution format to xml_generator expected format
        self._convert_evolution_format_to_standard(sections, metadata_fields)

        return sections

    def _parse_options(self, options_text: str) -> List[Dict[str, str]]:
        """Parse multiple choice options - supports both manual and GenAI formats."""
        options = []

        # Pattern for options - matches BOTH formats:
        # Original: A. Option text
        # GenAI:    **A)** Option text
        # Also captures ✓ for correct answer marking
        option_pattern = r'^(?:\*\*)?([A-Z])[.)]\**\s+(.+?)(?=\n(?:\*\*)?[A-Z][.)]|\Z)'

        for match in re.finditer(option_pattern, options_text, re.MULTILINE | re.DOTALL):
            letter = match.group(1)
            text = match.group(2).strip()

            # Check if this option is marked correct with ✓
            is_correct = '✓' in text
            # Remove ✓ from text if present
            text = text.replace('✓', '').strip()

            options.append({
                'letter': letter,
                'text': text,
                'correct': is_correct
            })

        return options

    def _extract_feedback(self, block: str, question_type: str = '', field_contents: Dict[str, Any] = None) -> Dict[str, str]:
        """Extract all feedback sections (v6.5 format with @@field: subfields)."""
        feedback = {}

        # Reuse pre-parsed fields if provided, otherwise parse
        if field_contents is None:
            field_contents = self._extract_fields_v65(block)

        # Map feedback subfield IDs to expected output keys
        field_mapping = {
            'general_feedback': 'general',
            'correct_feedback': 'correct',
            'incorrect_feedback': 'incorrect',
            'partial_feedback': 'partial',
            'unanswered_feedback': 'unanswered',
            'answered_feedback': 'answered'
        }

        # v6.5: feedback field contains nested subfields as a dict
        feedback_content = field_contents.get('feedback', {})
        if isinstance(feedback_content, dict):
            for field_id, content in feedback_content.items():
                if field_id in field_mapping:
                    output_key = field_mapping[field_id]
                    feedback[output_key] = content
        elif isinstance(feedback_content, str) and feedback_content.strip():
            # Simple string feedback (no subfields)
            feedback['general'] = feedback_content

        return feedback

    def _parse_option_specific_feedback(self, text: str) -> Dict[str, str]:
        """Parse option-specific feedback."""
        option_feedback = {}

        # Pattern: - **A**: Feedback text
        pattern = r'-\s+\*\*([A-Z])\*\*:\s+(.+?)(?=\n-\s+\*\*[A-Z]\*\*:|\Z)'

        for match in re.finditer(pattern, text, re.DOTALL):
            letter = match.group(1)
            feedback_text = match.group(2).strip()
            option_feedback[letter] = feedback_text

        return option_feedback


    def _parse_image_section(self, text: str) -> Dict[str, Any]:
        """
        Parse image metadata section.

        Expected format:
        **File**: images/diagram.png
        **Canvas Height**: 500
        **Title**: Optional title
        **Logical Name**: Optional logical name

        Returns:
            Dictionary with image metadata
        """
        image_data = {}

        # Extract file path
        file_match = re.search(r'\*\*File\*\*:\s*(.+?)(?=\n|$)', text)
        if file_match:
            image_data['file'] = file_match.group(1).strip()

        # Extract canvas height
        height_match = re.search(r'\*\*Canvas Height\*\*:\s*(\d+)', text)
        if height_match:
            image_data['canvas_height'] = int(height_match.group(1))
        else:
            image_data['canvas_height'] = 400  # Default

        # Extract title
        title_match = re.search(r'\*\*Title\*\*:\s*(.+?)(?=\n|$)', text)
        if title_match:
            image_data['title'] = title_match.group(1).strip()
        else:
            image_data['title'] = 'Question Image'

        # Extract logical name (optional)
        logical_name_match = re.search(r'\*\*Logical Name\*\*:\s*(.+?)(?=\n|$)', text)
        if logical_name_match:
            image_data['logical_name'] = logical_name_match.group(1).strip()
        else:
            # Generate logical name from filename if not provided
            if 'file' in image_data:
                # Extract filename without extension
                filename = os.path.basename(image_data['file'])
                logical_name = os.path.splitext(filename)[0]
                image_data['logical_name'] = logical_name

        # Extract width (optional)
        width_match = re.search(r'\*\*Width\*\*:\s*(\d+)', text)
        if width_match:
            image_data['width'] = int(width_match.group(1))

        # Extract height (optional, different from canvas_height)
        img_height_match = re.search(r'\*\*Height\*\*:\s*(\d+)', text)
        if img_height_match:
            image_data['height'] = int(img_height_match.group(1))

        return image_data

    def _parse_hotspots_section(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse hotspots section for hotspot questions.

        Expected format:
        ### Hotspot 1
        **Shape**: rect
        **Coordinates**: 100,150,200,250
        **Label**: Heart
        **Correct**: true

        Returns:
            List of hotspot dictionaries
        """
        hotspots = []

        # Split by ### Hotspot headers
        hotspot_pattern = r'###\s+Hotspot\s+(\d+)\s*\n+(.*?)(?=\n###\s+Hotspot|\Z)'

        for match in re.finditer(hotspot_pattern, text, re.DOTALL):
            hotspot_num = match.group(1)
            hotspot_text = match.group(2)

            hotspot = {'id': f'HOTSPOT{hotspot_num}'}

            # Extract shape
            shape_match = re.search(r'\*\*Shape\*\*:\s*(\w+)', hotspot_text)
            if shape_match:
                hotspot['shape'] = shape_match.group(1).strip().lower()
            else:
                hotspot['shape'] = 'rect'  # Default

            # Extract coordinates
            coords_match = re.search(r'\*\*Coordinates\*\*:\s*(.+?)(?=\n|$)', hotspot_text)
            if coords_match:
                coords_str = coords_match.group(1).strip()
                hotspot['coords'] = self._parse_coordinates(coords_str, hotspot['shape'])
            else:
                raise ValueError(f"Hotspot {hotspot_num} missing coordinates")

            # Extract label (optional)
            label_match = re.search(r'\*\*Label\*\*:\s*(.+?)(?=\n|$)', hotspot_text)
            if label_match:
                hotspot['label'] = label_match.group(1).strip()
            else:
                hotspot['label'] = str(hotspot_num)

            # Extract correct flag
            correct_match = re.search(r'\*\*Correct\*\*:\s*(true|false|yes|no)', hotspot_text, re.IGNORECASE)
            if correct_match:
                correct_value = correct_match.group(1).lower()
                hotspot['correct'] = correct_value in ['true', 'yes']
            else:
                hotspot['correct'] = False

            hotspots.append(hotspot)

        return hotspots

    def _parse_coordinates(self, coords_str: str, shape: str) -> str:
        """
        Parse and validate coordinates based on shape type.

        Args:
            coords_str: Coordinate string (e.g., "100,150,200,250" or "x=100, y=150, width=100, height=100")
            shape: Shape type ('rect' or 'circle')

        Returns:
            Validated coordinates string in QTI format

        Raises:
            ValueError: If coordinates are invalid for the shape type
        """
        # Check if using x=, y=, width=, height= format and convert to x1,y1,x2,y2
        if 'x=' in coords_str and 'y=' in coords_str:
            x_match = re.search(r'x=(\d+)', coords_str)
            y_match = re.search(r'y=(\d+)', coords_str)

            if shape in ['rect', 'rectangle']:
                width_match = re.search(r'width=(\d+)', coords_str)
                height_match = re.search(r'height=(\d+)', coords_str)

                if x_match and y_match and width_match and height_match:
                    x = int(x_match.group(1))
                    y = int(y_match.group(1))
                    width = int(width_match.group(1))
                    height = int(height_match.group(1))
                    # Convert to x1,y1,x2,y2 format
                    coords_str = f"{x},{y},{x+width},{y+height}"
            elif shape == 'circle':
                radius_match = re.search(r'radius=(\d+)', coords_str)
                if x_match and y_match and radius_match:
                    x = int(x_match.group(1))
                    y = int(y_match.group(1))
                    radius = int(radius_match.group(1))
                    # Convert to x,y,radius format
                    coords_str = f"{x},{y},{radius}"

        # Remove whitespace
        coords_str = coords_str.replace(' ', '')

        # Split by comma
        coords = coords_str.split(',')

        if shape in ['rect', 'rectangle']:
            # Rectangle requires 4 coordinates: x1,y1,x2,y2
            if len(coords) != 4:
                raise ValueError(f"Rectangle hotspot requires 4 coordinates (x1,y1,x2,y2), got {len(coords)}")
            # Validate all are numbers
            try:
                [int(c) for c in coords]
            except ValueError:
                raise ValueError(f"Rectangle coordinates must be integers: {coords_str}")

        elif shape == 'circle':
            # Circle requires 3 coordinates: x,y,radius
            if len(coords) != 3:
                raise ValueError(f"Circle hotspot requires 3 coordinates (x,y,radius), got {len(coords)}")
            # Validate all are numbers
            try:
                [int(c) for c in coords]
            except ValueError:
                raise ValueError(f"Circle coordinates must be integers: {coords_str}")

        else:
            raise ValueError(f"Unknown shape type: {shape}")

        return coords_str

    def _parse_hotspot_definitions(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse hotspot definitions section (legacy hotspot format).

        Expected format:
        ### Hotspot 1: Refining
        **Region Type**: rectangle
        **Coordinates**: x1=250, y1=150, x2=400, y2=250
        **Correct**: true
        **Points**: 1

        Returns:
            List of hotspot dictionaries
        """
        hotspots = []

        # Split by ### Hotspot headers with optional label
        hotspot_pattern = r'###\s+Hotspot\s+(\d+)(?::\s+([^\n]+))?\s*\n+(.*?)(?=\n###\s+Hotspot|\Z)'

        for match in re.finditer(hotspot_pattern, text, re.DOTALL):
            hotspot_num = match.group(1)
            hotspot_label = match.group(2)  # Optional label after colon
            hotspot_text = match.group(3)

            hotspot = {'id': f'HOTSPOT{hotspot_num}'}

            # Extract region type / shape
            shape_match = re.search(r'\*\*Region Type\*\*:\s*(\w+)', hotspot_text, re.IGNORECASE)
            if shape_match:
                shape_text = shape_match.group(1).strip().lower()
                # Map "rectangle" to "rect"
                hotspot['shape'] = 'rect' if shape_text in ['rectangle', 'rect'] else 'circle'
            else:
                hotspot['shape'] = 'rect'  # Default

            # Extract coordinates (legacy hotspot format: x1=250, y1=150, x2=400, y2=250)
            coords_match = re.search(r'\*\*Coordinates\*\*:\s*(.+?)(?=\n|$)', hotspot_text)
            if coords_match:
                coords_str = coords_match.group(1).strip()
                # Parse legacy hotspot format: x1=250, y1=150, x2=400, y2=250
                # Convert to standard format: 250,150,400,250
                if '=' in coords_str:
                    # Extract values
                    values = {}
                    for part in coords_str.split(','):
                        key, val = part.split('=')
                        values[key.strip()] = val.strip()

                    if hotspot['shape'] == 'rect':
                        # Rectangle: support both formats
                        # Format 1: x1, y1, x2, y2
                        # Format 2: x, y, width, height (convert to x1, y1, x2, y2)
                        if 'x1' in values and 'y1' in values:
                            coords = f"{values.get('x1', '0')},{values.get('y1', '0')},{values.get('x2', '0')},{values.get('y2', '0')}"
                        elif 'x' in values and 'y' in values and 'width' in values and 'height' in values:
                            x = int(values['x'])
                            y = int(values['y'])
                            width = int(values['width'])
                            height = int(values['height'])
                            coords = f"{x},{y},{x+width},{y+height}"
                        else:
                            coords = "0,0,0,0"
                    else:
                        # Circle: x, y, radius
                        coords = f"{values.get('x', '0')},{values.get('y', '0')},{values.get('radius', '0')}"

                    hotspot['coords'] = coords
                else:
                    # Already in standard format
                    hotspot['coords'] = coords_str
            else:
                logger.warning(f"Hotspot {hotspot_num} missing coordinates, skipping")
                continue

            # Extract label
            if hotspot_label:
                hotspot['label'] = hotspot_label.strip()
            else:
                label_match = re.search(r'\*\*Label\*\*:\s*(.+?)(?=\n|$)', hotspot_text)
                if label_match:
                    hotspot['label'] = label_match.group(1).strip()
                else:
                    hotspot['label'] = str(hotspot_num)

            # Extract correct flag
            correct_match = re.search(r'\*\*Correct\*\*:\s*(true|false|yes|no)', hotspot_text, re.IGNORECASE)
            if correct_match:
                correct_value = correct_match.group(1).lower()
                hotspot['correct'] = correct_value in ['true', 'yes']
            else:
                hotspot['correct'] = False

            hotspots.append(hotspot)

        return hotspots

    def _extract_image_from_markdown(self, text: str) -> Dict[str, Any]:
        """
        Extract image information from markdown image syntax.

        Expected format: ![Alt Text](image_filename.png)

        Returns:
            Dictionary with image metadata
        """
        # Find markdown image: ![alt](path)
        image_match = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', text)

        if not image_match:
            return {}

        alt_text = image_match.group(1).strip()
        image_path = image_match.group(2).strip()

        return {
            'file': image_path,
            'title': alt_text or 'Question Image',
            'logical_name': os.path.splitext(os.path.basename(image_path))[0],
            'canvas_height': 400  # Default
        }

    def _parse_premises_section(self, text: str) -> List[Dict[str, str]]:
        """
        Parse premises (left column) for match questions.

        Expected format:
        1. First premise text
        2. Second premise text
        3. Third premise text

        Returns:
            List of premise dictionaries with id and text
        """
        premises = []

        # Pattern for numbered items: 1. Text
        premise_pattern = r'^(\d+)\.\s+(.+?)(?=\n\d+\.|\Z)'

        for match in re.finditer(premise_pattern, text, re.MULTILINE | re.DOTALL):
            premise_num = match.group(1)
            premise_text = match.group(2).strip()

            premises.append({
                'id': f'PREMISE{premise_num}',
                'number': int(premise_num),
                'text': premise_text
            })

        return premises

    def _parse_match_responses_section(self, text: str) -> List[Dict[str, str]]:
        """
        Parse responses (right column) for match questions.

        Expected format:
        A. First response text
        B. Second response text
        C. Third response text

        Returns:
            List of response dictionaries with id and text
        """
        responses = []

        # Pattern for lettered items: A. Text
        response_pattern = r'^([A-Z])\.\s+(.+?)(?=\n[A-Z]\.|\Z)'

        for match in re.finditer(response_pattern, text, re.MULTILINE | re.DOTALL):
            response_letter = match.group(1)
            response_text = match.group(2).strip()

            responses.append({
                'id': f'RESPONSE{response_letter}',
                'letter': response_letter,
                'text': response_text
            })

        return responses

    def _parse_scoring_section(self, text: str) -> Dict[str, Any]:
        """
        Parse scoring configuration section.

        Expected format:
        **Type**: partial_credit
        **Points per correct match**: 1
        **Points per incorrect match**: 0
        **Minimum score**: 0

        Returns:
            Dictionary with scoring configuration
        """
        scoring = {}

        # Extract scoring type
        type_match = re.search(r'\*\*Type\*\*:\s*(.+?)(?=\n|$)', text)
        if type_match:
            scoring['type'] = type_match.group(1).strip()

        # Extract points per correct
        correct_match = re.search(r'\*\*Points per correct.*?\*\*:\s*([0-9.]+)', text, re.IGNORECASE)
        if correct_match:
            scoring['points_each_correct'] = float(correct_match.group(1))

        # Extract points per incorrect/wrong
        wrong_match = re.search(r'\*\*Points per (?:incorrect|wrong).*?\*\*:\s*([0-9.-]+)', text, re.IGNORECASE)
        if wrong_match:
            scoring['points_each_wrong'] = float(wrong_match.group(1))

        # Extract minimum score
        min_match = re.search(r'\*\*Minimum score\*\*:\s*([0-9.-]+)', text, re.IGNORECASE)
        if min_match:
            scoring['points_minimum'] = float(min_match.group(1))

        # Extract maximum score
        max_match = re.search(r'\*\*Maximum score\*\*:\s*([0-9.]+)', text, re.IGNORECASE)
        if max_match:
            scoring['points_all_correct'] = float(max_match.group(1))

        return scoring

    def _parse_match_pairings(self, text: str) -> List[Dict[str, str]]:
        """
        Parse match pairings from answer section.

        Expected format:
        1 → A
        2 → B
        3 → C

        Also supports -> instead of →

        Returns:
            List of pairing dictionaries with premise and response IDs
        """
        pairings = []

        # Pattern for pairings: number → letter or number -> letter
        pairing_pattern = r'^(\d+)\s*(?:→|->)\s*([A-Z])'

        for match in re.finditer(pairing_pattern, text, re.MULTILINE):
            premise_num = match.group(1)
            response_letter = match.group(2)

            pairings.append({
                'premise': f'PREMISE{premise_num}',
                'response': f'RESPONSE{response_letter}'
            })

        return pairings

    def _parse_blanks_section(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse blanks section for text_entry questions.

        Expected format (supports both ## and ### headers):
        ### Blank 1  OR  ## Blank 1
        **Correct Answer**: mean
        **Accepted Alternatives**: average, arithmetic mean
        **Case Sensitive**: false
        **Expected Length**: 15

        Returns:
            List of blank dictionaries with correct answers and alternatives
        """
        blanks = []

        # Split by ### Blank or ## Blank headers (support both levels)
        blank_pattern = r'#{2,3}\s+Blank\s+(\d+)\s*\n+(.*?)(?=\n#{2,3}\s+Blank|\Z)'

        for match in re.finditer(blank_pattern, text, re.DOTALL):
            blank_num = match.group(1)
            blank_text = match.group(2)

            blank = {
                'identifier': f'RESPONSE-{blank_num}',
                'number': int(blank_num)
            }

            # Extract correct answer
            correct_match = re.search(r'\*\*Correct Answer\*\*:\s*(.+?)(?=\n|$)', blank_text)
            if correct_match:
                blank['correct_answer'] = correct_match.group(1).strip()
            else:
                raise ValueError(f"Blank {blank_num} missing correct answer")

            # Extract accepted alternatives (optional)
            alternatives_match = re.search(r'\*\*Accepted Alternatives\*\*:\s*(.+?)(?=\n|$)', blank_text)
            if alternatives_match:
                alternatives_text = alternatives_match.group(1).strip()
                # Split by comma and clean up
                alternatives = [alt.strip() for alt in alternatives_text.split(',') if alt.strip()]
                blank['alternatives'] = alternatives
            else:
                blank['alternatives'] = []

            # Extract case sensitive flag (optional)
            case_match = re.search(r'\*\*Case Sensitive\*\*:\s*(true|false|yes|no)', blank_text, re.IGNORECASE)
            if case_match:
                case_value = case_match.group(1).lower()
                blank['case_sensitive'] = case_value in ['true', 'yes']
            else:
                blank['case_sensitive'] = False  # Default to case-insensitive

            # Extract expected length (optional)
            length_match = re.search(r'\*\*Expected Length\*\*:\s*(\d+)', blank_text)
            if length_match:
                blank['expected_length'] = int(length_match.group(1))
            else:
                blank['expected_length'] = 15  # Default

            # Extract tolerance for numeric entry (optional)
            tolerance_match = re.search(r'\*\*Tolerance\*\*:\s*([\d.]+)', blank_text)
            if tolerance_match:
                blank['tolerance'] = float(tolerance_match.group(1))

            # Extract minimum value for numeric entry (optional)
            min_match = re.search(r'\*\*Minimum\*\*:\s*([\d.-]+)', blank_text)
            if min_match:
                blank['minimum'] = float(min_match.group(1))

            # Extract maximum value for numeric entry (optional)
            max_match = re.search(r'\*\*Maximum\*\*:\s*([\d.-]+)', blank_text)
            if max_match:
                blank['maximum'] = float(max_match.group(1))

            blanks.append(blank)

        return blanks

    def _parse_single_blank(self, content: str, blank_num: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single blank from @field: blank_N content.

        Supports both formats:
        - v6.3: **Correct Answer**: single answer + **Accepted Alternatives**: alt1, alt2
        - v6.4: **Correct Answers:** list of answers (first = correct, rest = alternatives)
        """
        blank = {
            'identifier': f'BLANK{blank_num}',
            'number': int(blank_num)
        }

        # Try v6.4 format first: **Correct Answers:** with list (colon inside bold markers)
        correct_answers_match = re.search(r'\*\*Correct Answers?:\*\*\s*\n(.*?)(?=\n+\*\*|\Z)', content, re.DOTALL)
        if correct_answers_match:
            answers_text = correct_answers_match.group(1).strip()
            answers = []
            for line in answers_text.split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    answers.append(line[2:].strip())
            if answers:
                blank['correct_answer'] = answers[0]  # First answer is the primary correct answer
                blank['alternatives'] = answers[1:] if len(answers) > 1 else []
            else:
                return None
        else:
            # Try v6.3 format: **Correct Answer**: single line
            correct_match = re.search(r'\*\*Correct Answer\*\*:\s*(.+?)(?=\n|$)', content)
            if correct_match:
                blank['correct_answer'] = correct_match.group(1).strip()
            else:
                return None

            # Extract accepted alternatives (v6.3 format)
            alternatives = []
            alt_match = re.search(r'\*\*Accepted Alternatives\*\*:\s*(.+?)(?=\n\*\*|\Z)', content, re.DOTALL)
            if alt_match:
                alt_text = alt_match.group(1).strip()
                if ',' in alt_text:
                    alternatives = [alt.strip() for alt in alt_text.split(',') if alt.strip()]
                else:
                    # Try list format
                    for line in alt_text.split('\n'):
                        line = line.strip()
                        if line.startswith('- '):
                            alternatives.append(line[2:].strip())
            blank['alternatives'] = alternatives

        # Extract case sensitive flag
        case_match = re.search(r'\*\*Case Sensitive\*\*:\s*(true|false|yes|no)', content, re.IGNORECASE)
        blank['case_sensitive'] = case_match and case_match.group(1).lower() in ['true', 'yes']

        # Extract expected length
        length_match = re.search(r'\*\*(?:Expected|Maximum) Length\*\*:\s*(\d+)', content)
        blank['expected_length'] = int(length_match.group(1)) if length_match else 15

        return blank

    def _parse_blank_v65(self, content: str, blank_num: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single blank from @@field: blank_N content (v6.5 format).

        v6.5 format uses ^ prefixed metadata:
        @@field: blank_1
        ^Correct_Answers
        - 42
        - 42.0
        ^Case_Sensitive No
        @@end_field

        Args:
            content: Content inside the @@field: blank_N ... @@end_field
            blank_num: The blank number (e.g., "1", "2")

        Returns:
            Dictionary with blank data or None if parsing fails
        """
        blank = {
            'identifier': f'BLANK{blank_num}',
            'number': int(blank_num)
        }

        lines = content.strip().split('\n') if isinstance(content, str) else []
        answers = []
        current_key = None

        for line in lines:
            line_stripped = line.strip()

            # Check for ^Key or ^Key Value
            if line_stripped.startswith('^'):
                match = re.match(r'^\^(\w+)\s*(.*)$', line_stripped)
                if match:
                    key = match.group(1)
                    value = match.group(2).strip() if match.group(2) else None

                    if key == 'Correct_Answers':
                        current_key = 'answers'
                    elif key == 'Case_Sensitive':
                        blank['case_sensitive'] = value.lower() in ['yes', 'true'] if value else False
                        current_key = None
                    elif key == 'Tolerance':
                        blank['tolerance'] = float(value) if value else 0
                        current_key = None
                    elif key == 'Input_type':
                        blank['input_type'] = value if value else 'text'
                        current_key = None
                    elif key == 'Expected_Length' or key == 'Maximum_Length':
                        blank['expected_length'] = int(value) if value and value.isdigit() else 15
                        current_key = None
                    else:
                        current_key = None
            elif line_stripped.startswith('- ') and current_key == 'answers':
                # List item under ^Correct_Answers
                answer_text = line_stripped[2:].strip()
                if answer_text:
                    answers.append(answer_text)

        if answers:
            blank['correct_answer'] = answers[0]
            blank['alternatives'] = answers[1:] if len(answers) > 1 else []
        else:
            return None

        # Set defaults if not specified
        if 'case_sensitive' not in blank:
            blank['case_sensitive'] = False
        if 'expected_length' not in blank:
            blank['expected_length'] = 15

        return blank

    def _parse_dropdown_content(self, content: str) -> Tuple[List[str], Optional[str]]:
        """
        Parse dropdown content from @field: dropdown_N.

        Supported formats:
        1. v6.5 inline marker: - option* (asterisk marks correct)
        2. v6.5 caret syntax: ^Correct_Answer value
        3. Legacy: **Correct Answer**: value

        Returns:
            Tuple of (options_list, correct_option)
        """
        options = []
        correct = None

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                option_text = line[2:].strip()
                # Check for ✓ marker (legacy) or * marker (v6.5)
                if '✓' in option_text:
                    option_text = option_text.replace('✓', '').strip()
                    correct = option_text
                elif option_text.endswith('*'):
                    option_text = option_text[:-1].strip()
                    correct = option_text
                options.append(option_text)

        # Check for v6.5 ^Correct_Answer format
        correct_match = re.search(r'\^Correct_Answer\s+(.+?)(?=\n|$)', content)
        if correct_match:
            correct = correct_match.group(1).strip()

        # Also check for legacy **Correct Answer**: field
        if not correct:
            correct_match = re.search(r'\*\*Correct Answer\*\*:\s*(.+?)(?=\n|$)', content)
            if correct_match:
                correct = correct_match.group(1).strip()

        return options, correct

    def _parse_individual_blanks(self, block: str) -> Optional[List[Dict[str, Any]]]:
        """
        Parse individual ## Blank N sections scattered throughout the question block.

        Expected format:
        ## Blank 1
        **Correct Answer**: Manufacturing of vehicles and infrastructure
        **Accepted Alternatives**:
        - Vehicle manufacturing
        - Vehicle production
        **Case Sensitive**: false
        **Maximum Length**: 60 characters

        Returns:
            List of blank dictionaries or None if no blanks found
        """
        blanks = []

        # Find all ## Blank N sections
        blank_pattern = r'##\s+Blank\s+(\d+)\s*\n+(.*?)(?=\n##\s+(?:Blank|Question|Feedback|Answer|Dropdown)|\Z)'

        for match in re.finditer(blank_pattern, block, re.DOTALL):
            blank_num = match.group(1)
            blank_text = match.group(2)

            blank = {
                'identifier': f'BLANK{blank_num}',
                'number': int(blank_num)
            }

            # Extract correct answer
            correct_match = re.search(r'\*\*Correct Answer\*\*:\s*(.+?)(?=\n|$)', blank_text)
            if correct_match:
                blank['correct_answer'] = correct_match.group(1).strip()
            else:
                logger.warning(f"Blank {blank_num} missing correct answer, skipping")
                continue

            # Extract accepted alternatives (can be list or comma-separated)
            alternatives = []

            # Try list format first
            alt_list_pattern = r'^\s*-\s+(.+)$'
            for alt_match in re.finditer(alt_list_pattern, blank_text, re.MULTILINE):
                alternatives.append(alt_match.group(1).strip())

            # If no list format, try inline format
            if not alternatives:
                alt_inline_match = re.search(r'\*\*Accepted Alternatives\*\*:\s*(.+?)(?=\n\*\*|\Z)', blank_text, re.DOTALL)
                if alt_inline_match:
                    alt_text = alt_inline_match.group(1).strip()
                    # Check if it's comma-separated (not a list)
                    if ',' in alt_text and not alt_text.startswith('-'):
                        alternatives = [alt.strip() for alt in alt_text.split(',') if alt.strip()]

            blank['alternatives'] = alternatives

            # Extract case sensitive flag
            case_match = re.search(r'\*\*Case Sensitive\*\*:\s*(true|false|yes|no)', blank_text, re.IGNORECASE)
            if case_match:
                case_value = case_match.group(1).lower()
                blank['case_sensitive'] = case_value in ['true', 'yes']
            else:
                blank['case_sensitive'] = False

            # Extract expected/maximum length
            length_match = re.search(r'\*\*(?:Expected|Maximum) Length\*\*:\s*(\d+)', blank_text)
            if length_match:
                blank['expected_length'] = int(length_match.group(1))
            else:
                blank['expected_length'] = 50  # Default for longer answers

            # Extract tolerance for numeric entry (optional)
            tolerance_match = re.search(r'\*\*Tolerance\*\*:\s*([\d.]+)', blank_text)
            if tolerance_match:
                blank['tolerance'] = float(tolerance_match.group(1))

            # Extract minimum value for numeric entry (optional)
            min_match = re.search(r'\*\*Minimum\*\*:\s*([\d.-]+)', blank_text)
            if min_match:
                blank['minimum'] = float(min_match.group(1))

            # Extract maximum value for numeric entry (optional)
            max_match = re.search(r'\*\*Maximum\*\*:\s*([\d.-]+)', blank_text)
            if max_match:
                blank['maximum'] = float(max_match.group(1))

            blanks.append(blank)

        return blanks if blanks else None

    def _parse_simplified_blanks(self, block: str) -> Optional[List[Dict[str, Any]]]:
        """
        Parse simplified blank format (Claude Desktop style).

        Expected format:
        ### Correct Answer
        -12

        ### Accepted Alternatives
        - −12
        - minus twelve

        This format is only valid for single-blank questions ({{BLANK-1}}).

        Returns:
            List with single blank dictionary or None if format not found
        """
        # Check if this format is used
        correct_match = re.search(
            r'###\s+Correct Answer\s*\n+(.+?)(?=\n###|\n##|\Z)',
            block,
            re.DOTALL
        )

        if not correct_match:
            return None

        # Extract the correct answer (first non-empty line)
        answer_text = correct_match.group(1).strip()
        # Get first line as the answer
        correct_answer = answer_text.split('\n')[0].strip()

        if not correct_answer:
            return None

        blank = {
            'identifier': 'BLANK1',
            'number': 1,
            'correct_answer': correct_answer,
            'alternatives': [],
            'case_sensitive': False,
            'expected_length': 50
        }

        # Extract accepted alternatives
        alt_match = re.search(
            r'###\s+Accepted Alternatives\s*\n+(.*?)(?=\n###|\n##|\Z)',
            block,
            re.DOTALL
        )

        if alt_match:
            alt_text = alt_match.group(1)
            # Parse list items (- item)
            for line in alt_text.split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    alt = line[2:].strip()
                    if alt:
                        blank['alternatives'].append(alt)

        # Check for Case Sensitive field
        case_match = re.search(r'###\s+Case Sensitive\s*\n+\s*(true|false|yes|no)', block, re.IGNORECASE)
        if case_match:
            case_value = case_match.group(1).lower()
            blank['case_sensitive'] = case_value in ['true', 'yes']

        logger.debug(f"Parsed simplified blank: {blank}")
        return [blank]

    def _parse_correct_answers_dict(self, text: str) -> Dict[str, str]:
        """
        Parse Correct Answers section with {{N}}: answer format (Evolution format).

        Example:
        {{1}}: mutationer
        {{2}}: resistenta

        Returns:
            Dictionary mapping {{N}} to answer
        """
        answers = {}
        # Pattern: {{1}}: answer or {{1}} : answer
        pattern = r'\{\{(\d+)\}\}\s*:\s*(.+?)(?=\n\{\{|\n##|\Z)'

        for match in re.finditer(pattern, text, re.DOTALL):
            field_num = match.group(1)
            answer = match.group(2).strip()
            answers[field_num] = answer

        return answers

    def _parse_accepted_alternatives(self, text: str) -> Any:
        """
        Parse Accepted Alternatives section (Evolution format).

        Can be either:
        1. List format (for fill_in_the_blank):
           - population
           - populationers

        2. Dict format (for text_entry):
           {{1}}: mutation, mutationer
           {{2}}: resistenta, motståndskraftiga

        Returns:
            Either a list of strings or a dict mapping {{N}} to comma-separated alternatives
        """
        # Check if it's dict format (has {{N}}:)
        if '{{' in text and '}}' in text:
            alternatives = {}
            # Pattern: {{1}}: alt1, alt2, alt3
            pattern = r'\{\{(\d+)\}\}\s*:\s*(.+?)(?=\n\{\{|\n##|\Z)'

            for match in re.finditer(pattern, text, re.DOTALL):
                field_num = match.group(1)
                alts_text = match.group(2).strip()
                # Split by comma and clean
                alts_list = [alt.strip() for alt in alts_text.split(',')]
                alternatives[field_num] = alts_list

            return alternatives
        else:
            # List format - extract lines starting with -
            alternatives = []
            pattern = r'^\s*-\s+(.+)$'

            for match in re.finditer(pattern, text, re.MULTILINE):
                alt = match.group(1).strip()
                alternatives.append(alt)

            return alternatives

    def _parse_inline_choices(self, text: str) -> Dict[str, List[str]]:
        """
        Parse Inline Choices section (Evolution format).

        Example:
        {{1}}: [slumpmässigt, riktat]
        {{2}}: [slumpmässigt, icke-slumpmässigt]

        Returns:
            Dictionary mapping {{N}} to list of choice options
        """
        choices = {}
        # Pattern: {{1}}: [option1, option2, option3]
        pattern = r'\{\{(\d+)\}\}\s*:\s*\[([^\]]+)\]'

        for match in re.finditer(pattern, text):
            field_num = match.group(1)
            options_text = match.group(2)
            # Split by comma and clean
            options = [opt.strip() for opt in options_text.split(',')]
            choices[field_num] = options

        return choices

    def _parse_dropdown_format(self, block: str) -> Optional[Dict[str, Any]]:
        """
        Parse alternative inline_choice dropdown format.

        Expected formats:
        Format 1 (per-dropdown correct answers):
        ## Dropdown 1
        **Options**:
        - cultivation and harvesting ✓
        - mining and extraction

        Format 2 (separate Correct Answer section):
        ### Dropdown 1
        **Options:**
        - option1
        - option2

        ## Correct Answer
        **Dropdown 1**: option1
        **Dropdown 2**: option2

        Returns:
            Dictionary with 'choices' and 'correct_answers' keys
        """
        choices = {}
        correct_answers = {}

        # Find all ## Dropdown N or ### Dropdown N sections (supports both formats)
        dropdown_pattern = r'###+\s+Dropdown\s+(\d+)\s*\n+(.*?)(?=\n###+\s+(?:Dropdown|Question|Feedback|Answer|Blanks|Correct)|\Z)'

        for match in re.finditer(dropdown_pattern, block, re.DOTALL):
            dropdown_num = match.group(1)
            dropdown_text = match.group(2)

            # Extract options (list items with optional ✓ marker)
            options = []
            correct_option = None

            # Pattern for list items: - option text (with optional ✓)
            option_pattern = r'^\s*-\s+(.+?)(\s*✓)?\s*$'

            for option_match in re.finditer(option_pattern, dropdown_text, re.MULTILINE):
                option_text = option_match.group(1).strip()
                is_correct = option_match.group(2) is not None

                options.append(option_text)

                if is_correct:
                    correct_option = option_text

            # Also check for explicit **Correct Answer**: field in dropdown section
            correct_match = re.search(r'\*\*Correct Answer\*\*:\s*(.+?)(?=\n|$)', dropdown_text)
            if correct_match:
                correct_option = correct_match.group(1).strip()

            if options:
                choices[dropdown_num] = options
                if correct_option:
                    correct_answers[dropdown_num] = correct_option

        # Also check for separate ## Correct Answer section (virus quiz format)
        correct_answer_section = re.search(
            r'##\s+Correct Answer\s*\n+(.*?)(?=\n##|\Z)',
            block,
            re.DOTALL
        )
        if correct_answer_section:
            correct_text = correct_answer_section.group(1)
            # Pattern: **Dropdown N**: answer
            dropdown_answer_pattern = r'\*\*Dropdown\s+(\d+)\*\*:\s*(.+?)(?=\n|$)'
            for ans_match in re.finditer(dropdown_answer_pattern, correct_text, re.MULTILINE):
                dropdown_num = ans_match.group(1)
                answer = ans_match.group(2).strip()
                correct_answers[dropdown_num] = answer

        # Return both choices and correct answers if found
        if choices:
            return {
                'choices': choices,
                'correct_answers': correct_answers
            }

        return None

    def _parse_matching_pairs_evolution(self, text: str) -> Dict[str, List]:
        """
        Parse Matching Pairs section (Evolution format).

        Example:
        **Urvalstyper:**
        1. Riktat urval (Directional selection)
        2. Stabiliserande urval (Stabilizing selection)

        **Beskrivningar:**
        A. Gynnar genomsnittet, missgynnar båda extremerna
        B. Gynnar en extrem, missgynnar den andra extremen

        Returns:
            Dictionary with 'premises' and 'responses' lists
        """
        premises = []
        responses = []

        # Extract premises (numbered items 1., 2., 3., etc.)
        premise_pattern = r'^(\d+)\.\s+(.+?)(?=\n\d+\.|\n\*\*|\Z)'
        for match in re.finditer(premise_pattern, text, re.MULTILINE | re.DOTALL):
            premise_num = match.group(1)
            premise_text = match.group(2).strip()

            premises.append({
                'id': f'PREMISE{premise_num}',
                'number': int(premise_num),
                'text': premise_text
            })

        # Extract responses (lettered items A., B., C., etc.)
        response_pattern = r'^([A-Z])\.\s+(.+?)(?=\n[A-Z]\.|\n\*\*|\n##|\Z)'
        for match in re.finditer(response_pattern, text, re.MULTILINE | re.DOTALL):
            response_letter = match.group(1)
            response_text = match.group(2).strip()

            responses.append({
                'id': f'RESPONSE{response_letter}',
                'letter': response_letter,
                'text': response_text
            })

        return {
            'premises': premises,
            'responses': responses
        }

    def _parse_pairs_genai_format(self, text: str) -> Dict[str, List]:
        """
        Parse Pairs section (GenAI/Claude Desktop format).

        Example:
        1. Replikation → DNA kopieras till DNA
        2. Transkription → DNA kopieras till RNA
        3. Translation → RNA används för att bygga protein

        Returns:
            Dictionary with 'premises' and 'responses' lists
        """
        premises = []
        responses = []

        # Pattern: "1. Premise → Response"
        pair_pattern = r'^(\d+)\.\s+(.+?)\s*(?:→|->)\s*(.+?)$'

        for match in re.finditer(pair_pattern, text, re.MULTILINE):
            premise_num = match.group(1)
            premise_text = match.group(2).strip()
            response_text = match.group(3).strip()

            premises.append({
                'id': f'PREMISE{premise_num}',
                'number': int(premise_num),
                'text': premise_text
            })

            responses.append({
                'id': f'RESPONSE{premise_num}',
                'letter': premise_num,  # Use number as identifier
                'text': response_text
            })

        return {
            'premises': premises,
            'responses': responses
        }

    def _parse_correct_matches(self, text: str) -> List[Dict[str, str]]:
        """
        Parse Correct Matches section (Evolution format).

        Example:
        1 → B
        2 → A
        3 → C

        Returns:
            List of pairing dictionaries
        """
        pairings = []
        # Pattern: 1 → B or 1->B or 1 -> B
        pattern = r'(\d+)\s*(?:→|->)\s*([A-Z])'

        for match in re.finditer(pattern, text):
            premise_num = match.group(1)
            response_letter = match.group(2)

            pairings.append({
                'premise': f'PREMISE{premise_num}',
                'response': f'RESPONSE{response_letter}'
            })

        return pairings

    def _convert_evolution_format_to_standard(self, sections: Dict[str, Any], fields: Dict[str, Any]) -> None:
        """
        Convert Evolution format parsed data to the format expected by xml_generator.

        Modifies sections dict in-place.
        """
        question_type = fields.get('question_type', '')

        # Handle fill_in_the_blank -> convert to text_entry with single blank
        if question_type == 'fill_in_the_blank':
            if 'correct_answer_text' in sections and 'accepted_alternatives' in sections:
                # Create blanks list with single blank
                correct = sections['correct_answer_text']
                alternatives_list = sections.get('accepted_alternatives', [])

                # Create blank in expected format
                blank = {
                    'number': 1,
                    'identifier': 'BLANK1',
                    'correct_answer': correct,
                    'alternatives': alternatives_list if isinstance(alternatives_list, list) else [],
                    'case_sensitive': False,
                    'expected_length': 15
                }

                sections['blanks'] = [blank]

                # Replace underscore placeholder with {{1}} marker for generator
                if 'question_text' in sections:
                    sections['question_text'] = sections['question_text'].replace('_____', '{{1}}', 1)

        # Handle text_entry Evolution format -> convert to blanks format
        elif question_type == 'text_entry':
            if 'correct_answers_dict' in sections:
                correct_answers = sections['correct_answers_dict']
                alternatives_dict = sections.get('accepted_alternatives', {})

                blanks = []
                for field_num in sorted(correct_answers.keys(), key=int):
                    correct = correct_answers[field_num]
                    alternatives_list = alternatives_dict.get(field_num, []) if isinstance(alternatives_dict, dict) else []

                    blank = {
                        'number': int(field_num),
                        'identifier': f'BLANK{field_num}',
                        'correct_answer': correct,
                        'alternatives': alternatives_list,
                        'case_sensitive': False,
                        'expected_length': 15
                    }

                    blanks.append(blank)

                # Only set if not already set from old format
                if 'blanks' not in sections or not sections['blanks']:
                    sections['blanks'] = blanks

        # Handle inline_choice - store data for xml_generator
        elif question_type == 'inline_choice':
            # The inline_choices and correct_answers_dict are already parsed
            # xml_generator will need to use these
            pass

    def _parse_draggable_items(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse draggable items section for graphicgapmatch_v2.

        Expected format:
        **Item 1**: Description text here
        **Item 2**: Another description
        ...

        Returns:
            List of draggable item dictionaries with identifier and text
        """
        items = []

        # Pattern to match **Item N**: text
        item_pattern = r'\*\*Item\s+(\d+)\*\*:\s*(.+?)(?=\n\*\*Item\s+\d+\*\*:|\Z)'

        for match in re.finditer(item_pattern, text, re.DOTALL):
            item_num = match.group(1)
            item_text = match.group(2).strip()

            # Remove any trailing markers like "(DISTRAKTOR)" from text
            # but keep track of whether it's a distractor
            is_distractor = '(DISTRAKTOR' in item_text.upper() or '(DISTRACTOR' in item_text.upper()
            # Remove distractor markers for clean text
            item_text = re.sub(r'\s*\([Dd][Ii][Ss][Tt][Rr][Aa][Kk][Tt][Oo][Rr].*?\)', '', item_text).strip()

            items.append({
                'number': item_num,
                'identifier': f'ITEM_{item_num}',
                'text': item_text,
                'is_distractor': is_distractor
            })

        return items

    def _parse_hotspot_zones(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse hotspot zones section for graphicgapmatch_v2.

        Expected format:
        ### Zone 1: Label
        **Shape**: circle
        **Coordinates**: 100,200,50
        **Correct Item**: Item 3
        **Identifier**: zone1

        Returns:
            List of zone dictionaries with coordinates, shape, and correct item mapping
        """
        zones = []

        # Pattern to match ### Zone N: Label sections
        zone_pattern = r'###\s+Zone\s+(\d+)(?::\s*([^\n]+))?\s*\n+(.*?)(?=\n###\s+Zone|\Z)'

        for match in re.finditer(zone_pattern, text, re.DOTALL):
            zone_num = match.group(1)
            zone_label = match.group(2)  # Optional label after colon
            zone_text = match.group(3)

            zone = {'number': zone_num}

            # Extract shape
            shape_match = re.search(r'\*\*Shape\*\*:\s*(\w+)', zone_text, re.IGNORECASE)
            if shape_match:
                shape = shape_match.group(1).strip().lower()
                zone['shape'] = 'rect' if shape in ['rect', 'rectangle'] else shape
            else:
                zone['shape'] = 'circle'  # Default

            # Extract coordinates
            coords_match = re.search(r'\*\*Coordinates\*\*:\s*(.+?)(?=\n|$)', zone_text)
            if coords_match:
                coords_str = coords_match.group(1).strip()

                # Handle separate Radius field for circles (if present)
                if zone['shape'] == 'circle':
                    radius_match = re.search(r'\*\*Radius\*\*:\s*(\d+)', zone_text)
                    if radius_match and ',' in coords_str:
                        # Coordinates has x,y and Radius is separate
                        coord_parts = coords_str.split(',')
                        if len(coord_parts) == 2:
                            # Add radius to make x,y,radius
                            coords_str = f"{coord_parts[0].strip()},{coord_parts[1].strip()},{radius_match.group(1)}"

                # Security: coords are interpolated unescaped into an XML attribute.
                # Keep only digits and commas so a crafted value cannot break out.
                zone['coords'] = re.sub(r'[^0-9,]', '', coords_str)
            else:
                logger.warning(f"Zone {zone_num} missing coordinates, skipping")
                continue

            # Extract identifier
            identifier_match = re.search(r'\*\*Identifier\*\*:\s*(.+?)(?=\n|$)', zone_text, re.IGNORECASE)
            if identifier_match:
                # Security: sanitise — the identifier is used unescaped in XML
                # attributes and in the mapping/value references.
                zone['identifier'] = sanitize_identifier(identifier_match.group(1).strip())
            else:
                zone['identifier'] = f'ZONE_{zone_num}'

            # Extract correct item reference
            correct_item_match = re.search(r'\*\*Correct Item\*\*:\s*Item\s+(\d+)', zone_text, re.IGNORECASE)
            if correct_item_match:
                zone['correct_item_num'] = correct_item_match.group(1)
            else:
                logger.warning(f"Zone {zone_num} missing Correct Item reference")

            # Extract label
            if zone_label:
                zone['label'] = zone_label.strip()

            zones.append(zone)

        return zones


def markdown_to_xhtml(markdown_text: str) -> str:
    """
    Convert markdown text to XHTML suitable for QTI.

    For MVP, this performs basic conversions:
    - XML entity escaping (FIRST - prevents injection)
    - Paragraphs wrapped in <p> tags
    - **bold** to <strong>
    - *italic* to <em>
    - ![alt](path) to <img> tags with resources/ prefix
    - Line breaks preserved

    Args:
        markdown_text: Markdown formatted text

    Returns:
        XHTML formatted text with properly escaped XML entities
    """
    def convert_image(match):
        """Convert markdown image to XHTML img tag with resources/ prefix."""
        alt_text = match.group(1)
        image_path = match.group(2)
        # Extract just the filename (remove any directory path)
        filename = os.path.basename(image_path)
        # Note: alt_text is already escaped at this point
        return f'<img src="resources/{filename}" alt="{alt_text}"/>'

    # CRITICAL: Escape XML entities FIRST before any other processing
    # This prevents & < > " ' from breaking XML parsing
    markdown_text = escape_xml(markdown_text)

    # Handle multiple paragraphs
    paragraphs = markdown_text.split('\n\n')
    xhtml_paragraphs = []

    for para in paragraphs:
        if not para.strip():
            continue

        # Convert markdown images (after escaping - safe for attributes)
        # Pattern: ![alt text](path/to/image.png)
        para = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', convert_image, para)

        # Convert markdown formatting
        para = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', para)
        para = re.sub(r'\*(.+?)\*', r'<em>\1</em>', para)
        para = re.sub(r'`(.+?)`', r'<code>\1</code>', para)

        # Convert line breaks to <br/>
        para = para.replace('\n', '<br/>')

        # Wrap in paragraph tag
        xhtml_paragraphs.append(f'<p>{para}</p>')

    return '\n'.join(xhtml_paragraphs)