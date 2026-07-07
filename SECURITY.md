# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ |
| < 0.1   | ❌ |

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Report vulnerabilities privately through GitHub's [private vulnerability reporting](https://github.com/tikankika/question-forge/security/advisories/new) (the **Security** tab → **Report a vulnerability**).

Please include:

- a description of the issue and its impact,
- steps to reproduce (a minimal example if possible),
- any suggested mitigation.

You can expect an acknowledgement within a week, and responsible disclosure is appreciated — please allow time for a fix before any public disclosure.

## Data protection

QuestionForge processes real teaching materials (lectures, slides, course
documents), and this is a public repository. One rule is non-negotiable:
**no real personal data may ever enter the repo** — in code, tests, examples,
documentation or commit messages, anywhere in the working tree or its git
history.

- Never commit real names (students, colleagues, teachers), school or
  institution names, identifying places, personal-identity numbers, file paths
  containing a username (`/Users/...`), or secrets (API keys, tokens, `.env`
  contents).
- Use fabricated or anonymised data in every example and test — `School A`,
  `Colleague_A`, `/path/to/project`.
- Watch quasi-identifiers: a class plus a date plus a subject can identify a
  student even with no name attached.
- Found real personal data already committed? Deleting the file is not enough —
  it remains in the git history. Report it privately (see above) so the history
  can be scrubbed and any exposed secret rotated.

See [CONTRIBUTING](CONTRIBUTING.md) for the contributor-facing version of these
rules.

## Scope notes

- The MCP servers read local files you point them at and write outputs to your
  project directories. Review the paths you grant access to.
- `qti-core` produces QTI packages from local markdown; it makes no network calls
  as part of generation.
