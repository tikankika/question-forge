"""Wrapper for XMLGenerator from QTI-Generator-for-Inspera.

Provides clean functions for generating QTI XML from parsed question data.
"""

from typing import List, Optional, Tuple

from ..errors import GenerationError

# Import from QTI-Generator (path configured in __init__.py)
from src.generator.xml_generator import XMLGenerator

# Singleton generator instance
_generator: Optional[XMLGenerator] = None


def get_generator() -> XMLGenerator:
    """Get singleton XMLGenerator instance.

    Returns:
        Configured XMLGenerator instance.
    """
    global _generator
    if _generator is None:
        _generator = XMLGenerator()
    return _generator


def generate_xml(question_data: dict, language: str = "sv") -> str:
    """Generate QTI XML for a single question.

    Args:
        question_data: Parsed question dictionary.
        language: Language code ('sv', 'en', etc.). Defaults to 'sv'.

    Returns:
        Complete QTI XML string for the question.

    Raises:
        GenerationError: If XML generation fails.
    """
    try:
        return get_generator().generate_question(question_data, language)
    except Exception as e:
        q_id = question_data.get("identifier", "unknown")
        raise GenerationError(
            f"Failed to generate XML for question {q_id}: {e}", source_error=e
        )


def generate_all_xml(
    questions: List[dict], language: str = "sv"
) -> List[Tuple[str, str]]:
    """Generate QTI XML for all questions.

    Args:
        questions: List of parsed question dictionaries.
        language: Language code ('sv', 'en', etc.). Defaults to 'sv'.

    Returns:
        List of (identifier, xml_content) tuples.

    Raises:
        GenerationError: If XML generation fails for any question.
    """
    gen = get_generator()
    result = []

    for i, q in enumerate(questions):
        try:
            xml = gen.generate_question(q, language)
            identifier = q.get("identifier", f"Q{i+1:03d}")
            result.append((identifier, xml))
        except Exception as e:
            q_id = q.get("identifier", f"question {i+1}")
            raise GenerationError(
                f"Failed to generate XML for {q_id}: {e}", source_error=e
            )

    return result


def get_supported_types() -> List[str]:
    """Get list of supported question types.

    Returns:
        List of question type identifiers.
    """
    return [
        "multiple_choice_single",
        "multiple_response",
        "true_false",
        "inline_choice",
        "text_entry",
        "text_entry_numeric",
        "text_entry_math",
        "text_area",
        "essay",
        "match",
        "hotspot",
        "graphicgapmatch_v2",
        "text_entry_graphic",
        "audio_record",
        "composite_editor",
        "nativehtml",
    ]
