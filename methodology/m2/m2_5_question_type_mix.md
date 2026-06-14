# M2 Stage 5: QUESTION TYPE MIX PLANNING

**Stage:** 5 of 7  
**Purpose:** Determines which question format types to use and in what proportions

---

## STAGE 5: QUESTION TYPE MIX PLANNING

### Purpose and Type Affordances

Stage 5 determines which question format types to use and in what proportions. Question type selection influences both assessment validity (how well questions measure intended learning) and practical feasibility (grading resources, platform capabilities, completion time).

Different question types offer distinct affordances for assessing cognitive levels and content types:

**Selected-Response Formats:**

*Multiple Choice (Single Answer)*: Students select one correct answer from multiple options. This format efficiently assesses recognition of concepts, identification of correct procedures, and selection among alternatives. Works well for Remember (identify term), Understand (select explanation), Apply (choose appropriate procedure), and Analyze (identify relationship) levels. Limited for Evaluate level unless options represent alternative positions requiring judgment.

*Multiple Choice (Multiple Answers)*: Students select all correct answers from options. This format assesses complex understanding requiring recognition that multiple factors contribute to phenomena. Works well for Understand (identify all relevant concepts) and Analyze (identify all applicable principles) levels. More cognitively demanding than single-answer because students must evaluate each option independently.

*True/False*: Students judge statement accuracy. This format enables quick assessment of many factual elements but risks encouraging guessing (50% chance). Works best for Remember (verify facts) and Understand (judge statement accuracy) levels. Often criticised in assessment literature for encouraging superficial engagement, best used sparingly.

*Matching*: Students connect items from two lists (e.g., terms to definitions, concepts to examples). This format efficiently assesses understanding of relationships among multiple related elements. Works well for Remember (match terms to definitions) and Understand (match concepts to examples) levels. Particularly useful when content involves systematic relationships among several elements.

**Constructed-Response Formats:**

*Fill-in-Blank (auto-graded constructed response)*: Students type a word or phrase to complete a statement — they construct the answer, but grading is automatic because correct answers are tightly constrained. This format requires recall rather than mere recognition, providing somewhat stronger evidence of learning than multiple choice. Works well for Remember (recall terms), Understand (complete explanation with key term), and Apply (insert appropriate value/formula).

*Text Area (Short Answer)*: Students type brief response (typically 1-3 sentences). This format requires students to generate rather than recognise answers, providing stronger evidence of understanding. Works well for Understand (explain briefly), Apply (solve and show work), and Analyze (identify and explain relationship) levels. Requires manual grading but allows partial credit and diagnostic feedback.

*Extended Text (Essay)*: Students compose longer response (multiple paragraphs). This format enables assessment of sophisticated reasoning, synthesis of multiple concepts, and evaluative judgment. Essential for Evaluate level (assess alternatives with justification). Requires substantial manual grading time but provides richest assessment data about student thinking.

**Interactive Formats:**

*Inline Choice*: Students select options embedded within passage text. This format assesses understanding in authentic context, requiring students to complete narrative or procedural description with appropriate terms/concepts. Works well for Understand (complete explanation) and Apply (insert appropriate procedure step) levels.

*Gap Match*: Students drag items into appropriate locations (e.g., labels onto diagram, steps into correct sequence). This format assesses organisational understanding and procedural sequencing. Works well for Understand (organise concept relationships) and Apply (sequence procedure steps) levels.

*Hotspot*: Students click correct regions on image or diagram. This format assesses spatial or visual understanding requiring students to identify features on diagrams. Works well for Remember (locate structures), Understand (identify regions showing phenomena), and Apply (identify where to measure/intervene) levels.

**Specialised Formats:**

Beyond the core types above, the platform supports specialised formats for particular content: numeric entry and mathematics entry (computed answers with tolerance), graphic entry, audio recording, composite items combining several interactions, and custom HTML content. These follow the same planning logic — match the format to the cognitive level and content — and are documented in the format reference.

### Distribution Framework: Cognitive-Type Mapping

Stage 5 uses systematic mapping between cognitive levels (from Stage 4 distribution) and appropriate question types:

