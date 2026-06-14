# M2 Stage 4: BLOOM'S DISTRIBUTION PLANNING

**Stage:** 4 of 7  
**Purpose:** Determines how questions distribute across Bloom's cognitive levels

---

## STAGE 4: BLOOM'S DISTRIBUTION PLANNING

### Purpose and Pedagogical Foundations

Stage 4 determines how the total question count distributes across Bloom's cognitive levels (Remember, Understand, Apply, Analyze, Evaluate, and occasionally Create). This distribution decision fundamentally shapes assessment character by establishing cognitive emphasis—what types of thinking the assessment prioritises.

Distribution decisions draw on several pedagogical principles:

**Alignment with Learning Objectives:** Question distribution should reflect the distribution of learning objectives across cognitive levels established in Stage 1. If 40% of objectives target Understanding level, approximately 40% of questions should assess Understanding unless teachers explicitly decide to weight differently.

**Assessment Purpose Influence:** Formative assessments often weight toward accessible cognitive levels (Remember, Understand) to build student confidence while identifying gaps. Summative assessments typically seek balanced distributions that discriminate across the full performance range, requiring substantial higher-order questions.

**Content Complexity:** Some content domains naturally emphasise particular cognitive levels. Procedural content may weight toward Apply level (demonstrate procedure execution). Conceptual content may emphasise Understand (explain relationships). Policy analysis may weight toward Evaluate (assess alternatives). Distribution should respect natural cognitive demands of content.

**Student Development Level:** Introductory courses typically emphasise foundational levels while advanced courses emphasise higher-order thinking. Distribution should match where students are in their learning progression.

### Distribution Calculation and Recommendation

The AI system generates initial distribution recommendations using a two-step process:

**Step 1: Objective-Based Default Distribution**

Calculate distribution that mirrors learning objective distribution from Stage 1:

```
Objective-Based Distribution:

Learning Objectives by Level (from Stage 1):
- Remember: [N1] objectives ([X1]%)
- Understand: [N2] objectives ([X2]%)
- Apply: [N3] objectives ([X3]%)
- Analyze: [N4] objectives ([X4]%)
- Evaluate: [N5] objectives ([X5]%)

Proportional Question Distribution:
Total questions: [Q]

- Remember: [Q × X1%] = [R] questions
- Understand: [Q × X2%] = [U] questions  
- Apply: [Q × X3%] = [A] questions
- Analyze: [Q × X4%] = [A2] questions
- Evaluate: [Q × X5%] = [E] questions

This distribution maintains alignment between objectives and questions.
```

**Step 2: Purpose-Based Adjustment Recommendations**

Adjust default distribution based on formative vs. summative purpose:

```
Purpose-Based Adjustment Recommendations:

[For Formative Assessment:]

Current distribution has [X]% at Remember/Understand and [Y]% at higher levels.

Formative recommendation: Increase accessible questions slightly
- Remember: [R + adjustment] questions ([new %])
- Understand: [U + adjustment] questions ([new %])
- Apply/Analyze/Evaluate: [adjusted] questions ([new %])

Rationale: Formative assessments benefit from more accessible questions that 
help students identify specific gaps without excessive difficulty that 
discourages practice.

[For Summative Assessment:]

Current distribution has [X]% at Remember/Understand and [Y]% at higher levels.

Summative recommendation: Ensure balanced representation across range
- Maintain current distribution if already balanced
- OR increase higher-order slightly if heavily weighted toward foundation

Rationale: Summative assessments should discriminate across performance levels, 
requiring substantial higher-order questions while maintaining foundational 
coverage.
```

### Dialogue Pattern: Distribution Negotiation

The Stage 4 dialogue presents calculations and recommendations, then invites teacher refinement based on pedagogical judgment:

```
AI System Presentation:

"Question distribution across Bloom's levels:

Alignment-based distribution (mirrors objectives):
- Remember: [R] questions ([X1]%)
- Understand: [U] questions ([X2]%)
- Apply: [A] questions ([X3]%)
- Analyze: [A2] questions ([X4]%)
- Evaluate: [E] questions ([X5]%)

[Purpose-based] recommendation: [adjustment description]
Adjusted distribution:
- Remember: [R'] questions ([X1']%)
- Understand: [U'] questions ([X2']%)
- Apply: [A'] questions ([X3']%)
- Analyze: [A2'] questions ([X4']%)
- Evaluate: [E'] questions ([X5']%)

Analysis:
- Foundational (Remember + Understand): [%]
- Higher-order (Apply + Analyze + Evaluate): [%]

This distribution [emphasises foundational / balances foundation and higher-order / 
emphasises higher-order thinking].

Does this distribution match your assessment priorities? 

Considerations:
- More foundational questions → more accessible, good for formative
- More higher-order questions → more discriminating, good for summative
- Balance depends on student readiness and course level"
```

Teachers commonly request adjustments in several patterns:

**Increase Foundation:** "Students struggle with basics. Let's increase Remember and Understand to 60% total." AI system recalculates distribution, reducing higher-order proportionally, and notes implications for discriminating advanced performance.

**Increase Higher-Order:** "This is an advanced class. Let's push Apply/Analyze/Evaluate to 70% total." AI system recalculates, reducing foundation proportionally, and notes students must have strong grasp of basics for this to work well.

