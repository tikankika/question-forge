# M4: PHASE 1 - TECHNICAL VALIDATION

**Phase:** Phase 1 - Technical Validation
**Classification:** 🔷🔶 MECHANISED CHECKS + FLAGS FOR JUDGMENT
**Duration:** fast where mechanised (~minutes for 40-50 questions)
**Primary Input:** Generated questions from M3
**Primary Output:** Technical validation report

---

## PURPOSE

Verify structural correctness and platform compliance before investing instructor time in pedagogical review. Mechanised checks clear away technical distractions so that experts can focus on pedagogical quality.

**Honesty principle (ADR-017 — the framework's decision that quality assurance must be executed, not merely reported):** A check that can be expressed as a deterministic rule is *executed* as code and produces inspectable evidence (the offending items, the measured values, the threshold applied). A check in this list that is **not** yet mechanised is surfaced as a **flag for expert judgment** — it is never reported as a silent PASS. The phase distinguishes between what the code verified and what a human still needs to look at.

---

## TECHNICAL CHECKS

The checks below fall into two groups: those that are mechanisable (run deterministically, with per-item evidence) and those that currently require human judgment or are flagged for review. The report keeps the two apart.

### Format Compliance (mechanisable)

**Markdown Structure:**
- Correct markdown structure
- Required sections present (metadata, question, answers, feedback)
- Proper element nesting
- No formatting errors

### Metadata Validation

**Required Fields (mechanisable):**
- All required fields populated
- No missing or empty critical fields

**Learning Objective Validation (mechanisable — ID lookup against the blueprint):**
- Learning objective IDs match the M2 blueprint
- Objectives exist in approved list
- No orphaned or invalid objective references

**Bloom's Level Validation (mechanisable — vocabulary check only):**
- Bloom's levels use approved vocabulary (Remember, Understand, Apply, Analyze, Evaluate, Create)
- No misspellings or non-standard terms
- Levels match approved taxonomy

**Question Type Validation (mechanisable):**
- Question types match QTI formats
- Valid types map to supported QTI question types
- No unsupported or custom types without QTI mapping

**Difficulty Level Validation (mechanisable — vocabulary check only):**
- Difficulty levels valid (Easy, Medium, Hard)
- Consistent capitalisation
- No non-standard terms

**Point Value Validation (mechanisable — range and format only):**
- Point values within acceptable range
- Integer or half-point values only
*(Whether points are proportional to difficulty and cognitive demand is a judgment call — see Quality Indicators below.)*

**Identifier Validation (mechanisable):**
- All question identifiers unique
- Valid format (no special characters, appropriate length)
- No duplicates within question set

### QTI Compliance (mechanisable — conversion dry-run)

**Question Structures:**
- Question structures convert cleanly to QTI format
- All elements have QTI equivalents
- No unsupported formatting or elements

**Metadata Mapping:**
- Metadata maps correctly to QTI elements
- All required QTI fields can be populated
- No orphaned metadata without QTI destination

**Conversion Blockers:**
- No conversion-blocking elements identified
- All media references valid
- All response processing rules valid

### Cross-Reference Validation (mechanisable for ID/type matching; alignment judgments flagged)

**Learning Objectives:**
- Learning objectives exist in the M2 blueprint
- Objective metadata matches blueprint definitions
- No mismatched cognitive levels

**Bloom's Levels:**
- Declared Bloom's level matches the level recorded for the objective in the blueprint (mechanisable label comparison)
*(Whether the question genuinely demands its declared cognitive level is a judgment call — see Quality Indicators below.)*

**Question Types:**
- Question types match metadata declarations
- Format supports claimed question type
- Response processing appropriate for type

### Quality Indicators (flags for expert review, not pass/fail)

These are heuristics that *surface* items for a human to judge. They are not verdicts.

**Reading Level Analysis:**
- Flesch-Kincaid grade level
- Sentence length analysis
- Vocabulary complexity
- Technical term density

**Language Complexity Metrics:**
- Average sentence length
- Passive voice frequency
- Subordinate clause density
- Readability scores

**Cognitive and Scoring Judgments (moved here from the checks above):**
- Does the question genuinely demand its declared Bloom's level, or can it be answered by recall?
- Are point values proportional to difficulty and cognitive demand?

**Structural Anomalies:**
- Unusually long question stems
- Excessive answer choices
- Unbalanced choice lengths (a correct-answer-longest cue — the kind of check ADR-017 requires be made executable with per-item evidence)
- Missing feedback elements

**Potential Bias Terms:**
- Gender-specific language
- Cultural references
- Stereotyping indicators
- Accessibility concerns

---

## VALIDATION REPORT OUTPUT

### Technical Validation Report Structure

**Critical Errors (Must Fix):**
- Format violations
- Missing required fields
- Invalid metadata values
- QTI incompatibilities
- Duplicate identifiers

**Warnings (Recommended Fixes):**
- Suboptimal formatting
- Inconsistent terminology
- Edge-case compliance issues
- Missing optional metadata

**Quality Flags (Expert Review Needed):**
- High reading level
- Language complexity
- Structural anomalies
- Potential bias indicators

### Status Determination

**PASS:** All *executed* critical checks passed — proceed to Phase 2. Checks that are not mechanised are reported as flags for judgment, not as silent passes.
**FAIL:** Critical errors identified — return to M3 for correction.

---

## ERROR HANDLING

### When Technical Validation Fails

**Critical Errors Identified:**
1. Document specific errors clearly
2. Provide correction guidance
3. Return questions to M3
4. Re-run validation after corrections

**Process:**
- DO NOT proceed to pedagogical review with technical errors
- Fix all critical issues first
- Re-validate before Phase 2
- Document correction cycle

---

## EFFICIENCY NOTES

### For AI Systems

**Execution:**
- Run mechanised checks deterministically; emit per-item, inspectable evidence
- Batch similar error types
- Generate actionable error messages
- Provide correction examples
- Do not report PASS for a check that was not executed

**Report Generation:**
- Clear severity classification
- Specific location identification
- Suggested fixes included
- Prioritised action list

### For Instructors

**Review Priority:**
- Focus on quality flags first (require judgment)
- Rely on the executed checks for the mechanical compliance they cover; treat flags and non-mechanised items as requiring your judgment
- Review correction recommendations
- Approve fixes when appropriate

**Time Investment:**
- Mechanised checks: fast (minutes)
- Quality flag review: ~5-10 minutes
- Correction approval: ~5 minutes
- **Total Phase 1:** ~15-20 minutes for 40-50 questions

---

## PHASE 1 COMPLETION CHECKPOINT

✅ **This phase is now complete.**

**REQUIRED ACTIONS:**
1. Review technical validation report
2. Address all critical errors (return to M3 if needed)
3. Review quality flags
4. WAIT for explicit instruction to proceed to Phase 2

**Teacher must explicitly say:** "Proceed to Phase 2" or "Start pedagogical review"

**DO NOT proceed automatically to Phase 2.**

---

**Next File:** m4_2_pedagogical_review (Phase 2: Pedagogical Quality Review)
