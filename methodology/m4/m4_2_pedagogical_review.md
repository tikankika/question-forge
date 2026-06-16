# M4: PHASE 2 - PEDAGOGICAL QUALITY REVIEW

**Phase:** Phase 2 - Pedagogical Quality Review  
**Classification:** 🔶 EXPERT JUDGMENT  
**Duration:** ~1-2 minutes per question  
**Primary Input:** Technically validated questions from Phase 1  
**Primary Output:** Pedagogical review decisions per question

---

## PURPOSE

Expert evaluation of teaching effectiveness and disciplinary accuracy. This phase requires instructor expertise to assess dimensions that cannot be automated: alignment authenticity, cognitive demand accuracy, disciplinary correctness, and pedagogical soundness.

---

## REVIEW DIMENSIONS

### Alignment Verification

**Core Questions:**
- Does question assess specified learning objective authentically?
- Can students answer correctly without mastering the objective?
- Does context match authentic application of the objective?

**Quality Criteria:**
- Strong Alignment: Question directly assesses objective mastery
- Adequate Alignment: Question relates to objective, minor context issues
- Weak Alignment: Tenuous connection or unintended focus

**Warning Signs:**
- Students could answer using unrelated knowledge
- Context artificial or disconnected from objective
- Question assesses prerequisite rather than stated objective

### Cognitive Demand Validation

**Core Questions:**
- Does question require claimed Bloom's level?
- Could students answer using lower-level cognitive processes?
- Is cognitive demand appropriate for learning objective?

**Quality Criteria:**
- **Remember:** Recall facts, terms, concepts
- **Understand:** Explain ideas, summarise, interpret
- **Apply:** Use knowledge in new situations, implement
- **Analyze:** Break down structures, identify relationships
- **Evaluate:** Make judgments, critique, assess
- **Create:** Generate new products, design, construct

**Common Mismatches:**
- Question claims "Analyze" but only requires recall
- "Application" question solvable through memorisation
- Authentic higher-order thinking present but uncredited

### Difficulty Calibration

**Expected Success Rates:**
- **Easy:** 80-95% of prepared students succeed
- **Medium:** 60-79% of prepared students succeed
- **Hard:** 40-59% of prepared students succeed

**Calibration Checks:**
- Does difficulty rating match actual cognitive demand?
- Is question appropriately challenging for objective?
- Will difficulty distribution support fair assessment?

**Adjustment Signals:**
- Difficulty seems mismatched to cognitive complexity
- Language complexity affecting difficulty inappropriately
- Trick elements creating artificial difficulty

### Disciplinary Accuracy

**Content Validation:**
- Factually correct content
- Reflects current disciplinary understanding (not outdated)
- Correct terminology usage
- Authentic scenarios from discipline

**Common Issues:**
- Oversimplified to point of inaccuracy
- Outdated concepts or frameworks
- Terminology misuse
- Artificial scenarios that misrepresent authentic practice

**Severity Assessment:**
- Critical: Fundamental misconceptions taught
- Important: Minor inaccuracies or outdated framing
- Note: Pedagogical simplifications appropriate for level

### Language Clarity

**Clarity Standards:**
- Unambiguous task presentation
- Appropriate vocabulary for student level
- Clear sentence structure
- No unnecessary linguistic complexity

**Quality Indicators:**
- Students understand what is being asked
- One clear correct answer or response expectation
- No multiple interpretations of question stem
- Language appropriate for student reading level

**Problematic Patterns:**
- Double negatives
- Ambiguous pronouns
- Complex subordinate clauses
- Unnecessarily technical vocabulary

### Distractor Quality (Selected-Response Questions)

**Quality Criteria:**
- Represent plausible alternative conceptions
- Reflect common student misconceptions
- Similar length to correct answer
- No obvious format mismatches

**Effective Distractors:**
- Based on documented misconceptions when possible
- Grammatically parallel to correct answer
- Require genuine understanding to eliminate
- Not trivially implausible

**Poor Distractors:**
- Obviously incorrect
- Different format from correct answer
- Include giveaway terms ("always," "never")
- Unrelated to question content

### Constructed-Response Rubrics

**Rubric Quality:**
- Clear scoring criteria
- Complete/partial credit defined explicitly
- Examples provided at different score levels
- Consistent scoring guidance across similar questions

**Essential Elements:**
- Point values justified
- Performance levels described clearly
- Common incomplete responses anticipated
- Scoring consistent with learning objective

### Feedback Quality

**Effective Feedback:**
- Explains why answers correct/incorrect
- Connects to underlying concepts
- Addresses common misconceptions
- Instructional rather than judgmental tone

