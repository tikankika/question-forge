"""
Assessment Test Generator for QTI Question Sets

Generates assessmentTest XML for Inspera Question Sets with:
- Multiple sections based on tags/points filtering
- Random selection (pull X from Y questions)
- Shuffle support per section

Usage:
    generator = AssessmentTestGenerator()
    xml = generator.generate(
        title="Evolution Quiz",
        identifier="QUIZ_001",
        sections=sections_config,
        questions=questions_list
    )
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
import logging

from ..xml_utils import escape_xml

logger = logging.getLogger(__name__)

# Known tag categories for auto-categorisation / filtering
BLOOM_TAGS = {'remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'}
DIFFICULTY_TAGS = {'easy', 'medium', 'hard'}


@dataclass
class SectionConfig:
    """Configuration for a question set section.

    Filter logic:
    - Within a category (bloom/difficulty/custom): OR logic
    - Between categories: AND logic
    Example: (Remember OR Understand) AND Easy AND Cellbiologi
    """
    name: str
    filter_bloom: Optional[List[str]] = None      # Bloom taxonomy tags (OR within)
    filter_difficulty: Optional[List[str]] = None  # Difficulty tags (OR within)
    filter_custom: Optional[List[str]] = None      # Custom tags (OR within)
    filter_points: Optional[List[int]] = None      # Point values (OR within)
    select: Optional[int] = None  # Number to randomly select (None = all)
    shuffle: bool = True


class AssessmentTestGenerator:
    """Generates QTI assessmentTest XML for Question Sets."""

    # QTI 2.2 namespaces
    NAMESPACES = {
        '': 'http://www.imsglobal.org/xsd/imsqti_v2p2',
        'inspera': 'http://ns.inspera.no',
    }

    def __init__(self):
        # Register namespaces (empty prefix registers the default namespace)
        for prefix, uri in self.NAMESPACES.items():
            ET.register_namespace(prefix, uri)

    def generate(
        self,
        title: str,
        identifier: str,
        sections: List[SectionConfig],
        questions: List[Dict[str, Any]],
        language: str = 'sv'
    ) -> str:
        """
        Generate assessmentTest XML.

        Args:
            title: Test title
            identifier: Unique test identifier
            sections: List of SectionConfig defining question pools
            questions: List of question dictionaries with tags, points, identifier
            language: Language code (sv, en)

        Returns:
            XML string for assessmentTest
        """
        # Build XML manually to avoid namespace issues
        lang_code = 'sv_se' if language == 'sv' else 'en_us'

        # Build sections
        sections_xml = []
        for i, section_data in enumerate(sections, 1):
            # Check if sections is dict (new format) or SectionConfig (old format)
            if isinstance(section_data, dict):
                # New format: dict with 'config' and 'questions'
                section_config = section_data['config']
                section_questions = section_data['questions']
            else:
                # Backward compatibility: old format (SectionConfig only)
                section_config = section_data
                section_questions = self._filter_questions(questions, section_config)

            if not section_questions:
                continue  # Skip empty sections

            logger.info(f"Section '{section_config.name}': {len(section_questions)} questions, "
                       f"select={section_config.select}")

            section_id = f'section_{i}_{self._sanitize_id(section_config.name)}'
            section_xml = self._create_section_xml(
                section_config,
                section_questions,
                section_id=section_id
            )
            sections_xml.append(section_xml)

        if not sections_xml:
            return None

        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<assessmentTest identifier="ID_{identifier}" title="{self._escape_xml(title)}"
    xmlns="http://www.imsglobal.org/xsd/imsqti_v2p2"
    xmlns:inspera="http://ns.inspera.no"
    inspera:supportedLanguages="{lang_code}">
  <testPart identifier="test-part-{identifier}" navigationMode="nonlinear" submissionMode="simultaneous">
{''.join(sections_xml)}
  </testPart>
</assessmentTest>'''

        return xml

    def _create_section_xml(
        self,
        config: SectionConfig,
        questions: List[Dict[str, Any]],
        section_id: str
    ) -> str:
        """Create assessmentSection XML string."""
        ordering_xml = '      <ordering shuffle="true"/>\n' if config.shuffle else ''

        selection_xml = ''
        if config.select and config.select < len(questions):
            selection_xml = f'      <selection select="{config.select}"/>\n'

        item_refs = []
        for q in questions:
            q_id = q.get('identifier', q.get('id', 'Q000'))
            item_refs.append(f'      <assessmentItemRef href="{q_id}-item.xml" identifier="ID_{q_id}"/>')

        return f'''    <assessmentSection identifier="ID_{section_id}" title="{self._escape_xml(config.name)}" visible="false"
        inspera:allowStimulusResizing="true" inspera:stimulusSize="50">
{ordering_xml}{selection_xml}{chr(10).join(item_refs)}
    </assessmentSection>
'''

    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters."""
        return escape_xml(text)

    def _filter_questions(
        self,
        questions: List[Dict[str, Any]],
        section_config: SectionConfig
    ) -> List[Dict[str, Any]]:
        """Filter questions based on section configuration.

        Logic:
        - Within a category (Bloom, Difficulty, Custom): OR
        - Between categories: AND
        Example: (Remember OR Understand) AND Easy AND Cellbiologi
        """
        filtered = []

        # Known tag categories (module-level constants)
        bloom_tags = BLOOM_TAGS
        difficulty_tags = DIFFICULTY_TAGS

        for q in questions:
            # Check points filter (OR logic within points)
            if section_config.filter_points is not None:
                q_points = q.get('points', 1)
                if q_points not in section_config.filter_points:
                    continue

            # Get question tags
            q_tags = q.get('tags', [])
            if isinstance(q_tags, str):
                q_tags = [tag.strip() for tag in q_tags.split(',')]
            q_tags_normalized = [t.lstrip('#').lower() for t in q_tags]

            # Categorize question tags
            q_bloom = [t for t in q_tags_normalized if t in bloom_tags]
            q_difficulty = [t for t in q_tags_normalized if t in difficulty_tags]
            q_custom = [t for t in q_tags_normalized if t not in bloom_tags and t not in difficulty_tags]

            # Check Bloom filter (OR within category)
            if section_config.filter_bloom:
                bloom_match = any(b in q_bloom for b in [t.lower() for t in section_config.filter_bloom])
                if not bloom_match:
                    continue

            # Check Difficulty filter (OR within category)
            if section_config.filter_difficulty:
                diff_match = any(d in q_difficulty for d in [t.lower() for t in section_config.filter_difficulty])
                if not diff_match:
                    continue

            # Check Custom tags filter (OR within category)
            if section_config.filter_custom:
                custom_match = any(c in q_custom for c in [t.lower() for t in section_config.filter_custom])
                if not custom_match:
                    continue

            filtered.append(q)

        return filtered

    def _sanitize_id(self, name: str) -> str:
        """Convert name to valid XML ID."""
        # Remove special characters, replace spaces with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', name.replace(' ', '_'))
        return sanitized[:50]  # Limit length

