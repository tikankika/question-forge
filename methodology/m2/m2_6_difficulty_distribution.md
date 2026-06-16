# M2 Stage 6: DIFFICULTY DISTRIBUTION PLANNING

**Stage:** 6 of 7  
**Purpose:** Determines how questions distribute across difficulty levels

---

## STAGE 6: DIFFICULTY DISTRIBUTION PLANNING

### Purpose and Difficulty Conceptualisation

Stage 6 determines how questions distribute across difficulty levels (typically Easy, Medium, Hard). Difficulty decisions influence assessment accessibility, discriminatory power (ability to distinguish performance levels), and student experience. This stage integrates difficulty considerations with previously established cognitive levels and question types to create comprehensive specifications for each question.

Difficulty operates as a distinct dimension from cognitive level. A Remember-level question asking students to recall a rarely mentioned term may be quite difficult due to unfamiliarity, while an Analyze-level question asking students to compare concepts thoroughly discussed in class may be relatively accessible due to extensive prior engagement. Difficulty reflects multiple factors: concept familiarity, contextual complexity, time pressure, required integration of multiple elements, and cognitive load.

### Difficulty Framework and Definitions

The AI system presents standardised difficulty definitions that maintain consistency across questions:

```
Difficulty Level Definitions:

EASY:
- Assesses well-practised content
- Uses familiar contexts and examples
- Requires single-step reasoning
- Correct answer clearly distinguishable from distractors
- Minimal cognitive load
- Expected success rate: 70-90%

MEDIUM:
- Assesses content requiring integration
- Uses contexts similar to instruction but not identical
- Requires two-step reasoning or simple integration
- Distractors require discrimination but reasonable
- Moderate cognitive load
- Expected success rate: 40-70%

HARD:
- Assesses content requiring synthesis or transfer
- Uses novel contexts requiring adaptation of concepts
- Requires multi-step reasoning or complex integration
- Distractors closely resemble correct answer
- High cognitive load
- Expected success rate: 20-40%

These definitions combine content familiarity, contextual complexity, and 
reasoning demands.
```

### Distribution Patterns by Assessment Purpose

Difficulty distribution varies substantially based on formative vs. summative purpose established in Stage 2:

**Formative Assessment Distribution:**

```
Recommended Difficulty Distribution for Formative Assessment:

EASY: 40-50% of questions
MEDIUM: 35-45% of questions
HARD: 10-20% of questions

Rationale:
Formative assessments serve learning rather than evaluation. Higher proportion 
of accessible questions helps students:
- Build confidence through initial success
- Identify specific gaps (not feel overwhelmed)
- Progress from accessible to challenging
- Maintain engagement rather than become discouraged

Hard questions remain important to challenge advanced students and preview 
summative expectations, but dominating with difficulty discourages practice.

Example distribution for 40 questions:
- 18 Easy (45%)
- 16 Medium (40%)
- 6 Hard (15%)
```

**Summative Assessment Distribution:**

```
Recommended Difficulty Distribution for Summative Assessment:

EASY: 20-30% of questions
MEDIUM: 45-55% of questions
HARD: 20-30% of questions

Rationale:
Summative assessments measure achievement across performance range. Balanced 
distribution helps assessment:
- Discriminate among performance levels effectively
- Avoid floor effects (everyone fails) or ceiling effects (everyone succeeds)
- Maintain validity by ensuring adequate challenge
- Represent full scope of learning expectations

Easy questions establish baseline and prevent complete failure. Medium questions 
differentiate most students. Hard questions identify exceptional performance.

Example distribution for 40 questions:
- 10 Easy (25%)
- 22 Medium (55%)
- 8 Hard (20%)
```

### Cognitive Level and Difficulty Interaction

Difficulty interacts with cognitive level in complex ways. Stage 6 integrates these dimensions:

```
Cognitive Level × Difficulty Integration:

REMEMBER level can vary in difficulty:
- Easy: Recall frequently emphasised term
- Medium: Recall term mentioned but not emphasised
- Hard: Recall term mentioned once in complex context

UNDERSTAND level can vary in difficulty:
- Easy: Explain concept thoroughly discussed
- Medium: Explain relationship between concepts
- Hard: Explain concept in novel context requiring adaptation

APPLY level can vary in difficulty:
- Easy: Apply procedure to standard problem
- Medium: Apply procedure to problem with minor variation
- Hard: Adapt procedure to novel problem type

ANALYZE level can vary in difficulty:
- Easy: Compare two concepts directly discussed together
- Medium: Compare concepts discussed separately requiring connection
- Hard: Analyze relationships among multiple concepts requiring synthesis

EVALUATE level can vary in difficulty:
- Easy: Evaluate alternatives using provided criteria
- Medium: Evaluate alternatives developing appropriate criteria
- Hard: Evaluate in complex scenario requiring nuanced judgment

Each cognitive level spans full difficulty range. Stage 6 planning ensures 
appropriate difficulty variety within each level.
```

### Dialogue Pattern: Distribution Negotiation

The Stage 6 dialogue presents recommended difficulty distribution based on assessment purpose, then facilitates teacher adjustment:

```
AI System Recommendation:

"Difficulty distribution for [N] questions:

Based on [formative/summative] purpose, I recommend:

EASY: [N1] questions ([X1]%)
MEDIUM: [N2] questions ([X2]%)
HARD: [N3] questions ([X3]%)

Distribution by cognitive level:

REMEMBER ([R] questions):
- Easy: [Re] questions
- Medium: [Rm] questions  
- Hard: [Rh] questions

UNDERSTAND ([U] questions):
- Easy: [Ue] questions
- Medium: [Um] questions
- Hard: [Uh] questions

APPLY ([A] questions):
- Easy: [Ae] questions
- Medium: [Am] questions
- Hard: [Ah] questions

ANALYZE ([A2] questions):
- Easy: [A2e] questions
- Medium: [A2m] questions
- Hard: [A2h] questions

EVALUATE ([E] questions):
- Easy: [Ee] questions
- Medium: [Em] questions
- Hard: [Eh] questions

This distribution [builds confidence / discriminates performance / balances 
accessibility and challenge] appropriate for [formative/summative] purpose.

Expected performance:
- Most students succeed on Easy questions (70-90% correct)
- Students differentiate on Medium questions (40-70% correct)
- Advanced students distinguish themselves on Hard questions (20-40% correct)

Does this difficulty profile match your assessment goals?

Considerations:
- More Easy → more accessible, less discriminating
- More Hard → more challenging, risks discouragement
- Balanced → serves diverse student performance levels"
```

Teachers typically adjust difficulty distribution in several patterns:

**Increase Accessibility:** "Students struggle with this material. Let's increase Easy to 50% and reduce Hard." AI system recalculates, noting improved confidence-building but reduced discrimination among advanced students.

**Increase Challenge:** "This is an honors section. Let's increase Hard to 35% and reduce Easy." AI system recalculates, noting improved discrimination but potential discouragement for struggling students.

**Balance Within Cognitive Level:** "I want easier questions at Remember level specifically." AI system adjusts Remember-level difficulty distribution while maintaining overall targets, explaining rationale.

**Question Grade Weighting:** "Should Hard questions be worth more points?" AI system presents options for uniform vs. weighted point schemes, discussing implications for student strategy and grade distribution.

### Difficulty Assignment Strategy

After finalising overall distribution, Stage 6 addresses how difficulty levels assign to specific questions:

```
Difficulty Assignment Approaches:

DISTRIBUTED Approach:
Each cognitive level receives proportional difficulty distribution
- Every level has some Easy, Medium, Hard questions
- Maintains variety within each level
- Recommended for most assessments

Example for Remember level (10 questions):
- 4 Easy (40%)
- 4 Medium (40%)
- 2 Hard (20%)

PROGRESSIVE Approach:
Lower cognitive levels emphasise easier difficulty
Higher cognitive levels emphasise harder difficulty
- Aligns cognitive and difficulty progression
- Creates natural scaffolding
- Recommended when cognitive levels build sequentially

Example progression:
- Remember: 60% Easy, 30% Medium, 10% Hard
- Understand: 50% Easy, 40% Medium, 10% Hard
- Apply: 30% Easy, 50% Medium, 20% Hard
- Analyze: 20% Easy, 40% Medium, 40% Hard
- Evaluate: 10% Easy, 30% Medium, 60% Hard

Which approach better fits your assessment design?
```

