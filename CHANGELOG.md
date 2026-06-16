# Changelog

All notable changes to QuestionForge are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — First public release

First public release of QuestionForge: a teacher-led, AI-assisted framework for
creating educational assessment questions from real teaching materials and
exporting them to QTI.

### Added

- **qf-scaffolding** (Node) — MCP server providing the M1–M4 methodology guidance
  (content analysis, assessment planning, question generation, quality assurance)
  plus an M5 formatting flow.
- **qf-pipeline** (Python) — MCP server for the technical pipeline: validation,
  auto-fix, and QTI export.
- **qti-core** (Python) — standalone library that turns question markdown into
  QTI 2.2 packages; 16 supported question types.
- Methodology guides (M1–M5) and a question-format reference.
- Getting-started and workflow documentation.

[0.1.0]: https://github.com/tikankika/question-forge/releases/tag/v0.1.0