**Adjust Specific Level:** "I want more Application questions specifically, not just 'higher-order' generally." AI system adjusts Apply level while maintaining relative balance among other levels.

**Validate Against Content:** "Does this distribution adequately cover [specific topic]?" AI system reviews which objectives relate to that topic and confirms appropriate question allocation, adjusting if needed.

### Distribution Validation Checks

After any distribution adjustment, the AI system validates that the distribution remains pedagogically sound:

```
Distribution Validation:

✅ All Bloom's levels present (avoid complete absence of any level)
✅ Each objective's level has sufficient questions to assess it
✅ Distribution aligns with [formative/summative] purpose
✅ Foundation adequate to assess basic understanding
✅ Higher-order adequate to discriminate performance

[If any validation fails:]
⚠️  [Description of problem]
Recommended adjustment: [specific fix]
```

Common validation failures include:

- **Insufficient foundation:** Very low Remember/Understand percentages risk assuming prerequisite knowledge not actually established
- **Insufficient higher-order:** Very low Apply/Analyze/Evaluate percentages fail to assess transfer and deep understanding
- **Orphan objectives:** Bloom's level represented in objectives but not in question distribution
- **Coverage mismatch:** Essential objectives (Tier 1) receiving fewer questions than secondary objectives (Tier 2)

### Bloom's Taxonomy Definitions Reference

For clarity during distribution planning, the AI system can present Bloom's taxonomy level definitions:

```
Bloom's Taxonomy Level Definitions:

REMEMBER: Retrieve relevant knowledge from memory
- Action verbs: Identify, list, name, recognise, recall, define
- Question examples: "What is...", "List the...", "Identify the..."
- Assessment focus: Factual knowledge, terminology, basic concepts

UNDERSTAND: Construct meaning from information
- Action verbs: Explain, describe, summarise, interpret, classify
- Question examples: "Explain why...", "What is the relationship between..."
- Assessment focus: Conceptual understanding, relationships, explanations

APPLY: Use procedures in given situations
- Action verbs: Calculate, solve, demonstrate, use, apply
- Question examples: "Calculate...", "Apply the procedure to..."
- Assessment focus: Procedural knowledge, problem-solving with familiar methods

ANALYZE: Break material into parts and determine relationships
- Action verbs: Compare, contrast, differentiate, examine, analyse
- Question examples: "Compare and contrast...", "Analyse the relationship..."
- Assessment focus: Structural analysis, pattern recognition, critical examination

EVALUATE: Make judgments based on criteria
- Action verbs: Assess, judge, critique, evaluate, justify
- Question examples: "Evaluate the effectiveness...", "Which approach is better..."
- Assessment focus: Judgment, decision-making, critical evaluation

CREATE: Put elements together to form coherent whole (rarely used in typical assessments)
- Action verbs: Design, construct, develop, create, generate
- Question examples: "Design a solution...", "Create a plan..."
- Assessment focus: Creative synthesis, original production
```

### Stage 4 Checkpoint

Stage 4 concludes with finalised Bloom's distribution that will guide question generation:

```
Bloom's Distribution: FINALISED

Question allocation by cognitive level:
- Remember: [R] questions ([X1]%)
- Understand: [U] questions ([X2]%)
- Apply: [A] questions ([X3]%)
- Analyze: [A2] questions ([X4]%)
- Evaluate: [E] questions ([X5]%)

Distribution character:
- Foundational emphasis: [X]%
- Higher-order emphasis: [Y]%
- Assessment: [Accessible / Balanced / Challenging]

Alignment validation:
✅ Distribution reflects learning objective priorities
✅ Sufficient coverage at each represented cognitive level
✅ Appropriate for [formative/summative] purpose
✅ Feasible for [student level] students

Next stage determines question type mix (selected-response, constructed-response, 
interactive formats) to implement this cognitive distribution effectively.

Proceed to Stage 5: Question Type Mix Planning?
```

---

## STAGE 4 COMPLETION CHECKPOINT

**This stage is now complete.**

### Required Action Before Proceeding

1. **STOP HERE** - Do not proceed to Stage 5 automatically
2. **Present** the Bloom's Distribution to teacher
3. **WAIT** for teacher to explicitly approve the cognitive distribution
4. **Next stage requires:** m2_5_question_type_mix (Stage 5: Question Type Mix Planning)

### Teacher Must Explicitly Confirm

The teacher must explicitly say one of the following:
- "Proceed to Stage 5"
- "Start Stage 5"
- "Continue to question type mix planning"
- "Yes, let's determine question types"

### DO NOT

- ❌ Start Stage 5 dialogue without teacher approval
- ❌ Proceed without m2_5_question_type_mix loaded
- ❌ Improvise question type recommendations
- ❌ Skip the approval checkpoint

### What Happens Next

After teacher approval, Stage 5 will determine:
- Which question format types to use (MC-Single, MC-Multiple, Text Area, etc.)
- Percentage distribution across question types
- Balance between auto-graded and manual-graded formats
- Question type appropriateness for cognitive levels

**Status:** Stage 4 complete, awaiting teacher approval to proceed to Stage 5

---

**Previous File:** m2_3_question_target (Stage 3: Question Target Determination)  
**Next File:** m2_5_question_type_mix (Stage 5: Question Type Mix Planning)  
