# QTI 2.2 XML Templates for Inspera

This directory contains QTI 2.2 XML templates extracted from actual Inspera exports.
Each template is guaranteed to work with the Inspera Assessment Platform.

---

## Overview

**Template Count**: 17 (16 question types + 1 manifest)
**Coverage**: 87.0% of all questions in analysed exports
**Status**: Production-ready for Priority 1, 2 & 3 types

---

## Available Templates

### Question Templates

#### Priority 1 Templates (52.6% coverage)

| Template File | Question Type | inspera:objectType | Questions | % | Status |
|---------------|--------------|-------------------|-----------|---|--------|
| `essay.xml` | Essay / Extended Response | `content_question_qti2_extendedtext` | 47 | 24.2% | ✅ Ready |
| `multiple_choice_single.xml` | Multiple Choice (Single) | `content_question_qti2_multiple_choice` | 31 | 16.0% | ✅ Ready |
| `text_area.xml` | Text Area (Short Response) | `content_question_qti2_text_area` | 18 | 9.3% | ✅ Ready |
| `multiple_response.xml` | Multiple Choice (Multiple) | `content_question_qti2_multiple_response` | 6 | 3.1% | ✅ Ready |

#### Priority 2 Templates (24.2% coverage)

| Template File | Question Type | inspera:objectType | Questions | % | Status |
|---------------|--------------|-------------------|-----------|---|--------|
| `gapmatch.xml` | Drag Text into Gaps | `content_question_qti2_gapmatch` | 13 | 6.7% | ✅ Ready |
| `graphicgapmatch_v2.xml` | Drag onto Image Hotspots | `content_question_qti2_graphicgapmatch_v2` | 9 | 4.6% | ✅ Ready |
| `text_entry_graphic.xml` | Fill-in on Image | `content_question_qti2_text_entry_graphic` | 6 | 3.1% | ✅ Ready |
| `inline_choice.xml` | Inline Dropdown Selections | `content_question_qti2_inline_choice` | 4 | 2.1% | ✅ Ready |
| `hotspot.xml` | Click on Image Areas | `content_question_qti2_hotspot` | 4 | 2.1% | ✅ Ready |
| `text_entry.xml` | Inline Fill-in-the-Blank | `content_question_qti2_text_entry` | 3 | 1.5% | ✅ Ready |
| `text_entry_math.xml` | Math Entry (x²) | `content_question_qti2_text_entry_math` | - | - | ✅ Ready |
| `text_entry_numeric.xml` | Numeric Entry (99) | `content_question_qti2_text_entry_numeric` | - | - | ✅ Ready |
| `match.xml` | Matching Pairs | `content_question_qti2_match` | 3 | 1.5% | ✅ Ready |

#### Priority 3 Templates (10.3% coverage)

| Template File | Question Type | inspera:objectType | Questions | % | Status |
|---------------|--------------|-------------------|-----------|---|--------|
| `nativehtml.xml` | Information/Instructions | `content_nativehtml` | 14 | 7.2% | ✅ Ready |
| `composite_editor.xml` | Mixed Question Types | `content_question_qti2_composite_editor` | 5 | 2.6% | ✅ Ready |
| `audio_record.xml` | Audio Recording | `content_question_qti2_audio_record` | 1 | 0.5% | ✅ Ready |

**Total Coverage**: 169 questions out of 194 (87.0%)

### Package Templates

| Template File | Purpose | Status |
|---------------|---------|--------|
| `imsmanifest_template.xml` | IMS Content Package manifest | ✅ Ready |

---

## Template Structure

All question templates follow this structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<assessmentItem
    adaptive="false"
    identifier="{{IDENTIFIER}}"
    inspera:objectType="content_question_qti2_[TYPE]"
    timeDependent="false"
    title="{{TITLE}}"
    xmlns="http://www.imsglobal.org/xsd/imsqti_v2p2"
    xmlns:inspera="http://www.inspera.no/qti"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="...">

    <!-- 1. Response Declaration(s) -->
    <!-- 2. Outcome Declarations -->
    <!-- 3. Template Declarations -->
    <!-- 4. Item Body -->
    <!-- 5. Response Processing -->
    <!-- 6. Modal Feedback -->