```
Cognitive Level → Suitable Question Types Mapping:

REMEMBER level questions → Best served by:
- Primary: Fill-in-blank (recall terms)
- Secondary: Multiple choice (recognise definitions)
- Tertiary: Matching (connect terms to definitions)
- Avoid: Extended text (over-complex for simple recall)

UNDERSTAND level questions → Best served by:
- Primary: Multiple choice (select correct explanation)
- Secondary: Short answer (explain briefly)
- Tertiary: Matching (connect concepts to examples)
- Consider: Inline choice (complete explanation)

APPLY level questions → Best served by:
- Primary: Multiple choice (select appropriate procedure)
- Secondary: Short answer (solve problem, show work)
- Tertiary: Gap match (sequence procedure steps)
- Consider: Fill-in-blank (insert calculation result)

ANALYZE level questions → Best served by:
- Primary: Multiple choice multiple-answer (identify all factors)
- Secondary: Short answer (identify and explain relationship)
- Tertiary: Multiple choice (select relationship description)
- Consider: Hotspot (identify interacting elements)

EVALUATE level questions → Best served by:
- Primary: Extended text (assess alternatives with justification)
- Secondary: Multiple choice (select best alternative with complex options)
- Tertiary: Short answer (briefly justify position)
- Limited: Selected-response (difficulty capturing genuine evaluation)
```

This mapping provides default recommendations that teachers may adjust based on context.

### Practical Constraint Integration

Question type distribution must respect practical constraints from Stage 2:

**Grading Resource Constraints:**

Limited grading time → Emphasise selected-response formats (auto-gradable)
- Target: 70-90% selected-response
- Constructed-response only for critical objectives requiring it

Moderate grading time → Balance selected and constructed-response
- Target: 50-70% selected-response, 30-50% constructed

Extensive grading time → Can emphasise constructed-response
- Target: 30-50% selected-response, 50-70% constructed

**Platform Capability Constraints:**

A basic LMS supporting only standard formats → Limited to standard formats
- Available: Multiple choice, True/False, Fill-blank, Text area
- Unavailable: Most interactive formats (inline choice, gap match, hotspot)

A full QTI-capable platform (such as the target platform) → Full format range
- Available: All standard + interactive formats
- May still have limitations on specific features

**Time Constraint Influence:**

Short assessment time → Favor faster formats
- Emphasise: Multiple choice, True/False, Fill-blank
- Minimise: Constructed-response (time-consuming)

Adequate assessment time → Full format range feasible
- Balance based on cognitive and validity considerations

### Dialogue Pattern: Type Mix Negotiation

The Stage 5 dialogue presents recommended type mix based on constraints, then allows teacher adjustment:

```
AI System Recommendation:

"Question type distribution for [N] questions:

Recommended mix based on:
- Cognitive distribution from Stage 4
- [Grading resource level] from Stage 2  
- [Platform capabilities] from Stage 2
- [Time constraint] from Stage 2

AUTO-GRADED FORMATS ([X]% total):
- Multiple Choice (Single): [N1] questions ([%]) 
  Rationale: Versatile for Remember through Analyze levels
- Multiple Choice (Multiple): [N2] questions ([%])
  Rationale: Complex understanding at Analyze level
- True/False: [N3] questions ([%])
  Rationale: Quick checks for Remember level
- Fill-in-Blank: [N4] questions ([%])
  Rationale: Recall for Remember level
- Matching: [N5] questions ([%])
  Rationale: Relationships for Remember/Understand

MANUAL-GRADED FORMATS ([Y]% total):
- Text Area (Short Answer): [N6] questions ([%])
  Rationale: Brief explanations for Understand/Apply/Analyze
- Extended Text (Essay): [N7] questions ([%])
  Rationale: Required for Evaluate level

[If platform supports interactive formats:]
INTERACTIVE FORMATS ([Z]% total):
- Inline Choice: [N8] questions ([%])
  Rationale: Contextual understanding for Understand/Apply
- Gap Match: [N9] questions ([%])
  Rationale: Sequencing for Apply level
- Hotspot: [N10] questions ([%])
  Rationale: Spatial identification for Remember/Apply

Analysis:
- Auto-graded: [X]% (feasible for [grading constraint])
- Manual-graded: [Y]% (manageable with [grading resource])
- Type variety: [assessment - Good/Excellent variety]

Does this type mix work for your assessment needs?

Adjustments to consider:
- Increase/decrease manual-graded %
- Add/remove specific types
- Emphasise particular formats"
```

