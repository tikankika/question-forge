# QFMD Format Reference

> **WARNING:** This is a "second source of truth".
> The real source of truth is `packages/qti-core/src/parser/markdown_parser.py`,
> with canonical worked examples for every type in
> `packages/qti-core/tests/fixtures/v65/`. When the parser changes, update this
> reference to match.
>
> **Coverage:** this reference currently documents 4 of the supported question
> types (`text_entry_numeric`, `text_entry_math`, `multiple_choice_single`,
> `multiple_response`) plus the mathematics guidance. For all other supported
> types, use the fixtures above as templates — they are validated against the
> parser.

---

## Basic structure

```markdown
# Q001A [Title]
^question Q001A
^type [question type]
^identifier [COURSE_CODE]_[NNN]
^title [Title]
^points [number]
^labels #label1 #label2

@field: question_text
[Question text here]
@end_field

[Type-specific fields - see below]

@field: feedback

@@field: incorrect_feedback
[Feedback for incorrect answers]
@@end_field

@end_field
```

### Critical rules

| Rule | Correct | Wrong |
|------|---------|-------|
| Question ID | `# Q001A` (UPPERCASE) | `# Q001a` (lowercase) |
| Metadata | `^type value` | `^type: value` (no colon!) |
| Field | `@field: name` | `@field name` (colon required) |
| Nested field | `@@field: name` | `@field: name` (double-@) |

---

## ⚠️ Mathematics in Inspera

### Answer fields (work automatically)
For `text_entry_math` the QTI generator creates `inspera:type="math"`, which gives the student a maths editor.

### Question text (limitation)
**NOTE:** LaTeX in the question text (`\(...\)` or `$...$`) is **NOT rendered automatically** in Inspera after QTI import.

**Solution:** Write simple mathematics using Unicode characters:

| Instead of LaTeX | Write |
|------------------|-------|
| `\(4x^2\)` | `4x²` |
| `\(x \cdot y\)` | `x · y` or `x * y` |
| `\(\frac{1}{2}\)` | `1/2` or `½` |
| `\(\sqrt{x}\)` | `√x` |
| `\(\pm\)` | `±` |

### Common Unicode characters to copy

```
Exponents:   ⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹ ⁿ
Subscripts:  ₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉
Operators:   · × ÷ ± ∓ √ ∛ ∑ ∏ ∫
Relations:   ≤ ≥ ≠ ≈ ∝ ∞
Arrows:      → ← ↔ ⇒ ⇐ ⇔
Greek:       α β γ δ ε θ λ μ π σ ω
```

### Example

Example 1:

```markdown
@field: question_text
Calculate 5(2 + 2 · 4) = {{blank_1}}
@end_field
```

Example 2:

```markdown
@field: question_text
Solve the equation: 2x + 6 = 16, x = {{blank_1}}
@end_field
```

### Complex mathematics?
If you need complex formulae (fractions, roots, etc.):
1. Export to QTI
2. Open the question in Inspera
3. Use the Math Editor (the Σ button) to add formulae manually

---

## text_entry_numeric

For questions with **numeric answers** (integers, decimals).

```markdown
# Q001A [Title]
^question Q001A
^type text_entry_numeric
^identifier [COURSE_CODE]_001
^title [Title]
^points 1
^labels #subject #bloom_apply #difficulty_easy

@field: question_text
Calculate 10 + 2 · 5 = {{blank_1}}
@end_field

@field: blanks

@@field: blank_1
^Correct_Answers
- 20
- 20.0
^Tolerance 0.1
^Input_type numeric
@@end_field

@end_field

@field: feedback

@@field: incorrect_feedback
Remember: multiplication before addition.
@@end_field

@end_field
```

### Required fields

| Field | Description |
|-------|-------------|
| `question_text` | Must contain `{{blank_1}}` |
| `blanks` | Container for blank definitions |
| `blank_1` | With a `^Correct_Answers` list |

### Optional fields in a blank

| Field | Description |
|-------|-------------|
| `^Tolerance` | Tolerance for numeric answers (e.g. `0.1`) |
| `^Input_type` | `numeric` |

---

## text_entry_math

For questions with **mathematical expressions** as answers (algebra, equations).

```markdown
# Q001A [Title]
^question Q001A
^type text_entry_math
^identifier [COURSE_CODE]_001
^title [Title]
^points 1
^labels #subject #bloom_apply #difficulty_medium

@field: question_text
Solve the equation: 2x + 6 = 16

x = {{blank_1}}
@end_field

@field: blanks

@@field: blank_1
^Correct_Answers
- 5
- x=5
- x = 5
^Input_type math
@@end_field

@end_field

@field: feedback

@@field: incorrect_feedback
Subtract 6 from both sides, then divide by 2.
@@end_field

@end_field
```