</assessmentItem>
```

---

## Placeholder Reference

Templates use `{{PLACEHOLDER}}` syntax for dynamic content replacement.

### Common Placeholders (All Templates)

| Placeholder | Type | Description | Example |
|-------------|------|-------------|---------|
| `{{IDENTIFIER}}` | string | Unique question ID | `Q001`, `MC_STAT_001` |
| `{{TITLE}}` | string | Question title | `Introduction to Statistics` |
| `{{LANGUAGE}}` | string | ISO 639-1 code | `en`, `sv`, `no` |
| `{{MAX_SCORE}}` | number | Maximum points | `1`, `5`, `10` |
| `{{QUESTION_TEXT}}` | XHTML | Question prompt | `<p>What is...?</p>` |
| `{{QUESTION_IMAGES}}` | XHTML | Optional images | `<img src="..."/>` |
| `{{FEEDBACK_UNANSWERED}}` | string | Unanswered feedback | `Please answer...` |

### Multiple Choice Specific

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{CORRECT_CHOICE_ID}}` | ID of correct answer | `rId0`, `rId1` |
| `{{SHUFFLE}}` | Randomize options | `true`, `false` |
| `{{CHOICES}}` | List of options | See format below |
| `{{FEEDBACK_CORRECT}}` | Correct feedback | `Well done!` |
| `{{FEEDBACK_INCORRECT}}` | Incorrect feedback | `Not quite...` |

**Choice Format**:
```xml
<simpleChoice identifier="rId0"><p>Option A text</p></simpleChoice>
<simpleChoice identifier="rId1"><p>Option B text</p></simpleChoice>
```

### Multiple Response Specific

| Placeholder | Description |
|-------------|-------------|
| `{{CORRECT_CHOICES}}` | List of correct IDs |
| `{{MAPPING_ENTRIES}}` | Score mapping |
| `{{POINTS_EACH_CORRECT}}` | Points per correct |
| `{{POINTS_EACH_WRONG}}` | Points per incorrect |
| `{{POINTS_ALL_CORRECT}}` | Bonus for all correct |
| `{{POINTS_MINIMUM}}` | Score floor |
| `{{PROMPT_TEXT}}` | Selection prompt |

### Text Area / Essay Specific

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{INITIAL_LINES}}` | Text area height | `3`, `10`, `20` |
| `{{FIELD_WIDTH}}` | Width percentage | `100%`, `50%` |
| `{{SHOW_WORD_COUNT}}` | Display counter | `true`, `false` |
| `{{EDITOR_PROMPT}}` | Placeholder text | `Enter your answer...` |
| `{{MAX_WORDS}}` | Word limit | `500`, leave empty for unlimited |
| `{{FEEDBACK_ANSWERED}}` | Answered feedback | `Thank you` |

---

## Usage Example

### 1. Select Template

```python
# For multiple choice question
template_path = "templates/xml/multiple_choice_single.xml"
```

### 2. Load Template

```python
with open(template_path, 'r') as f:
    template = f.read()
```

### 3. Replace Placeholders

```python
xml = template.replace('{{IDENTIFIER}}', 'Q001')
xml = xml.replace('{{TITLE}}', 'Capital of Sweden')
xml = xml.replace('{{LANGUAGE}}', 'en')
xml = xml.replace('{{MAX_SCORE}}', '1')
xml = xml.replace('{{CORRECT_CHOICE_ID}}', 'rId1')
xml = xml.replace('{{SHUFFLE}}', 'true')

# Build choices dynamically
choices = """
<simpleChoice identifier="rId0"><p>Oslo</p></simpleChoice>
<simpleChoice identifier="rId1"><p>Stockholm</p></simpleChoice>
<simpleChoice identifier="rId2"><p>Copenhagen</p></simpleChoice>
"""
xml = xml.replace('{{CHOICES}}', choices)

# Add feedback
xml = xml.replace('{{FEEDBACK_CORRECT}}', 'Correct! Stockholm is the capital of Sweden.')
xml = xml.replace('{{FEEDBACK_INCORRECT}}', 'Not quite. Stockholm is the capital.')
```

### 4. Write QTI File

```python
with open('output/Q001-item.xml', 'w') as f:
    f.write(xml)
