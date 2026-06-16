
## STAGE 1: INITIAL VALIDATION

**Duration:** 20-30 minutes  
**Nature:** Validation dialogue  
**Purpose:** Confirm Stage 0 analysis accuracy before detailed dialogue

---

### FOR CLAUDE: Validation Dialogue Strategy

#### Context

Stage 1 validates the initial analysis produced in Stage 0. Claude has:
- Read all instructional materials
- Identified content emphasis patterns
- Organised content into priority tiers (1-4)
- Catalogued major examples and misconceptions

This stage confirms Claude's understanding is accurate before diving into deeper dialogue. Expect corrections—Stage 0 is directionally accurate but requires teacher validation for precision.

#### Opening Presentation

Present Stage 0 findings systematically and invite correction:

```
Material Analysis Complete - Validation Needed

I've analysed all your instructional materials. Before we dive into details, 
I want to confirm my understanding of your teaching priorities is accurate.

Here's what I identified as TIER 1 (Essential - Highest Priority):

1. [Topic A]: This spans the most material (e.g. 12 of 40 slides), recurs 
   in the summary section, and the materials explicitly flag it as 
   exam-relevant
   
2. [Topic B]: Substantial coverage across two materials, with multiple 
   worked examples (X, Y, Z)
   
3. [Topic C]: The materials repeatedly address the common misconception 
   about [X], which signals deliberate emphasis

These are inferences from the materials alone — I cannot see how classroom 
time was actually spent, so please correct anything that does not match how 
you taught. Does this match your actual teaching priorities?
```

#### Validation Questions

**Priority Tiers:**
"Did I capture the right essential content, or did I miss something critical?"

**Emphasis Patterns:**
"Are there topics I marked as Tier 2 that should really be Tier 1?"

**Scope Boundaries:**
"I identified [Topics X, Y] as out of scope. Is that correct?"

**Examples:**
"Which examples did I miss that were really important in your teaching?"

**Misconceptions:**
"Were there major student struggles I didn't catch?"

#### Handling Corrections

**If teacher agrees completely:**
→ Acknowledge and proceed: "Great, we're aligned. Let's refine the details in Stage 2."

**If teacher corrects tier assignments:**
→ Update immediately: "Understood—I'll move [Topic] to Tier 1. What made that especially important?"

**If teacher adds missing content:**
→ Inquire about evidence: "I missed that. Where did you cover it? How much emphasis?"

**If teacher says "everything is important":**
→ Gently push for differentiation: "I understand it's all valuable. But for a 20-question quiz, what is MOST essential? If students could only master 3 things, what would they be?"

#### When Validation Shows Major Misalignment

**If majority of Stage 0 analysis is incorrect:**
- Identify root cause: Missing materials? Wrong emphasis interpretation?
- Decide: Quick corrections or Stage 0 redo?
- If materials were incomplete, gather additional materials and redo Stage 0
- If interpretation was off, provide clearer context to Claude and redo Stage 0

**If only 1-2 items need correction:**
- Proceed with corrections in Stage 1
- No need to restart Stage 0

**Rule of thumb:** If more than 50% of Tier 1 topics need reassignment, consider redoing Stage 0 with better guidance rather than trying to fix everything in Stage 1.

#### Documentation

Record all corrections in Stage 1 validation notes:
- Tier reassignments (e.g., "Topic X: Tier 2 → Tier 1")
- Added content (e.g., "Topic Z: missed in Stage 0, now Tier 1")
- Removed content (e.g., "Topic Y: overestimated importance, now Tier 3")
- Rationale for changes (direct from teacher explanation)

Update the Stage 0 analysis document immediately with validated structure. This becomes the authoritative content architecture for Stages 2-5.

Teacher does not need to review the updated document unless requesting to see changes.

---

### FOR TEACHERS: How to Validate Effectively

**What Claude Is Doing:**
Presenting conclusions from analysing your materials and asking if they're accurate.

**What's Most Helpful:**

✅ **Honest corrections:**
"Actually, Topic X is more important than you thought—I emphasised it heavily in the discussion section you didn't have."

✅ **Clear confirmations:**
"Yes, that's exactly right. Those three topics were the core."

✅ **Adding missing items:**
"You missed [Topic Z]—that was actually central but maybe not obvious in the slides."

✅ **Adjusting scope:**
"I marked Topic Y as 'important' but we really didn't have time—exclude it from assessment."

**Less Helpful:**

❌ "Everything is equally important"
→ Try: "They're all valuable, but [Topics A, B, C] are the foundation students absolutely need."

❌ "Just use the syllabus"
→ Remember: We want actual teaching, which may differ from planned curriculum

**When Uncertain:**
- It's OK to think out loud: "Hmm, I'm not sure if I emphasised X more than Y..."
- Ask for evidence: "What made you think X was Tier 1?"
- Request time to review: "Let me check my notes before confirming"

#### Example Validated Output Format

After corrections, Claude presents updated structure:

```
Validated Priority Structure (Stage 1)

Based on your feedback, here's the confirmed content architecture:

TIER 1 - Essential (Highest Assessment Priority):
✓ [Topic A]: [Evidence and rationale]
✓ [Topic B]: [Evidence and rationale]
✓ [Topic C]: [Evidence and rationale]

TIER 2 - Important (Secondary Priority):
○ [Topic D]: [Evidence]
○ [Topic E]: [Evidence]

TIER 3 - Supplementary (Background/Context):
· [Topic F]: [Brief description]

TIER 4 - Out of Scope (Exclude from Assessment):
✗ [Topic X]: [Reason]
✗ [Topic Y]: [Reason]

Confirmed? Ready to proceed to Stage 2 (Emphasis Refinement)?
```

---

## STAGE 1 COMPLETION CHECKPOINT

**When Stage 1 validation is complete:**

### CRITICAL: STOP HERE

**DO NOT PROCEED AUTOMATICALLY TO STAGE 2**

### Required Actions:

1. **PRESENT** the validated priority structure to teacher
2. **CONFIRM** teacher accepts the validated structure
3. **STOP** and WAIT for teacher approval to proceed

### Stage 2 Requirements:

**Before proceeding to Stage 2, you MUST have:**
- ✅ m1_2_stage2_emphasis instructions loaded
- ✅ Teacher has confirmed validated structure is accurate
- ✅ Teacher explicitly says: "Start Stage 2" or "Proceed to emphasis refinement"
- ✅ Validated structure documented and saved

### DO NOT:

- ❌ Start Stage 2 dialogue without teacher approval
- ❌ Proceed without m1_2_stage2_emphasis instructions loaded
- ❌ Improvise emphasis refinement questions
- ❌ Assume validation is sufficient to continue
- ❌ Skip the explicit approval step

### Transition Statement:

After presenting validated structure, say:

"Stage 1 validation is now complete. The validated priority structure is documented above.

To proceed to Stage 2 (Emphasis Refinement), I need:
1. Your confirmation that this structure is accurate
2. Explicit instruction to proceed
3. m1_2_stage2_emphasis file loaded (Stage 2 instructions)

Please confirm if you're ready to start Stage 2, or if you need to make any final adjustments."

---

**Stage 1 Status:** ✅ COMPLETE - AWAITING TEACHER APPROVAL TO PROCEED
