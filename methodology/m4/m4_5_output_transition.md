# M4: OUTPUT & TRANSITION

**Phase:** Output & Transition to export  
**Classification:** 🔷🔶 HYBRID  
**Primary Input:** Validated question set with QA report  
**Primary Output:** Export-ready question package

---

## M4 OUTPUT ARTEFACTS

### Primary Outputs

**1. Validated Question Set**
- All questions with approved status
- Quality metadata attached to each question
- Technical validation confirmed
- Pedagogical review complete
- Collective analysis validated

**2. Quality Assurance Report**
- Executive summary
- Technical validation results
- Pedagogical review findings
- Collective analysis outcomes
- Approval determination
- Quality metadata

**3. QA Approval Certificate**
- Formal approval documentation
- Instructor signature
- Validation date
- Deployment authorisation

**4. Coverage and Distribution Matrices**
- Learning objective coverage map
- Bloom's taxonomy distribution
- Question type distribution
- Difficulty distribution
- Assessment blueprint alignment

### Supporting Documentation

**Quality Evidence:**
- Phase 1 technical validation report
- Phase 2 pedagogical review decisions
- Phase 3 collective analysis
- Phase 4 quality documentation

**Improvement Data:**
- Common issues identified
- Revision patterns
- Time investment data
- Quality trends

---

## VALIDATION WORKFLOWS

### Standard Workflow (New Questions)

**Process Flow:**
```
M3 (Generated Questions)
    ↓
M4 Phase 1 (Technical Validation)
    ↓
[If FAIL] → Return to M3 for correction → Re-validate
    ↓
[If PASS] → M4 Phase 2 (Pedagogical Review)
    ↓
[If REVISE/REJECT] → Return to M3 for improvement → Re-validate
    ↓
[If APPROVE] → M4 Phase 3 (Collective Analysis)
    ↓
[If GAPS/IMBALANCE] → Return to M3 for additional generation
    ↓
[If PASS] → M4 Phase 4 (Documentation)
    ↓
Export (qf-pipeline)
```

**Error Handling:**
- **Phase 1 fails:** Return to M3 for technical correction, re-validate Phase 1
- **Phase 2 issues:** Revise in M3 or make minor corrections in M4, re-validate Phase 2
- **Phase 3 gaps:** Return to M3 for targeted generation, re-validate Phase 3

### Revision Workflow (Existing Questions)

**Process Flow:**
```
Existing Questions
    ↓
M4 Diagnostic Analysis (identify specific issues)
    ↓
Targeted Improvements (address identified problems)
    ↓
Re-validation (phases as needed)
    ↓
Approval
    ↓
Export (qf-pipeline)
```

**Efficiency Strategy:**
- Focus validation on dimensions needing improvement
- Skip phases where quality is already verified
- Document diagnostic findings
- Targeted corrections rather than complete regeneration

### Import Preparation (Technical Validation Focus)

**Process Flow:**
```
Ready Questions (pedagogically validated elsewhere)
    ↓
M4 Phase 1 (Technical Validation Only)
    ↓
[If technical issues] → Correct → Re-validate
    ↓
[If PASS] → M4 Phase 4 (Documentation)
    ↓
Export (qf-pipeline)
```

**Use Case:**
- Questions validated through other quality processes
- Import from external sources
- Platform migration requiring technical validation
- Legacy questions needing platform compliance check

---

## INTEGRATION POINTS

### From M3 (Question Generation)

**Required Inputs:**
- Generated questions in structured format
- Initial quality checks passed during generation
- Complete metadata
- Alignment to blueprint specifications

**Quality Expectations:**
- M3 catches basic errors during generation
- M4 performs comprehensive validation
- M3 provides "good enough to validate"
- M4 ensures "ready for deployment"

### To Export (qf-pipeline)

Before export, the approved questions are converted to QFMD in M5 (Question Formatting); the pipeline then validates the QFMD and generates the QTI package.

**Provided Outputs:**
- Validated question set (all questions approved)
- QA approval certificate
- Quality metadata embedded in each question
- Coverage and distribution matrices
- Platform-ready status confirmed

