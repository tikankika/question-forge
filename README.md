# QuestionForge

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](CHANGELOG.md)
[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/License-PolyForm%20Noncommercial%201.0.0-lightgrey.svg)](LICENSE)

> A teacher-led, AI-assisted framework for creating high-quality educational assessment questions from real teaching materials — and exporting them to QTI for import into Inspera and other QTI-compatible platforms.

## What is QuestionForge?

QuestionForge helps educators create pedagogically sound assessment questions through a structured, AI-assisted process. Most assessment tools work from curriculum documents; QuestionForge analyses **what was actually taught** (lectures, slides, materials) so that assessments match what students experienced.

The teacher stays in control at every step — the tools scaffold and document the method; they do not replace the teacher's judgement.

## The three packages (pick your door)

QuestionForge is a small monorepo of three independent packages. Use whichever fits your need:

| Package | Install | What it gives you |
|---------|---------|-------------------|
| **qf-scaffolding** | From source (Node) | An MCP server that guides the methodology (M1–M5): content analysis, assessment planning, question generation, quality assurance, question formatting. |
| **qf-pipeline** | From source (Python) | An MCP server for the technical pipeline: validate question markdown, auto-fix, and export a QTI package. |
| **qti-core** | From source (Python) | The standalone QTI generation library that `qf-pipeline` builds on — usable on its own to turn question markdown into QTI 2.2. |

These packages are not published to npm/PyPI — install from source (see the quick start below). Registry publishing may come later but isn't needed to use them.

The two MCP servers are designed for use with an MCP-capable assistant (e.g. Claude Desktop). `qti-core` is a plain library with no assistant required.

> **Language note:** the scaffolding MCP's interactive messages are currently in Swedish — QuestionForge was built with and for Swedish teachers, and an English interface layer is planned. The methodology guides and documentation are in English, and generated question *content* follows the language of your teaching materials.

## Quick start (from source)

```bash
git clone https://github.com/tikankika/question-forge.git
cd question-forge

# qf-pipeline (Python)
cd packages/qf-pipeline && pip install -e . && cd ../..

# qti-core (Python library)
cd packages/qti-core && pip install -e . && cd ../..

# qf-scaffolding (TypeScript)
cd packages/qf-scaffolding && npm install && npm run build && cd ../..
```

See [Getting Started](docs/GETTING_STARTED.md) for first-project setup, and [the workflow guide](WORKFLOW.md) for the full process.

## How it works

```
Instructional materials
        │
        ▼
  qf-scaffolding  (methodology, teacher-led)
   M1 Content Analysis → M2 Assessment Planning
   → M3 Question Generation → M4 Quality Assurance
   → M5 Question Formatting
        │  (QFMD — QuestionForge Markdown)
        ▼
  qf-pipeline  (technical)
   Validate → Auto-fix → Export
        │
        ▼
   QTI package  →  Inspera / QTI-compatible LMS
```

1. **M1 – Content Analysis:** analyse materials, identify what was emphasised.
2. **M2 – Assessment Planning:** objectives, Bloom's distribution, question-type mix, blueprint.
3. **M3 – Question Generation:** author questions aligned with the conducted instruction.
4. **M4 – Quality Assurance:** review, validate, refine.
5. **M5 – Question Formatting:** turn approved questions into QFMD (QuestionForge Markdown), the structured question format the pipeline reads.
6. **Pipeline:** validate format, auto-fix, export to QTI.

## Question types

16 supported types — multiple-choice (single and multiple response), true/false, inline choice, text entry (plain, numeric, mathematical, graphic), text area, essay, match, hotspot, graphic gap-match, audio record, composite editor, and native HTML. The authoritative list is what the `list_types` tool reports. See the [format reference](methodology/m5/FORMAT_REFERENCE.md).

## Requirements

- **Python** — 3.10+ for `qf-pipeline`; 3.8+ for `qti-core`
- **Node.js** — 18+ recommended for `qf-scaffolding`
- An MCP-capable assistant (for the two MCP servers)

## Documentation

- [Getting Started](docs/GETTING_STARTED.md) — installation and your first project
- [Workflow Guide](WORKFLOW.md) — the complete process
- [Methodology](methodology/) — the M1–M5 guides (in the guides, 🔷 marks a mechanised/executable check and 🔶 a human-judgement check)
- [Contributing](CONTRIBUTING.md)

## Licence

**PolyForm Noncommercial 1.0.0** — free for noncommercial use (including education and research); commercial use requires a separate licence. See [LICENSE](LICENSE).

- ✅ Use for educational purposes
- ✅ Adapt and build upon (share alike)
- ✅ Share with attribution
- ❌ Commercial use without permission

## Acknowledgements

QuestionForge builds on established research in assessment design — constructive alignment (Biggs & Tang), formative assessment (Black & Wiliam), and Swedish assessment research (Lundahl, Hirsh).

---

*QuestionForge — forging quality questions.*
