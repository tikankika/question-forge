# Security Policy

## Supported versions

QuestionForge is in early release. Security fixes are provided for the latest
published version only.

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |
| < 0.1   | ❌        |

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Report vulnerabilities privately through GitHub's
[private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
on this repository (the **Security** tab → **Report a vulnerability**).

Please include:

- a description of the issue and its impact,
- steps to reproduce (a minimal example if possible),
- any suggested mitigation.

You can expect an acknowledgement within a reasonable time, and we will keep you
informed as the issue is assessed and resolved. Responsible disclosure is
appreciated — please give us time to release a fix before any public disclosure.

## Scope notes

- The MCP servers read local files you point them at and write outputs to your
  project directories. Review the paths you grant access to.
- `qti-core` produces QTI packages from local markdown; it makes no network calls
  as part of generation.