**Quality Preservation Requirements:**

The export stage (qf-pipeline) MUST preserve during export:
- All validated content without modification
- All approved metadata exactly as validated
- Question structure as validated
- Pedagogical intent documented in QA
- Quality assurance evidence

**Critical Handoff:**
```
M4 → export Transfer Requirements:

✅ PRESERVE:
- Validated question content (no changes)
- Approved metadata (exact values)
- Question structure (as validated)
- Quality metadata (complete)
- Pedagogical rationale (documented)

❌ DO NOT:
- Modify validated content
- Change approved metadata
- Restructure questions
- Remove quality documentation
- Alter pedagogical design
```

---

## EFFICIENCY GUIDELINES

### For AI Systems

**Mechanised checks:**
- Conduct technical checks first (Phase 1); execute the mechanisable ones as code with per-item evidence
- Eliminate technical distractions before expert review
- Flag potential issues with clear severity classification; never report PASS for a check not executed (ADR-017)
- Batch similar issues for efficient review
- Apply straightforward corrections with approval

**Report Generation:**
- Generate concise, actionable reports
- Prioritise critical issues
- Provide correction examples
- Track quality patterns
- Document time investment

**Workflow Optimisation:**
- Pre-validate during generation when possible
- Catch obvious errors early
- Suggest corrections proactively
- Learn from quality patterns
- Streamline repeated validations

### For Instructors

**Review Efficiency:**
- Review questions by learning objective (maintains context)
- Focus on critical quality dimensions first:
  1. Alignment (most important)
  2. Disciplinary accuracy (critical for validity)
  3. Clarity (essential for fairness)
  4. Other dimensions as applicable
- Accept "adequate" quality rather than pursuing "perfect"
- Document significant decisions for future reference
- Use structured protocols (prevents missing dimensions)

**Time Management:**
- Phase 1: mechanised checks (fast)
- Phase 2: ~1-2 minutes per question
- Phase 3: ~15-20 minutes
- Phase 4: ~10-15 minutes
- **Total:** 1-2 hours for 40-50 questions

**Batching Strategies:**
- Group similar questions for review
- Use templates for common feedback
- Document patterns rather than repeating notes
- Delegate mechanisable checks to code; keep judgment calls with the instructor

---

## COMMON QUALITY ISSUES

### Technical Issues (Phase 1)

**Frequent Problems:**
- Malformed metadata
- Invalid identifiers (duplicates or format issues)
- QTI incompatible structures
- Missing required fields
- Cross-reference errors (invalid objective IDs)

**Prevention:**
- Validate during generation (M3)
- Use templates with required fields
- Automated identifier generation
- Reference validation before Phase 1

### Pedagogical Issues (Phase 2)

**Frequent Problems:**
- Misalignment with learning objectives
- Cognitive level mismatch (claiming higher than actual)
- Inappropriate difficulty calibration
- Unclear or ambiguous language
- Weak distractors (obviously wrong or implausible)
- Inadequate feedback (no conceptual explanation)
- Accessibility barriers (unnecessary complexity)

**Prevention:**
- Clear generation specifications
- Example-based training
- Misconception-informed distractors
- Explicit alignment checking during generation

### Collective Issues (Phase 3)

**Frequent Problems:**
- Coverage gaps (essential objectives missing)
- Distribution imbalances (>10% variance)
- Question dependencies (unintended)
- Excessive redundancy (near-identical questions)
- Inconsistent terminology across questions

**Prevention:**
- Systematic generation from blueprint
- Distribution monitoring during generation
- Independence checking
- Terminology management

---

## QUALITY STANDARDS SUMMARY

### Critical (Must Meet)

**Non-Negotiable Requirements:**
- ✅ Technical validation passes (all questions)
- ✅ All questions aligned with learning objectives
- ✅ Disciplinary accuracy confirmed
- ✅ Minimum coverage requirements met (Tier 1 objectives)
- ✅ No accessibility barriers identified

