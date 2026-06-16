# M4: INTRODUCTION & FOUNDATIONS

**Classification:** 🔷🔶 HYBRID (automated checks + expert judgment)
**Primary Input:** Assembled question set from M3
**Primary Output:** Validated question set with a quality-assurance report
**Purpose:** Ensure questions meet technical, pedagogical, and disciplinary quality standards at assessment level
**Estimated Duration:** 1-2 hours (for 40-50 questions)

---

## OVERVIEW AND PURPOSE

M4 is the critical quality gate between question generation and export. This module examines the assembled question set from M3 and prepares it for production through systematic, multi-dimensional review that combines mechanisable technical checks with expert pedagogical judgment.

Quality assurance in assessment development serves several functions beyond simple error detection. The review process examines constructive alignment between questions and learning objectives, considers cognitive demand levels, checks technical compliance with platform requirements, confirms disciplinary accuracy, and assesses overall pedagogical soundness.

The hybrid character of this module reflects the dual nature of quality assurance. Some controls are mechanisable — structural correctness, metadata consistency, format compliance, distribution counts — and where a control can be expressed as a deterministic rule it should be executed as code that produces inspectable evidence, not summarised in prose. Other dimensions — disciplinary accuracy, authentic scenarios, appropriate language, cultural sensitivity, teaching value — require expert judgment that only a qualified instructor can provide. M4 keeps the two honestly separate: a check that has not been executed is not reported as passed, and a judgment call is presented as a judgment call rather than as a verified result.

Quality assurance differs from the iterative refinement that occurs during question generation in M3. Generation focuses on creating individual questions that meet specifications. M4 then examines the complete question set as a coherent assessment instrument, identifying systemic issues that emerge only when viewing questions collectively.

**Working from the assembled set:** M4 operates on the full set of questions produced in M3, reviewed together. Set-level summaries — coverage, distribution, consistency across questions — support the collective-analysis phase (Phase 3), so exam-level review does not require recalculating distributions by hand.

---

## THEORETICAL FOUNDATIONS

### Assessment Validity Framework

Quality assurance operationalises Messick's (1995) unified validity framework, which conceptualises validity as the degree to which evidence and theory support interpretations of assessment scores. M4 systematically gathers validity evidence across multiple dimensions.

**Content validity** is examined by systematically checking that questions align with specified learning objectives and provide adequate coverage across content domains. The framework requires explicit verification that each learning objective receives appropriate assessment.

**Construct validity** is evaluated through Bloom's taxonomy alignment checking. The framework verifies that questions claiming to assess "analysis" genuinely require analytical reasoning rather than mere recall, and that cognitive demand matches both the learning objective specification and the assigned difficulty level.

**Consequential validity** enters consideration through accessibility review, bias detection, and feedback quality evaluation. The framework examines whether questions disadvantage particular student groups through unnecessary linguistic complexity, culturally-specific references, or format barriers.

### Quality Dimensions in Assessment

M4 draws on Haladyna and Rodriguez's (2013) framework for question quality, extended to cover diverse question types. Their evidence-based guidelines identify specific quality criteria across several dimensions:

**Technical quality** encompasses structural correctness, format compliance, and operational functionality. Review ensures questions conform to QTI specifications, metadata follows required schemas, identifiers remain unique, and the technical elements necessary for successful platform import are present and correct.

**Linguistic quality** addresses clarity, precision, and appropriateness of language. Review checks that question stems present clear tasks without ambiguity, answer choices exhibit parallel structure, terminology remains consistent with instruction, and language complexity matches student reading levels.

**Pedagogical quality** evaluates instructional soundness and alignment. Review confirms that questions assess intended learning objectives authentically, cognitive demands match specified levels, difficulty reflects appropriate challenge, scenarios present realistic contexts, and distractors represent plausible alternative conceptions.

**Psychometric quality** considers statistical properties supporting reliable measurement. M4 conducts a logical psychometric review: checking that point values reflect relative difficulty and importance, that questions avoid unintended dependencies, and that the complete set provides adequate coverage and discrimination.

