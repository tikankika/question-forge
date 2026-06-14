# qti-core

> QTI Generator for Inspera — [QuestionForge](../../README.md)'s standalone QTI 2.2 conversion engine.

Convert markdown quiz files to QTI 2.2 packages for import into Inspera Assessment Platform.

## Quick Start - Get Running in 30 Seconds

```bash
# 1. Navigate to the package folder
cd packages/qti-core

# 2. Install in editable mode (first time only)
pip install -e .

# 3. Convert a quiz
qti-gen quiz.md output.zip
```

That's it! `qti-gen` validates the markdown, generates QTI XML, and packages the ZIP.

---

## Installation (Detailed)

```bash
# Basic installation
pip install -e .

# With development tools (testing, linting, formatting)
pip install -e ".[dev]"
```

This enables:
- Running the `qti-gen` command from anywhere
- Automatic inclusion of all templates and resources
- Development tools (pytest, black, flake8, mypy)

### Command Reference

```bash
# Convert markdown to a QTI package
qti-gen quiz.md output.zip
qti-gen quiz.md output.zip --verbose --language sv

# Validate the markdown only (no package generated)
qti-gen quiz.md --validate-only

# Pre-flight check of referenced images/files
qti-gen quiz.md --validate-resources

# Inspect / validate an existing package
qti-gen --inspect output/quiz.zip
qti-gen --validate output/quiz.zip
```

> The `scripts/step1_validate.py` … `step5_create_zip.py` step scripts are the
> internal interface used by `qf-pipeline`'s validate/export tools. For direct
> use, prefer `qti-gen`.

### Basic Usage

Convert a markdown quiz to QTI package:

```bash
qti-gen quiz.md output.zip
```

This creates **both** a browsable folder and a ZIP file:
- `output/quiz/` - Extracted folder for inspection
- `output/quiz.zip` - ZIP file for Inspera import

With custom options:

```bash
qti-gen quiz.md --output EX_COURSE_quiz.zip --language en --verbose
```

To create only the ZIP file (no extracted folder):

```bash
qti-gen quiz.md output.zip --no-keep-folder
```

### Example

```bash
qti-gen quiz.md output_quiz.zip --verbose
```

This generates:
- `output/output_quiz/` - Browsable folder structure (same format as Inspera exports)
- `output/output_quiz.zip` - QTI package ready for import into Inspera

You can manually inspect the folder contents before importing the ZIP file.

### Inspecting & Validating Packages

Inspect package contents (tree view):

```bash
qti-gen --inspect output/quiz.zip
```

Output:
```
quiz.zip/
├── Q01-item.xml (10.7KB)
├── Q02-item.xml (10.3KB)
...
├── imsmanifest.xml (2.7KB)
└── resources/ (when images present)
    ├── image1.png
    └── image2.jpg
```

Validate package structure:

```bash
qti-gen --validate output/quiz.zip
```

Output:
```
✓ Package validation passed: output/quiz.zip

Warnings:
  - resources/ folder missing (okay if no media files)
```

## Package Structure

By default, the tool creates **both** an extracted folder and a ZIP file in the `output/` directory. This allows you to:
1. Browse the folder structure for inspection and comparison with Inspera exports
2. Import the ZIP file directly into Inspera

The generated QTI packages follow Inspera's expected structure:

**Without media files:**
```
quiz.zip/
├── imsmanifest.xml
├── Q001-item.xml
├── Q002-item.xml
└── ...
```

**With media files:**
```
quiz.zip/
├── imsmanifest.xml
├── Q001-item.xml
├── Q002-item.xml
└── resources/
    ├── image1.png
    ├── image2.jpg
    └── ...
```

The `resources/` subfolder is automatically created when questions reference images or other media files. Media files must be referenced in question XML as `resources/filename.ext`.

## Markdown Format

See the [QFMD format reference](../../methodology/m5/FORMAT_REFERENCE.md) for the authoritative format documentation.

### Basic Structure

