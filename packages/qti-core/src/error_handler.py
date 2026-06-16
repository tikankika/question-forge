#!/usr/bin/env python3
"""
Enhanced error handling with helpful suggestions.

Provides contextual error messages with:
- Line numbers
- Question context (ID, title)
- Suggestions for common mistakes
- Expected vs actual comparisons
"""

from typing import Optional, List, Dict
import difflib


class ParsingError(Exception):
    """Enhanced parsing error with context and suggestions."""

    def __init__(
        self,
        message: str,
        line_number: Optional[int] = None,
        question_num: Optional[int] = None,
        question_id: Optional[str] = None,
        question_title: Optional[str] = None,
        suggestion: Optional[str] = None,
        expected: Optional[str] = None,
        found: Optional[str] = None
    ):
        self.message = message
        self.line_number = line_number
        self.question_num = question_num
        self.question_id = question_id
        self.question_title = question_title
        self.suggestion = suggestion
        self.expected = expected
        self.found = found

        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format a detailed error message."""
        parts = []

        # Question context
        if self.question_num and self.question_id:
            parts.append(f"Question {self.question_num} ({self.question_id})")
        elif self.question_id:
            parts.append(f"Question {self.question_id}")

        # Line number
        if self.line_number:
            parts.append(f"Line {self.line_number}")

        # Main error message
        error_header = " - ".join(parts) if parts else "Error"
        formatted = f"\n{'='*70}\n{error_header}\n{'='*70}\n"
        formatted += f"\n{self.message}\n"

        # Expected vs found
        if self.expected and self.found:
            formatted += f"\nExpected: {self.expected}\n"
            formatted += f"Found:    {self.found}\n"
        elif self.expected:
            formatted += f"\nExpected: {self.expected}\n"

        # Suggestion
        if self.suggestion:
            formatted += f"\n💡 Suggestion: {self.suggestion}\n"

        formatted += f"{'='*70}\n"
        return formatted


class ErrorSuggester:
    """Provides helpful suggestions for common errors."""

    # Common typos and their corrections
    TYPE_SUGGESTIONS = {
        'multiple_choice': 'multiple_choice_single',
        'multi_choice': 'multiple_choice_single',
        'mcq': 'multiple_choice_single',
        'multiple_select': 'multiple_response',
        'multi_select': 'multiple_response',
        'checkbox': 'multiple_response',
        'true_or_false': 'true_false',
        'tf': 'true_false',
        'fill_in': 'text_entry',
        'fill_blank': 'text_entry',
        'short_answer': 'text_entry',
        'dropdown': 'inline_choice',
        'select': 'inline_choice',
        'matching': 'match',
        'match_pairs': 'match',
        'hotspots': 'hotspot',
        'click_map': 'hotspot',
        'extended_text': 'essay',
        'long_answer': 'essay',
    }

    @staticmethod
    def suggest_question_type(invalid_type: str) -> Optional[str]:
        """
        Suggest correct question type based on common typos.

        Args:
            invalid_type: The invalid type string

        Returns:
            Suggested correct type or None
        """
        # Direct match
        if invalid_type.lower() in ErrorSuggester.TYPE_SUGGESTIONS:
            return ErrorSuggester.TYPE_SUGGESTIONS[invalid_type.lower()]

        # Fuzzy match against valid types
        valid_types = [
            'multiple_choice_single', 'multiple_response', 'true_false',
            'text_entry', 'inline_choice', 'match', 'hotspot',
            'graphicgapmatch_v2', 'text_entry_graphic',
            'text_area', 'essay', 'audio_record'
        ]

        matches = difflib.get_close_matches(
            invalid_type.lower(),
            valid_types,
            n=1,
            cutoff=0.6
        )

        return matches[0] if matches else None

    @staticmethod
    def suggest_missing_section(question_type: str, missing_section: str) -> str:
        """
        Suggest how to fix missing section based on question type.

        Args:
            question_type: Type of question
            missing_section: Name of missing section

        Returns:
            Helpful suggestion text
        """
        suggestions = {
            ('multiple_choice_single', 'options'): (
                'Add an "options" section with @field marker:\n'
                '  ### Options\n'
                '  @field: options\n'
                '  A. First option\n'
                '  B. Second option\n'
                '  C. Third option\n'
                '  @end_field'
            ),
            ('multiple_choice_single', 'answer'): (
                'Add an "answer" section with @field marker:\n'
                '  ### Answer\n'
                '  @field: answer\n'
                '  A\n'
                '  @end_field'
            ),
            ('text_entry', 'blanks'): (
                'Add a "blanks" section with @field markers:\n'
                '  ### Blanks\n'
                '  @field: blanks\n'
                '  #### Blank 1\n'
                '  @field: blank_1\n'
                '  **Correct Answers:** answer1, answer2\n'
                '  **Case Sensitive:** false\n'
                '  @end_field\n'
                '  @end_field'
            ),
            ('inline_choice', 'dropdown'): (
                'Add "dropdown_N" sections with @field markers:\n'
                '  ### Dropdowns\n'
                '  @field: dropdowns\n'
                '  #### Dropdown 1\n'
                '  @field: dropdown_1\n'
                '  **Options:** option1, option2, option3\n'
                '  **Correct Answer:** option1\n'
                '  @end_field\n'
                '  @end_field'
            ),
            ('match', 'pairs'): (
                'Add a "pairs" section with @field marker:\n'
                '  ### Matching Pairs\n'
                '  @field: pairs\n'
                '  **Premises:**\n'
                '  1. First premise\n'
                '  2. Second premise\n'
                '  **Responses:**\n'
                '  A. First response\n'
                '  B. Second response\n'
                '  @end_field'
            ),
            ('hotspot', 'hotspots'): (
                'Add a "hotspots" section with @field marker:\n'
                '  ### Hotspot Definitions\n'
                '  @field: hotspots\n'
                '  #### Hotspot 1: Description\n'
                '  @field: hotspot_1\n'
                '  **Shape:** rect\n'
                '  **Coordinates:** x,y,width,height\n'
                '  @end_field\n'
                '  @end_field'
            ),
        }

        key = (question_type, missing_section)
        return suggestions.get(key, f'Add a "@field: {missing_section}" section')

    @staticmethod
    def suggest_invalid_metadata(field_name: str) -> str:
        """
        Suggest how to fix invalid metadata field.

        Args:
            field_name: Name of the metadata field

        Returns:
            Helpful suggestion text
        """
        suggestions = {
            'Type': (
                'Ensure @type: is specified with format:\n'
                '  @type: multiple_choice_single\n\n'
                'Valid types: multiple_choice_single, multiple_response, true_false, '
                'text_entry, inline_choice, match, hotspot, graphicgapmatch_v2, '
                'text_entry_graphic, text_area, essay'
            ),
            'Identifier': (
                'Ensure @identifier: is specified with format:\n'
                '  @identifier: MC_Q001\n\n'
                'Should be UPPERCASE_UNDERSCORES, e.g., MC_Q001, Q_EVOL_012'
            ),
            'Points': (
                'Ensure @points: is specified as a number:\n'
                '  @points: 2\n\n'
                'Can be integer (1, 2, 3) or decimal (1.5, 2.0)'
            ),
            'Language': (
                'Ensure language is a valid ISO 639-1 code:\n'
                '  --language sv\n\n'
                'Examples: en, sv, sv_se, nb_no, en_us'
            ),
        }

        return suggestions.get(
            field_name,
            f'Check the format of the @{field_name.lower()}: field'
        )


def create_parsing_error(
    message: str,
    line_num: Optional[int] = None,
    question_num: Optional[int] = None,
    question_id: Optional[str] = None,
    question_title: Optional[str] = None,
    auto_suggest: bool = True
) -> ParsingError:
    """
    Create a ParsingError with automatic suggestions.

    Args:
        message: Error message
        line_num: Line number where error occurred
        question_num: Question number (1-indexed)
        question_id: Question identifier
        question_title: Question title
        auto_suggest: Automatically add suggestions based on error type

    Returns:
        Configured ParsingError
    """
    suggestion = None

    # Auto-suggest based on error message (v6.4 format)
    if auto_suggest:
        if 'Missing @type' in message or 'Invalid question type' in message:
            suggestion = ErrorSuggester.suggest_invalid_metadata('Type')
        elif 'Missing @identifier' in message:
            suggestion = ErrorSuggester.suggest_invalid_metadata('Identifier')
        elif 'Missing @points' in message:
            suggestion = ErrorSuggester.suggest_invalid_metadata('Points')
        elif 'Missing' in message and 'section' in message.lower():
            # Extract section name and question type if available
            # This is a simplified approach - can be enhanced
            suggestion = 'Ensure all required @field: sections are present for this question type'

    return ParsingError(
        message=message,
        line_number=line_num,
        question_num=question_num,
        question_id=question_id,
        question_title=question_title,
        suggestion=suggestion
    )