```

---

## Template Details

### essay.xml

**Purpose**: Essay questions with rich text editor

**Key Features**:
- Rich text formatting (bold, italic, lists, etc.)
- Embedded images and media
- Word count tracking
- Manual grading required

**When to Use**:
- Long-form responses
- Analysis and evaluation questions
- Creative writing
- Reflective essays

**Typical Points**: 10-50

---

### multiple_choice_single.xml

**Purpose**: Traditional multiple choice with one correct answer

**Key Features**:
- Automatic scoring
- Option shuffling
- Immediate feedback
- Partial credit not supported (all or nothing)

**When to Use**:
- Knowledge recall
- Conceptual understanding
- Quick assessments

**Typical Points**: 1-3

**Recommended**: 3-5 options per question

---

### text_area.xml

**Purpose**: Short-form text responses without formatting

**Key Features**:
- Plain text only (no formatting)
- Adjustable text area size
- Manual grading required
- Can have multiple text areas in one question

**When to Use**:
- Short answer questions
- Fill-in definitions
- Brief explanations
- Calculations (show work)

**Typical Points**: 1-5

---

### multiple_response.xml

**Purpose**: "Select all that apply" questions

**Key Features**:
- Automatic scoring
- Partial credit support
- Flexible scoring models
- Score floor/ceiling enforcement

**Scoring Options**:
1. **All or nothing**: Full points only if all correct
2. **Per item**: Points for each correct selection
3. **Penalty**: Negative points for wrong selections
4. **Bonus**: Extra points for getting all correct

**When to Use**:
- Multiple correct answers
- Comprehensive coverage
- Complex scenarios

**Typical Points**: 2-10

---

### nativehtml.xml

**Purpose**: Informational content pages with no student interaction

**Key Features**:
- No scoring or response collection
- Pure HTML content display
- Rich text formatting support
- Language attribute configuration

**When to Use**:
- Test instructions and guidelines
- Section breaks between question groups
- Explanatory content or diagrams
- Context information for upcoming questions

**Typical Use Cases**:
- "This section contains 10 questions about..."
- "Read the following case study before answering..."
- "Instructions: You have 30 minutes for this section..."

---

### audio_record.xml

**Purpose**: Audio recording questions for spoken responses

**Key Features**:
- File upload interaction (audio recording)
- Manual grading required
- Simple feedback (answered/unanswered)
- Configurable maximum score

**When to Use**:
- Language pronunciation assessment
- Oral explanations and reasoning
- Interview-style responses
- Speaking proficiency tests

**Typical Points**: 5-20

**Note**: Students record audio directly in the Inspera interface. Instructor must listen to recording and manually assign grade.

---

### composite_editor.xml

**Purpose**: Comprehensive questions combining multiple interaction types

**Key Features**:
- Mix of text entry, multiple choice, and other interactions
- Individual scoring per sub-question
- Aggregate feedback across all components
- Partial credit support
- Per-response correctness tracking

**Interaction Types Supported**:
- Text entry (fill-in-the-blank)
- Multiple choice (single answer)
- Multiple response (multiple answers)
- Inline choice (dropdowns)

**When to Use**:
- Complex multi-part questions
- Comprehensive topic assessment
- Questions requiring multiple response types
- Scaffolded problem-solving tasks

**Typical Points**: 5-20 (sum of all sub-questions)

**Complexity**: Most complex template type. Requires careful setup of:
- Sequential response numbering (RESPONSE-1, RESPONSE-2, etc.)
- Mixed correctness checking (stringMatch for text, member for choices)
- Aggregate scoring logic
- Comprehensive feedback conditions

---

### imsmanifest_template.xml

**Purpose**: Package all questions into importable ZIP

**Structure**:
```xml
<manifest>
  <metadata>...</metadata>
  <resources>
    <resource identifier="Q001" type="imsqti_item_xmlv2p2">
      <file href="Q001-item.xml"/>
    </resource>
    ...
  </resources>
</manifest>
```

---

## Labels vs Custom Metadata

Inspera supports two types of tagging in `imsmanifest.xml`:

### Labels (Free-form tags)
Labels are user-defined text tags for organising and filtering content in Inspera.

- **NO** `<imsmd:id>` element - just the value
- Any text value (searchable if 3+ characters)
- Apply to Questions AND Question Sets
- In MQG format: `^labels #Easy #EXAMPLE_COURSE #Prokaryot`

**Common uses:**
- Difficulty: `Easy`, `Medium`, `Hard`
- Course codes: `EXAMPLE_COURSE`, `EX_COURSE`
- Topics: `Prokaryot`, `Celltyper`, `Evolution`
- Bloom's levels: `Remember`, `Understand`, `Apply`

```xml
<imsmd:taxon>
  <imsmd:entry>
    <imsmd:langstring>Easy</imsmd:langstring>
  </imsmd:entry>
</imsmd:taxon>
```