```markdown
---
test_metadata:
  title: "Quiz Title"
  identifier: "QUIZ_ID"
  language: "en"
  description: "Quiz description"
  subject: "Course Name"
  author: "Author Name"
  created_date: "2025-10-30"

assessment_configuration:
  type: "formative"
  time_limit: 15
  shuffle_questions: true
  shuffle_choices: true
  feedback_mode: "immediate"
  attempts_allowed: 3

learning_objectives:
  - id: "LO1"
    description: "Students will be able to..."
---

# Question 1: Question Title

**Type**: multiple_choice_single
**Identifier**: Q001
**Points**: 1
**Learning Objectives**: LO1
**Bloom's Level**: Remember

## Question Text

What is 2 + 2?

## Options

A. 3
B. 4
C. 5
D. 6

## Answer

B

## Feedback

### General Feedback
Basic arithmetic question.

### Correct Response Feedback
Correct! 2 + 2 = 4.

### Incorrect Response Feedback
Not quite. Try again.

### Unanswered Feedback
Please select an answer.

### Option-Specific Feedback
- **A**: Too low
- **B**: Correct!
- **C**: Too high
- **D**: Too high

---

# Question 2: Next Question Title
...
```

## Supported Question Types

All 16 types:

```
multiple_choice_single    text_entry              match
multiple_response         text_entry_math         hotspot
true_false                text_entry_numeric      graphicgapmatch_v2
inline_choice             text_area               text_entry_graphic
essay                     audio_record            composite_editor
nativehtml
```

## Project Structure

```
qti-core/
├── pyproject.toml          # Package metadata; qti-gen entry point
├── requirements.txt        # Python dependencies
├── src/
│   ├── cli.py             # qti-gen CLI
│   ├── parser/            # Markdown parsing
│   ├── generator/         # XML generation
│   └── packager/          # QTI package creation
├── scripts/               # Step scripts used internally by qf-pipeline
├── templates/
│   └── xml/               # QTI 2.2 templates for all 16 types
├── tests/                 # pytest suite + fixtures
└── output/                # Generated QTI packages (created on first run)
```

## Import into Inspera

1. Log in to Inspera Assessment
2. Navigate to Question Bank or Test Designer
3. Click "Import" and select "QTI 2.2"
4. Upload the generated ZIP file
5. Review imported questions

## Features

- ✅ YAML frontmatter for quiz metadata
- ✅ All 16 question types (see list above)
- ✅ Rich text support (bold, italic, code)
- ✅ Mathematical notation (MathML)
- ✅ Detailed feedback (correct, incorrect, unanswered, option-specific)
- ✅ Automatic QTI 2.2 XML generation
- ✅ IMS Content Package (ZIP) creation
- ✅ Inspera-specific namespace support
- ✅ **resources/ folder structure** for media files
- ✅ **Package validation** (verify structure before import)
- ✅ **Package inspection** (tree view of ZIP contents)

## Documentation

- [QFMD format reference](../../methodology/m5/FORMAT_REFERENCE.md) - the input format this generator expects
- [Methodology guides](../../methodology/) - the question-authoring process (M1-M5)
- `templates/xml/README.md` - XML template documentation

## Development

### Running Tests

```bash
# Run the test suite
pytest

# Smoke-test with a quiz file
qti-gen quiz.md test_output.zip --verbose

# Verify output structure
unzip -l output/test_output.zip
```

### Adding New Question Types

1. Create XML template in `templates/xml/`
2. Update parser if new markdown fields needed
3. Update generator to handle new template placeholders
4. Test with example questions

## Licence

CC BY-NC-SA 4.0 - See [LICENSE.md](../../LICENSE.md)

## Citation

When citing this software in academic work:

**APA:**
```
Karlsson, N. (2025). qti-core: QTI Generator for Inspera (Version 0.2.4) [Computer software].
https://github.com/tikankika/question-forge
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support

For issues or questions:
- Check the [methodology guides](../../methodology/) and the format reference
- Open an issue on GitHub

## Version History

See the project [CHANGELOG.md](../../CHANGELOG.md).

---

**Built with Claude Code by Anthropic**
