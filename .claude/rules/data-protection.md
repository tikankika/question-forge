---
paths:
  - "**/*"
---

# Data Protection — Treat As If Public

Whether or not this repo is private today, treat everything in it as if it were
already public. A private repo can be made public, forked, cloned, or leaked, and
anything committed is permanent. The only safe assumption is that every file and
every past commit is visible to the world.

## Hard rule (non-negotiable)

Real person or student data must **NEVER** exist in this repo — or any repo — in
any form, anywhere in the working tree **or its git history**. Prevention is the
only safe path: once committed it lives in the history forever (see
"Already committed?" below).

## NEVER write in files or commit messages:
- Personal names (colleagues, research participants, teachers, students)
- School names or abbreviations that identify specific schools
- University or institution names
- Research programme names (funded projects, grants)
- Place names (streets, buildings, venues) that identify locations
- Hardcoded file paths containing usernames (`/Users/...`, `/home/...`)
- Research questions specific enough to identify a study
- Chat history or session transcripts
- Secrets: API keys, tokens, passwords, `.env` contents, credentials

## ALWAYS use instead:
- `School A`, `School B`, `Colleague_A` for anonymised references
- `/path/to/project` for file path examples
- `SPEAKER_01`, `L1` for participant references
- Generic descriptions for research programmes
- Synthetic/fabricated data in examples

## Check before committing:
- Think before writing — does this text contain any personal names, paths, or identifiers?
- Would a reader identify a specific person, school, or study from this text —
  **directly**, OR by combining quasi-identifiers (e.g. class + date + subject can
  identify a student without naming them)?
- This is your judgement. The `pii_scan` commit gate is the deterministic backstop —
  it catches what you miss, but it is not a substitute for the check above.

## Already committed? Deletion is NOT enough.

If real data is found already in the repo, removing the file in a new commit does
**not** remove it from git history — it remains in every past commit, clone, and
fork. To actually remove it you must scrub the history (fresh-repo rebuild or a
history filter) **and** rotate any exposed secret. Stop and escalate before
publishing or flipping such a repo.

## This applies to ALL content:
- Source code, comments, error messages
- Documentation, RFCs, changelogs, roadmaps
- Commit messages
- Test data and examples
