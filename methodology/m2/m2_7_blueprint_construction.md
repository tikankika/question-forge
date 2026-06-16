# M2 Stage 7: Blueprint Construction and Validation

**Stage:** 7 of 7  
**Purpose:** Synthesises all design decisions into comprehensive Assessment Blueprint

---

## STAGE 7: BLUEPRINT CONSTRUCTION AND VALIDATION

### Purpose and Blueprint Function

Stage 7 synthesises all decisions from Stages 1-6 into a comprehensive Assessment Blueprint that serves as the authoritative specification for question generation in M3. The blueprint functions as a detailed contract between assessment design (M2) and question generation (M3), ensuring that generated questions systematically implement the pedagogical decisions made during design.

The Assessment Blueprint serves multiple functions:

**Specification Function:** Provides complete, unambiguous specifications for each question to be generated, including learning objective, cognitive level, question type, difficulty level, and point value.

**Validation Function:** Enables systematic verification that design decisions are internally consistent, pedagogically sound, and practically feasible before question generation begins.

**Documentation Function:** Creates permanent record of design rationale, facilitating future assessment revision, quality assurance review, and institutional learning about effective assessment design.

**Communication Function:** Makes assessment structure transparent to all stakeholders—teachers understand what will be assessed, students understand assessment expectations, and AI systems understand generation requirements.

### Blueprint Components

The complete Assessment Blueprint consists of several integrated components:

#### 1. Design Summary

```
ASSESSMENT BLUEPRINT - DESIGN SUMMARY

Assessment Information:
- Course/Unit: [name]
- Topic/Module: [specific content area]
- Assessment Type: [Formative / Summative / Hybrid]
- Purpose: [brief description of assessment goals]
- Target Students: [student level and preparation]
- Platform: [LMS name and capabilities]
- Available Time: [X] minutes
- Estimated Completion Time: [Y] minutes (with buffer)

Design Decisions Summary:
- Total Questions: [N]
- Learning Objectives Assessed: [M] objectives
- Cognitive Distribution: [X]% foundation, [Y]% higher-order
- Question Type Mix: [X]% auto-graded, [Y]% manual-graded
- Difficulty Profile: [X]% easy, [Y]% medium, [Z]% hard
- Point Allocation: [Uniform / Weighted]

Date Created: [YYYY-MM-DD]
Designer: [teacher name]
Version: [X.X]
```

#### 2. Learning Objectives Mapping

```
LEARNING OBJECTIVES REFERENCE

[For each learning objective:]

LO-01: [Action verb] [content]
- Bloom's Level: [Remember/Understand/Apply/Analyze/Evaluate]
- Content Tier: [Tier 1 / Tier 2 / Tier 3]
- Questions Allocated: [N] questions
- Coverage Rationale: [why this number of questions]

LO-02: [Action verb] [content]
- Bloom's Level: [level]
- Content Tier: [tier]
- Questions Allocated: [N] questions
- Coverage Rationale: [rationale]

[Continue for all objectives...]

Objective Coverage Summary:
- Tier 1 (Essential) objectives: [N] objectives, [X] questions ([%] of total)
- Tier 2 (Important) objectives: [N] objectives, [X] questions ([%] of total)
- Tier 3 (Enrichment) objectives: [N] objectives, [X] questions ([%] of total)
```

#### 3. Question Specification Table

The Question Specification Table is the core blueprint component, providing complete specifications for each question:

```
QUESTION SPECIFICATION TABLE

Q# | LO | Bloom | Type | Diff | Points | Notes
---|-------|-------|------------|------|--------|---------------------------
001| LO-01 | Rem | MC-Single | Easy | 1 | Well-practised term recall
002| LO-01 | Rem | FIB | Med | 1 | Less emphasised term
003| LO-02 | Und | MC-Single | Easy | 1 | Core concept explanation
004| LO-02 | Und | SA | Med | 2 | Explain relationship
005| LO-03 | App | MC-Single | Med | 1 | Standard procedure application
006| LO-03 | App | SA | Hard | 2 | Adapted procedure, novel context
007| LO-04 | Ana | MC-Multiple| Med | 2 | Identify all relevant factors
008| LO-04 | Ana | SA | Hard | 2 | Compare concepts, explain differences
009| LO-05 | Eva | Essay | Hard | 5 | Evaluate alternatives with justification
[... continue for all N questions ...]

Column Definitions:
- Q#: Question number (sequential identifier)
- LO: Learning objective code (e.g., LO-01)
- Bloom: Cognitive level (Rem/Und/App/Ana/Eva/Cre)
- Type: Question format (MC-Single, MC-Multiple, TF, FIB, Match, SA, Essay, IC, GM, HS)
- Diff: Difficulty level (Easy/Med/Hard)
- Points: Point value for question
- Notes: Generation guidance, context, special requirements
```

#### 4. Distribution Validation Matrices

```
DISTRIBUTION VALIDATION

Cognitive Level Distribution:
Bloom Level | Target # | Target % | Actual # | Actual % | Status
------------|----------|----------|----------|----------|--------
Remember    | [N]      | [X]%     | [N]      | [X]%     | ✅
Understand  | [N]      | [X]%     | [N]      | [X]%     | ✅
Apply       | [N]      | [X]%     | [N]      | [X]%     | ✅
Analyze     | [N]      | [X]%     | [N]      | [X]%     | ✅
Evaluate    | [N]      | [X]%     | [N]      | [X]%     | ✅
TOTAL       | [N]      | 100%     | [N]      | 100%     | ✅

Question Type Distribution:
Type        | Target # | Target % | Actual # | Actual % | Status
------------|----------|----------|----------|----------|--------
MC-Single   | [N]      | [X]%     | [N]      | [X]%     | ✅
MC-Multiple | [N]      | [X]%     | [N]      | [X]%     | ✅
True/False  | [N]      | [X]%     | [N]      | [X]%     | ✅
Fill-Blank  | [N]      | [X]%     | [N]      | [X]%     | ✅
Matching    | [N]      | [X]%     | [N]      | [X]%     | ✅
Short Answer| [N]      | [X]%     | [N]      | [X]%     | ✅
Essay       | [N]      | [X]%     | [N]      | [X]%     | ✅
Interactive | [N]      | [X]%     | [N]      | [X]%     | ✅
TOTAL       | [N]      | 100%     | [N]      | 100%     | ✅

Difficulty Distribution:
Difficulty  | Target # | Target % | Actual # | Actual % | Status
------------|----------|----------|----------|----------|--------
Easy        | [N]      | [X]%     | [N]      | [X]%     | ✅
Medium      | [N]      | [X]%     | [N]      | [X]%     | ✅
Hard        | [N]      | [X]%     | [N]      | [X]%     | ✅
TOTAL       | [N]      | 100%     | [N]      | 100%     | ✅
```

#### 5. Cross-Tabulation Analysis

```
CROSS-TABULATION: BLOOM × DIFFICULTY

            | Easy | Medium | Hard | Total
------------|------|--------|------|-------
Remember    | [N]  | [N]    | [N]  | [N]
Understand  | [N]  | [N]    | [N]  | [N]
Apply       | [N]  | [N]    | [N]  | [N]
Analyze     | [N]  | [N]    | [N]  | [N]
Evaluate    | [N]  | [N]    | [N]  | [N]
------------|------|--------|------|-------
Total       | [N]  | [N]    | [N]  | [N]

Analysis:
- Each cognitive level has appropriate difficulty variety
- Difficulty increases appropriately with cognitive level
- No problematic empty cells (e.g., all Remember questions Easy)

CROSS-TABULATION: BLOOM × TYPE

            | MC-S | MC-M | SA | Essay | Other | Total
------------|------|------|-------|-------|-------|-------
Remember    | [N]  | [N]  | [N]   | [N]   | [N]   | [N]
Understand  | [N]  | [N]  | [N]   | [N]   | [N]   | [N]
Apply       | [N]  | [N]  | [N]   | [N]   | [N]   | [N]
Analyze     | [N]  | [N]  | [N]   | [N]   | [N]   | [N]
Evaluate    | [N]  | [N]  | [N]   | [N]   | [N]   | [N]
------------|------|------|-------|-------|-------|-------
Total       | [N]  | [N]  | [N]   | [N]   | [N]   | [N]

Analysis:
- Question types appropriate for cognitive levels
- Higher-order thinking has adequate constructed-response
- Remember/Understand balanced between recognition and recall
```