Most teachers select distributed approach for balanced assessments, progressive approach when cognitive levels represent clear skill progression.

### Point Allocation Considerations

Stage 6 also addresses whether difficulty should influence point values:

```
Point Allocation Options:

UNIFORM Points (All questions worth same value):
Advantages:
- Simple and transparent
- Encourages attempting all questions
- Prevents strategic point hunting

Disadvantages:
- Hard questions have same value as Easy questions
- May not reflect cognitive effort required

WEIGHTED Points (Hard questions worth more):
Example weighting:
- Easy questions: 1 point each
- Medium questions: 2 points each
- Hard questions: 3 points each

Advantages:
- Rewards higher cognitive effort
- Discriminates performance more clearly

Disadvantages:
- More complex grading
- May discourage attempts at hard questions
- Can disadvantage struggling students

Recommendation: Uniform points for formative, weighted points optional for 
summative.
```

### Stage 6 Checkpoint

Stage 6 concludes with comprehensive difficulty specifications integrated with previous distributions:

```
Difficulty Distribution: FINALISED

Overall difficulty profile for [N] questions:
- Easy: [N1] questions ([X1]%)
- Medium: [N2] questions ([X2]%)
- Hard: [N3] questions ([X3]%)

Distribution by cognitive level:
[Table showing breakdown of each cognitive level by difficulty]

Assignment approach: [Distributed / Progressive]

Point allocation: [Uniform / Weighted]
[If weighted, specify point values per difficulty level]

Expected performance characteristics:
- Accessibility: [High/Moderate/Low] (based on Easy %)
- Discrimination: [High/Moderate/Low] (based on Medium/Hard balance)
- Challenge level: [Accessible/Balanced/Demanding]

Validation:
✅ Difficulty distribution appropriate for [formative/summative] purpose
✅ Adequate variety within each cognitive level
✅ Expected performance patterns align with assessment goals
✅ Point allocation approach determined

All distribution dimensions now specified:
✅ Question count: [N] questions
✅ Cognitive distribution: Remember through Evaluate
✅ Question type mix: Selected/Constructed/Interactive
✅ Difficulty distribution: Easy/Medium/Hard

Ready to synthesise into comprehensive Assessment Blueprint in Stage 7.

Proceed to Stage 7: Blueprint Construction?
```

---

## STAGE 6 COMPLETION CHECKPOINT

**This stage is now complete.**

### Required Action Before Proceeding

1. **STOP HERE** - Do not proceed to Stage 7 automatically
2. **Present** the Difficulty Distribution to teacher
3. **WAIT** for teacher to explicitly approve the difficulty profile
4. **Next stage requires:** m2_7_blueprint_construction (Stage 7: Blueprint Construction and Validation)

### Teacher Must Explicitly Confirm

The teacher must explicitly say one of the following:
- "Proceed to Stage 7"
- "Start Stage 7"
- "Continue to blueprint construction"
- "Yes, let's create the blueprint"

### DO NOT

- ❌ Start Stage 7 dialogue without teacher approval
- ❌ Proceed without m2_7_blueprint_construction loaded
- ❌ Improvise blueprint structure
- ❌ Skip the approval checkpoint

### What Happens Next

After teacher approval, Stage 7 will:
- Synthesise all decisions from Stages 1-6 into comprehensive blueprint
- Create Question Specification Table with complete details
- Run systematic validation checks (performed by the AI system in dialogue — not executed code)
- Present complete blueprint for final approval
- Prepare transition to M3 (Question Generation)

**Status:** Stage 6 complete, awaiting teacher approval to proceed to Stage 7

---

**Previous File:** m2_5_question_type_mix (Stage 5: Question Type Mix Planning)  
**Next File:** m2_7_blueprint_construction (Stage 7: Blueprint Construction and Validation)  
