# QuestionForge Workflow

**Version:** 1.3
**Date:** 2026-02-04
**Related:** ADR-014 (Shared Session), RFC-012 (Pipeline-Script Alignment), RFC-013 (Pipeline Architecture v2.1), qf-scaffolding-spec.md, qf-pipeline-spec.md

---

## Overview

QuestionForge is an AI-assisted framework for creating pedagogically grounded quiz questions. It consists of two MCPs that work together:

| MCP | Language | Purpose |
|-----|----------|---------|
| **qf-pipeline** | Python | Technical processing (validation, export to QTI) |
| **qf-scaffolding** | TypeScript | Methodology guidance (M1-M4 modules) |

Both share the **same session** for a unified user experience.

---

## Entry Points

**Entry point = where you START, but you can jump freely between modules!**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           QUESTIONFORGE                                      │
│                                                                              │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌──────────────┐ │
│   │   M1    │   │   M2    │   │   M3    │   │   M4    │   │    Export    │ │
│   │Analysis │──▶│Blueprint│──▶│Questions│──▶│   QA    │──▶│     QTI      │ │
│   └────▲────┘   └────▲────┘   └────▲────┘   └────▲────┘   └──────▲───────┘ │
│        │             │             │              │               │          │
│   ┌────┴────┐   ┌────┴────┐   ┌────┴────┐   ┌────┴────┐    ┌────┴────┐    │
│   │   m1    │   │   m2    │   │   m3    │   │   m4    │    │pipeline │    │
│   │Material │   │  Goals  │   │  Plan   │   │   QA    │    │ Direct  │    │
│   └─────────┘   └─────────┘   └─────────┘   └─────────┘    └─────────┘    │
│                                                                              │
│          ◀── ── ── CAN JUMP BETWEEN MODULES ── ── ──▶                       │
│                                                                              │
│   M1 = Content Analysis    M3 = Question Generation                         │
│   M2 = Assessment Design   M4 = Quality Assurance                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Entry | Starts at | Recommended path | Can jump to |
|-------|-----------|------------------|-------------|
| **m1** Material | M1 | M1 → M2 → M3 → M4 → Pipeline | All modules |
| **m2** Goals | M2 | M2 → M3 → M4 → Pipeline | M1, M3, M4, Pipeline |
| **m3** Plan | M3 | M3 → M4 → Pipeline | M1, M2, M4, Pipeline |
| **m4** QA | M4 | M4 → Pipeline | M1, M2, M3, Pipeline |
| **pipeline** Direct | Pipeline | Step1 → Step2 → Step4 | M1, M2, M3, M4 |

---

## Complete Flow Diagram

```
                              ┌──────────────┐
                              │    START     │
                              └──────┬───────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │   init (both MCPs)  │
                          │   "What do you have?"│
                          └─────────┬───────────┘
                                    │
            ┌───────────┬───────────┼───────────┬───────────┐
            │           │           │           │           │
            ▼           ▼           ▼           ▼           ▼
      ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
      │   m1    │ │   m2    │ │   m3    │ │   m4    │ │pipeline │
      │Material │ │  Goals  │ │  Plan   │ │   QA    │ │ Direct  │
      └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
           │           │           │           │           │
           └───────────┴───────────┴───────────┴───────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │    step0_start      │
                       │  (qf-pipeline)      │
                       │  Creates session    │
                       └─────────┬───────────┘
                                 │
                                 ▼
                       ┌─────────────────────┐
                       │   Session created   │
                       │   session.yaml      │
                       └─────────┬───────────┘
                                 │
    ┌────────────┬───────────────┼───────────────┬────────────┐
    │            │               │               │            │
    ▼            ▼               ▼               ▼            ▼
┌───────┐   ┌───────┐       ┌───────┐       ┌───────┐   ┌─────────┐
│  m1   │   │  m2   │       │  m3   │       │  m4   │   │pipeline │
│ M1-M4 │   │ M2-M4 │       │ M3-M4 │       │M4 only│   │  direct │
└───┬───┘   └───┬───┘       └───┬───┘       └───┬───┘   └────┬────┘
         │                      │                      │
         ▼                      ▼                      │
   ┌───────────┐          ┌───────────┐                │
   │list_modules│         │list_modules│               │
   │(scaffolding)│        │(scaffolding)│              │
   └─────┬─────┘          └─────┬─────┘                │
         │                      │                      │
         ▼                      ▼                      │
   ┌───────────┐          ┌───────────┐                │
   │ M1: Content│         │ M2 or M3  │                │
   │ Analysis   │         │ (skip M1) │                │
   └─────┬─────┘          └─────┬─────┘                │
         │                      │                      │
         ▼                      │                      │
   ┌───────────┐                │                      │
   │ M2: Plan  │◄───────────────┘                      │
   └─────┬─────┘                                       │
         │                                             │
         ▼                                             │
   ┌───────────┐                                       │
   │ M3: Gen   │◄──────────────────────────────────────┤
   └─────┬─────┘                                       │
         │                                             │
         ▼                                             │
   ┌───────────┐                                       │
   │ M4: QA    │                                       │
   └─────┬─────┘                                       │
         │                                             │
         └──────────────────┬──────────────────────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   step2_validate    │
                 │   (qf-pipeline)     │
                 └─────────┬───────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
        ┌──────────┐             ┌──────────┐
        │  VALID   │             │ INVALID  │
        └────┬─────┘             └────┬─────┘
             │                        │
             ▼                        ▼
      ┌─────────────┐          ┌─────────────┐
      │step4_export │          │  Fix errors │
      │  (QTI)      │          │step1_fix_*  │
      └─────────────┘          └──────┬──────┘
                                      │
                                      └──→ (validate again)
```