### Blueprint Construction Process

The AI system constructs the blueprint through systematic steps:

#### Step 1: Generate Question Specifications

For each question to be generated, create complete specification:

```
Question Generation Logic:

For Q#001:
1. Select learning objective (from Stage 1 list, ensuring coverage targets met)
2. Assign cognitive level (from Stage 4 distribution, matching objective's level)
3. Assign question type (from Stage 5 mix, appropriate for cognitive level)
4. Assign difficulty (from Stage 6 distribution, balanced within cognitive level)
5. Assign points (from Stage 6 allocation scheme)
6. Generate notes (provide context for question generation in M3)

Repeat for all N questions, tracking distributions to ensure targets met.
```

The AI system allocates questions strategically:

- **Priority 1:** Ensure every learning objective receives minimum coverage (typically 2 questions)
- **Priority 2:** Allocate additional questions to Tier 1 (essential) objectives
- **Priority 3:** Distribute remaining questions to achieve target distributions
- **Priority 4:** Ensure variety within each objective (different types, difficulties)

#### Step 2: Validate Distributions

Run systematic validation checks on the completed specification table. These checks are performed by the AI system in dialogue — they are not executed code, so the teacher should spot-check the arithmetic that matters most:

```
Systematic Validation Checks:

✅ Total question count matches Stage 3 target: [N] questions
✅ Cognitive distribution matches Stage 4 targets (±5% tolerance)
✅ Question type distribution matches Stage 5 targets (±5% tolerance)
✅ Difficulty distribution matches Stage 6 targets (±5% tolerance)
✅ Every learning objective has minimum coverage (≥2 questions)
✅ Tier 1 objectives have appropriate emphasis
✅ Point allocation follows specified scheme
✅ No cognitive-type mismatches (e.g., Essay for Remember level)
✅ Cross-tabulations show appropriate variety
✅ Estimated time within available time budget

[If any validation fails:]
⚠️  [Specific validation failure]
Recommendation: [Adjustment needed to fix]
```

#### Step 3: Generate Supporting Documentation

Create additional blueprint components:

**Grading Workload Estimate:**
```
Grading Workload Analysis:

Auto-graded questions: [N] ([X]%)
- Estimated grading time: Instant (automated)

Manual-graded questions: [M] ([Y]%)
- Short answer ([N1] questions): ~3 min/question = [time] total
- Essay ([N2] questions): ~10 min/question = [time] total
- Total manual grading time: [time] minutes per student
- For [Z] students: [time × Z] minutes = [hours] hours total

Recommended grading strategy:
[Suggestions for efficient grading, rubric development, etc.]
```

**Expected Performance Patterns:**
```
Expected Student Performance:

Based on difficulty distribution:
- Strong students (top 25%): 75-90% correct overall
  - Should excel on Easy and Medium, succeed on most Hard
- Average students (middle 50%): 55-75% correct overall
  - Should excel on Easy, succeed on most Medium, struggle on Hard
- Struggling students (bottom 25%): 35-55% correct overall
  - Should succeed on most Easy, struggle on Medium, rarely succeed on Hard

Score distribution characteristics:
- Mean: ~65% (if difficulty calibrated correctly)
- Standard deviation: ~15-20% (good discrimination)
- Range: 30-95% (no floor or ceiling effects)

If actual performance differs significantly from expectations, consider:
- Difficulty calibration issues
- Instruction-assessment alignment gaps
- Student preparation level misestimation
```

### Dialogue Pattern: Blueprint Review

After constructing the complete blueprint, the AI system presents it for teacher review:

```
AI System Presentation:

"Complete Assessment Blueprint constructed.

Summary Statistics:
- Total questions: [N]
- Learning objectives: [M] fully covered
- Cognitive distribution: [foundation X%, higher-order Y%]
- Question types: [X% auto-graded, Y% manual-graded]
- Difficulty: [X% easy, Y% medium, Z% hard]
- Estimated completion time: [time] minutes
- Estimated grading time: [time] hours for [N] students

Validation Status: [All checks passed / X issues identified]

[If issues identified:]
Issues requiring attention:
1. [Issue description and recommended fix]
2. [Issue description and recommended fix]
...

Blueprint Document Sections:
1. ✅ Design Summary (metadata and decisions)
2. ✅ Learning Objectives Mapping ([M] objectives)
3. ✅ Question Specification Table ([N] rows)
4. ✅ Distribution Validation Matrices (all distributions verified)
5. ✅ Cross-Tabulation Analysis (cognitive × difficulty, cognitive × type)
6. ✅ Grading Workload Estimate
7. ✅ Expected Performance Patterns

Would you like to:
A) Approve blueprint and proceed to question generation (M3)
B) Review specific sections in detail
C) Make adjustments to distributions
D) Export blueprint for review"
```

### Blueprint Output Formats

The blueprint can be exported in multiple formats:

**Markdown Format (Primary):**
- Complete documentation as structured markdown
- Suitable for version control, collaborative editing
- Includes all tables, validations, analyses

**Spreadsheet Format (Alternative):**
- Question Specification Table as CSV/Excel
- Enables filtering, sorting, analysis
- Useful for tracking generation progress

**JSON Format (Machine-readable):**
- Structured data for programmatic processing
- Enables automation of question generation
- Facilitates integration with other tools

### Blueprint Revision Process

If teacher identifies needed changes during review:

```
Revision Workflow:

Teacher identifies issue: "I want more Analyze-level questions"

AI System Response:
"Current Analyze allocation: [N] questions ([X]%)
Increasing to: [N+Y] questions ([X+Z]%)

This requires reducing other levels. Options:
A) Reduce Remember proportionally
B) Reduce Understand proportionally  
C) Reduce Apply proportionally
D) Custom redistribution

Which level should provide the additional questions?"

[After teacher selection:]
"Revised distribution:
- Remember: [N1] questions ([X1]%)
- Understand: [N2] questions ([X2]%)
- Apply: [N3] questions ([X3]%)
- Analyze: [N4+Y] questions ([X4+Z]%)
- Evaluate: [N5] questions ([X5]%)

Regenerating Question Specification Table with adjustments...
[Presents revised table]

Validation status: [Updated]

Approve this revision?"
```

Revisions loop until teacher approves final blueprint.

### Stage 7 Checkpoint

Stage 7 concludes with approved, validated Assessment Blueprint ready for question generation:

```
Assessment Blueprint: FINALISED AND APPROVED

Blueprint Status:
✅ All design decisions synthesised
✅ Question Specification Table complete ([N] questions fully specified)
✅ All distributions validated and balanced
✅ Cross-tabulations show appropriate variety
✅ Grading workload estimated and feasible
✅ Expected performance patterns documented
✅ Blueprint exported in requested format(s)

Blueprint Approval:
- Approved by: [teacher name]
- Date: [YYYY-MM-DD]
- Version: [X.X]

This blueprint serves as authoritative specification for M3 
(Question Generation). Any deviations from blueprint during generation must 
be explicitly documented and approved.

Next Steps:
- M3 (Question Generation): Generate questions according to the blueprint
- M4 (Quality Assurance): Validate the generated questions
- M5 (Question Formatting): Convert approved questions to QFMD
- qf-pipeline: Validate and export the QTI package for import into Inspera (or another QTI-compatible platform)

Ready to proceed?
```

---

## STAGE 7 COMPLETION CHECKPOINT

**This stage is now complete. M2 is now complete.**

### Required Action Before Proceeding

1. **STOP HERE** - Do not proceed to M3 (Question Generation) automatically
2. **Present** the complete Assessment Blueprint to teacher
3. **WAIT** for teacher to explicitly approve the blueprint
4. **Save/Export** the blueprint in teacher's preferred format
5. **Next module:** M3 (Question Generation)