def parse_question_set_config(frontmatter: Dict[str, Any]) -> Optional[List[SectionConfig]]:
    """
    Parse question_set configuration from markdown frontmatter.

    Expected format (new):
    ```yaml
    question_set:
      sections:
        - name: "Section Name"
          filter:
            bloom: ["Remember", "Understand"]
            difficulty: ["Easy"]
            custom: ["Cellbiologi"]
            points: [1, 2]
          select: 8
          shuffle: true
    ```

    Old format (backward compatible):
    ```yaml
    question_set:
      sections:
        - name: "Section Name"
          filter:
            tags: ["tag1", "tag2"]
            points: 1
          select: 8
          shuffle: true
    ```

    Returns:
        List of SectionConfig or None if no question_set defined
    """
    question_set = frontmatter.get('question_set')
    if not question_set:
        return None

    sections_data = question_set.get('sections', [])
    if not sections_data:
        return None

    # Known tag categories (module-level constants)
    bloom_tags = BLOOM_TAGS
    difficulty_tags = DIFFICULTY_TAGS

    sections = []
    for s in sections_data:
        filter_config = s.get('filter', {})

        # Check if using new categorized format
        if 'bloom' in filter_config or 'difficulty' in filter_config or 'custom' in filter_config:
            # New format: use categorized filters directly
            config = SectionConfig(
                name=s.get('name', 'Untitled Section'),
                filter_bloom=filter_config.get('bloom'),
                filter_difficulty=filter_config.get('difficulty'),
                filter_custom=filter_config.get('custom'),
                filter_points=filter_config.get('points'),
                select=s.get('select'),
                shuffle=s.get('shuffle', True)
            )
        else:
            # Old format: auto-categorize tags
            old_tags = filter_config.get('tags', [])
            if old_tags:
                bloom_list = []
                difficulty_list = []
                custom_list = []

                for tag in old_tags:
                    tag_lower = tag.lower()
                    if tag_lower in bloom_tags:
                        bloom_list.append(tag)
                    elif tag_lower in difficulty_tags:
                        difficulty_list.append(tag)
                    else:
                        custom_list.append(tag)

                config = SectionConfig(
                    name=s.get('name', 'Untitled Section'),
                    filter_bloom=bloom_list if bloom_list else None,
                    filter_difficulty=difficulty_list if difficulty_list else None,
                    filter_custom=custom_list if custom_list else None,
                    filter_points=filter_config.get('points'),
                    select=s.get('select'),
                    shuffle=s.get('shuffle', True)
                )
            else:
                # No filters at all
                config = SectionConfig(
                    name=s.get('name', 'Untitled Section'),
                    filter_points=filter_config.get('points'),
                    select=s.get('select'),
                    shuffle=s.get('shuffle', True)
                )

        sections.append(config)

    return sections


# Convenience function for direct use
def generate_assessment_test(
    quiz_data: Dict[str, Any],
    language: str = 'sv'
) -> Optional[str]:
    """
    Generate assessmentTest XML from parsed quiz data.

    Args:
        quiz_data: Parsed quiz data with 'metadata' and 'questions'
        language: Language code

    Returns:
        XML string or None if no question_set configured
    """
    metadata = quiz_data.get('metadata', {})
    questions = quiz_data.get('questions', [])

    # Parse section configuration
    sections = parse_question_set_config(metadata)
    if not sections:
        return None

    # Get test metadata (check both root level and test_metadata)
    test_meta = metadata.get('test_metadata', {})
    title = test_meta.get('title', metadata.get('title', 'Question Set'))
    identifier = test_meta.get('identifier', metadata.get('identifier', 'QUIZ_001'))

    # Generate XML
    generator = AssessmentTestGenerator()
    return generator.generate(
        title=title,
        identifier=identifier,
        sections=sections,
        questions=questions,
        language=language
    )
