# M2 Stage 3: QUESTION TARGET DETERMINATION

**Stage:** 3 of 7  
**Purpose:** Determines appropriate total number of questions for the assessment

**Prerequisites:** m2_1_objective_validation (Stage 1: Learning objectives validated), m2_2_strategy_definition (Stage 2: Assessment purpose and constraints established). This stage uses objective count and time constraints from previous stages.

---

## STAGE 3: QUESTION TARGET DETERMINATION

### Purpose and Calculation Framework

Stage 3 determines the appropriate total number of questions for the assessment based on learning objectives, time constraints, and assessment purpose established in previous stages. This determination balances competing considerations: sufficient questions to reliably assess each learning objective, feasible question counts given time constraints, and appropriate scope for assessment purpose.

### Coverage-Based Minimum Calculation

The foundation for question target calculation derives from the principle that each learning objective requires multiple questions to reliably assess student achievement. Single-question assessment of an objective provides insufficient evidence to distinguish between genuine understanding and fortunate guessing or narrow memorisation.

Assessment design literature suggests minimum ranges for objective coverage:

- **2 questions per objective:** Minimal coverage suitable only for low-stakes formative assessment
- **3-4 questions per objective:** Adequate coverage for most formative assessments
- **4-6 questions per objective:** Robust coverage appropriate for summative assessments
- **6+ questions per objective:** Extensive coverage for high-stakes summative assessments

The AI system calculates coverage-based targets using these ranges:

```
Coverage-Based Question Target Calculation:

Learning objectives: [N] total

Minimum coverage (2 questions/objective):
[N objectives] × 2 = [minimum total] questions

Adequate coverage (3-4 questions/objective):  
[N objectives] × 3.5 (average) = [adequate total] questions

Robust coverage (4-6 questions/objective):
[N objectives] × 5 (average) = [robust total] questions

Recommendation based on [formative/summative] purpose:
[adequate/robust] coverage = approximately [X] questions
```

This calculation provides the starting point for discussion, not a mandate. Teachers may adjust based on time constraints and other factors.

### Time-Based Constraint Validation

Simultaneously with coverage calculations, the AI system validates time feasibility using general timing guidelines for question types:

**Selected-Response Formats:**
- Multiple choice (single answer): 45-60 seconds per question
- Multiple choice (multiple answers): 60-90 seconds per question  
- True/False: 30-45 seconds per question
- Matching: 60-120 seconds per question set

**Constructed-Response Formats:**
- Fill-in-blank (auto-graded): 30-60 seconds per question
- Text area (short answer): 3-5 minutes per question
- Extended text (essay): 15-30 minutes per question

**Interactive Formats:**
- Inline choice: 45-90 seconds per question
- Gap match: 90-180 seconds per question
- Hotspot: 60-120 seconds per question

The AI system uses weighted average timing based on anticipated question type distribution:

```
Time-Based Feasibility Check:

Available time: [X] minutes

Assuming question type distribution:
- [Y]% selected-response (avg 60 seconds) = [Y% × total] questions × 1 minute
- [Z]% constructed-response (avg 4 minutes) = [Z% × total] questions × 4 minutes

Implied maximum questions given time:
If primarily selected-response: [X minutes ÷ 1 min] = approximately [N] questions
If balanced mix: [X minutes ÷ 2 min] = approximately [N] questions  
If primarily constructed-response: [X minutes ÷ 4 min] = approximately [N] questions

Coverage-based target of [C] questions appears [feasible / ambitious / infeasible] 
given [X] minutes available.
```

When coverage-based targets exceed time constraints, the AI system presents options: reduce question count below optimal coverage, extend assessment time, or split into multiple assessment sessions.

### Dialogue Pattern: Target Negotiation

Stage 3 dialogue negotiates between pedagogical ideals (adequate coverage) and practical constraints (available time):

```
AI System Recommendation:

"Based on [N] learning objectives, I recommend [X] questions to provide 
[adequate/robust] coverage:

Coverage analysis:
- [N] objectives × [3-4 / 4-6] questions = [X] total
- This provides multiple measurements per objective for [reliable/very reliable] 
  assessment

Time feasibility:
- [X] questions using [expected question type mix]
- Estimated completion time: [Y] minutes
- Available time: [Z] minutes
- Assessment: [Feasible / Ambitious / Requires adjustment]

[If time insufficient:]
Options to consider:
1. Reduce to [lower N] questions (minimum 2 per objective)
2. Extend assessment time to [higher Z] minutes
3. Split into multiple assessment sessions
4. Emphasise faster question types (selected-response)

[If time sufficient:]
This scope should comfortably fit within available time with buffer for 
students who work more slowly.

What question target works for your context?"
```