---

## Project Structure

When session is created with `step0_start`:

```
project_name/
├── materials/              ← Input (lectures, slides) - M1 reads
├── methodology/            ← Method guides (copied in Step 0)
│   ├── m1_guide.md
│   ├── m2_guide.md
│   └── ...
├── preparation/            ← M1 + M2 output (foundation for questions)
│   ├── m1_content.md       ← Content analysis from M1
│   └── m2_blueprint.md     ← Assessment blueprint from M2
├── questions/              ← Questions (M3 creates, M4/M5 edit)
│   ├── questions.md        ← Current version
│   └── history/            ← Automatic backups per step
├── pipeline/               ← Step 1-3 working area
│   ├── working.md          ← Step 1 working file (with YAML progress)
│   ├── validation.txt      ← Step 2 report
│   └── history/            ← Backups
├── output/                 ← Step 4 final output
│   └── qti/                ← QTI package (.zip)
├── session.yaml            ← Session state (both MCPs)
└── logs/                   ← Action logs
```

### Data Flow

```
Step 0: Creates folders + copies methodology/ guides
M1: Reads materials/ → Writes preparation/m1_content.md
M2: Reads preparation/m1_content.md → Writes preparation/m2_blueprint.md
M3: Reads preparation/m2_blueprint.md → Creates questions/questions.md
M4: Reads questions/questions.md → Edits + backup to history/
M5: Reads questions/questions.md → Edits + backup to history/
Step1: Copies to pipeline/working.md → Edits → Back to questions/
Step2: Reads questions/ → Writes pipeline/validation.txt
Step3: Edits questions/questions.md + backup
Step4: Reads questions/ → Writes output/qti/
```

---

## Modules (M1-M4)

### M1: Content Analysis
**Purpose:** Analyse what was actually taught  
**Input:** Teaching materials (lectures, slides, transcripts)  
**Output:** Learning objectives, example catalogue, misconceptions  
**Duration:** 2.5-3.5 hours  
**Stages:** 8

```
Stage 0: Material Analysis (AI solo, 60-90 min)
Stage 1: Initial Validation (dialogue, 20-30 min)
Stage 2: Emphasis Refinement (dialogue, 30-45 min)
Stage 3: Example Catalogue (dialogue, 20-30 min)
Stage 4: Misconception Registry (dialogue, 20-30 min)
Stage 5: Scope & Objectives (dialogue, 45-60 min)
```

### M2: Assessment Planning
**Purpose:** Design the assessment structure  
**Input:** Learning objectives (from M1 or your own)  
**Output:** Blueprint with question distribution  
**Stages:** 9

```
Stage 1: Objective Validation
Stage 2: Strategy Definition
Stage 3: Question Target
Stage 4: Bloom's Distribution
Stage 5: Question Type Mix
Stage 6: Difficulty Distribution
Stage 7: Blueprint Construction
```

### M3: Question Generation
**Purpose:** Create the questions  
**Input:** Blueprint (from M2 or your own)  
**Output:** Markdown questions  
**Stages:** 5

```
Stage 1: Template Selection
Stage 2: Basic Generation
Stage 3: Distribution Review
Stage 4: Finalisation
```

### M4: Quality Assurance
**Purpose:** Validate questions pedagogically  
**Input:** Questions (from M3 or existing)  
**Output:** Reviewed, validated questions  
**Stages:** 6

```
Phase 1: Automated Validation
Phase 2: Pedagogical Review
Phase 3: Collective Analysis
Phase 4: Documentation
```

---

## Tool Reference

### qf-pipeline Tools

