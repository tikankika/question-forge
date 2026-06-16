# M4: PHASE 4 - QUALITY DOCUMENTATION

**Phase:** Phase 4 - Quality Documentation and Reporting  
**Classification:** 🔶 EXPERT JUDGMENT + 🔷 MECHANISED CHECKS  
**Duration:** ~10-15 minutes  
**Primary Input:** Validation results from Phases 1-3  
**Primary Output:** QA Report and approval documentation

---

## PURPOSE

Document validation process and produce evidence for stakeholders. Quality documentation serves multiple purposes: provides approval justification, creates institutional memory, supports quality improvement, enables accountability, and facilitates communication with stakeholders.

---

## QA REPORT STRUCTURE

**Honesty principle (ADR-017) — applies to every section of this report:** A PASS line may only be shown for a check that was actually *executed* and produced inspectable evidence. A check that is not mechanised is reported as the instructor's judgment, not as a PASS. Every section below must distinguish what the code verified from what a human reviewed, and all figures in this template are an illustrative example of the report's shape, not a guaranteed result.

### Executive Summary

**Overall Status:**
- **APPROVED FOR DEPLOYMENT:** All standards met, ready for export
- **CONDITIONAL APPROVAL:** Minimum standards met, enhancements noted for future
- **REVISIONS REQUIRED:** Specific corrections needed before approval
- **MAJOR RECONSTRUCTION:** Fundamental problems, return to M3

**Quality Rating:**
- Overall quality assessment (Excellent/Good/Adequate/Needs Improvement)
- Confidence in assessment validity
- Readiness for deployment

**Key Strengths:**
- What went well in validation
- Exemplary question characteristics
- Notable quality achievements

**Areas Requiring Attention:**
- Issues identified during validation
- Patterns of concern
- Recommendations for improvement

### Technical Validation Results

*(Honesty principle above applies: PASS only for executed checks; figures illustrative.)*

**Checks Status:**
```
Technical Validation Summary:
- Format compliance: ✅ PASS (48/48 questions)
- Metadata validation: ✅ PASS (48/48 questions)
- QTI compliance: ✅ PASS (48/48 questions)
- Cross-reference validation: ✅ PASS (48/48 questions)
- Identifier validation: ✅ PASS (48/48 questions unique)

Critical Errors: 0
Warnings: 2 (resolved)
Quality Flags: 5 (reviewed)
```

**Errors and Warnings:**
- List of issues identified
- Resolution status
- Remaining concerns

**Quality Indicators:**
- Reading level analysis results
- Language complexity findings
- Structural anomalies flagged
- Bias indicator review

### Pedagogical Review Results

**Questions by Status:**
```
Pedagogical Review Summary:
- APPROVED: 42 questions (88%)
- APPROVED WITH NOTES: 5 questions (10%)
- REVISE REQUIRED: 1 question (2%)
- REJECTED: 0 questions (0%)

Total Questions Reviewed: 48
```

**Quality Dimension Ratings:**
```
Dimension            | Strong | Adequate | Weak
Alignment            | 85%    | 15%      | 0%
Cognitive Demand     | 78%    | 20%      | 2%
Difficulty           | 90%    | 10%      | 0%
Disciplinary Acc.    | 100%   | 0%       | 0%
Clarity              | 80%    | 18%      | 2%
Distractors          | 75%    | 20%      | 5%
Feedback             | 82%    | 18%      | 0%
Accessibility        | 100%   | 0%       | 0%
```

**Issues by Category:**
```
Issue Category           | Count | % of Total
Alignment concerns       | 2     | 4%
Cognitive level mismatch | 3     | 6%
Clarity needs improvement| 4     | 8%
Weak distractors         | 5     | 10%
Other                    | 1     | 2%
```

### Collective Analysis Results

**Coverage Validation:**
```
Coverage Analysis (computed):
- Total Learning Objectives: 12
- Objectives at or above minimum coverage (≥2 questions): 11 (92%)
- Objectives below minimum coverage (1 question): 1 (8%) — ⚠️ FLAG for judgment
- Objectives with no coverage: 0 (0%)

Tier 1 Coverage: ✅ COMPLETE (8/8 objectives at ≥2 questions)
Tier 2 Coverage: ⚠️ FLAG (3/4 objectives at ≥2 questions; 1 below minimum)
```

**Distribution Validation:**
```
Bloom's Distribution:
Level       | Blueprint | Actual | Variance | Status
Remember    | 15%       | 13%    | -2%      | ✅ Within tolerance
Understand  | 30%       | 32%    | +2%      | ✅ Within tolerance
Apply       | 35%       | 35%    | 0%       | ✅ Match
Analyze     | 15%       | 15%    | 0%       | ✅ Match
Evaluate    | 5%        | 5%     | 0%       | ✅ Match

Question Type Distribution: ✅ Within tolerance
Difficulty Distribution: ✅ Within tolerance
```

**Consistency Checks:**
```
Consistency Review (instructor judgment — not mechanised):
- Terminology consistency: reviewed by instructor — no issues noted
- Question independence: reviewed by instructor — no dependencies noted
- Redundancy assessment: reviewed by instructor — minimal overlap, acceptable
- Point allocation: reviewed by instructor — judged proportional
```

**Assessment Character:**
```
Assessment Character Evaluation (instructor judgment — not mechanised):
- Purpose alignment: judged to match formative intent
- Cognitive emphasis: judged appropriate for course level
- Time requirements: estimated ~85 minutes (within 90-minute slot)
- Difficulty profile: judged a balanced challenge distribution
```

