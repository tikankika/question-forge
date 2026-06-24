---
paths:
  - "**/*"
---

# Publish Readiness — Pre-publish checklist

This rule defines what makes a repository ready to flip from private to public. Used by the `/publish-check` slash-command.

## Severity rubric

### Blocker — MUST fix before public

A finding that, if left in, exposes personal data, breaks user trust, or makes the repository misleading. Public-flip is unsafe until resolved.

Examples:
- Personal names, hardcoded user-home paths, e-mail addresses
- README claims that contradict source code (false advertising)

### Warning — SHOULD fix before public

A finding that signals carelessness or inconsistency to public readers. Public-flip is possible but degrades reception.

Examples:
- British-English drift in user-facing prose
- Missing community files referenced from README
- Outdated supported-versions in `SECURITY.md`

### Nice-to-have — MAY add or improve

A finding that, if added, increases professionalism but is not expected by readers.

Examples:
- `CODE_OF_CONDUCT.md`
- `.github/dependabot.yml`
- Issue / pull-request templates

## Scan axes

The `/publish-check` command runs five scans:

1. **data-protection** — sources truth from `data-protection.md` rule (user-home paths, personal names, e-mail addresses)
2. **language** — sources truth from `language-british-english.md` rule (American-English drift in prose)
3. **docs-freshness** — `README`, `ROADMAP`, `SECURITY` versions and counts vs the source (`package.json`, `src/`)
4. **release-hygiene** — community files exist and are current
5. **readme-sections** — README carries the golden-standard mandatory sections (see "README golden standard" below); sources truth from `readme_check.py`

## README golden standard

Every project README must clear one bar: **a newcomer understands what the project is
within the first ~15 lines** — the situation in plain language, before any architecture,
philosophy or jargon, defining terms the first time they are used. Complete structure is
not enough; comprehension is the test.

The canonical template lives in ACDM at `templates/README.template.md`. It is a *reference*,
**not** seeded into projects (per ADR-016 + the doc-model: `templates/` is a repo-side
artifact ACDM owns; `init_project` distributes enforcement, not content scaffold). Copy its
structure when writing or revising a README.

**Mandatory sections** (enforced by Scan 5 / `readme_check.py`):

- **What is `<Project>`?** — the plain-language on-ramp.
- **Development status** (or **Status and maturity**) — honest maturity; early publication
  is fine, overclaiming is not.
- **Data & privacy** — mandatory *only* when the tool touches personal data (human
  judgement; deliberately not auto-checked).

Recommended (not auto-enforced): ecosystem block (if part of a family), "who is this for?"
doors, how it works, Documentation, Requirements, Licence, Support, Acknowledgements. See
the template for the full shape and per-section guidance.

## Out of scope (v1)

- Auto-fix (report-only)
- Continuous-integration enforcement
- Pre-commit hook integration
- Security review (`/security-review` — separate skill)
- Code-quality review (`/simplify` — separate skill)
- README *quality* / textual review — does the prose actually communicate? (manual pass, or the `doc-reviewer` agent; Scan 5 checks section *presence*, not quality)
- INSTALL / LICENSE textual review (manual pass required)
- Version-bump decisions (project-internal)

These are documented as v2 promotions or out-of-tool concerns.

## Consuming the report safely

When `/publish-check` produces findings and you start fixing them:

1. **Verify the working tree is clean first** — `git status` shows no untracked or modified files you didn't expect. After `init_project(update=True)` the disk holds new files not yet visible to git.
2. **Stage explicit per finding** — `git add <file>`, not `git add -A`. The `-A` form picks up unrelated upstream drift.
3. **Verify the diff per file before commit** — `git diff --staged <file>`.
4. **Be extra careful immediately after `init_project --update`** — distributed templates may overwrite earlier per-project fixes; the report you ran against may not reflect the disk state.

Context: Teacher_MCP PR #61 (2026-05-05) used `git add -A` against undetected upstream drift and introduced 2 new BE-drift findings while fixing 9. Explicit staging would have prevented this.

## Building the public artifact (fresh-repo flips)

When the flip strategy is a fresh repository (no carried-over git history), the published repo is *built* from the working tree through an include/exclude step. Three principles keep that build trustworthy:

1. **Verify the built artifact, not the working tree.** A scan against the source tree never tests the include/exclude list itself — a file the list fails to exclude still sits in the tree the scan passed. Build the fresh repo into a staging location, then run the publish scans against *that*, before publishing. The artifact is what readers get; the artifact is what you verify. (This is distinct from "verify the working tree is clean" above: that guards the fixing step; this guards the published output.)
2. **Allowlist what ships; do not denylist what doesn't.** Start the fresh repo from empty and copy in only named paths. A denylist (copy everything, minus exclusions) fails open — anything you forget to list is published. An allowlist fails closed.
3. **Run the gate as a reproducible script against a committed checkpoint.** A single ad-hoc grep pass is not a gate — globs and mounts misfire silently. Commit the prep work to the still-private branch first, so there is an auditable diff and a stable state to build from, then run the scan as a script the human can re-run.

A token grep (names, course codes) finds known strings; it cannot find sensitive content that lacks them (personal reflections, opinions about colleagues, self-flagged private documents). Where shipping files carry a privacy field in front-matter (e.g. `privacy: private`), treat that field — not a name grep — as the primary ship / no-ship filter.

Context: the Teacher_MCP private→public flip (2026-05-27) scanned the working tree before the fresh-repo build, leaving the include/exclude list unverified; an independent grep pass misfired (wrong glob, slow mount) before being corrected; and a self-flagged `privacy: private` document was caught only by chance through a name grep.
