---
type: decision
status: superseded
created: 2026-06-24
superseded: 2026-07-07
origin: code
project: QuestionForge
relates_to: [ADR-015, ADR-016]
---

# ADR-017: Track the three repo-policy rules in `.claude/rules/`

> **Superseded** by ACDM ADR-017 (*Rule distribution — `.claude/` is dev-tooling;
> public policy lives in conventional docs*, 2026-06-24) and walked back in #33:
> the "read by repo-tooling" rationale below was wrong — the tooling that reads
> these rules is local and has them on disk regardless of git-tracking, and
> `.claude/rules/*.md` are agent instructions, not contributor-facing policy.
> `.claude/` is now wholly gitignored; the public data-protection policy lives
> in `SECURITY.md`. The text below is kept as the historical record.

## Context

`.claude/` holds Claude Code / ACDM configuration. Historically the whole
directory was git-ignored (`.claude/` in `.gitignore`) because most of it is
local, path-sensitive, or personal tooling that should not travel with a clone:
`acdm.json`, `.mcp.json`, `CLAUDE.md`, and the process rules (`acdm-workflow`,
`tdd-required`, `escalation`, `decisions`, `language-british-english`,
`pre-push-review`).

But three of the rule files are different in kind. They are not personal
configuration — they are **guardrails that describe the repository itself** and
are read by repo-tooling:

- `data-protection.md` — the non-negotiable "never commit personal data" rule.
- `internal-docs-boundary.md` — what belongs in the repo vs the project's
  internal Nextcloud documentation.
- `publish-readiness.md` — the severity rubric and scan axes that drive the
  `/publish-check` command.

## Problem

If those three rules stay git-ignored, the protections they encode exist **only
on the original author's machine**. Anyone who clones or forks the public repo
gets the code but not the rules that say "do not commit PII here", "this is the
repo boundary", or "this is what publish-readiness means". The guardrail does
not travel with the thing it guards.

This is the inverse of ADR-015's principle ("flexible project init — protection
travels with the repo"): a public repository should carry the rules that keep it
safe, not assume every contributor reconstructs them.

## Alternatives considered

1. **Keep all of `.claude/` ignored (status quo).**
   - Pro: simplest; nothing in `.claude/` is ever public by accident.
   - Con: the PII / boundary / publish guardrails do not reach a clone or fork;
     contributors work without the rules that protect the repo.

2. **Track the whole `.claude/` directory.**
   - Pro: everything travels.
   - Con: publishes personal/local config (`acdm.json` paths, `.mcp.json`,
     `CLAUDE.md`, process memos) that is path-sensitive or simply not useful to
     outsiders — and risks leaking local paths. Fails the data-protection rule's
     own "treat as if public" test.

3. **Track only the three repo-policy rules; keep the rest ignored. (chosen)**
   - Pro: the guardrails travel with the repo; nothing personal/local is
     exposed. The `.gitignore` whitelist is explicit and fails closed
     (ignore `.claude/*`, then re-include only the three named files).
   - Con: the `.gitignore` stanza is slightly more intricate; the set of
     "policy" vs "process" rules must be maintained deliberately.

## Decision

Track exactly three rule files and keep the rest of `.claude/` ignored, via an
explicit allowlist in `.gitignore`:

```gitignore
.claude/*
!.claude/rules/
.claude/rules/*
!.claude/rules/data-protection.md
!.claude/rules/internal-docs-boundary.md
!.claude/rules/publish-readiness.md
```

The three files were reviewed before tracking and contain **no personal data,
no real file paths, and no secrets** — they are generic policy text using
placeholders (`School A`, `/path/to/project`, `<Project>`). They are therefore
safe to be public, which is a precondition for tracking them at all.

A future rule only joins this set if it (a) describes the repo or is read by
repo-tooling, and (b) passes the same "safe to be public" review.

## Consequences

- A clone or fork of the public repo now carries the PII-prevention rule, the
  internal-docs boundary, and the publish-readiness rubric — the protections
  travel with the repo.
- Process rules, `acdm.json`, `.mcp.json`, and `CLAUDE.md` stay git-ignored.
- `publish-readiness.md` references lessons learned from another project's
  private→public flip by its former name; this is process "lessons learned"
  text, not personal data, and is acceptable in a public file.
- Adding a new rule to the tracked set is a deliberate act: extend the
  `.gitignore` allowlist and review the file as public-safe first.
