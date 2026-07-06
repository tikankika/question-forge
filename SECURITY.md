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

## Scope notes

- The MCP servers read local files you point them at and write outputs to your
  project directories. Review the paths you grant access to.
- `qti-core` produces QTI packages from local markdown; it makes no network calls
  as part of generation.