Teachers commonly request adjustments:

**Reduce Manual Grading:** "I have limited time. Can we reduce short answer and essay?" AI system redistributes to selected-response while noting loss of assessment depth for higher-order thinking.

**Increase Variety:** "This seems too heavily multiple choice. Can we diversify?" AI system increases matching, fill-blank, and (if available) interactive formats while explaining slight time increase.

**Add Missing Format:** "Can we include [specific type]?" AI system adds requested type if platform supports it, redistributing questions from other types, and notes purpose that format serves.

**Platform Limitation:** "My LMS doesn't support [format]. What alternatives?" AI system proposes substitute formats achieving similar assessment goals using available capabilities.

### Type Distribution Validation

After adjustments, the AI system validates the question type mix:

```
Type Distribution Validation:

✅ All cognitive levels have appropriate question types
✅ Auto-graded % feasible for grading resources
✅ All types supported by platform
✅ Type variety adequate (avoiding over-reliance on single format)
✅ Format matches content characteristics

[If validation issues:]
⚠️  [Description of problem]
Recommended adjustment: [specific fix]
```

### Question Type Code Reference

For blueprint documentation, the AI system uses standardised question type codes:

```
Question Type Codes:

MC-Single: Multiple Choice (Single Answer)
MC-Multiple: Multiple Choice (Multiple Answers)
TF: True/False
FIB: Fill-in-Blank
Match: Matching
SA: Short Answer (Text Area)
Essay: Extended Text
IC: Inline Choice
GM: Gap Match
HS: Hotspot
```

### Stage 5 Checkpoint

Stage 5 concludes with finalised question type distribution:

```
Question Type Mix: FINALISED

Type distribution for [N] total questions:

Selected-Response (Auto-graded): [X]%
- Multiple Choice (Single): [N1] questions
- Multiple Choice (Multiple): [N2] questions
- True/False: [N3] questions
- Fill-in-Blank: [N4] questions
- Matching: [N5] questions

Constructed-Response (Manual-graded): [Y]%
- Text Area: [N6] questions
- Extended Text: [N7] questions

[If applicable:]
Interactive Formats: [Z]%
- Inline Choice: [N8] questions
- Gap Match: [N9] questions
- Hotspot: [N10] questions

Validation:
✅ Mix appropriate for cognitive distribution
✅ Grading workload: [feasible/manageable] for available resources
✅ All types supported by [platform]
✅ Type variety provides [good/excellent] assessment balance

Next stage determines difficulty distribution (easy, medium, hard) across 
these question types and cognitive levels.

Proceed to Stage 6: Difficulty Distribution Planning?
```

---

## STAGE 5 COMPLETION CHECKPOINT

**This stage is now complete.**

### Required Action Before Proceeding

1. **STOP HERE** - Do not proceed to Stage 6 automatically
2. **Present** the Question Type Mix to teacher
3. **WAIT** for teacher to explicitly approve the type distribution
4. **Next stage requires:** m2_6_difficulty_distribution (Stage 6: Difficulty Distribution Planning)

### Teacher Must Explicitly Confirm

The teacher must explicitly say one of the following:
- "Proceed to Stage 6"
- "Start Stage 6"
- "Continue to difficulty distribution planning"
- "Yes, let's determine difficulty levels"

### DO NOT

- ❌ Start Stage 6 dialogue without teacher approval
- ❌ Proceed without m2_6_difficulty_distribution loaded
- ❌ Improvise difficulty distribution recommendations
- ❌ Skip the approval checkpoint

### What Happens Next

After teacher approval, Stage 6 will determine:
- How questions distribute across difficulty levels (Easy, Medium, Hard)
- Difficulty calibration appropriate for assessment purpose
- Difficulty distribution within each cognitive level
- Expected performance patterns for students

**Status:** Stage 5 complete, awaiting teacher approval to proceed to Stage 6

---

**Previous File:** m2_4_blooms_distribution (Stage 4: Bloom's Distribution Planning)  
**Next File:** m2_6_difficulty_distribution (Stage 6: Difficulty Distribution Planning)  