### Required fields

| Field | Description |
|-------|-------------|
| `question_text` | Must contain `{{blank_1}}` |
| `blanks` | Container for blank definitions |
| `blank_1` | With a `^Correct_Answers` list |

### Tips for Correct_Answers

Include several accepted formats:
```markdown
^Correct_Answers
- 14x + 2y
- 14x+2y
- 2y + 14x
- 2y+14x
```

---

## multiple_choice_single

For multiple-choice questions with **one correct answer**.

```markdown
# Q001A [Title]
^question Q001A
^type multiple_choice_single
^identifier [COURSE_CODE]_001
^title [Title]
^points 1
^labels #subject #bloom_understand

@field: question_text
Which planet is closest to the Sun?
@end_field

@field: options
^Shuffle Yes
A. Venus
B. Mercury
C. Mars
D. Earth
@end_field

@field: answer
B
@end_field

@field: feedback

@@field: correct_feedback
Correct! Mercury is closest to the Sun.
@@end_field

@@field: incorrect_feedback
Incorrect. Mercury is the planet closest to the Sun.
@@end_field

@end_field
```

### Required fields

| Field | Description |
|-------|-------------|
| `question_text` | The question text |
| `options` | The options, one per line (`A. Text`), without any correctness marker |
| `answer` | The letter of the correct option (e.g. `B`) in its own field block |

### Options format

- Each option on its own line
- Format: `A. Text` or `A) Text`
- Do **not** mark the correct answer inside the options — the parser treats any
  marker as literal option text. The correct answer is declared in the separate
  `@field: answer` block.
- `^Shuffle Yes` to shuffle the options

---

## multiple_response

For multiple-choice questions with **several correct answers**.

```markdown
# Q001A [Title]
^question Q001A
^type multiple_response
^identifier [COURSE_CODE]_001
^title [Title]
^points 2
^labels #subject #bloom_analyze

@field: question_text
Which of the following are prime numbers? (Select all that apply)
@end_field

@field: options
^Shuffle Yes
A. 2
B. 3
C. 4
D. 5
E. 6
@end_field

@field: correct_answers
A, B, D
@end_field

@field: scoring
^Type PartialCredit
^Correct_selections A, B, D (1 point each)
^Incorrect_selections C, E (-0.5 points each)
^Points_minimum 0
@end_field

@field: feedback

@@field: correct_feedback
Correct! 2, 3 and 5 are prime numbers.
@@end_field

@@field: incorrect_feedback
A prime number is divisible only by 1 and itself.
@@end_field

@@field: partial_feedback
Partially correct. Check each option again.
@@end_field

@end_field
```

### Required fields

| Field | Description |
|-------|-------------|
| `question_text` | The question text |
| `options` | The options, one per line, without any correctness marker |
| `correct_answers` | Comma-separated letters of all correct options (e.g. `A, B, D`) |

### Optional fields

| Field | Description |
|-------|-------------|
| `scoring` | Partial-credit rules (`^Type PartialCredit`, per-selection points, `^Points_minimum`) |

---

## Feedback structure

All question types can have feedback:

```markdown
@field: feedback

@@field: general_feedback
Always shown after answering.
@@end_field

@@field: correct_feedback
Shown for a correct answer.
@@end_field

@@field: incorrect_feedback
Shown for an incorrect answer.
@@end_field

@@field: partial_feedback
Shown for a partially correct answer (multiple_response).
@@end_field

@end_field
```

---

## Labels/Tags

Format: `#tag` (with hash)

```markdown
^labels #COURSE_CODE #bloom_apply #difficulty_medium #subject
```

### Common Bloom levels
- `#bloom_remember`
- `#bloom_understand`
- `#bloom_apply`
- `#bloom_analyze`
- `#bloom_evaluate`
- `#bloom_create`

### Common difficulty levels
- `#difficulty_easy`
- `#difficulty_medium`
- `#difficulty_hard`

---

## Checklist before step2

- [ ] Question ID is UPPERCASE: `# Q001A`, not `# Q001a`
- [ ] No colon after `^type`: `^type text_entry_numeric`
- [ ] text_entry has `{{blank_1}}` in question_text
- [ ] text_entry has `@field: blanks` with `@@field: blank_1`
- [ ] `^Correct_Answers` has at least one answer
- [ ] All `@field:` have a matching `@end_field`
- [ ] All `@@field:` have a matching `@@end_field`
