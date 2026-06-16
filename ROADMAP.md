# Roadmap

QuestionForge is at **v0.1.0** — a first public release. The five-stage methodology
(M1–M5) and the QTI export pipeline work end to end, and the tool has been used to author
real exam questions for Swedish upper-secondary teaching. As with its sibling tools, the
version tracks the maturity of the **method**, not just the code.

This roadmap describes direction, not dated commitments.

## Now — v0.1.0

- Three packages: `qf-scaffolding` (M1–M5 methodology guidance), `qf-pipeline`
  (validate, auto-fix, QTI export), and `qti-core` (the standalone QTI 2.2 library).
- 16 supported question types, exported to QTI for Inspera and other QTI-compatible
  platforms.
- Methodology guides (M1–M5) and a question-format reference.
- Teacher-led by design: the tools scaffold and document the method; the teacher decides.

## Towards 1.0

1.0 means the methodology and the tool have been **validated in real use beyond the
maintainer**, and the question-authoring method is stable.

- **English interface layer.** The scaffolding server's interactive messages are
  currently in Swedish; an English layer is planned so the tool is usable beyond Swedish
  teachers.
- **Methodology maturation.** The M1–M5 guides continue to be developed and grounded in
  assessment-design research (constructive alignment, formative assessment).
- **Wider testing** across subjects and question types, to surface edge cases in
  generation and QTI export.
- **Validation beyond the maintainer** — testing with other teachers in practice.

## Not planned for 1.0

- Automation of the teacher's judgement — the design principle is *scaffolding, not
  automation*: the teacher authors and approves; the tools structure and check.
- Handling of student personal data — QuestionForge works from teaching materials and
  produces questions; it is not part of the student-data (assessment) workflow.

## Following along

This is an early, openly-developed project. Questions, ideas, and bug reports are welcome
(see [CONTRIBUTING.md](CONTRIBUTING.md)) — especially from teachers authoring questions in
practice.
