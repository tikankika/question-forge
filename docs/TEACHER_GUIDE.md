# QuestionForge: Teacher Collaboration Guide

> **This is not software you operate. It's an AI colleague you author questions with.**

---

## What This Is (And What It Isn't)

| Traditional question bank | QuestionForge |
|---------------------------|---------------|
| You write every item by hand | You and Claude author together, from what you taught |
| Fixed editor, same steps each time | Adaptive dialogue that adjusts to your material |
| Questions drawn from a syllabus | Questions grounded in what was *actually* taught |
| You format and export manually | The pipeline validates and exports QTI for you |

**QuestionForge** is an AI-assisted framework for creating high-quality assessment
questions from your own teaching materials, and exporting them to QTI for Inspera and
other QTI-compatible platforms. The AI (Claude) works with:

- your teaching materials (lectures, slides, transcripts) — what was emphasised
- a five-stage methodology (M1–M5) for sound assessment design
- tools that generate, check, format, and export your questions

**You stay in control.** Claude proposes questions and flags issues; you approve, edit,
or reject. The tools scaffold and document the method — they do not replace your
judgement about what is worth assessing or what a good question looks like.

---

## The Two Servers

QuestionForge is two MCP servers you talk to through Claude Desktop, plus a library:

- **qf-scaffolding** — guides the methodology, stage by stage (M1–M5).
- **qf-pipeline** — the technical side: validate your question markdown, auto-fix, and
  export a QTI package.
- **qti-core** — the underlying QTI 2.2 library (you rarely call it directly).

You do not need to know which tool is doing what. Describe your goal; Claude picks the
tools.

> **Language note:** the scaffolding server's interactive messages are currently in
> Swedish (an English layer is planned). The methodology guides and documentation are in
> English, and the questions Claude generates follow the language of your teaching
> materials.

---

## How to Start a Session

### 1. Describe what you already have

The best starting point depends on where you are. Just say so:

```
I have three lectures' worth of slides and want a quiz from them.
```

or

```
I already have my learning objectives — I just need questions.
```

or

```
I have questions written in markdown; I just want to export them to QTI.
```

**Why this matters:** QuestionForge lets you *enter where your material is*. You do not
have to start at M1 every time.

### 2. Point to your material and project

Give Claude the paths:

```
Material: /path/to/BIOLOGY_LECTURES/
Project:  /path/to/BIOLOGY_Quiz_2026/
```

Claude will create a session and read your material with the MCP tools.

### 3. State your goal

Be explicit:

- "Build a 15-question formative quiz from these lectures."
- "I want a mix of multiple-choice and short text-entry, mostly recall and application."
- "Validate and export the questions I already wrote."

---

## The Modules: Capabilities, Not a Fixed Track

QuestionForge has five modules. They have a natural order, but you can **start where your
material is and jump between them** — they are capabilities, not a rigid sequence.

| Module | Purpose | When to use |
|--------|---------|-------------|
| **M1 — Content Analysis** | Work out what was actually taught and emphasised | When you start from raw teaching materials |
| **M2 — Assessment Planning** | Objectives, Bloom's spread, question-type mix, a blueprint | When you need a plan before writing items |
| **M3 — Question Generation** | Draft questions aligned with the instruction | When the blueprint (or your own plan) is ready |
| **M4 — Quality Assurance** | Review and validate questions pedagogically | Always, before export |
| **M5 — Question Formatting** | Turn approved questions into QFMD, the format the pipeline reads | Before validate and export |
| **Pipeline** | Validate, auto-fix, export to QTI | The final step to a QTI package |

The methodology guides distinguish *mechanised/executable checks* (the pipeline can run
them for you) from *human-judgement checks* (yours to make) — so it is always clear where
the tool helps and where your decision is required.

### Typical Paths

**From teaching materials (full process):**
```
M1 (analyse) → M2 (plan) → M3 (generate) → M4 (QA) → M5 (format) → Pipeline (export QTI)
```

**From ready objectives (skip M1):**
```
M2 → M3 → M4 → M5 → Pipeline
```

**From finished question markdown (just export):**
```
Pipeline: validate → auto-fix if needed → export QTI
```

---

## Working With Claude: Key Principles