### Teacher Must Explicitly Confirm

The teacher must explicitly say one of the following:
- "Approve the blueprint and proceed to M3"
- "The blueprint is approved, let's continue"
- "Yes, let's move to question generation"

### DO NOT

- ❌ Start M3 (Question Generation) without teacher approval of the blueprint
- ❌ Proceed without complete, validated blueprint document
- ❌ Generate any questions before blueprint approval
- ❌ Skip the blueprint export/save step
- ❌ Assume approval without explicit confirmation

### What Happens Next

After teacher approval, the workflow proceeds:

**Standard path:**
- Proceed to M3 (Question Generation): generate questions according to the blueprint specifications
- Then M4 (Quality Assurance): review and validate the generated questions
- Then M5 (Question Formatting): convert the approved questions to QFMD
- Then validate and export through the qf-pipeline: produce the QTI package for import into the target platform (e.g. Inspera)

**Revision path:**
- Return to earlier stages to adjust decisions
- Regenerate the blueprint with modifications
- Re-validate and seek approval again

### Critical Success Factors

Before proceeding, ensure:
- ✅ Blueprint document is complete and saved
- ✅ Teacher has reviewed all distributions
- ✅ Validation checks all passed
- ✅ Grading workload is feasible
- ✅ Expected timeline is realistic
- ✅ All stakeholders understand assessment structure

**Status:** M2 complete, awaiting teacher approval to proceed to M3 (Question Generation)

---

## M2 COMPLETION SUMMARY

### What Was Accomplished

M2 has transformed learning objectives into a comprehensive, validated Assessment Blueprint through seven connected stages:

**Stage 1:** Validated learning objectives for assessment suitability
**Stage 2:** Established assessment purpose and practical constraints  
**Stage 3:** Determined appropriate total question count
**Stage 4:** Allocated questions across Bloom's cognitive levels
**Stage 5:** Selected question format types and proportions
**Stage 6:** Distributed questions across difficulty levels
**Stage 7:** Synthesised all decisions into validated blueprint

### Deliverables Produced

1. **Assessment Blueprint Document** containing:
   - Design summary with all decisions documented
   - Learning objectives mapping with coverage allocations
   - Question Specification Table (complete specifications for [N] questions)
   - Distribution validation matrices (cognitive, type, difficulty)
   - Cross-tabulation analyses
   - Grading workload estimates
   - Expected performance patterns

2. **Validated Design Decisions:**
   - All distributions verified against targets
   - Pedagogical soundness confirmed
   - Practical feasibility validated
   - Teacher approval obtained

3. **Clear Specifications for Question Generation:**
   - Each question fully specified (LO, cognitive level, type, difficulty, points)
   - Generation guidance provided in notes column
   - Quality standards established

### Integration with Framework

**Inputs Received:**
- Learning objectives (from M1)
- OR curriculum standards (standards-driven entry)
- OR existing assessment (revision-driven entry)

**Outputs Produced:**
- Assessment Blueprint (specifications for M3 Question Generation)
- Quality criteria (for M4 Quality Assurance)

**Next Steps:**
- M3: Question Generation (create questions per blueprint)
- M4: Quality Assurance (validate the generated questions)
- M5: Question Formatting (convert approved questions to QFMD)
- qf-pipeline: validate and export the QTI package

### Design Philosophy Preserved

M2 maintained the framework's core principles:

**Teacher Pedagogical Authority:** All strategic decisions made by teacher, AI provided analysis and recommendations

**Systematic Structure:** Staged process ensured logical progression from objectives to complete specifications

**Explicit Documentation:** All decisions and rationale captured for transparency and future reference

**Validation at Every Stage:** Gate checkpoints prevented proceeding with problematic decisions

**Flexibility and Adaptation:** Process accommodated multiple entry points and revision cycles

---

**Previous File:** m2_6_difficulty_distribution (Stage 6: Difficulty Distribution Planning)  
**Next File:** m3_0_intro (Question Generation)  
