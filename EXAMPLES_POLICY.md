# Examples Policy

**All example, illustrative and test data in this repository is fabricated —
with one deliberate exception: course codes are real.**

QuestionForge works with a teacher's real course material in their own
workspace, but **none of that material is ever committed here**. Every name,
question, answer, transcript snippet, file path and student identifier that
appears anywhere in this repository as an *example* is invented for
documentation or testing. No real student, teacher, colleague or school is
represented.

This policy exists so the question *"are these examples real?"* has a single,
documented answer: **no — except the course codes, which are real on purpose.**

## The one exception: course codes are real

Course codes such as `BIOG200x` are **genuine** and kept that way deliberately.
QuestionForge has to detect and read material inside a teacher's real course
folder structure (a course vault keyed by its real course code), so the test
fixtures and examples use real course codes rather than placeholders — otherwise
the tests would not exercise the behaviour they exist to verify.

A course code is **not personal data**: it identifies a course offering, not a
person. An edusafe scan that flags `BIOG200x` (or the `course_code` shape) is a
false positive — it is expected to be present and is safe to accept.

Everything *else* — including anything that could identify a person — is
fabricated.

## Scope

This applies to all illustrative and sample content, including:

- Code and tool examples in `README.md`, `CLAUDE.md`, and `docs/`
- Illustrative snippets inside the methodology documents (`methodology/`)
- Test fixtures and sample inputs under `packages/*/tests/` and
  `packages/*/src/**/__tests__/`

It does **not** apply to genuine project metadata that is meant to be real:
authorship in git history, licence text, dependency lists, real course codes
(see above), and similar.

## What "fabricated" means

- **People** are referred to generically or not at all — never by a real name.
  Tokens such as `res`, `mats`, `win` or `cid` that appear in the code are
  variable names, not people.
- **Student identifiers and logins** (e.g. `lesson3`, `set1`, `course1`) are
  invented test labels, never a real student's ID.
- **Questions, answers and transcript content** are written to be realistic but
  are entirely invented; they describe no real student work or classroom event.
- **File paths** in examples use generic placeholders, never a real user-home
  path.
- **IP addresses and similar literals** in the security tests (`127.0.0.1`,
  `169.254.169.254`, `8.8.8.8`, …) are well-known fixtures used to verify that
  the URL fetcher blocks private/internal addresses — not real infrastructure.

These conventions follow the repository's data-protection and
internal-docs-boundary rules.

## For contributors

- When adding or editing fixtures, examples or illustrative snippets, use **only
  fabricated data** for anything that could identify a person — never paste from
  a real workspace, transcript, or set of student answers.
- **Real course codes are allowed and expected** in fixtures; everything else
  must be invented.
- Never commit anything synced from Nextcloud, Dropbox, OneDrive or another
  external store.

If you are ever unsure whether a piece of sample data is safe to commit, treat
it as real and leave it out.