| Tool | Purpose | When to use |
|------|---------|-------------|
| `init` | Critical instructions | ALWAYS first |
| `step0_start` | Create session | After init, when paths are clear |
| `step0_status` | Show session | Check progress |
| `step1_start` | Start guided build | If v6.3 format |
| `step1_fix_auto` | Auto-fix problems | After analysis |
| `step1_fix_manual` | Manual fix | Requires input |
| `step2_validate` | Validate markdown | Before export |
| `step2_read` | Read working file | Troubleshooting |
| `step4_export` | Export QTI | When valid |
| `list_types` | List question types | Reference |
| `list_projects` | List projects | Find files |

### qf-scaffolding Tools

| Tool | Purpose | When to use |
|------|---------|-------------|
| `init` | Critical instructions | ALWAYS first (same as pipeline) |
| `list_modules` | Show M1-M4 | After session created |
| `load_stage` | Load methodology | Progressively per stage |
| `module_status` | Show progress | Check where you are |

---

## Common Scenarios

### Scenario A: Teacher has lecture materials

```
1. User: "I want to create a quiz from my lectures"
2. Claude: init → "What do you have?" → User: "Material"
3. Claude: "Where is the material? Where should the project be saved?"
4. User: Provides paths
5. Claude: step0_start → Session created
6. Claude: list_modules → "Start with M1?"
7. User: "Yes"
8. Claude: load_stage(m1, 0) → Shows intro
9. User: "Ok"
10. Claude: load_stage(m1, 1) → Stage 0 (AI analyses material)
... continues through M1-M4 ...
11. Claude: step2_validate → Validates
12. Claude: step4_export → Exports QTI
```

### Scenario B: Teacher has learning objectives ready

```
1. User: "I have learning objectives, want to create quiz"
2. Claude: init → "What do you have?" → User: "Learning objectives"
3. Claude: step0_start → Session created
4. Claude: list_modules → "You can skip M1. Start M2?"
5. User: "Yes"
6. Claude: load_stage(m2, 0) → Starts M2
... continues M2-M4 ...
```

### Scenario C: Teacher has finished markdown

```
1. User: "I have quiz questions in markdown, want to export"
2. Claude: init → "What do you have?" → User: "Markdown with questions"
3. Claude: step0_start → Session created
4. Claude: step2_validate → Validates
5. If valid: step4_export
6. If invalid: step1_fix_* or manual fix
```

---

## Session State

### session.yaml Structure

```yaml
# ===== QF-PIPELINE =====
session_id: "project_20260114_103000"
created_at: "2026-01-14T10:30:00"
source_file: "/path/to/questions.md"
working_file: "/path/to/02_working/questions.md"
output_folder: "/path/to/03_output"
validation_status: "valid"  # pending | valid | invalid
question_count: 25
exports:
  - path: "questions_QTI.zip"
    timestamp: "2026-01-14T11:45:00"
    question_count: 25

# ===== QF-SCAFFOLDING =====
methodology:
  entry_point: "m1"  # m1 | m2 | m3 | m4 | pipeline
  active_module: "m2"
  
  m1:
    status: "completed"
    loaded_stages: [0, 1, 2, 3, 4, 5, 6, 7]
    outputs:
      objectives: "methodology/m1_objectives.md"
      examples: "methodology/m1_examples.md"
      misconceptions: "methodology/m1_misconceptions.md"
  
  m2:
    status: "in_progress"
    loaded_stages: [0, 1, 2]
    current_stage: 2
    outputs: {}
  
  m3:
    status: "not_started"
    loaded_stages: []
    outputs: {}
  
  m4:
    status: "not_started"
    loaded_stages: []
    outputs: {}
```

---

## Critical Rules

### For Claude

1. **ALWAYS start with init** - returns critical instructions
2. **ASK what the user has** - never assume m1/m2/m3/m4/pipeline
3. **WAIT for response** - don't guess paths
4. **One stage at a time** - progressive loading
5. **STOP at stage gates** - wait for teacher approval
6. **Validate before export** - step2_validate ALWAYS before step4_export

### Stage Gate Pattern

```
load_stage(m1, 2) returns:
{
  document: { content: "..." },
  requires_approval: true,
  approval_prompt: "Stage 1 complete. Continue to Stage 2?"
}

→ Claude MUST ask the teacher
→ Wait for "yes" / "ok" / confirmation
→ THEN load_stage(m1, 3)
```

---

## Troubleshooting

### "No active session"
```
Cause: qf-scaffolding called without session
Solution: Run step0_start (qf-pipeline) first
```

### "File not found"
```
Cause: Incorrect path
Solution: Use list_projects to find the correct folder
```

### "Invalid format"
```
Cause: Markdown does not follow v6.5 spec
Solution: Run step1_fix_auto or step1_fix_manual
```

### "Claude skips stages"
```
Cause: Stage gate not respected
Solution: load_stage has requires_approval - Claude MUST wait
```