**Quality Standards:**
- Goes beyond "correct/incorrect" declaration
- References learning objective content
- Provides conceptual explanation
- Helps students learn from mistakes

**Feedback Problems:**
- Merely restates correct answer
- No conceptual explanation
- Judgmental or discouraging language
- Missing for some answer choices

### Accessibility Review

**Language Accessibility:**
- Appropriate for non-native speakers
- No unnecessary idiomatic expressions
- Clear, direct language
- Definitions provided for essential technical terms

**Cultural Considerations:**
- No unnecessary cultural references
- Scenarios relevant across backgrounds
- Avoids assumptions about student experiences
- No stereotyping or cultural bias

**Format Accessibility:**
- Screen reader compatible
- No reliance solely on colour
- Clear visual hierarchy
- Alternative text for images

**Inclusivity Check:**
- No exclusionary language
- Diverse representation when applicable
- Avoids stereotypes
- Respectful terminology

---

## REVIEW DECISION PER QUESTION

### Decision Categories

**APPROVE:**
- Meets all quality standards
- Ready for deployment
- No revisions needed

**APPROVE WITH NOTES:**
- Acceptable quality overall
- Minor enhancements possible for future
- Deployment authorised
- Notes captured for next iteration

**REVISE REQUIRED:**
- Specific revisions needed before approval
- Clear correction path identified
- Not ready for deployment
- Return to M3 for targeted improvement

**REJECT:**
- Fundamental pedagogical problems
- No clear correction path
- Requires complete regeneration
- Remove from question set

### Documentation Requirements

**For Each Question:**
```yaml
pedagogical_review:
  reviewer: [instructor name]
  review_date: [date]
  decision: [approve/approve_with_notes/revise/reject]
  
  dimension_ratings:
    alignment: [strong/adequate/weak]
    cognitive_demand: [accurate/lower/higher]
    difficulty: [appropriate/too_easy/too_hard]
    disciplinary_accuracy: [correct/minor_issues/significant_issues]
    clarity: [clear/adequate/needs_improvement]
    distractors: [effective/adequate/weak] # if applicable
    rubric: [clear/adequate/unclear] # if applicable
    feedback: [instructional/adequate/insufficient]
    accessibility: [accessible/minor_concerns/barriers]
  
  notes: [specific observations]
  revision_guidance: [if revise required]
```

---

## REVIEW PROTOCOLS

### Efficient Review Strategy

**Review by Learning Objective:**
- Group questions by learning objective
- Maintains context across similar questions
- Identifies consistency issues
- Reduces cognitive switching

**Focus on Critical Dimensions:**
1. Alignment (most important)
2. Disciplinary accuracy (critical for validity)
3. Clarity (essential for fairness)
4. Other dimensions as applicable

**Accept "Adequate" Quality:**
- Not every question needs to be exemplary
- "Good enough" often sufficient for formative assessment
- Perfect is enemy of deployed
- Focus corrections on significant issues

### Time Management

**Per Question (1-2 minutes):**
- Quick alignment check: 20 seconds
- Cognitive demand verification: 20 seconds
- Accuracy/clarity scan: 20 seconds
- Distractor/rubric review: 30 seconds
- Decision and notes: 20 seconds

**Batch Processing:**
- Review similar questions together
- Document patterns rather than repeating notes
- Use templates for common feedback

---

## COMMON PEDAGOGICAL ISSUES

### Frequent Problems

**Alignment Issues:**
- Question assesses different objective than claimed
- Can be answered without objective mastery
- Context doesn't match authentic application

**Cognitive Level Mismatches:**
- Question claims higher level but tests recall
- Authentic application not recognised
- Cognitive shortcuts available

**Clarity Problems:**
- Ambiguous language
- Unclear expectations
- Multiple valid interpretations

**Weak Distractors:**
- Obviously incorrect options
- Don't reflect actual misconceptions
- Format mismatches with correct answer

---

## PHASE 2 COMPLETION CHECKPOINT

✅ **This phase is now complete.**

**REQUIRED ACTIONS:**
1. Review pedagogical evaluations for all questions
2. Confirm approval decisions
3. Document revision requirements for any REVISE/REJECT questions
4. WAIT for explicit instruction to proceed to Phase 3

**Teacher must explicitly say:** "Proceed to Phase 3" or "Start collective analysis"

**DO NOT proceed automatically to Phase 3.**

---

**Next File:** m4_3_collective_analysis (Phase 3: Collective Assessment Analysis)