### Custom Metadata (Structured fields)
Custom Metadata are admin-defined fields with predefined values, managed at tenant level.

- **HAS** `<imsmd:id>` element (Field name)
- Predefined values configured by Custom Metadata Manager in Inspera Admin
- Apply to Questions AND Question Sets
- Field types: Single-select, Multi-select, Numbers, Dates

**Common uses:**
- `Nivåer`: `nivå 1`, `nivå 2`, `nivå 3`
- `Område Biologi`: `cellbiologi`, `fysiologi`, `genetik`
- `Academic Year`: `2024/25`, `2025/26`

```xml
<imsmd:taxon>
  <imsmd:id>Bloom</imsmd:id>                           <!-- Field name -->
  <imsmd:entry>
    <imsmd:langstring>Understand</imsmd:langstring>    <!-- Value -->
  </imsmd:entry>
</imsmd:taxon>
```

### Multi-select Custom Metadata
Multiple `<imsmd:taxon>` entries with the same `<imsmd:id>`:

```xml
<imsmd:taxon>
  <imsmd:id>Område</imsmd:id>
  <imsmd:entry><imsmd:langstring>cellbiologi</imsmd:langstring></imsmd:entry>
</imsmd:taxon>
<imsmd:taxon>
  <imsmd:id>Område</imsmd:id>
  <imsmd:entry><imsmd:langstring>fysiologi</imsmd:langstring></imsmd:entry>
</imsmd:taxon>
```

### Summary Table

| Feature | Labels | Custom Metadata |
|---------|--------|-----------------|
| Has `<imsmd:id>`? | ❌ No | ✅ Yes |
| Structure | Free text | Field name + Value |
| Question Sets | ✅ Yes | ✅ Yes |
| Questions | ✅ Yes | ✅ Yes |
| Field Types | Text only | Single-select, Multi-select, Numbers, Dates |

---

## Inspera-Specific Requirements

### Required Namespaces

All templates include:
```xml
xmlns="http://www.imsglobal.org/xsd/imsqti_v2p2"
xmlns:inspera="http://www.inspera.no/qti"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
```

### Required Attributes

- `inspera:objectType`: Identifies question type
- `inspera:defaultLanguage`: UI language
- `inspera:supportedLanguages`: Available translations

### Template Declarations

All scored questions must include:
```xml
<templateDeclaration identifier="SCORE_EACH_CORRECT">
<templateDeclaration identifier="SCORE_EACH_WRONG">
<templateDeclaration identifier="SCORE_ALL_CORRECT">
<templateDeclaration identifier="SCORE_MINIMUM">
<templateDeclaration identifier="SCORE_UNANSWERED">
```

---

## Validation

Templates can be validated against:

1. **QTI 2.2 XSD Schema**: Standard compliance
2. **Inspera Exports**: Structural comparison
3. **Round-trip Test**: Import into Inspera

---

## Remaining Question Types

After implementing Priority 1-3 templates (87.0% coverage), there are **25 questions (13.0%)** remaining from miscellaneous rare types:

- Various specialized or legacy question types
- Platform-specific experimental types
- Low-frequency edge cases

These may be added in future releases based on user demand.

---

## References

- **QTI 2.2 Specification**: https://www.imsglobal.org/question/qtiv2p2/imsqti_v2p2.html
- **Inspera Documentation**: https://support.inspera.com/
- **Source Exports**: `/QTI_test1/`, `/QTI_downloads_*/`
- **Research Documentation**: `../../docs/research/qti-question-types-inventory.md`

---

## Version History

**v1.3** (2025-11-30):
- Renamed `extended_text.xml` to `essay.xml` for clarity
- Updated `text_area.xml` to use `RESPONSE-1` identifier (matches Inspera exports)
- Simplified modalFeedback to self-closing tags

**v1.2** (2025-10-31):
- Added 3 Priority 3 templates (nativehtml, audio_record, composite_editor)
- Coverage increased to 87.0% (169/194 questions)
- All priority tiers (1-3) now complete

**v1.1** (2025-10-30):
- Added 7 Priority 2 templates
- Coverage increased to 76.8% (149/194 questions)

**v1.0** (2025-10-30):
- Initial release with 4 Priority 1 question templates
- Coverage: 52.6% (102/194 questions)
- Extracted from 194 analysed QTI files

---

## Document Metadata

**Created**: 2025-10-30
**Last Updated**: 2025-11-30
**Status**: Production-ready for all priority types
**Coverage**: 169/194 questions (87.0%)