---

## Appendix A: Pipeline-Script Alignment

### A.1 Background

MCP pipeline (`qf-pipeline`) and manual scripts (`qti-core/scripts/`) should produce **identical results**. A review on 2026-01-22 identified deviations.

**Related documentation:**
- RFC-012: `/docs/rfcs/rfc-012-pipeline-script-alignment.md`
- Checklist: `/docs/rfcs/rfc-012-phase1-checklist.md`
- Discussion: `/docs/rfcs/rfc-012-discussion-summary.md`

---

### A.2 Step-by-step Comparison (VERIFIED 2026-01-22)

**Status:** ✅ Verified via source code analysis (7/9 steps correct)

| Step | Manual Script | MCP Pipeline (step4_export) | Status |
|------|---------------|----------------------------|--------|
| **1. Validate** | `step1_validate.py` → `validate_markdown_file()` | `step2_validate` (separate) or nothing | ⚠️ Pipeline skips validation in step4! |
| **2. Create folders** | `step2_create_folder.py` → mkdir quiz/, resources/, .workflow/ | `QTIPackager.create_package()` creates folders | ⚠️ Created during packaging (later) |
| **3. Parse markdown** | `step4_generate_xml.py` → `MarkdownQuizParser` | `parse_file()` → `MarkdownQuizParser` | ✅ Same parser |
| **4. Validate resources** | `step3_copy_resources.py` → `ResourceManager.validate_resources()` | `validate_resources()` | ✅ Same logic |
| **5. Copy resources** | `step3_copy_resources.py` → `ResourceManager.copy_resources()` | `copy_resources()` | ✅ Same logic |
| **6. Update paths** | `step4_generate_xml.py` → `apply_resource_mapping()` | ❌ **MISSING ENTIRELY** | 🔴 **CRITICAL BUG** |
| **7. Generate XML** | `step4_generate_xml.py` → `XMLGenerator.generate_question()` | `generate_all_xml()` → `XMLGenerator` | ✅ Same generator |
| **8. Create manifest** | `step5_create_zip.py` → `QTIPackager` | `create_qti_package()` → `QTIPackager` | ✅ Same packager |
| **9. Create ZIP** | `step5_create_zip.py` → zipfile | `create_qti_package()` | ✅ Same logic |

---

### A.3 Critical Bug: apply_resource_mapping() Missing

**Problem:** Pipeline never calls `apply_resource_mapping()` after `copy_resources()`.

**Consequence:**
```
QTI package contains:
✅ resources/Q001_image.png  (file copied correctly)
❌ XML references: image.png   (original path, not updated)
→ Images DO NOT display in Inspera!
```

**Manual process (step4_generate_xml.py):**
```python
# 1. Load mapping from step3
resource_mapping = load_resource_mapping(workflow_dir)
# {'image.png': 'Q001_image.png'}

# 2. Update ALL question fields with new paths
for question in quiz_data['questions']:
    if 'image' in question:
        question['image']['path'] = f"resources/{renamed}"
    question['question_text'] = update_image_paths_in_text(...)
    # ... feedback, premises, etc.

# 3. THEN generate XML with updated paths
xml = xml_generator.generate_question(question)
```

**Pipeline process (server.py):**
```python
# 1. Copy resources (returns mapping)
copy_result = copy_resources(...)
# copy_result['mapping'] ← IGNORED!

# 2. ❌ MISSING: apply_resource_mapping()

# 3. Generate XML with OLD paths
xml_list = generate_all_xml(questions, language)  # Wrong paths!
```

---

### A.4 Solution: Hybrid Approach (RFC-012)

**PHASE 1 (NOW) - Subprocess:**
Pipeline runs scripts directly via `subprocess.run()`:

```python
# step2_validate → runs step1_validate.py
# step4_export → runs ALL 5 scripts sequentially
```

**Benefits:**
- ✅ Guaranteed consistency (same code = same result)
- ✅ Fixes critical bug immediately
- ✅ No risk of forgetting steps
- ✅ Output in MCP matches Terminal

**PHASE 2 (LATER) - Refactor:**
Scripts refactored to importable functions:

```python
from qti_core.scripts.step1_validate import validate
result = validate(Path(file_path), verbose=True)
```

**Status:** Phase 1 ready for implementation (2026-01-22)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.3 | 2026-02-04 | Translated to British English |
| 1.2 | 2026-01-25 | Updated folder structure (RFC-013): preparation/, questions/, pipeline/, output/ |
| 1.1 | 2026-01-22 | Added Appendix A: Pipeline-Script Alignment (RFC-012) |
| 1.0 | 2026-01-14 | Initial workflow document |

---

*QuestionForge Workflow v1.3 | 2026-02-04*
