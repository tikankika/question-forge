"""
XML Generator

Generates QTI 2.2 XML files from parsed question data using templates.
"""

import os
from typing import Dict, List, Any
from pathlib import Path
import re

from ..xml_utils import escape_xml


class XMLGenerator:
    """Generate QTI XML files from question data."""

    def __init__(self, templates_dir: str = None):
        """
        Initialize XML generator.

        Args:
            templates_dir: Path to XML templates directory.
                          Defaults to project's templates/xml/
        """
        if templates_dir is None:
            # Default to project templates directory
            project_root = Path(__file__).parent.parent.parent
            templates_dir = project_root / 'templates' / 'xml'

        self.templates_dir = Path(templates_dir)

        if not self.templates_dir.exists():
            raise ValueError(f"Templates directory not found: {self.templates_dir}")

    def generate_question(self, question_data: Dict[str, Any], language: str = 'en') -> str:
        """
        Generate QTI XML for a single question.

        Args:
            question_data: Parsed question dictionary
            language: ISO 639-1 language code

        Returns:
            Complete QTI XML string for the question
        """
        question_type = question_data.get('question_type', 'multiple_choice_single')

        # Load appropriate template
        template = self._load_template(question_type)

        # Fill template with question data
        xml = self._fill_template(template, question_data, language)

        return xml

    def _load_template(self, question_type: str) -> str:
        """Load XML template for question type."""
        # Map question types to template names
        template_mappings = {
            'fill_in_the_blank': 'text_entry',  # Same structure as text_entry
            'matching': 'match',  # Template is named match.xml
            'gap_match': 'gapmatch'  # Template is named gapmatch.xml
        }

        question_type = template_mappings.get(question_type, question_type)

        template_file = (self.templates_dir / f'{question_type}.xml').resolve()

        # Security: prevent path traversal via crafted question_type
        try:
            template_file.relative_to(self.templates_dir.resolve())
        except ValueError:
            raise ValueError(f"Invalid question type (path traversal blocked): {question_type}")

        if not template_file.exists():
            raise ValueError(f"Template not found for question type: {question_type}")

        with open(template_file, 'r', encoding='utf-8') as f:
            return f.read()

    def _normalize_language_code(self, language: str) -> str:
        """
        Normalize language code to Inspera format (with country code).

        Args:
            language: Language code (e.g., 'sv', 'en', 'no')

        Returns:
            Normalized language code (e.g., 'sv_se', 'en_us', 'no_no')
        """
        # Map simple codes to Inspera's expected format
        language_map = {
            'sv': 'sv_se',
            'en': 'en_us',
            'no': 'no_no',
            'da': 'da_dk',
            'fi': 'fi_fi'
        }

        # Return mapped value if exists, otherwise return original
        return language_map.get(language.lower(), language)

    def _fill_template(self, template: str, question_data: Dict[str, Any], language: str) -> str:
        """Fill template placeholders with question data."""
        from ..parser.markdown_parser import markdown_to_xhtml

        # Normalize language code for Inspera (sv -> sv_se)
        language = self._normalize_language_code(language)

        # Extract common data
        identifier = question_data.get('identifier', 'Q001')
        title = question_data.get('title', 'Question')
        points = question_data.get('points', 1)
        question_text = question_data.get('question_text', '')
        feedback = question_data.get('feedback', {})
        question_type = question_data.get('question_type', 'multiple_choice_single')

        # Convert markdown to XHTML
        question_text_xhtml = markdown_to_xhtml(question_text)

        # Route to appropriate handler based on question type
        if question_type == 'true_false':
            replacements = self._build_true_false_replacements(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )
        elif question_type == 'essay':
            replacements = self._build_essay_replacements(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )
        elif question_type == 'text_area':
            replacements = self._build_text_area_replacements(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )
        elif question_type == 'multiple_response':
            replacements = self._build_multiple_response_replacements(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )
        elif question_type == 'multiple_choice_single':
            replacements = self._build_multiple_choice_replacements(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )
        # Priority 2 types - full implementation for some, stubs for others
        elif question_type == 'hotspot':
            replacements = self._build_hotspot_replacements(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )
        elif question_type in ['match', 'matching']:
            replacements = self._build_match_replacements(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )
        elif question_type in ['text_entry', 'fill_in_the_blank']:
            # fill_in_the_blank is converted to text_entry format by parser
            replacements = self._build_text_entry_replacements(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )
        elif question_type == 'text_entry_math':
            # Math entry: string-based with inspera:type="math"
            replacements = self._build_text_entry_math_replacements(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )
        elif question_type == 'text_entry_numeric':
            # Numeric entry: float-based with tolerance/range support
            replacements = self._build_text_entry_numeric_replacements(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )
        elif question_type == 'inline_choice':
            # Full implementation for inline_choice
            replacements = self._build_inline_choice_replacements(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )
        elif question_type == 'graphicgapmatch_v2':
            # Full implementation for graphicgapmatch_v2
            replacements = self._build_graphicgapmatch_v2_replacements(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )
        elif question_type in ['gapmatch', 'text_entry_graphic']:
            # These complex types require additional data not yet in markdown format
            # For now, provide basic structure with TODO comments
            replacements = self._build_complex_type_stub(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback, question_type
            )
        # Priority 3 types
        elif question_type == 'nativehtml':
            replacements = self._build_nativehtml_replacements(
                question_data, language, identifier, title, question_text_xhtml
            )
        elif question_type == 'audio_record':
            replacements = self._build_audio_record_replacements(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )
        elif question_type == 'composite_editor':
            replacements = self._build_composite_editor_stub(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )
        else:
            # Default to multiple choice
            replacements = self._build_multiple_choice_replacements(
                question_data, language, identifier, title, points,
                question_text_xhtml, feedback
            )

        # Replace all placeholders
        xml = template
        for placeholder, value in replacements.items():
            xml = xml.replace(placeholder, value)

        # Strip XML comments to prevent validation errors from '--' in content
        xml = self._strip_xml_comments(xml)

        return xml

    def _generate_choices(self, options: List[Dict[str, str]], correct_answer: str) -> str:
        """
        Generate simpleChoice XML elements for options.

        Args:
            options: List of option dictionaries with 'letter' and 'text'
            correct_answer: Letter of correct answer (A, B, C, etc.)

        Returns:
            XML string with all simpleChoice elements
        """
        from ..parser.markdown_parser import markdown_to_xhtml

        choices = []

        for i, option in enumerate(options):
            letter = option['letter']
            text = option['text']
            choice_id = f'rId{i}'

            # Convert option text to XHTML
            text_xhtml = markdown_to_xhtml(text)

            # Create simpleChoice element with feedbackInline (Inspera requirement)
            choice_xml = f'<simpleChoice identifier="{choice_id}">{text_xhtml}<feedbackInline identifier="{choice_id}" outcomeIdentifier="RESPONSE" showHide="show"/></simpleChoice>'
            choices.append(choice_xml)

        return '\n            '.join(choices)

    def _get_correct_choice_id(self, options: List[Dict[str, str]], correct_answer: str) -> str:
        """Get the choice identifier for the correct answer."""
        for i, option in enumerate(options):
            if option['letter'] == correct_answer:
                return f'rId{i}'

        # Default to first option if not found
        return 'rId0'

    def _get_true_false_labels(self, language: str) -> tuple:
        """
        Get language-specific True/False labels.

        Args:
            language: ISO 639-1 language code (en, sv, no, etc.)

        Returns:
            Tuple of (true_label, false_label)
        """
        labels = {
            'en': ('True', 'False'),
            'sv': ('Sant', 'Falskt'),
            'no': ('Sann', 'Falsk'),
            'nb': ('Sann', 'Falsk'),  # Norwegian Bokmål
            'nn': ('Sann', 'Falsk'),  # Norwegian Nynorsk
            'da': ('Sandt', 'Falsk'),  # Danish
            'de': ('Wahr', 'Falsch'),  # German
            'es': ('Verdadero', 'Falso'),  # Spanish
            'fr': ('Vrai', 'Faux'),  # French
        }

        # Default to English if language not found
        return labels.get(language, ('True', 'False'))

    def _escape_xml(self, text: str) -> str:
        """Escape special XML characters."""
        return escape_xml(text)

    def _strip_xml_comments(self, xml: str) -> str:
        """
        Remove XML comments from generated XML.

        Template files contain documentation comments that may include
        placeholder values with '--' which violates XML comment syntax.
        Stripping comments after generation prevents validation errors.

        Args:
            xml: XML string potentially containing comments

        Returns:
            XML string with all comments removed
        """
        import re
        # Remove all XML comments (<!-- ... -->)
        # Non-greedy match to handle multiple comments
        return re.sub(r'<!--.*?-->', '', xml, flags=re.DOTALL)

    def _build_true_false_replacements(self, question_data: Dict[str, Any], language: str,
                                       identifier: str, title: str, points: int,
                                       question_text_xhtml: str, feedback: Dict[str, str]) -> Dict[str, str]:
        """Build replacements dictionary for true_false questions."""
        correct_answer = question_data.get('correct_answer', 'A')

        # Get language-specific True/False labels
        true_label, false_label = self._get_true_false_labels(language)

        # Map answer to choice IDs (A=rId0/True, B=rId1/False)
        correct_choice_id = 'rId0' if correct_answer == 'A' else 'rId1'
        incorrect_choice_id = 'rId1' if correct_answer == 'A' else 'rId0'

        # INSPERA REQUIREMENT: All feedback must be identical across states
        # Try 'correct' first, fall back to 'general' (unlabeled format), then placeholder
        unified_feedback = self._escape_xml(
            feedback.get('correct') or feedback.get('general') or 'Correct!'
        )

        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{MAX_SCORE}}': str(points),
            '{{CORRECT_CHOICE_ID}}': correct_choice_id,
            '{{INCORRECT_CHOICE_ID}}': incorrect_choice_id,
            '{{QUESTION_TEXT}}': question_text_xhtml,
            '{{TRUE_LABEL}}': true_label,
            '{{FALSE_LABEL}}': false_label,
            '{{FEEDBACK_CORRECT}}': unified_feedback,
            '{{FEEDBACK_INCORRECT}}': unified_feedback,
            '{{FEEDBACK_UNANSWERED}}': unified_feedback
        }

    def _build_multiple_choice_replacements(self, question_data: Dict[str, Any], language: str,
                                            identifier: str, title: str, points: int,
                                            question_text_xhtml: str, feedback: Dict[str, str]) -> Dict[str, str]:
        """Build replacements dictionary for multiple_choice_single questions."""
        options = question_data.get('options', [])
        correct_answer = question_data.get('correct_answer', 'A')

        # Generate choices XML
        choices_xml = self._generate_choices(options, correct_answer)

        # Find correct choice ID
        correct_choice_id = self._get_correct_choice_id(options, correct_answer)

        # INSPERA REQUIREMENT: All feedback must be identical across states
        # Try 'correct' first, fall back to 'general' (unlabeled format), then placeholder
        unified_feedback = self._escape_xml(
            feedback.get('correct') or feedback.get('general') or 'Correct!'
        )

        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{MAX_SCORE}}': str(points),
            '{{CORRECT_CHOICE_ID}}': correct_choice_id,
            '{{SHUFFLE}}': 'true',  # Default to shuffling
            '{{QUESTION_TEXT}}': question_text_xhtml,
            '{{QUESTION_IMAGES}}': '',  # No images in MVP
            '{{CHOICES}}': choices_xml,
            '{{FEEDBACK_CORRECT}}': unified_feedback,
            '{{FEEDBACK_INCORRECT}}': unified_feedback,
            '{{FEEDBACK_PARTIALLY_CORRECT}}': unified_feedback,
            '{{FEEDBACK_UNANSWERED}}': unified_feedback
        }

    def _build_essay_replacements(self, question_data: Dict[str, Any], language: str,
                                   identifier: str, title: str, points: int,
                                   question_text_xhtml: str, feedback: Dict[str, str]) -> Dict[str, str]:
        """Build replacements dictionary for essay questions."""
        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{MAX_SCORE}}': str(points),
            '{{QUESTION_TEXT}}': question_text_xhtml,
            '{{QUESTION_IMAGES}}': '',  # No images in MVP
            '{{INITIAL_LINES}}': str(question_data.get('initial_lines', 10)),
            '{{MAX_WORDS}}': str(question_data.get('max_words', '')) if question_data.get('max_words') else '',
            '{{SHOW_WORD_COUNT}}': str(question_data.get('show_word_count', 'true')).lower(),
            '{{EDITOR_PROMPT}}': self._escape_xml(question_data.get('editor_prompt', 'Enter your answer here...')),
            '{{FEEDBACK_UNANSWERED}}': self._escape_xml(feedback.get('unanswered', 'Please answer this question.')),
            '{{FEEDBACK_ANSWERED}}': self._escape_xml(feedback.get('answered', 'Thank you for your response.'))
        }

    def _build_text_area_replacements(self, question_data: Dict[str, Any], language: str,
                                      identifier: str, title: str, points: int,
                                      question_text_xhtml: str, feedback: Dict[str, str]) -> Dict[str, str]:
        """Build replacements dictionary for text_area questions."""
        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{MAX_SCORE}}': str(points),
            '{{QUESTION_TEXT}}': question_text_xhtml,
            '{{QUESTION_IMAGES}}': '',  # No images in MVP
            '{{INITIAL_LINES}}': str(question_data.get('initial_lines', 3)),
            '{{FIELD_WIDTH}}': question_data.get('field_width', '100%'),
            '{{SHOW_WORD_COUNT}}': str(question_data.get('show_word_count', 'false')).lower(),
            '{{EDITOR_PROMPT}}': self._escape_xml(question_data.get('editor_prompt', 'Enter your answer here...')),
            '{{FEEDBACK_UNANSWERED}}': self._escape_xml(feedback.get('unanswered', 'Please answer this question.')),
            '{{FEEDBACK_ANSWERED}}': self._escape_xml(feedback.get('answered', 'Thank you for your response.'))
        }

    def _build_multiple_response_replacements(self, question_data: Dict[str, Any], language: str,
                                              identifier: str, title: str, points: int,
                                              question_text_xhtml: str, feedback: Dict[str, str]) -> Dict[str, str]:
        """Build replacements dictionary for multiple_response questions."""
        options = question_data.get('options', [])
        correct_answers = question_data.get('correct_answers', [])

        # If correct_answer is a single letter, convert to list
        if 'correct_answer' in question_data and not correct_answers:
            correct_answers = [question_data['correct_answer']]

        # Generate choices XML
        choices_xml = self._generate_choices(options, None)

        # Generate correct choices XML
        correct_choices_xml = self._generate_correct_choices(options, correct_answers)

        # Generate mapping entries
        mapping_entries = self._generate_mapping_entries(options, correct_answers, points)

        # Generate match logic
        correct_match_logic = self._generate_correct_match_logic(options, correct_answers)
        incorrect_choices_check = self._generate_incorrect_choices_check(options, correct_answers)
        partial_match_logic = self._generate_partial_match_logic(options, correct_answers)

        # Scoring configuration
        points_each_correct = question_data.get('points_each_correct', 1)
        points_each_wrong = question_data.get('points_each_wrong', 0)
        points_all_correct = question_data.get('points_all_correct', points)
        points_minimum = question_data.get('points_minimum', 0)

        # INSPERA REQUIREMENT: All feedback must be identical across states
        # Try 'correct' first, fall back to 'general' (unlabeled format), then placeholder
        unified_feedback = self._escape_xml(
            feedback.get('correct') or feedback.get('general') or 'Correct!'
        )

        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{MAX_SCORE}}': str(points),
            '{{POINTS_EACH_CORRECT}}': str(points_each_correct),
            '{{POINTS_EACH_WRONG}}': str(points_each_wrong),
            '{{POINTS_ALL_CORRECT}}': str(points_all_correct),
            '{{POINTS_MINIMUM}}': str(points_minimum),
            '{{SHUFFLE}}': 'true',  # Default to shuffling
            '{{PROMPT_TEXT}}': self._escape_xml(question_data.get('prompt_text', 'Select all that apply')),
            '{{QUESTION_TEXT}}': question_text_xhtml,
            '{{QUESTION_IMAGES}}': '',  # No images in MVP
            '{{CHOICES}}': choices_xml,
            '{{CORRECT_CHOICES}}': correct_choices_xml,
            '{{MAPPING_ENTRIES}}': mapping_entries,
            '{{CORRECT_MATCH_LOGIC}}': correct_match_logic,
            '{{INCORRECT_CHOICES_CHECK}}': incorrect_choices_check,
            '{{PARTIAL_MATCH_LOGIC}}': partial_match_logic,
            '{{FEEDBACK_CORRECT}}': unified_feedback,
            '{{FEEDBACK_INCORRECT}}': unified_feedback,
            '{{FEEDBACK_PARTIALLY_CORRECT}}': unified_feedback,
            '{{FEEDBACK_UNANSWERED}}': unified_feedback
        }

    def _generate_correct_choices(self, options: List[Dict[str, str]], correct_answers: List[str]) -> str:
        """Generate correct response values for multiple response."""
        values = []
        for i, option in enumerate(options):
            if option['letter'] in correct_answers:
                values.append(f'<value>rId{i}</value>')
        return '\n            '.join(values)

    def _generate_mapping_entries(self, options: List[Dict[str, str]], correct_answers: List[str], points: int) -> str:
        """Generate mapping entries for multiple response scoring."""
        entries = []
        points_per_correct = points / len(correct_answers) if correct_answers else 1

        for i, option in enumerate(options):
            if option['letter'] in correct_answers:
                entries.append(f'<mapEntry mapKey="rId{i}" mappedValue="{points_per_correct}"/>')
        return '\n            '.join(entries)

    def _generate_correct_match_logic(self, options: List[Dict[str, str]], correct_answers: List[str]) -> str:
        """Generate logic to check all correct answers are selected."""
        conditions = []
        for i, option in enumerate(options):
            if option['letter'] in correct_answers:
                conditions.append(f'<member>\n                        <baseValue baseType="identifier">rId{i}</baseValue>\n                        <variable identifier="RESPONSE"/>\n                    </member>')
        return '\n                    '.join(conditions)

    def _generate_incorrect_choices_check(self, options: List[Dict[str, str]], correct_answers: List[str]) -> str:
        """Generate logic to check no incorrect answers are selected."""
        conditions = []
        for i, option in enumerate(options):
            if option['letter'] not in correct_answers:
                conditions.append(f'<member>\n                                <baseValue baseType="identifier">rId{i}</baseValue>\n                                <variable identifier="RESPONSE"/>\n                            </member>')
        return '\n                            '.join(conditions) if conditions else '<not><not><isNull><variable identifier="RESPONSE"/></isNull></not></not>'

    def _generate_partial_match_logic(self, options: List[Dict[str, str]], correct_answers: List[str]) -> str:
        """Generate logic to check at least one correct answer is selected."""
        conditions = []
        for i, option in enumerate(options):
            if option['letter'] in correct_answers:
                conditions.append(f'<member>\n                        <baseValue baseType="identifier">rId{i}</baseValue>\n                        <variable identifier="RESPONSE"/>\n                    </member>')
        return '\n                    '.join(conditions)

    def _build_nativehtml_replacements(self, question_data: Dict[str, Any], language: str,
                                       identifier: str, title: str, question_text_xhtml: str) -> Dict[str, str]:
        """Build replacements dictionary for nativehtml (informational content)."""
        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{QUESTION_IMAGES}}': '',  # No images in MVP
            '{{HTML_CONTENT}}': question_text_xhtml
        }

    def _build_audio_record_replacements(self, question_data: Dict[str, Any], language: str,
                                         identifier: str, title: str, points: int,
                                         question_text_xhtml: str, feedback: Dict[str, str]) -> Dict[str, str]:
        """Build replacements dictionary for audio_record questions."""
        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{MAX_SCORE}}': str(points),
            '{{QUESTION_TEXT}}': question_text_xhtml,
            '{{QUESTION_IMAGES}}': '',  # No images in MVP
            '{{UPLOAD_PROMPT}}': self._escape_xml(question_data.get('upload_prompt', 'Click to record your answer')),
            '{{FEEDBACK_UNANSWERED}}': self._escape_xml(feedback.get('unanswered', 'Please record your answer.')),
            '{{FEEDBACK_ANSWERED}}': self._escape_xml(feedback.get('answered', 'Thank you for your recording.'))
        }

    def _build_hotspot_replacements(self, question_data: Dict[str, Any], language: str,
                                    identifier: str, title: str, points: int,
                                    question_text_xhtml: str, feedback: Dict[str, str]) -> Dict[str, str]:
        """Build replacements dictionary for hotspot questions."""
        # Get image data
        image_data = question_data.get('image', {})
        hotspots_data = question_data.get('hotspots', [])

        # Find the correct hotspot
        correct_hotspot_id = None
        for hotspot in hotspots_data:
            if hotspot.get('correct', False):
                correct_hotspot_id = hotspot['id']
                break

        if not correct_hotspot_id and hotspots_data:
            # Default to first hotspot if none marked correct
            correct_hotspot_id = hotspots_data[0]['id']

        # Generate hotspot choice elements
        hotspots_xml = self._generate_hotspots_xml(hotspots_data)

        # Extract image configuration
        # Get the filename and ensure it has the resources/ prefix
        # Try 'path' first (modern inline images), fallback to 'file' (old format), then default
        image_file = image_data.get('path', image_data.get('file', 'image.png'))
        # If file path doesn't start with resources/, add it
        if not image_file.startswith('resources/'):
            # Extract just the filename if it has a path
            import os
            image_filename = os.path.basename(image_file)
            background_image = f'resources/{image_filename}'
        else:
            background_image = image_file

        canvas_height = image_data.get('canvas_height', 400)
        image_title = image_data.get('title', 'Question Image')
        logical_name = image_data.get('logical_name', 'image')

        # Coloring configuration (optional in question_data)
        enable_coloring = str(question_data.get('enable_coloring', 'true')).lower()
        shape_color = question_data.get('shape_color', '#0e98f0')
        shape_opacity = str(question_data.get('shape_opacity', '0.4'))

        # For hotspot questions, remove <img> tags from question text to avoid duplicate images
        # The image should only appear in the hotspot interaction, not in the question text
        cleaned_question_text = re.sub(r'<img[^>]*/?>', '', question_text_xhtml)

        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{MAX_SCORE}}': str(points),
            '{{SCORE_WRONG}}': '0',
            '{{SCORE_UNANSWERED}}': '0',
            '{{QUESTION_TEXT}}': cleaned_question_text,
            '{{QUESTION_IMAGES}}': '',  # Optional additional images above hotspot
            '{{PROMPT_TEXT}}': self._escape_xml(question_data.get('prompt_text', 'Click on the correct area')),
            '{{BACKGROUND_IMAGE}}': background_image,
            '{{IMAGE_LOGICAL_NAME}}': logical_name,
            '{{IMAGE_TITLE}}': self._escape_xml(image_title),
            '{{CANVAS_HEIGHT}}': str(canvas_height),
            '{{CORRECT_HOTSPOT_ID}}': correct_hotspot_id or 'HOTSPOT1',
            '{{HOTSPOTS}}': hotspots_xml,
            '{{ENABLE_COLORING}}': enable_coloring,
            '{{SHAPE_COLOR}}': shape_color,
            '{{SHAPE_OPACITY}}': shape_opacity,
            # INSPERA REQUIREMENT: All feedback must be identical across states
            # Try 'correct' first, fall back to 'general' (unlabeled format), then placeholder
            '{{FEEDBACK_CORRECT}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Correct!'),
            '{{FEEDBACK_INCORRECT}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Correct!'),
            '{{FEEDBACK_PARTIALLY_CORRECT}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Correct!'),
            '{{FEEDBACK_UNANSWERED}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Correct!')
        }

    def _generate_hotspots_xml(self, hotspots: List[Dict[str, Any]]) -> str:
        """
        Generate hotspotChoice XML elements for hotspot questions.

        Args:
            hotspots: List of hotspot dictionaries with id, shape, coords, label

        Returns:
            XML string with all hotspotChoice elements
        """
        hotspot_elements = []

        for hotspot in hotspots:
            hotspot_id = hotspot['id']
            shape = hotspot['shape']
            coords = hotspot['coords']
            label = hotspot.get('label', '')

            hotspot_xml = f'<hotspotChoice coords="{coords}" hotspotLabel="{self._escape_xml(label)}" identifier="{hotspot_id}" matchMax="0" shape="{shape}"/>'
            hotspot_elements.append(hotspot_xml)

        return '\n            '.join(hotspot_elements)

    def _build_match_replacements(self, question_data: Dict[str, Any], language: str,
                                  identifier: str, title: str, points: int,
                                  question_text_xhtml: str, feedback: Dict[str, str]) -> Dict[str, str]:
        """Build replacements dictionary for match questions."""
        # Get match data
        premises = question_data.get('premises', [])
        match_responses = question_data.get('match_responses', [])
        pairings = question_data.get('match_pairings', [])
        scoring = question_data.get('scoring', {})

        # Get scoring configuration
        points_each_correct = scoring.get('points_each_correct', 1)
        points_each_wrong = scoring.get('points_each_wrong', 0)
        points_minimum = scoring.get('points_minimum', 0)
        # Default total points: number of correct pairings * points each
        points_all_correct = scoring.get('points_all_correct', len(pairings) * points_each_correct)

        # Generate XML elements
        left_column_xml = self._generate_match_premises_xml(premises)
        right_column_xml = self._generate_match_responses_xml(match_responses, len(premises))
        correct_pairs_xml = self._generate_correct_pairs_xml(pairings)
        mapping_entries_xml = self._generate_mapping_entries_xml(pairings, points_each_correct, points_each_wrong)

        # Generate response processing checks
        correct_pair_checks = self._generate_directed_pair_checks(pairings, 'RESPONSE-1')
        any_correct_checks = self._generate_any_correct_pair_checks(pairings, 'RESPONSE-1')

        # Match configuration
        max_associations = len(pairings)  # Should equal number of pairs (Inspera format)
        randomize = question_data.get('randomize', '')  # Empty string default (Inspera format)
        shuffle = str(question_data.get('shuffle', 'false')).lower()

        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{POINTS_EACH_CORRECT}}': str(points_each_correct),
            '{{POINTS_EACH_WRONG}}': str(points_each_wrong),
            '{{POINTS_ALL_CORRECT}}': str(points_all_correct),
            '{{POINTS_MINIMUM}}': str(points_minimum),
            '{{POINTS_UNANSWERED}}': '0',
            '{{QUESTION_TEXT}}': question_text_xhtml,
            '{{QUESTION_IMAGES}}': '',
            '{{PROMPT_TEXT}}': self._escape_xml(question_data.get('prompt_text', 'Match the items:')),
            '{{MAX_ASSOCIATIONS}}': str(max_associations),
            '{{RANDOMIZE}}': randomize,
            '{{SHUFFLE}}': shuffle,
            '{{LEFT_COLUMN_ITEMS}}': left_column_xml,
            '{{RIGHT_COLUMN_ITEMS}}': right_column_xml,
            '{{CORRECT_PAIRS}}': correct_pairs_xml,
            '{{MAPPING_ENTRIES}}': mapping_entries_xml,
            '{{CORRECT_PAIR_CHECKS}}': correct_pair_checks,
            '{{ANY_CORRECT_PAIR_CHECKS}}': any_correct_checks,
            # INSPERA REQUIREMENT: All feedback must be identical across states
            # Try 'correct' first, fall back to 'general' (unlabeled format), then placeholder
            '{{FEEDBACK_CORRECT}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Excellent! All matches are correct.'),
            '{{FEEDBACK_INCORRECT}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Excellent! All matches are correct.'),
            '{{FEEDBACK_PARTIALLY_CORRECT}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Excellent! All matches are correct.'),
            '{{FEEDBACK_UNANSWERED}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Excellent! All matches are correct.')
        }

    def _generate_match_premises_xml(self, premises: List[Dict[str, Any]]) -> str:
        """Generate simpleAssociableChoice elements for left column (premises)."""
        premise_elements = []

        for premise in premises:
            premise_id = premise['id']
            premise_text = self._escape_xml(premise['text'])

            premise_xml = f'<simpleAssociableChoice identifier="{premise_id}" matchMax="1">\n                    <span class="label">{premise_text}</span>\n                </simpleAssociableChoice>'
            premise_elements.append(premise_xml)

        return '\n                '.join(premise_elements)

    def _generate_match_responses_xml(self, responses: List[Dict[str, Any]], num_premises: int) -> str:
        """Generate simpleAssociableChoice elements for right column (responses)."""
        response_elements = []

        for response in responses:
            response_id = response['id']
            response_text = self._escape_xml(response['text'])

            # Responses can match multiple premises (matchMax = number of premises, Inspera format)
            response_xml = f'<simpleAssociableChoice identifier="{response_id}" matchMax="{num_premises}">\n                    <span class="label">{response_text}</span>\n                </simpleAssociableChoice>'
            response_elements.append(response_xml)

        return '\n                '.join(response_elements)

    def _generate_correct_pairs_xml(self, pairings: List[Dict[str, str]]) -> str:
        """Generate correct response values for match questions."""
        pair_values = []

        for pairing in pairings:
            premise_id = pairing['premise']
            response_id = pairing['response']
            pair_values.append(f'<value>{premise_id} {response_id}</value>')

        return '\n            '.join(pair_values)

    def _generate_mapping_entries_xml(self, pairings: List[Dict[str, str]],
                                      points_correct: float, points_wrong: float) -> str:
        """Generate mapping entries for directed pairs."""
        entries = []

        for pairing in pairings:
            premise_id = pairing['premise']
            response_id = pairing['response']
            entries.append(f'<mapEntry mapKey="{premise_id} {response_id}" mappedValue="{points_correct}"/>')

        return '\n            '.join(entries)

    def _generate_directed_pair_checks(self, pairings: List[Dict[str, str]], response_id: str) -> str:
        """Generate member checks for all correct directed pairs (for all correct condition)."""
        checks = []

        for pairing in pairings:
            premise_id = pairing['premise']
            response_id_val = pairing['response']
            check_xml = f'<member>\n                        <baseValue baseType="directedPair">{premise_id} {response_id_val}</baseValue>\n                        <variable identifier="{response_id}"/>\n                    </member>'
            checks.append(check_xml)

        return '\n                    '.join(checks)

    def _generate_any_correct_pair_checks(self, pairings: List[Dict[str, str]], response_id: str) -> str:
        """Generate member checks for any correct directed pair (for partial correct condition)."""
        checks = []

        for pairing in pairings:
            premise_id = pairing['premise']
            response_id_val = pairing['response']
            check_xml = f'<member>\n                        <baseValue baseType="directedPair">{premise_id} {response_id_val}</baseValue>\n                        <variable identifier="{response_id}"/>\n                    </member>'
            checks.append(check_xml)

        return '\n                        '.join(checks)

    def _build_text_entry_replacements(self, question_data: Dict[str, Any], language: str,
                                       identifier: str, title: str, points: int,
                                       question_text_xhtml: str, feedback: Dict[str, str]) -> Dict[str, str]:
        """Build replacements dictionary for text_entry questions."""
        # Get blanks data
        blanks = question_data.get('blanks', [])
        scoring = question_data.get('scoring', {})

        if not blanks:
            raise ValueError("Text entry question requires blanks definition")

        # Get scoring configuration
        points_each_correct = scoring.get('points_each_correct', 1)
        points_each_wrong = scoring.get('points_each_wrong', 0)
        points_all_correct = scoring.get('points_all_correct', len(blanks) * points_each_correct)
        points_unanswered = scoring.get('points_unanswered', 0)

        # Generate response declarations for each blank
        response_declarations = self._generate_text_entry_response_declarations(blanks)

        # Generate outcome declarations for per-field correctness
        outcome_declarations = self._generate_text_entry_outcome_declarations(blanks)

        # Replace {{blank_N}} markers with textEntryInteraction elements
        question_text_with_fields = self._generate_text_entry_fields(question_text_xhtml, blanks)

        # Generate field scoring logic (string matching for each field)
        field_scoring_logic = self._generate_text_entry_scoring_logic(blanks, points_each_correct)

        # Generate checks for response processing
        unanswered_checks = self._generate_text_entry_unanswered_checks(blanks)
        all_correct_checks = self._generate_text_entry_all_correct_checks(blanks)
        any_correct_checks = self._generate_text_entry_any_correct_checks(blanks)

        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{POINTS_EACH_CORRECT}}': str(points_each_correct),
            '{{POINTS_EACH_WRONG}}': str(points_each_wrong),
            '{{POINTS_ALL_CORRECT}}': str(points_all_correct),
            '{{POINTS_UNANSWERED}}': str(points_unanswered),
            '{{RESPONSE_DECLARATIONS}}': response_declarations,
            '{{OUTCOME_DECLARATIONS}}': outcome_declarations,
            '{{QUESTION_TEXT_WITH_FIELDS}}': question_text_with_fields,
            '{{QUESTION_IMAGES}}': '',  # No images in text_entry
            '{{FIELD_SCORING_LOGIC}}': field_scoring_logic,
            '{{UNANSWERED_CHECKS}}': unanswered_checks,
            '{{ALL_CORRECT_CHECKS}}': all_correct_checks,
            '{{ANY_CORRECT_CHECKS}}': any_correct_checks,
            # INSPERA REQUIREMENT: All feedback must be identical across states
            # Try 'correct' first, fall back to 'general' (unlabeled format), then placeholder
            '{{FEEDBACK_CORRECT}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Excellent! All answers are correct.'),
            '{{FEEDBACK_INCORRECT}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Excellent! All answers are correct.'),
            '{{FEEDBACK_PARTIALLY_CORRECT}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Excellent! All answers are correct.'),
            '{{FEEDBACK_UNANSWERED}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Excellent! All answers are correct.')
        }

    def _generate_text_entry_response_declarations(self, blanks: List[Dict[str, Any]]) -> str:
        """Generate response declarations for each text entry field."""
        declarations = []

        for blank in blanks:
            blank_id = blank['identifier']
            correct_answer = self._escape_xml(blank['correct_answer'])

            declaration = f'''<responseDeclaration baseType="string" cardinality="single" identifier="{blank_id}">
        <correctResponse>
            <value>{correct_answer}</value>
        </correctResponse>
    </responseDeclaration>'''
            declarations.append(declaration)

        return '\n\n    '.join(declarations)

    def _generate_text_entry_outcome_declarations(self, blanks: List[Dict[str, Any]]) -> str:
        """Generate per-field correctness outcome declarations."""
        declarations = []

        for blank in blanks:
            blank_id = blank['identifier']
            declaration = f'<outcomeDeclaration baseType="boolean" cardinality="single" identifier="isCorrect_{blank_id}"/>'
            declarations.append(declaration)

        return '\n    '.join(declarations)

    def _generate_text_entry_fields(self, question_text: str, blanks: List[Dict[str, Any]]) -> str:
        """Replace {{blank_N}} markers with textEntryInteraction elements."""
        result = question_text

        for blank in blanks:
            blank_num = blank['number']
            blank_id = blank['identifier']
            expected_length = blank.get('expected_length', 15)

            # Create textEntryInteraction element
            interaction = f'<textEntryInteraction expectedLength="{expected_length}" responseIdentifier="{blank_id}"/>'

            # Replace v6.5 marker: {{blank_N}}
            marker = f'{{{{blank_{blank_num}}}}}'
            result = result.replace(marker, interaction)

        return result

    def _generate_text_entry_scoring_logic(self, blanks: List[Dict[str, Any]], points_per_correct: float) -> str:
        """Generate string matching logic for each field with alternatives."""
        logic_blocks = []

        for blank in blanks:
            blank_id = blank['identifier']
            correct_answer = blank['correct_answer']
            alternatives = blank.get('alternatives', [])
            case_sensitive = blank.get('case_sensitive', False)

            # Build string match conditions (correct answer + alternatives)
            all_answers = [correct_answer] + alternatives
            match_conditions = []

            case_attr = 'true' if case_sensitive else 'false'

            for answer in all_answers:
                answer_escaped = self._escape_xml(answer)
                match_condition = f'''<stringMatch caseSensitive="{case_attr}">
                        <baseValue baseType="string">{answer_escaped}</baseValue>
                        <variable identifier="{blank_id}"/>
                    </stringMatch>'''
                match_conditions.append(match_condition)

            # If multiple answers, wrap in <or>
            if len(match_conditions) > 1:
                condition_logic = f'''<or>
                    {chr(10).join(match_conditions)}
                </or>'''
            else:
                condition_logic = match_conditions[0]

            # Build response condition block
            logic_block = f'''<responseCondition>
            <responseIf>
                <and>
                    {condition_logic}
                </and>
                <setOutcomeValue identifier="SCORE">
                    <sum>
                        <variable identifier="SCORE"/>
                        <variable identifier="SCORE_EACH_CORRECT"/>
                    </sum>
                </setOutcomeValue>
                <setOutcomeValue identifier="isCorrect_{blank_id}">
                    <baseValue baseType="boolean">true</baseValue>
                </setOutcomeValue>
            </responseIf>
        </responseCondition>'''

            logic_blocks.append(logic_block)

        return '\n\n        '.join(logic_blocks)

    def _generate_text_entry_unanswered_checks(self, blanks: List[Dict[str, Any]]) -> str:
        """Generate null checks for all fields."""
        checks = []

        for blank in blanks:
            blank_id = blank['identifier']
            checks.append(f'<isNull>\n                        <variable identifier="{blank_id}"/>\n                    </isNull>')

        return '\n                    '.join(checks)

    def _generate_text_entry_all_correct_checks(self, blanks: List[Dict[str, Any]]) -> str:
        """Generate correctness checks for all fields."""
        checks = []

        for blank in blanks:
            blank_id = blank['identifier']
            checks.append(f'''<equal toleranceMode="exact">
                        <variable identifier="isCorrect_{blank_id}"/>
                        <baseValue baseType="boolean">true</baseValue>
                    </equal>''')

        return '\n                    '.join(checks)

    def _generate_text_entry_any_correct_checks(self, blanks: List[Dict[str, Any]]) -> str:
        """Generate check for at least one correct field."""
        checks = []

        for blank in blanks:
            blank_id = blank['identifier']
            checks.append(f'''<equal toleranceMode="exact">
                        <variable identifier="isCorrect_{blank_id}"/>
                        <baseValue baseType="boolean">true</baseValue>
                    </equal>''')

        return '\n                    '.join(checks)

    # =========================================================================
    # TEXT ENTRY MATH - String-based with inspera:type="math"
    # =========================================================================

    def _build_text_entry_math_replacements(self, question_data: Dict[str, Any], language: str,
                                            identifier: str, title: str, points: int,
                                            question_text_xhtml: str, feedback: Dict[str, str]) -> Dict[str, str]:
        """Build replacements dictionary for text_entry_math questions."""
        # Get blanks data
        blanks = question_data.get('blanks', [])
        scoring = question_data.get('scoring', {})

        if not blanks:
            raise ValueError("text_entry_math question requires blanks definition")

        # Get scoring configuration
        points_each_correct = scoring.get('points_each_correct', points / len(blanks) if blanks else 1)
        points_each_wrong = scoring.get('points_each_wrong', 0)

        # Generate response declarations (string-based for math)
        response_declarations = self._generate_text_entry_math_response_declarations(blanks)

        # Generate outcome declarations
        outcome_declarations = self._generate_text_entry_outcome_declarations(blanks)

        # Replace markers with textEntryInteraction (with inspera:type="math")
        question_text_with_fields = self._generate_text_entry_math_fields(question_text_xhtml, blanks)

        # Generate string matching logic
        field_scoring_logic = self._generate_text_entry_math_scoring_logic(blanks)

        # Generate checks
        unanswered_checks = self._generate_text_entry_unanswered_checks(blanks)
        all_correct_checks = self._generate_text_entry_all_correct_checks(blanks)
        any_correct_checks = self._generate_text_entry_any_correct_checks(blanks)

        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{MAX_SCORE}}': str(points),
            '{{POINTS_EACH_CORRECT}}': str(points_each_correct),
            '{{POINTS_EACH_WRONG}}': str(points_each_wrong),
            '{{RESPONSE_DECLARATIONS}}': response_declarations,
            '{{OUTCOME_DECLARATIONS}}': outcome_declarations,
            '{{QUESTION_TEXT_WITH_FIELDS}}': question_text_with_fields,
            '{{FIELD_SCORING_LOGIC}}': field_scoring_logic,
            '{{UNANSWERED_CHECKS}}': unanswered_checks,
            '{{ALL_CORRECT_CHECKS}}': all_correct_checks,
            '{{ANY_CORRECT_CHECKS}}': any_correct_checks,
            '{{FEEDBACK_CORRECT}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or ''),
            '{{FEEDBACK_INCORRECT}}': self._escape_xml(feedback.get('incorrect') or feedback.get('general') or ''),
            '{{FEEDBACK_PARTIALLY_CORRECT}}': self._escape_xml(feedback.get('partially_correct') or feedback.get('general') or ''),
            '{{FEEDBACK_UNANSWERED}}': self._escape_xml(feedback.get('unanswered') or '')
        }

    def _generate_text_entry_math_response_declarations(self, blanks: List[Dict[str, Any]]) -> str:
        """Generate string-based response declarations for math entry."""
        declarations = []

        for blank in blanks:
            blank_id = blank['identifier']
            correct_answer = blank['correct_answer']
            alternatives = blank.get('alternatives', [])

            # Combine correct answer with alternatives
            all_answers = [correct_answer] + alternatives

            # Generate <value> tags for all correct answers
            value_tags = '\n            '.join([
                f'<value>{self._escape_xml(str(answer))}</value>'
                for answer in all_answers
            ])

            declaration = f'''<responseDeclaration baseType="string" cardinality="single" identifier="{blank_id}">
        <correctResponse>
            {value_tags}
        </correctResponse>
    </responseDeclaration>'''
            declarations.append(declaration)

        return '\n\n    '.join(declarations)

    def _generate_text_entry_math_fields(self, question_text: str, blanks: List[Dict[str, Any]]) -> str:
        """Replace markers with textEntryInteraction elements (inspera:type="math")."""
        result = question_text

        for blank in blanks:
            blank_num = blank['number']
            blank_id = blank['identifier']
            expected_length = blank.get('expected_length', 20)

            # Create textEntryInteraction with inspera:type="math"
            interaction = f'<textEntryInteraction expectedLength="{expected_length}" inspera:type="math" responseIdentifier="{blank_id}"/>'

            # Replace v6.5 marker: {{blank_N}}
            marker = f'{{{{blank_{blank_num}}}}}'
            result = result.replace(marker, interaction)

        return result

    def _generate_text_entry_math_scoring_logic(self, blanks: List[Dict[str, Any]]) -> str:
        """Generate string matching logic for math entry fields with alternatives."""
        logic_blocks = []

        for blank in blanks:
            blank_id = blank['identifier']
            correct_answer = blank['correct_answer']
            alternatives = blank.get('alternatives', [])
            case_sensitive = blank.get('case_sensitive', False)
            case_attr = 'true' if case_sensitive else 'false'

            # Combine correct answer with alternatives
            all_answers = [correct_answer] + alternatives
            match_conditions = []

            for answer in all_answers:
                answer_escaped = self._escape_xml(str(answer))
                match_condition = f'''<stringMatch caseSensitive="{case_attr}" inspera:ignoredCharacters="">
                    <baseValue baseType="string">{answer_escaped}</baseValue>
                    <variable identifier="{blank_id}"/>
                </stringMatch>'''
                match_conditions.append(match_condition)

            # If multiple answers, wrap in <or>
            if len(match_conditions) > 1:
                condition_logic = '<or>\n                    ' + '\n                    '.join(match_conditions) + '\n                </or>'
            else:
                condition_logic = match_conditions[0]

            logic_block = f'''<responseCondition>
            <responseIf>
                {condition_logic}
                <setOutcomeValue identifier="SCORE">
                    <sum>
                        <variable identifier="SCORE"/>
                        <variable identifier="SCORE_EACH_CORRECT"/>
                    </sum>
                </setOutcomeValue>
                <setOutcomeValue identifier="isCorrect_{blank_id}">
                    <baseValue baseType="string">true</baseValue>
                </setOutcomeValue>
            </responseIf>
            <responseElse>
                <setOutcomeValue identifier="SCORE">
                    <sum>
                        <variable identifier="SCORE"/>
                        <variable identifier="SCORE_EACH_WRONG"/>
                    </sum>
                </setOutcomeValue>
            </responseElse>
        </responseCondition>'''

            logic_blocks.append(logic_block)

        return '\n\n        '.join(logic_blocks)

    # =========================================================================
    # TEXT ENTRY NUMERIC - Float-based with range/tolerance support
    # =========================================================================

    def _build_text_entry_numeric_replacements(self, question_data: Dict[str, Any], language: str,
                                               identifier: str, title: str, points: int,
                                               question_text_xhtml: str, feedback: Dict[str, str]) -> Dict[str, str]:
        """Build replacements dictionary for text_entry_numeric questions."""
        # Get blanks data
        blanks = question_data.get('blanks', [])
        scoring = question_data.get('scoring', {})

        if not blanks:
            raise ValueError("text_entry_numeric question requires blanks definition")

        # Get scoring configuration
        points_each_correct = scoring.get('points_each_correct', points / len(blanks) if blanks else 1)
        points_each_wrong = scoring.get('points_each_wrong', 0)

        # Generate response declarations (float-based for numeric)
        response_declarations = self._generate_text_entry_numeric_response_declarations(blanks)

        # Generate outcome declarations
        outcome_declarations = self._generate_text_entry_outcome_declarations(blanks)

        # Replace markers with textEntryInteraction (with inspera:type="numeric")
        question_text_with_fields = self._generate_text_entry_numeric_fields(question_text_xhtml, blanks)

        # Generate numeric range comparison logic
        field_scoring_logic = self._generate_text_entry_numeric_scoring_logic(blanks)

        # Generate checks
        unanswered_checks = self._generate_text_entry_unanswered_checks(blanks)
        all_correct_checks = self._generate_text_entry_all_correct_checks(blanks)
        any_correct_checks = self._generate_text_entry_any_correct_checks(blanks)

        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{MAX_SCORE}}': str(points),
            '{{POINTS_EACH_CORRECT}}': str(points_each_correct),
            '{{POINTS_EACH_WRONG}}': str(points_each_wrong),
            '{{RESPONSE_DECLARATIONS}}': response_declarations,
            '{{OUTCOME_DECLARATIONS}}': outcome_declarations,
            '{{QUESTION_TEXT_WITH_FIELDS}}': question_text_with_fields,
            '{{FIELD_SCORING_LOGIC}}': field_scoring_logic,
            '{{UNANSWERED_CHECKS}}': unanswered_checks,
            '{{ALL_CORRECT_CHECKS}}': all_correct_checks,
            '{{ANY_CORRECT_CHECKS}}': any_correct_checks,
            '{{FEEDBACK_CORRECT}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or ''),
            '{{FEEDBACK_INCORRECT}}': self._escape_xml(feedback.get('incorrect') or feedback.get('general') or ''),
            '{{FEEDBACK_PARTIALLY_CORRECT}}': self._escape_xml(feedback.get('partially_correct') or feedback.get('general') or ''),
            '{{FEEDBACK_UNANSWERED}}': self._escape_xml(feedback.get('unanswered') or '')
        }

    def _generate_text_entry_numeric_response_declarations(self, blanks: List[Dict[str, Any]]) -> str:
        """Generate float-based response declarations for numeric entry."""
        declarations = []

        for blank in blanks:
            blank_id = blank['identifier']
            correct_answer = blank['correct_answer']

            declaration = f'''<responseDeclaration baseType="float" cardinality="single" identifier="{blank_id}">
        <correctResponse>
            <value>{correct_answer}</value>
        </correctResponse>
    </responseDeclaration>'''
            declarations.append(declaration)

        return '\n\n    '.join(declarations)

    def _generate_text_entry_numeric_fields(self, question_text: str, blanks: List[Dict[str, Any]]) -> str:
        """Replace markers with textEntryInteraction elements (inspera:type="numeric")."""
        result = question_text

        for blank in blanks:
            blank_num = blank['number']
            blank_id = blank['identifier']
            expected_length = blank.get('expected_length', 10)

            # Create textEntryInteraction with inspera:type="numeric"
            interaction = f'<textEntryInteraction expectedLength="{expected_length}" inspera:type="numeric" responseIdentifier="{blank_id}"/>'

            # Replace v6.5 marker: {{blank_N}}
            marker = f'{{{{blank_{blank_num}}}}}'
            result = result.replace(marker, interaction)

        return result

    def _generate_text_entry_numeric_scoring_logic(self, blanks: List[Dict[str, Any]]) -> str:
        """Generate numeric range comparison logic (gte/lte) for each field."""
        logic_blocks = []

        for blank in blanks:
            blank_id = blank['identifier']
            correct_answer = float(blank['correct_answer'])

            # Get tolerance or min/max values
            tolerance = blank.get('tolerance', 0)
            min_val = blank.get('minimum', correct_answer - tolerance)
            max_val = blank.get('maximum', correct_answer + tolerance)

            logic_block = f'''<responseCondition>
            <responseIf>
                <and>
                    <gte>
                        <variable identifier="{blank_id}"/>
                        <baseValue baseType="float">{min_val}</baseValue>
                    </gte>
                    <lte>
                        <variable identifier="{blank_id}"/>
                        <baseValue baseType="float">{max_val}</baseValue>
                    </lte>
                </and>
                <setOutcomeValue identifier="SCORE">
                    <sum>
                        <variable identifier="SCORE"/>
                        <variable identifier="SCORE_EACH_CORRECT"/>
                    </sum>
                </setOutcomeValue>
                <setOutcomeValue identifier="isCorrect_{blank_id}">
                    <baseValue baseType="string">true</baseValue>
                </setOutcomeValue>
            </responseIf>
            <responseElse>
                <setOutcomeValue identifier="SCORE">
                    <sum>
                        <variable identifier="SCORE"/>
                        <variable identifier="SCORE_EACH_WRONG"/>
                    </sum>
                </setOutcomeValue>
            </responseElse>
        </responseCondition>'''

            logic_blocks.append(logic_block)

        return '\n\n        '.join(logic_blocks)

    def _build_inline_choice_replacements(self, question_data: Dict[str, Any], language: str,
                                          identifier: str, title: str, points: int,
                                          question_text_xhtml: str, feedback: Dict[str, str]) -> Dict[str, str]:
        """Build replacements dictionary for inline_choice questions (Evolution format)."""
        # Get inline choices and correct answers from Evolution format
        inline_choices = question_data.get('inline_choices', {})
        correct_answers = question_data.get('correct_answers_dict', {})
        scoring = question_data.get('scoring', {})

        if not inline_choices or not correct_answers:
            raise ValueError("inline_choice question requires inline_choices and correct_answers_dict")

        # Get scoring configuration
        points_each_correct = scoring.get('points_each_correct', 1)
        points_each_wrong = scoring.get('points_each_wrong', 0)
        points_all_correct = scoring.get('points_all_correct', len(correct_answers) * points_each_correct)
        points_minimum = scoring.get('points_minimum', 0)
        points_unanswered = scoring.get('points_unanswered', 0)

        # Generate response declarations for each dropdown
        response_declarations = self._generate_inline_choice_response_declarations(
            inline_choices, correct_answers, points_each_correct, points_each_wrong
        )

        # Replace {{dropdown_N}} markers with inlineChoiceInteraction elements
        question_text_with_dropdowns = self._generate_inline_choice_interactions(
            question_text_xhtml, inline_choices, correct_answers
        )

        # Generate response processing checks
        unanswered_checks = self._generate_inline_choice_unanswered_checks(inline_choices)
        map_responses = self._generate_inline_choice_map_responses(inline_choices)
        all_correct_checks = self._generate_inline_choice_all_correct_checks(inline_choices, correct_answers)
        any_correct_checks = self._generate_inline_choice_any_correct_checks(inline_choices, correct_answers)

        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{NUM_DROPDOWNS}}': str(len(inline_choices)),
            '{{POINTS_EACH_CORRECT}}': str(points_each_correct),
            '{{POINTS_EACH_WRONG}}': str(points_each_wrong),
            '{{POINTS_ALL_CORRECT}}': str(points_all_correct),
            '{{POINTS_MINIMUM}}': str(points_minimum),
            '{{POINTS_UNANSWERED}}': str(points_unanswered),
            '{{RESPONSE_DECLARATIONS}}': response_declarations,
            '{{QUESTION_TEXT_WITH_DROPDOWNS}}': question_text_with_dropdowns,
            '{{QUESTION_IMAGES}}': '',
            '{{SHUFFLE}}': 'false',
            '{{UNANSWERED_CHECKS}}': unanswered_checks,
            '{{MAP_RESPONSES}}': map_responses,
            '{{ALL_CORRECT_CHECKS}}': all_correct_checks,
            '{{ANY_CORRECT_CHECKS}}': any_correct_checks,
            # INSPERA REQUIREMENT: All feedback must be identical across states
            # Try 'correct' first, fall back to 'general' (unlabeled format), then placeholder
            '{{FEEDBACK_CORRECT}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Correct!'),
            '{{FEEDBACK_INCORRECT}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Correct!'),
            '{{FEEDBACK_PARTIALLY_CORRECT}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Correct!'),
            '{{FEEDBACK_UNANSWERED}}': self._escape_xml(feedback.get('correct') or feedback.get('general') or 'Correct!')
        }

    def _build_complex_type_stub(self, question_data: Dict[str, Any], language: str,
                                 identifier: str, title: str, points: int,
                                 question_text_xhtml: str, feedback: Dict[str, str],
                                 question_type: str) -> Dict[str, str]:
        """
        Build stub replacements for complex Priority 2 question types.

        These question types require additional data (images, coordinates, etc.)
        not yet supported in the markdown format. This provides basic structure
        with placeholder values.

        TODO: Implement full support with enhanced markdown format or JSON config.
        """
        # INSPERA REQUIREMENT: All feedback must be identical across states
        # Try 'correct' first, fall back to 'general' (unlabeled format), then placeholder
        unified_feedback = self._escape_xml(
            feedback.get('correct') or feedback.get('general') or 'Correct!'
        )

        # Common replacements for all complex types
        common = {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{QUESTION_TEXT}}': question_text_xhtml,
            '{{QUESTION_IMAGES}}': '',
            '{{POINTS_EACH_CORRECT}}': '1',
            '{{POINTS_EACH_WRONG}}': '0',
            '{{POINTS_ALL_CORRECT}}': str(points),
            '{{POINTS_MINIMUM}}': '0',
            '{{POINTS_UNANSWERED}}': '0',
            '{{MAX_SCORE}}': str(points),
            '{{FEEDBACK_CORRECT}}': unified_feedback,
            '{{FEEDBACK_INCORRECT}}': unified_feedback,
            '{{FEEDBACK_PARTIALLY_CORRECT}}': unified_feedback,
            '{{FEEDBACK_UNANSWERED}}': unified_feedback
        }

        # Type-specific stub placeholders
        if question_type == 'text_entry':
            common.update({
                '{{RESPONSE_DECLARATIONS}}': '<responseDeclaration baseType="string" cardinality="single" identifier="RESPONSE-1"><correctResponse><value>TODO</value></correctResponse></responseDeclaration>',
                '{{OUTCOME_DECLARATIONS}}': '<outcomeDeclaration baseType="boolean" cardinality="single" identifier="isCorrect_RESPONSE-1"/>',
                '{{QUESTION_TEXT_WITH_FIELDS}}': f'{question_text_xhtml}<p>Fill in the blank: <textEntryInteraction expectedLength="15" responseIdentifier="RESPONSE-1"/></p>',
                '{{FIELD_SCORING_LOGIC}}': '<responseCondition><responseIf><and><stringMatch caseSensitive="false"><baseValue baseType="string">TODO</baseValue><variable identifier="RESPONSE-1"/></stringMatch></and><setOutcomeValue identifier="SCORE"><sum><variable identifier="SCORE"/><variable identifier="SCORE_EACH_CORRECT"/></sum></setOutcomeValue><setOutcomeValue identifier="isCorrect_RESPONSE-1"><baseValue baseType="boolean">true</baseValue></setOutcomeValue></responseIf></responseCondition>',
                '{{UNANSWERED_CHECKS}}': '<isNull><variable identifier="RESPONSE-1"/></isNull>',
                '{{ALL_CORRECT_CHECKS}}': '<equal toleranceMode="exact"><variable identifier="isCorrect_RESPONSE-1"/><baseValue baseType="boolean">true</baseValue></equal>',
                '{{ANY_CORRECT_CHECKS}}': '<equal toleranceMode="exact"><variable identifier="isCorrect_RESPONSE-1"/><baseValue baseType="boolean">true</baseValue></equal>'
            })
        elif question_type == 'inline_choice':
            common.update({
                '{{RESPONSE_DECLARATIONS}}': '<responseDeclaration baseType="identifier" cardinality="single" identifier="RESPONSE-1"><correctResponse><value>choice_1_1</value></correctResponse><mapping defaultValue="0"><mapEntry mapKey="choice_1_1" mappedValue="1"/></mapping></responseDeclaration>',
                '{{QUESTION_TEXT_WITH_DROPDOWNS}}': f'{question_text_xhtml}<p>Select the correct answer: <inlineChoiceInteraction maxChoices="1" responseIdentifier="RESPONSE-1" shuffle="false"><simpleChoice identifier="choice_1_1">Option 1</simpleChoice><simpleChoice identifier="choice_1_2">Option 2</simpleChoice></inlineChoiceInteraction></p>',
                '{{UNANSWERED_CHECKS}}': '<isNull><variable identifier="RESPONSE-1"/></isNull>',
                '{{MAP_RESPONSES}}': '<mapResponse identifier="RESPONSE-1"/>',
                '{{ALL_CORRECT_CHECKS}}': '<match><variable identifier="RESPONSE-1"/><correct identifier="RESPONSE-1"/></match>',
                '{{ANY_CORRECT_CHECKS}}': '<match><variable identifier="RESPONSE-1"/><correct identifier="RESPONSE-1"/></match>'
            })
        elif question_type in ['gapmatch', 'graphicgapmatch_v2']:
            # Extract image information
            image_data = question_data.get('image', {})
            image_path = image_data.get('path', 'TODO_image.png')
            image_alt = image_data.get('alt', 'Question Image')
            # Extract just the filename (without directory) for logical name
            image_filename = image_path.split('/')[-1]  # Get last part of path
            image_logical_name = image_filename.rsplit('.', 1)[0]  # Remove extension

            common.update({
                '{{PROMPT_TEXT}}': 'Drag items to the correct positions',
                '{{REUSE_ALTERNATIVES}}': 'false',
                '{{TOKEN_ORDER}}': 'random',
                '{{TOKEN_POSITION}}': 'top',
                '{{TOKEN_SIZE}}': 'autoSize',
                '{{TYPE}}': 'plainText',
                '{{GAP_SIZE}}': 'sameSize',
                '{{GAP_ITEMS}}': '<gapText identifier="GAP_ITEM_1">Option 1</gapText>',
                '{{GAP_TEXTS}}': '<gapText identifier="GAP_ITEM_1" matchMax="1"><p>Option 1</p></gapText>',
                '{{CONTENT_WITH_GAPS}}': '<blockquote><p>Fill in the gap: <gap identifier="GAP1"/></p></blockquote>',
                '{{CORRECT_PAIRS}}': '<value>GAP_ITEM_1 GAP1</value>',
                '{{MAPPING_ENTRIES}}': '<mapEntry mapKey="GAP_ITEM_1 GAP1" mappedValue="1"/>',
                '{{CORRECT_PAIR_CHECKS}}': '<member><baseValue baseType="directedPair">GAP_ITEM_1 GAP1</baseValue><variable identifier="RESPONSE"/></member>',
                '{{ANY_CORRECT_PAIR_CHECKS}}': '<member><baseValue baseType="directedPair">GAP_ITEM_1 GAP1</baseValue><variable identifier="RESPONSE"/></member>',
                # Keep full path for packager to find the file, but it will be flattened to resources/ folder
                '{{BACKGROUND_IMAGE}}': f'resources/{image_filename}',
                '{{IMAGE_LOGICAL_NAME}}': image_logical_name,
                '{{IMAGE_TITLE}}': self._escape_xml(image_alt),
                '{{HOTSPOTS}}': '<associableHotspot coords="100,100,200,200" hotspotLabel="" identifier="HOTSPOT1" matchMax="1" shape="rect"/>'
            })
        elif question_type == 'match':
            common.update({
                '{{PROMPT_TEXT}}': 'Match the items',
                '{{MAX_ASSOCIATIONS}}': '10',
                '{{RANDOMIZE}}': 'none',
                '{{SHUFFLE}}': 'false',
                '{{LEFT_COLUMN_ITEMS}}': '<simpleAssociableChoice identifier="PREMISE1" matchMax="1"><span class="label">Left 1</span></simpleAssociableChoice>',
                '{{RIGHT_COLUMN_ITEMS}}': '<simpleAssociableChoice identifier="RESPONSE1" matchMax="1"><span class="label">Right 1</span></simpleAssociableChoice>',
                '{{CORRECT_PAIRS}}': '<value>PREMISE1 RESPONSE1</value>',
                '{{MAPPING_ENTRIES}}': '<mapEntry mapKey="PREMISE1 RESPONSE1" mappedValue="1"/>',
                '{{CORRECT_PAIR_CHECKS}}': '<member><baseValue baseType="directedPair">PREMISE1 RESPONSE1</baseValue><variable identifier="RESPONSE-1"/></member>',
                '{{ANY_CORRECT_PAIR_CHECKS}}': '<member><baseValue baseType="directedPair">PREMISE1 RESPONSE1</baseValue><variable identifier="RESPONSE-1"/></member>'
            })
        elif question_type == 'hotspot':
            # Extract image information
            image_data = question_data.get('image', {})
            image_path = image_data.get('path', 'TODO_image.png')
            image_alt = image_data.get('alt', 'Question Image')
            # Extract just the filename for logical name (remove path and extension)
            image_filename = image_path.split('/')[-1]  # Get last part of path
            image_logical_name = image_filename.rsplit('.', 1)[0]  # Remove extension

            common.update({
                '{{PROMPT_TEXT}}': 'Click on the correct area',
                '{{BACKGROUND_IMAGE}}': f'resources/{image_filename}',
                '{{IMAGE_LOGICAL_NAME}}': image_logical_name,
                '{{IMAGE_TITLE}}': self._escape_xml(image_alt),
                '{{CANVAS_HEIGHT}}': '400',
                '{{CORRECT_HOTSPOT_ID}}': 'HOTSPOT1',
                '{{SCORE_WRONG}}': '0',
                '{{SCORE_UNANSWERED}}': '0',
                '{{ENABLE_COLORING}}': 'true',
                '{{SHAPE_COLOR}}': '#0e98f0',
                '{{SHAPE_OPACITY}}': '0.4',
                '{{HOTSPOTS}}': '<hotspotChoice coords="100,100,200,200" hotspotLabel="1" identifier="HOTSPOT1" matchMax="0" shape="rect"/><hotspotChoice coords="250,100,350,200" hotspotLabel="2" identifier="HOTSPOT2" matchMax="0" shape="rect"/>',
                '{{FEEDBACK_PARTIALLY_CORRECT}}': self._escape_xml(feedback.get('partial', 'Try again.'))
            })
        elif question_type == 'text_entry_graphic':
            common.update({
                '{{NUM_FIELDS}}': '1',
                '{{BACKGROUND_IMAGE}}': 'resources/TODO_image.png',
                '{{IMAGE_METADATA}}': 'width="600" height="400"',
                '{{RESPONSE_DECLARATIONS}}': '<responseDeclaration baseType="string" cardinality="single" identifier="RESPONSE-1"><correctResponse><value>TODO</value></correctResponse></responseDeclaration>',
                '{{OUTCOME_DECLARATIONS}}': '<outcomeDeclaration baseType="boolean" cardinality="single" identifier="isCorrect_RESPONSE-1"/>',
                '{{FIELDS_HTML}}': '<textEntryInteraction expectedLength="15" responseIdentifier="RESPONSE-1" inspera:style="position:absolute;left:100px;top:100px;width:150px;"/>',
                '{{FIELD_SCORING_LOGIC}}': '<responseCondition><responseIf><and><stringMatch caseSensitive="false"><baseValue baseType="string">TODO</baseValue><variable identifier="RESPONSE-1"/></stringMatch></and><setOutcomeValue identifier="SCORE"><sum><variable identifier="SCORE"/><variable identifier="SCORE_EACH_CORRECT"/></sum></setOutcomeValue><setOutcomeValue identifier="isCorrect_RESPONSE-1"><baseValue baseType="boolean">true</baseValue></setOutcomeValue></responseIf></responseCondition>',
                '{{UNANSWERED_CHECKS}}': '<isNull><variable identifier="RESPONSE-1"/></isNull>',
                '{{ALL_CORRECT_CHECKS}}': '<equal toleranceMode="exact"><variable identifier="isCorrect_RESPONSE-1"/><baseValue baseType="boolean">true</baseValue></equal>',
                '{{ANY_CORRECT_CHECKS}}': '<equal toleranceMode="exact"><variable identifier="isCorrect_RESPONSE-1"/><baseValue baseType="boolean">true</baseValue></equal>'
            })

        return common

    def _build_graphicgapmatch_v2_replacements(self, question_data: Dict[str, Any], language: str,
                                               identifier: str, title: str, points: int,
                                               question_text_xhtml: str, feedback: Dict[str, str]) -> Dict[str, str]:
        """
        Build replacements for graphicgapmatch_v2 (drag items onto image hotspots).

        Args:
            question_data: Parsed question with 'draggable_items', 'zones', 'image', 'scoring'
            language: Language code
            identifier: Question identifier
            title: Question title
            points: Total points
            question_text_xhtml: Question prompt in XHTML
            feedback: Feedback dictionary

        Returns:
            Dictionary of template replacements
        """
        # INSPERA REQUIREMENT: All feedback must be identical across states
        unified_feedback = self._escape_xml(
            feedback.get('correct') or feedback.get('general') or 'Correct!'
        )

        # Extract data
        draggable_items = question_data.get('draggable_items', [])
        zones = question_data.get('zones', [])
        image_data = question_data.get('image', {})
        scoring = question_data.get('scoring', {})

        # Image information
        image_path = image_data.get('path', 'TODO_image.png')
        image_alt = image_data.get('alt', 'Question Image')
        image_filename = image_path.split('/')[-1]
        image_logical_name = image_filename.rsplit('.', 1)[0]

        # Parse scoring
        points_each_correct = 1  # Default
        points_each_wrong = 0
        if scoring:
            # Try to extract points from scoring text
            points_match = re.search(r'(\d+)\s*point', scoring.get('correct_placement', ''), re.IGNORECASE)
            if points_match:
                points_each_correct = int(points_match.group(1))

        # Generate GAP_TEXTS (draggable items)
        gap_texts = []
        for item in draggable_items:
            item_id = item['identifier']
            item_text = self._escape_xml(item['text'])
            gap_text = f'<gapText identifier="{item_id}" matchMax="1"><p>{item_text}</p></gapText>'
            gap_texts.append(gap_text)

        gap_texts_xml = '\n            '.join(gap_texts) if gap_texts else '<gapText identifier="ITEM_1" matchMax="1"><p>Option 1</p></gapText>'

        # Generate HOTSPOTS (associable hotspots on image)
        hotspots = []
        for zone in zones:
            zone_id = zone['identifier']
            shape = zone['shape']
            coords = zone['coords']
            label = zone.get('label', '')

            hotspot = f'<associableHotspot coords="{coords}" hotspotLabel="{label}" identifier="{zone_id}" matchMax="1" shape="{shape}"/>'
            hotspots.append(hotspot)

        hotspots_xml = '\n            '.join(hotspots) if hotspots else '<associableHotspot coords="100,100,200,200" hotspotLabel="" identifier="ZONE1" matchMax="1" shape="rect"/>'

        # Generate CORRECT_PAIRS (mapping items to zones)
        correct_pairs = []
        mapping_entries = []

        for zone in zones:
            if 'correct_item_num' in zone:
                # Find the item with this number
                correct_item = next(
                    (item for item in draggable_items if item['number'] == zone['correct_item_num']),
                    None
                )
                if correct_item:
                    item_id = correct_item['identifier']
                    zone_id = zone['identifier']

                    # Add correct pair
                    correct_pairs.append(f'<value>{item_id} {zone_id}</value>')

                    # Add mapping entry for scoring
                    mapping_entries.append(f'<mapEntry mapKey="{item_id} {zone_id}" mappedValue="{points_each_correct}"/>')

        correct_pairs_xml = '\n            '.join(correct_pairs) if correct_pairs else '<value>ITEM_1 ZONE1</value>'
        mapping_entries_xml = '\n            '.join(mapping_entries) if mapping_entries else '<mapEntry mapKey="ITEM_1 ZONE1" mappedValue="1"/>'

        # Generate response condition checks for feedback
        correct_pair_checks = []
        for zone in zones:
            if 'correct_item_num' in zone:
                correct_item = next(
                    (item for item in draggable_items if item['number'] == zone['correct_item_num']),
                    None
                )
                if correct_item:
                    item_id = correct_item['identifier']
                    zone_id = zone['identifier']
                    correct_pair_checks.append(
                        f'<member><baseValue baseType="directedPair">{item_id} {zone_id}</baseValue><variable identifier="RESPONSE"/></member>'
                    )

        correct_pair_checks_xml = '\n                '.join(correct_pair_checks) if correct_pair_checks else '<member><baseValue baseType="directedPair">ITEM_1 ZONE1</baseValue><variable identifier="RESPONSE"/></member>'

        # Build common replacements
        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{POINTS_EACH_CORRECT}}': str(points_each_correct),
            '{{POINTS_EACH_WRONG}}': str(points_each_wrong),
            '{{POINTS_ALL_CORRECT}}': str(points),
            '{{POINTS_MINIMUM}}': '0',
            '{{POINTS_UNANSWERED}}': '0',
            '{{MAX_SCORE}}': str(points),
            '{{QUESTION_IMAGES}}': '',
            '{{QUESTION_TEXT}}': question_text_xhtml,
            '{{PROMPT_TEXT}}': 'Drag items to the correct positions',
            '{{REUSE_ALTERNATIVES}}': 'false',
            '{{TOKEN_ORDER}}': 'random',
            '{{TOKEN_POSITION}}': 'top',
            '{{TOKEN_SIZE}}': 'autoSize',
            '{{TYPE}}': 'plainText',
            '{{GAP_SIZE}}': 'sameSize',
            '{{GAP_TEXTS}}': gap_texts_xml,
            '{{BACKGROUND_IMAGE}}': f'resources/{image_filename}',
            '{{IMAGE_LOGICAL_NAME}}': image_logical_name,
            '{{IMAGE_TITLE}}': self._escape_xml(image_alt),
            '{{HOTSPOTS}}': hotspots_xml,
            '{{CORRECT_PAIRS}}': correct_pairs_xml,
            '{{MAPPING_ENTRIES}}': mapping_entries_xml,
            '{{CORRECT_PAIR_CHECKS}}': correct_pair_checks_xml,
            '{{ANY_CORRECT_PAIR_CHECKS}}': correct_pair_checks_xml,
            '{{FEEDBACK_CORRECT}}': unified_feedback,
            '{{FEEDBACK_INCORRECT}}': unified_feedback,
            '{{FEEDBACK_PARTIALLY_CORRECT}}': unified_feedback,
            '{{FEEDBACK_UNANSWERED}}': unified_feedback
        }

    def _build_composite_editor_stub(self, question_data: Dict[str, Any], language: str,
                                     identifier: str, title: str, points: int,
                                     question_text_xhtml: str, feedback: Dict[str, str]) -> Dict[str, str]:
        """
        Build stub replacements for composite_editor questions.

        Composite editor is very complex - it combines multiple interaction types.
        This stub provides basic structure.

        TODO: Implement full support for mixed interaction types.
        """
        # INSPERA REQUIREMENT: All feedback must be identical across states
        # Try 'correct' first, fall back to 'general' (unlabeled format), then placeholder
        unified_feedback = self._escape_xml(
            feedback.get('correct') or feedback.get('general') or 'Correct!'
        )

        return {
            '{{IDENTIFIER}}': identifier,
            '{{TITLE}}': self._escape_xml(title),
            '{{LANGUAGE}}': language,
            '{{POINTS_EACH_CORRECT}}': '1',
            '{{POINTS_EACH_WRONG}}': '0',
            '{{POINTS_ALL_CORRECT}}': str(points),
            '{{POINTS_MINIMUM}}': '0',
            '{{POINTS_UNANSWERED}}': '0',
            '{{MAX_SCORE}}': str(points),
            '{{QUESTION_IMAGES}}': '',
            '{{QUESTION_TEXT}}': question_text_xhtml,
            '{{NUM_RESPONSES}}': '1',
            '{{RESPONSE_DECLARATIONS}}': '<responseDeclaration baseType="string" cardinality="single" identifier="RESPONSE-1"><correctResponse><value>TODO</value></correctResponse></responseDeclaration>',
            '{{OUTCOME_DECLARATIONS}}': '<outcomeDeclaration baseType="boolean" cardinality="single" identifier="isCorrect_RESPONSE-1"/>',
            '{{INTERACTIONS}}': f'{question_text_xhtml}<p><textEntryInteraction expectedLength="15" responseIdentifier="RESPONSE-1"/></p>',
            '{{INDIVIDUAL_SCORING}}': '<responseCondition><responseIf><and><stringMatch caseSensitive="false"><baseValue baseType="string">TODO</baseValue><variable identifier="RESPONSE-1"/></stringMatch></and><setOutcomeValue identifier="SCORE"><sum><variable identifier="SCORE"/><variable identifier="SCORE_EACH_CORRECT"/></sum></setOutcomeValue><setOutcomeValue identifier="isCorrect_RESPONSE-1"><baseValue baseType="boolean">true</baseValue></setOutcomeValue></responseIf></responseCondition>',
            '{{UNANSWERED_CHECKS}}': '<isNull><variable identifier="RESPONSE-1"/></isNull>',
            '{{CHOICE_MAP_RESPONSES}}': '',
            '{{ALL_CORRECT_CHECKS}}': '<equal toleranceMode="exact"><variable identifier="isCorrect_RESPONSE-1"/><baseValue baseType="boolean">true</baseValue></equal>',
            '{{ANY_CORRECT_CHECKS}}': '<equal toleranceMode="exact"><variable identifier="isCorrect_RESPONSE-1"/><baseValue baseType="boolean">true</baseValue></equal>',
            '{{FEEDBACK_CORRECT}}': unified_feedback,
            '{{FEEDBACK_INCORRECT}}': unified_feedback,
            '{{FEEDBACK_PARTIALLY_CORRECT}}': unified_feedback,
            '{{FEEDBACK_UNANSWERED}}': unified_feedback
        }

    def _generate_inline_choice_response_declarations(self, inline_choices: Dict[str, List[str]],
                                                      correct_answers: Dict[str, str],
                                                      points_each_correct: int,
                                                      points_each_wrong: int) -> str:
        """Generate response declarations for inline_choice dropdowns."""
        declarations = []

        for field_num in sorted(inline_choices.keys(), key=int):
            choices = inline_choices[field_num]
            correct = correct_answers.get(field_num, choices[0])

            # Find correct choice ID
            try:
                correct_idx = choices.index(correct) + 1
            except ValueError:
                correct_idx = 1

            correct_choice_id = f'choice_{field_num}_{correct_idx}'

            declaration = f'''<responseDeclaration baseType="identifier" cardinality="single" identifier="RESPONSE-{field_num}">
        <correctResponse>
            <value>{correct_choice_id}</value>
        </correctResponse>
        <mapping defaultValue="{points_each_wrong}">
            <mapEntry mapKey="{correct_choice_id}" mappedValue="{points_each_correct}"/>
        </mapping>
    </responseDeclaration>'''

            declarations.append(declaration)

        return '\n    '.join(declarations)

    def _generate_inline_choice_interactions(self, question_text: str,
                                             inline_choices: Dict[str, List[str]],
                                             correct_answers: Dict[str, str]) -> str:
        """Replace {{dropdown_N}} markers with inlineChoiceInteraction elements."""
        result = question_text

        for field_num in sorted(inline_choices.keys(), key=int):
            choices = inline_choices[field_num]

            # Generate simpleChoice elements
            simple_choices = []
            for idx, choice_text in enumerate(choices, 1):
                choice_id = f'choice_{field_num}_{idx}'
                simple_choices.append(f'<simpleChoice identifier="{choice_id}">{self._escape_xml(choice_text)}</simpleChoice>')

            # Create inlineChoiceInteraction
            interaction = f'''<inlineChoiceInteraction maxChoices="1" responseIdentifier="RESPONSE-{field_num}" shuffle="false">
                {' '.join(simple_choices)}
            </inlineChoiceInteraction>'''

            # Replace v6.5 marker: {{dropdown_N}}
            marker = f'{{{{dropdown_{field_num}}}}}'
            result = result.replace(marker, interaction)

        return result

    def _generate_inline_choice_unanswered_checks(self, inline_choices: Dict[str, List[str]]) -> str:
        """Generate checks for unanswered inline_choice dropdowns."""
        checks = []
        for field_num in sorted(inline_choices.keys(), key=int):
            checks.append(f'<isNull><variable identifier="RESPONSE-{field_num}"/></isNull>')

        return '\n                    '.join(checks)

    def _generate_inline_choice_map_responses(self, inline_choices: Dict[str, List[str]]) -> str:
        """Generate mapResponse calls for each dropdown."""
        maps = []
        for field_num in sorted(inline_choices.keys(), key=int):
            maps.append(f'<mapResponse identifier="RESPONSE-{field_num}"/>')

        return '\n                        '.join(maps)

    def _generate_inline_choice_all_correct_checks(self, inline_choices: Dict[str, List[str]],
                                                   correct_answers: Dict[str, str]) -> str:
        """Generate checks for all dropdowns being correct."""
        checks = []
        for field_num in sorted(inline_choices.keys(), key=int):
            checks.append(f'<match><variable identifier="RESPONSE-{field_num}"/><correct identifier="RESPONSE-{field_num}"/></match>')

        return '\n                    '.join(checks)

    def _generate_inline_choice_any_correct_checks(self, inline_choices: Dict[str, List[str]],
                                                   correct_answers: Dict[str, str]) -> str:
        """Generate checks for any dropdown being correct."""
        checks = []
        for field_num in sorted(inline_choices.keys(), key=int):
            checks.append(f'<match><variable identifier="RESPONSE-{field_num}"/><correct identifier="RESPONSE-{field_num}"/></match>')

        return '\n                    '.join(checks)