### Detailed Findings

**Specific Issues Per Question:**
```
Question ID: Q-Bio-Cell-15
Status: REVISE REQUIRED
Issue: Cognitive demand mismatch
Details: Question claims "Analyze" but can be answered through recall
Recommendation: Revise scenario to require genuine analysis
Priority: HIGH

Question ID: Q-Bio-Cell-23
Status: APPROVED WITH NOTES
Issue: Distractor quality
Details: One distractor somewhat implausible
Recommendation: Consider stronger distractor for future revision
Priority: LOW
```

**Revision Guidance:**
- Clear description of required changes
- Specific examples or suggestions
- Priority levels assigned
- Re-validation requirements

---

## APPROVAL DETERMINATION

### Approval Categories

**APPROVED FOR DEPLOYMENT**

**Criteria:**
- All Phase 1 technical validation passed
- All questions approved or conditionally approved
- Coverage requirements satisfied
- Distributions within tolerance
- No critical issues identified

**Certification:**
```
QUALITY ASSURANCE CERTIFICATION

This question set has been validated and approved for deployment:

Assessment: [Assessment Name]
Course: [Course Code]
Question Count: [N]
Validation Date: [Date]

Technical Validation: PASS
Pedagogical Review: COMPLETE
Collective Analysis: VALIDATED

Approved by: [Instructor Name]
Approval Date: [Date]
Signature: ___________________

This question set meets institutional quality standards and is authorised for use in assessment.
```

**CONDITIONAL APPROVAL**

**Criteria:**
- Minimum quality standards met
- Minor enhancements possible but not required
- Deployment authorised with notes

**Documentation:**
```
CONDITIONAL APPROVAL NOTICE

This question set is approved for deployment with the following notes:

Strengths: [List key strengths]

Enhancement Opportunities: [List optional improvements]

These enhancements are noted for future revision cycles but do not affect deployment authorisation.
```

**REVISIONS REQUIRED**

**Criteria:**
- Specific issues identified requiring correction
- Clear revision path exists
- Not ready for deployment until corrected

**Documentation:**
```
REVISION REQUIREMENTS

The following specific revisions are required before approval:

Critical Revisions:
1. [Specific issue and required correction]
2. [Specific issue and required correction]

Recommended Revisions:
1. [Suggested improvement]
2. [Suggested improvement]

After revisions: Re-validate and resubmit for approval.
```

**MAJOR RECONSTRUCTION**

**Criteria:**
- Systematic quality problems
- Fundamental misalignment
- No clear correction path
- Requires return to earlier modules

**Documentation:**
```
RECONSTRUCTION REQUIRED

This question set requires major reconstruction:

Systemic Issues:
- [Fundamental problem 1]
- [Fundamental problem 2]

Recommended Actions:
1. Return to M2 (Assessment Planning) to review blueprint
2. Regenerate questions in M3 with revised specifications
3. Complete full validation cycle

This determination indicates structural problems requiring comprehensive regeneration rather than targeted revision.
```

---

## QUALITY METADATA

### Attached to Each Question

```yaml
quality_assurance:
  validation_date: "2024-11-10"
  reviewer: "Instructor Name"
  status: "approved"
  
  phase1_technical:
    # "pass" may only be recorded for checks actually executed (ADR-017)
    format_compliance: "pass"
    metadata_validation: "pass"
    qti_compliance: "pass"
    
  phase2_pedagogical:
    decision: "approve"
    alignment: "strong"
    cognitive_accuracy: "matches"
    difficulty: "appropriate"
    clarity: "clear"
    disciplinary_accuracy: "correct"
    accessibility: "accessible"
    
  phase3_collective:
    coverage_contribution: "adequate"
    distribution_alignment: "within_tolerance"
    
  approval:
    approved_by: "Instructor Name"
    approval_date: "2024-11-10"
    deployment_authorized: true
```

---

## STAKEHOLDER COMMUNICATION

### For Instructors

**Summary Format:**
- Overall approval status
- Key quality indicators
- Action items (if any)
- Timeline for deployment

### For Course Coordinators

**Programme-Level Information:**
- Assessment quality metrics
- Alignment with programme outcomes
- Quality assurance compliance
- Institutional standards met

### For Students (When Appropriate)

**Transparency Information:**
- Assessment quality-assured through executed checks and instructor review
- Alignment with learning objectives reviewed by the instructor
- Fair and accessible design reviewed by the instructor

### For Quality Assurance Offices

**Institutional Documentation:**
- Validation protocol followed
- Quality standards met
- Evidence of systematic review
- Continuous improvement data

---

## QUALITY IMPROVEMENT DATA

### For Continuous Enhancement

**Data Captured:**
- Common quality issues identified
- Time investment per phase
- Question revision patterns
- Distribution achievement rates

**Improvement Applications:**
- Refine generation prompts (M3)
- Adjust blueprint specifications (M2)
- Update validation protocols
- Train question authors

---

## PHASE 4 COMPLETION CHECKPOINT

✅ **This phase is now complete.**

**REQUIRED ACTIONS:**
1. Review complete QA report
2. Confirm approval determination
3. Obtain formal instructor approval signature
4. Attach quality metadata to all questions
5. WAIT for explicit instruction to proceed to export

**Teacher must explicitly say:** "Proceed to export" or "Export questions"

**DO NOT proceed automatically to export.**

---

**Next File:** m4_5_output_transition (Output & Transition)