### 1. Claude proposes, you decide

Claude will draft questions and suggest a structure:

> *"For a formative quiz on these three lectures, I'd suggest 12 questions: mostly
> multiple-choice for recall, two short text-entry for application. Want me to draft them,
> or adjust the mix first?"*

You can accept, decline, or modify. The teacher owns the blueprint and every item.

### 2. The methodology guides, not dictates

The M1–M5 guides describe good assessment-design practice (constructive alignment,
formative assessment). They are applied to your context — a quick formative quiz needs a
lighter touch than a high-stakes exam.

### 3. Jump and redirect anytime

You are not locked into a track:

- "Skip M1 — I already know what I want to assess."
- "Go back to M2, I want fewer recall questions."
- "Show me the blueprint again."
- "This question is ambiguous — rewrite the stem."

### 4. Your judgement is final

Claude flags weak distractors, misalignment, or unclear stems. But whether a question is
fair, relevant, and worth asking is your call. Approve before it goes to QA and export.

---

## Example: Adaptive Decision-Making

**Teacher:** "I have last term's slides. Can we make a quick quiz?"

**Claude:**
> *Yes. For a quick formative quiz, we don't need the full M1 analysis — I can scan the
> slides for the main points and propose objectives, then we go straight to generating
> questions.*
>
> *From the slides, three themes stand out: cell respiration, photosynthesis, and the
> link between them. I'd suggest 10 questions weighted towards the link, since that is
> where students usually struggle.*
>
> *Want me to draft those, or adjust the weighting first?*

**Teacher:** "Draft them, but make two of them short text-entry, not multiple-choice."

**Claude:** Adjusts the mix and drafts the questions for your review.

---

## Practical Tips

### Starting fresh
```
"New QuestionForge session. Material at /path/to/lectures/,
project at /path/to/quiz/. What do you suggest?"
```

### Resuming work
```
"Continue the quiz project. Where did we leave off?"
```

### Exporting what you already have
```
"I have questions in markdown at /path/to/questions.md.
Validate them and export QTI."
```

### Checking the question types
```
"What question types can we use?"   (Claude calls list_types)
```

### Asking for judgement
```
"Is this distractor too easy to rule out?"
"Does this question actually test application, or just recall?"
"Which of these two stems is clearer?"
```

---

## What Claude Needs From You

1. **Clear context** — what you have (materials, objectives, or draft questions) and your goal.
2. **Explicit decisions** — when Claude asks you to confirm a blueprint or a question, respond clearly.
3. **Corrections** — if a question misses the point of your teaching, say so.
4. **Your expertise** — you know your subject, your students, and what a fair question looks like.

---

## Common Questions

**Q: Do I have to start at M1?**

A: No. Start where your material is — raw materials (M1), ready objectives (M2), or
finished markdown (straight to the pipeline). You can jump between modules at any time.

**Q: Where do the questions come from?**

A: From what you actually taught. M1 analyses your materials so the assessment matches
what students experienced — not a generic syllabus.

**Q: What comes out at the end?**

A: A QTI 2.2 package you can import into Inspera or another QTI-compatible platform. The
pipeline validates the format and exports it for you.

**Q: What if I disagree with a generated question?**

A: Edit or reject it. Say "rewrite this stem" or "drop this one." Nothing is exported
until you have approved it through QA (M4).

**Q: Is anything sent about my students?**

A: No. QuestionForge works from your teaching materials and produces questions. It is not
part of the student-data (assessment) workflow — no student answers or grades pass
through it.

---

## Philosophy

QuestionForge embodies a specific philosophy:

1. **AI augments, not replaces, teacher judgement** — you author and approve; the tools scaffold and check.
2. **Assessment grounded in instruction** — questions reflect what was taught, not just what was planned.
3. **Flexibility** — enter where your material is; adapt to context rather than forcing a track.
4. **Teacher control** — you drive the process; Claude assists.

The goal is to make well-designed assessment questions *feasible* to produce from your own
teaching — not to automate the judgement away.

---

*For the full method, see the M1–M5 guides in `methodology/`; for the question format, see
`methodology/m5/FORMAT_REFERENCE.md`. For installation, see `docs/GETTING_STARTED.md`.*