**Deployment Blocked Without:**
- Technical compliance
- Fundamental alignment
- Disciplinary correctness
- Essential coverage
- Accessibility

### Important (Should Meet)

**Strong Quality Indicators:**
- ✅ Cognitive levels accurately matched
- ✅ Difficulty appropriately calibrated
- ✅ Language clear and appropriate for students
- ✅ Distributions within tolerance (±5%)
- ✅ Feedback instructionally valuable

**Deployment Conditional If Missing:**
- Document exceptions
- Plan improvements
- Accept with notes

### Desirable (Nice to Have)

**Enhanced Quality:**
- ✅ Excellent distractor quality (misconception-informed)
- ✅ Authentic scenarios (realistic applications)
- ✅ Sophisticated rubrics (detailed scoring guidance)
- ✅ Extensive coverage variety (diverse question types)

**Future Enhancement Targets:**
- Note for improvement
- Not deployment blockers
- Continuous quality goals

---

## M4 COMPLETION VERIFICATION

### Ready for Export (qf-pipeline) When:

**All Validation Complete:**
- ✅ All executed technical checks passed (non-mechanised items reported as flags, not silent passes — ADR-017)
- ✅ All questions approved or conditionally approved
- ✅ Coverage requirements satisfied
- ✅ Distribution validated (within tolerance)
- ✅ QA report completed
- ✅ Instructor approval obtained

**Quality Documentation:**
- ✅ QA report finalised
- ✅ Approval certificate signed
- ✅ Quality metadata attached to all questions
- ✅ Coverage matrices complete
- ✅ Distribution validation documented

**Status Confirmation:**
- ✅ Overall status: APPROVED FOR DEPLOYMENT
- ✅ No critical issues outstanding
- ✅ Revisions (if required) completed and re-validated
- ✅ Ready for export to target platform

---

## TRANSITION TO EXPORT (qf-pipeline)

### Handoff Requirements

**What export Receives:**
```
📦 Export Package Contents:

1. Validated Question Set
   - All questions (approved status)
   - Quality metadata embedded
   - Technical validation confirmed

2. Quality Assurance Documentation
   - QA Report (complete)
   - Approval Certificate (signed)
   - Coverage Matrices
   - Distribution Validation

3. Export Specifications
   - Target platform (e.g., Inspera)
   - Format requirements (QTI 2.1)
   - Metadata schema
   - Technical constraints

4. Quality Preservation Requirements
   - Do not modify validated content
   - Preserve all metadata
   - Maintain question structure
   - Include QA evidence
```

### Next Steps

**Export-stage (qf-pipeline) Actions:**
1. Convert validated questions to QTI format
2. Preserve all quality metadata in export
3. Validate QTI export completeness
4. Generate import package for target platform
5. Verify import success
6. Confirm deployed questions match validated versions

**Quality Continuity:**
- M4 validates → export preserves → Platform deploys
- No content modification after M4 approval
- Quality metadata travels with questions
- Deployment verification confirms integrity

---

## FINAL CHECKLIST

**Before Proceeding to export:**

**Technical Validation:**
- [ ] All executed checks passed (non-mechanised items flagged, not silently passed)
- [ ] All technical errors resolved
- [ ] QTI compliance confirmed
- [ ] Metadata validation complete

**Pedagogical Validation:**
- [ ] All questions reviewed
- [ ] Alignment confirmed for all questions
- [ ] Cognitive demands validated
- [ ] Disciplinary accuracy verified

**Collective Validation:**
- [ ] Coverage requirements met
- [ ] Distributions within tolerance
- [ ] Consistency confirmed
- [ ] Assessment character appropriate

**Documentation:**
- [ ] QA report complete
- [ ] Approval certificate signed
- [ ] Quality metadata attached
- [ ] Matrices finalised

**Authorisation:**
- [ ] Instructor approval obtained
- [ ] Deployment authorised
- [ ] Ready for export

**Status:** ✅ **READY TO PROCEED TO EXPORT**

---

**Previous:** M3 (Question Generation)  
**Next:** M5 (Question Formatting), then Export (qf-pipeline)  
