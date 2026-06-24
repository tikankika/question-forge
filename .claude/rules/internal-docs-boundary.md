---
paths:
  - "**/*"
---

# Internal Documentation Boundary

## These belong in the repo (public):
- Source code, tests, build config
- **Decision records** — `ADR-NNN` in `docs/decisions/` (the repo's design-record)
- Methodology documents (`methodology/`)
- Example files (`examples/`) — with fabricated data only
- User-facing docs: README, GETTING_STARTED, API, CONTRIBUTING, CHANGELOG
- Public design specs (`specs/`) — if intentionally public
- Templates (`templates/`)

## These do NOT belong in the repo (→ project's Nextcloud internal-documentation):
- Handoff documents (`type: handoff`, HANDOFF_*, *_HANDOFF_*)
- **Ideas** (`type: idea`, `docs/ideas/`) — quick internal captures
- **RFCs** (`type: rfc`) — design proposals; internal until ratified, then they become an ADR in `docs/decisions/`
- **Explorations and shapes** (`type: exploration` / `type: shape`) — strategic deliberation
- Internal planning docs / plans (CODE_HANDOFF_*)
- Development notes (`notes/`, `_internal/`)
- Chat history or session exports
- Process memos from actual research projects
- Files from Nextcloud, Dropbox, OneDrive or other external sync services

## If you are about to create or edit a file:
- Is this something a user who clones the repo needs? → Repo
- Is this internal planning, handoff, or development thinking? → NOT repo (use `save_document(doc_type=…)` → Nextcloud)

## The document model (ratified 2026-06-21)
Repo = **ADR** (the ratified decision-record) + code / methodology / examples / user-docs. ALL
deliberation (idea / rfc / exploration / shape / handoff) is **internal** → the project's Nextcloud
`<Project>_internal_documentation/` (routed via `save_document(doc_type=…)`). Enforced deterministically
by `internal_docs_guard` (gate on a doc's frontmatter `type:`): unambiguously-internal types are blocked
from the repo (git pre-commit), optional-public (rfc/plan/todo/spec) only warn.