Teachers typically respond in one of several patterns:

**Accept Recommendation:** "Let's go with [X] questions as recommended." Process proceeds using recommended target.

**Adjust for Time:** "We only have [Z] minutes, so let's reduce to [lower N] questions." AI system recalculates coverage per objective and notes which objectives will receive minimum coverage.

**Increase for Thoroughness:** "I want more robust assessment. Let's increase to [higher N] questions." AI system validates time feasibility and notes increased coverage reliability.

**Request Distribution First:** "Before deciding total, can we discuss how questions would distribute across cognitive levels?" Process loops to show anticipated distribution, then returns to target discussion.

### Uneven Objective Distribution Consideration

Not all learning objectives require equal question allocation. Stage 3 addresses whether to distribute questions evenly or weight certain objectives more heavily:

```
Question Distribution Options:

EVEN distribution:
[N] questions ÷ [M] objectives = [N/M] questions per objective
Every objective receives equal coverage regardless of importance

WEIGHTED distribution:
Core objectives receive more questions than secondary objectives
Example distribution:
- Tier 1 objectives (essential): 60% of questions
- Tier 2 objectives (important): 40% of questions

Which approach fits your priorities?
```

Most teachers choose weighted distribution aligned with content tiers from M1, ensuring essential content receives proportionally more assessment attention than enrichment content.

**Example Weighted Distribution Calculation:**

Total: 20 questions across 5 learning objectives (3 Tier 1 essential, 2 Tier 2 important)

*Weighted approach:*
- Tier 1 (essential): 60% × 20 = 12 questions ÷ 3 objectives = 4 questions per Tier 1 objective
- Tier 2 (important): 40% × 20 = 8 questions ÷ 2 objectives = 4 questions per Tier 2 objective

*Even approach for comparison:*
- All tiers: 20 questions ÷ 5 objectives = 4 questions per objective

In this example, even distribution yields same per-objective count due to the numbers, but with different totals (e.g., 25 questions, 4 Tier 1, 3 Tier 2), weighted ensures Tier 1 receives 15 questions (60%) versus Tier 2's 10 questions (40%), better reflecting content priorities.

### Stage 3 Checkpoint

Stage 3 concludes with agreed-upon question target and distribution approach:

```
Question Target: ESTABLISHED

Total questions: [N]

Rationale:
- Provides [X] questions per objective (average)
- Estimated time: [Y] minutes (fits within [Z] minutes available)
- [Even / Weighted] distribution across objectives

Coverage adequacy: [Minimum / Adequate / Robust]

Next stage will determine how these [N] questions distribute across:
- Bloom's cognitive levels (Remember through Evaluate)
- Question types (MC-Single, MC-Multiple, etc.)
- Difficulty levels (Easy, Medium, Hard)

Proceed to Stage 4: Bloom's Distribution Planning?
```

---

## STAGE 3 COMPLETION CHECKPOINT

**This stage is now complete.**

### Required Action Before Proceeding

1. **STOP HERE** - Do not proceed to Stage 4 automatically
2. **Present** the Question Target determination to teacher
3. **WAIT** for teacher to explicitly approve the question count
4. **Next stage requires:** m2_4_blooms_distribution (Stage 4: Bloom's Distribution Planning)

### Teacher Must Explicitly Confirm

The teacher must explicitly say one of the following:
- "Proceed to Stage 4"
- "Start Stage 4"
- "Continue to Bloom's distribution planning"
- "Yes, let's move to the next stage"

### DO NOT

- ❌ Start Stage 4 dialogue without teacher approval
- ❌ Proceed without m2_4_blooms_distribution loaded
- ❌ Improvise Bloom's distribution recommendations
- ❌ Skip the approval checkpoint

### What Happens Next

After teacher approval, Stage 4 will determine:
- How questions distribute across Bloom's cognitive levels
- Percentage allocation to Remember, Understand, Apply, Analyze, Evaluate
- Cognitive emphasis appropriate for assessment purpose
- Validation that distribution aligns with learning objectives

**Status:** Stage 3 complete, awaiting teacher approval to proceed to Stage 4

---

**Previous File:** m2_2_strategy_definition (Stage 2: Assessment Strategy Definition)  
**Next File:** m2_4_blooms_distribution (Stage 4: Bloom's Distribution Planning)  
