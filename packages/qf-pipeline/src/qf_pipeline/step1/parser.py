"""
Parse markdown file into individual questions.
Handles multiple input formats.
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ParsedQuestion:
    """A parsed question from the source file."""
    question_id: str           # Q001, Q002, etc.
    title: Optional[str]       # Title if present
    raw_content: str           # Original content
    line_start: int            # Starting line in file
    line_end: int              # Ending line in file
    detected_type: Optional[str]  # Detected question type


# Question delimiters for different formats
QUESTION_PATTERNS = [
    # QFMD/Legacy: # Q001 Title
    r'^#\s*(Q\d{3}[A-Z]?)\s*(.*?)$',

    # Semi-structured: # Question 1: Title
    r'^#\s*Question\s*(\d+):?\s*(.*?)$',

    # Alternative: ## Q001
    r'^##\s*(Q\d{3}[A-Z]?)\s*(.*?)$',
]


def parse_file(content: str) -> List[ParsedQuestion]:
    """
    Parse markdown content into list of questions.

    Args:
        content: Full markdown file content

    Returns:
        List of ParsedQuestion objects
    """
    lines = content.split('\n')
    questions = []

    # Find all question boundaries
    boundaries = []  # [(line_num, question_id, title), ...]

    for i, line in enumerate(lines):
        for pattern in QUESTION_PATTERNS:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                q_id = match.group(1)
                title = match.group(2).strip() if match.group(2) else None

                # Normalize question ID
                if q_id.isdigit():
                    q_id = f"Q{int(q_id):03d}"
                else:
                    # Ensure uppercase
                    q_id = q_id.upper()

                boundaries.append((i, q_id, title))
                break

    # Extract content between boundaries
    for idx, (line_num, q_id, title) in enumerate(boundaries):
        # End is either next question or end of file
        if idx + 1 < len(boundaries):
            end_line = boundaries[idx + 1][0]
        else:
            end_line = len(lines)

        # Extract raw content
        raw_content = '\n'.join(lines[line_num:end_line])

        # Detect question type
        detected_type = detect_question_type(raw_content)

        questions.append(ParsedQuestion(
            question_id=q_id,
            title=title,
            raw_content=raw_content,
            line_start=line_num + 1,  # 1-indexed
            line_end=end_line,
            detected_type=detected_type
        ))

    return questions


def detect_question_type(content: str) -> Optional[str]:
    """
    Detect question type from content.

    Returns:
        Question type string or None if unclear
    """
    content_lower = content.lower()

    # Explicit type declaration (both Legacy and QFMD syntax)
    type_match = re.search(r'(?:\^type|@type:)\s*(\w+)', content, re.IGNORECASE)
    if type_match:
        return normalize_type(type_match.group(1))

    # Infer from content patterns
    if '{{blank' in content_lower or '{{blank-' in content_lower:
        return 'text_entry'

    if '{{dropdown' in content_lower or '{{dropdown-' in content_lower:
        return 'inline_choice'

    if re.search(r'\|\s*\w+\s*\|', content):  # Table pattern
        if 'pair' in content_lower or 'match' in content_lower:
            return 'match'

    # Check for options/choices
    if re.search(r'^[A-F][.)]\s', content, re.MULTILINE) or \
       re.search(r'^\d+[.)]\s', content, re.MULTILINE):
        # Has options - but single or multiple?
        answer_match = re.search(r'(?:answer|svar|rätt).*?([A-F](?:\s*,\s*[A-F])*)', content, re.IGNORECASE)
        if answer_match:
            answer = answer_match.group(1)
            if ',' in answer:
                return 'multiple_response'
        return 'multiple_choice_single'

    # Essay/text area indicators
    if 'rubric' in content_lower or 'scoring rubric' in content_lower:
        return 'text_area'

    if 'short_response' in content_lower or 'essay' in content_lower:
        return 'text_area'

    return None


def normalize_type(type_str: str) -> str:
    """Normalize type string to standard format."""
    type_map = {
        'mc': 'multiple_choice_single',
        'mcq': 'multiple_choice_single',
        'multiple_choice': 'multiple_choice_single',
        'multiplechoice': 'multiple_choice_single',
        'mr': 'multiple_response',
        'multipleresponse': 'multiple_response',
        'fib': 'text_entry',
        'fill_in_blank': 'text_entry',
        'fillinblank': 'text_entry',
        'fillblank': 'text_entry',
        'dropdown': 'inline_choice',
        'inlinechoice': 'inline_choice',
        'matching': 'match',
        'essay': 'text_area',
        'short_response': 'text_area',
        'shortresponse': 'text_area',
        'textarea': 'text_area',
    }
    normalized = type_str.lower().replace(' ', '_').replace('-', '_')
    return type_map.get(normalized, normalized)


def get_question_by_id(questions: List[ParsedQuestion], question_id: str) -> Optional[ParsedQuestion]:
    """Get a question by its ID."""
    for q in questions:
        if q.question_id == question_id:
            return q
    return None