---

## PROCESS ARCHITECTURE

### Entry Points and Prerequisites

M4 accepts the assembled question set from M3 once questions have been generated, collected, and formatted. The framework accommodates several entry scenarios:

**Standard Entry (Post-Generation):** Teachers arrive with the complete question set from M3 in human-readable format, together with set-level summaries. Quality assurance uses those summaries for collective validation: coverage completeness, distribution balance, consistency across questions.

**Revision Entry (Improvement Iteration):** Teachers arrive with existing questions requiring quality improvement. Quality assurance emphasises diagnostic analysis identifying specific quality dimensions needing enhancement, followed by targeted improvement (returning to M3 if needed).

**Import Preparation Entry (Technical Validation Focus):** Teachers arrive with questions ready for deployment but requiring final technical validation before export. Quality assurance emphasises technical compliance checking, metadata validation, and import simulation.

**Audit Entry (Quality Documentation):** Institutional quality assurance processes or programme accreditation require documented evidence. Quality assurance produces quality reports demonstrating systematic review.

**Note:** The assembled question set supports all M4 phases. Set-level summaries enable quick collective analysis, while the human-readable question format supports detailed pedagogical review.

### Process Overview: Four Validation Phases

M4 implements a systematic four-phase process:

1. **Phase 1: Technical Validation** (m4_1)
   - Runs structural checks
   - Catches format errors
   - Metadata issues and identifier problems
   - QTI compliance violations

2. **Phase 2: Pedagogical Quality Review** (m4_2)
   - Engages instructor expertise
   - Evaluates teaching effectiveness
   - Disciplinary accuracy assessment
   - Student appropriateness review

3. **Phase 3: Collective Assessment Analysis** (m4_3)
   - Evaluates the complete question set as a coherent instrument
   - Checks coverage completeness
   - Validates distribution balance
   - Identifies question dependencies

4. **Phase 4: Quality Documentation and Reporting** (m4_4)
   - Synthesises review results
   - Identifies specific issues
   - Provides evidence of what was checked, and how
   - Recommends improvements

The process operates iteratively — when review identifies issues, questions return for refinement before re-review.

---

## USING THIS DOCUMENTATION

M4 documentation is organised into modular files:

**m4_0_intro** (this file)
- Overview and purpose
- Theoretical foundations
- Process architecture
- Entry points

**m4_1_technical_validation**
- Technical checks and compliance
- Format and metadata validation
- QTI compliance checking
- Quality indicators

**m4_2_pedagogical_review**
- Expert judgment protocols
- Alignment verification
- Cognitive demand validation
- Disciplinary accuracy

**m4_3_collective_analysis**
- Coverage validation
- Distribution checking
- Consistency validation
- Assessment character

**m4_4_documentation**
- Quality reports
- Approval determinations
- Quality metadata
- Stakeholder communication

**m4_5_output_transition**
- Output artefacts
- Transition to M5 (Question Formatting) and export (qf-pipeline)
- Integration requirements
- Critical notes

### Sequential Process

Each phase file includes:
- Phase-specific validation procedures
- Decision criteria
- Documentation requirements
- Completion checkpoint

**CRITICAL:** Complete phases systematically, with expert review before proceeding.

---

## PREREQUISITES

Before starting M4, ensure:

**From M3 (Question Generation):**
- Generated questions in structured format
- Initial quality checks passed
- Metadata complete

**Required Resources:**
- Assessment blueprint from M2
- Instructor time for expert review (1-2 hours)

**Time Commitment:**
- Phase 1: structural checks (fast where mechanised)
- Phase 2: ~1-2 minutes per question
- Phase 3: ~15-20 minutes
- Phase 4: ~10-15 minutes
- **Total:** 1-2 hours for 40-50 questions

---

**Next File:** m4_1_technical_validation (Phase 1: Technical Validation)
