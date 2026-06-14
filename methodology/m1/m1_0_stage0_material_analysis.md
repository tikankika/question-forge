# M1 Stage 0: Material Analysis - Teacher Guide

## QUICK START FOR TEACHERS

This is the simplified version. Full details below.

### Step 1: Start Stage 0
Say: "Start M1 Stage 0 material analysis"

### Step 2: For Each Material
Say: "Analyse [filename.pdf]"
[Upload the file when Claude asks]
Claude saves analysis DIRECTLY to file (no chat preview needed)
Say: "Continue to next file"

### Step 3: Complete Stage 0
Say: "Finalise Stage 0"

## Overview
You will guide Claude through analysing your instructional materials
one file at a time. Each analysis is saved to its OWN file in preparation/.

**Output structure:**
```
preparation/
├── m1_material_01_[name].md    ← Analysis of first material
├── m1_material_02_[name].md    ← Analysis of second material
├── m1_material_03_[name].md    ← ... and so on
└── m1_stage0_summary.md        ← Final summary (after all materials)
```

## Before Starting
- Make your materials available in ONE of two ways:
  - **Project mode:** place all files in `project/materials/` before starting — Claude lists and reads them from there, or
  - **Upload mode:** keep the files at hand and upload each one when Claude asks for it
- Block out 60-90 minutes
- Be ready to provide feedback on Claude's analysis

---

## Step-by-Step Instructions

### STEP 1: Start Stage 0
**You say:** "Start M1 Stage 0 analysis"

**Claude will:**
- Load Stage 0 methodology
- List your materials
- Ask which file to analyse first

---

### STEP 2: Analyse First Material
**You say:** "Analyse [filename.pdf]"
*(Example: "Analyse Lecture_Week1.pdf")*

**Claude will:**
- Read the material
- Analyse and save DIRECTLY to file
- Report: "✅ Saved to preparation/m1_material_01_lecture_week1.md"
- Ask: "Continue to next file?"

**You should:**
- Say "yes" to continue, or
- Say "show me" to review the saved analysis

---

### STEP 3: Continue with Next Material
**You say:** "Yes, continue" or "Next"

**Claude will:**
- Analyse next material
- Save DIRECTLY to file
- Report progress (e.g., "2/10 materials complete")

---

### STEP 4: Repeat for All Materials
Repeat until all materials analysed.

---

### STEP 5: Complete Stage 0
After all materials analysed:

**You say:** "Finalise Stage 0"

**Claude will:**
- Create summary: preparation/m1_stage0_summary.md (see specification below)
- Ask if you want to proceed to Stage 1

#### The Stage 0 Summary — what it must contain

The summary is the bridge to Stage 1: Stage 1 validation presents priority tiers, emphasis evidence and scope candidates to the teacher, so the summary MUST contain them. Synthesise across ALL per-material analyses:

```markdown
# Stage 0 Summary

## Priority Tiers (initial — for teacher validation in Stage 1)
- Tier 1 (Essential): topics with the strongest emphasis across materials
- Tier 2 (Important): substantial but secondary emphasis
- Tier 3 (Supporting): background/context topics
- Tier 4 (Mentioned): briefly touched — likely out of assessment scope

## Emphasis Evidence (per Tier 1-2 topic)
Which materials cover it, how much space (slides/pages/sections), recurrence

## Aggregated Instructional Examples (grouped by topic)

## Aggregated Misconceptions (grouped by topic)

## Out-of-Scope Candidates
Topics appearing only peripherally — for teacher confirmation in Stage 1
```

**Tier assignment rules:**
- Recurrence across materials outweighs depth in a single material
- Explicit signals in the materials (stated objectives, summaries, review sections) outweigh inferred emphasis
- When uncertain between two tiers, assign the lower tier and flag it for Stage 1 validation

**Evidence honesty:** cite only what the materials support (page/slide counts, recurrence, explicit statements *in* the materials). Claude cannot know classroom time or what was said aloud — present such things as hypotheses for the teacher to confirm in Stage 1, never as observations.

---

## Common Issues

**Q: Claude shows analysis in chat instead of saving directly**
A: Say: "Don't show in chat. Save DIRECTLY to file."

**Q: Claude tries to analyse multiple files at once**
A: Say: "Stop. Analyse ONLY [filename.pdf] and save to file."

**Q: I want to review an analysis**
A: Say: "Show me m1_material_01.md" or check the file directly

**Q: I need to pause mid-stage**
A: Progress is saved in individual files. Resume anytime with: "Continue Stage 0"

---

#### FOR CLAUDE: Critical Execution Rules

**RULE 1: DIRECT FILE WRITE - NO CHAT PREVIEW**
- Analyse material internally
- Write DIRECTLY to file using write_project_file
- Do NOT show full analysis in chat
- Only show confirmation: "✅ Saved to [filename]"

**RULE 2: ONE FILE PER MATERIAL**
Each material gets its own file:
```
preparation/m1_material_01_[sanitised_name].md
preparation/m1_material_02_[sanitised_name].md
...
```

Filename format:
- `m1_material_` + 2-digit number + `_` + sanitised original name
- Sanitise: lowercase, spaces→underscores, remove special chars
- Example: "What is AI?.pdf" → "m1_material_01_what_is_ai.md"

**RULE 3: ONE file per turn**
After listing materials:
- Ask user to upload FIRST file ONLY
- STOP - do not proceed until file uploaded

**RULE 4: Save then ask for next**
After analysing ONE file:
- Save to file immediately
- Report: "✅ Saved to preparation/m1_material_XX_name.md (X/N complete)"
- Ask: "Continue to next file?"
- STOP - wait for user

**CRITICAL: write_project_file Format**

```json
write_project_file({
  project_path: "<project_path>",
  relative_path: "preparation/m1_material_01_what_is_ai.md",
  content: "# Material 1: What is AI?\n\n**Type:** Introduction...\n\n## Topics & Concepts\n...\n\n## Emphasis\n...\n\n## Instructional Examples\n...\n\n## Misconceptions\n..."
})
```

**Analysis Template:**
```markdown
# Material N: [Original Filename]

**Type:** [Document type - lecture, textbook, slides, etc.]
**Source:** [Source/course]
**Date:** [Analysis date]

## Topics & Concepts

**Primary concepts (defined):**
- [Term] - [definition as presented]
- ...

**Secondary concepts (mentioned):**
- [Term], [Term], ...

## Emphasis & Priorities

1. **HIGHEST:** [What's emphasised most]
2. **HIGH:** [Secondary emphasis]
3. **MEDIUM:** [Moderate coverage]
...

## Instructional Examples

- [Concrete example from material]
- [Another example]
...

## Misconceptions

- **"[Common misconception]"** ❌ → [Correct understanding]
- ...
```

## TROUBLESHOOTING

**Problem: Claude shows long analysis in chat**
Solution: Say "STOP. Write DIRECTLY to file, don't show in chat."

**Problem: Claude tries to analyse multiple files at once**
Solution: Say "STOP. Analyse ONLY [filename.pdf]. Save to file and wait."

**Problem: Claude overwrites previous analysis**
Solution: Each material has unique filename - this shouldn't happen. Check filenames.

**Problem: Claude uses save_m1_progress instead of write_project_file**
Solution: Say "Use write_project_file to create separate files per material."
