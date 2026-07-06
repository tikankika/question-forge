# Contributing to QuestionForge

Thank you for your interest in contributing to QuestionForge!

## Critical rules — data protection

QuestionForge reads real teaching materials (lectures, slides, course documents).
This is a public repository — never let real personal data into the repo, in code,
tests, comments, documentation, examples or commit messages. Git history is permanent.

- **Never commit real personal data:** names (students, colleagues, teachers),
  school or institution names, identifying places, personal-identity numbers, file
  paths containing a username (`/Users/...`), secrets (API keys, tokens, `.env`),
  and real course materials that identify people or institutions.
- **Use fabricated or anonymised data in every example and test** — for example
  `School A`, `Colleague_A`, `/path/to/project`, a fake course code.
- **Watch quasi-identifiers:** a class plus a date plus a subject can identify a
  student even with no name attached.
- **Already committed something real?** Deleting the file is not enough — it stays
  in the git history forever. Stop, scrub the history, rotate any exposed secret,
  and escalate before the next push.

## How to contribute

### Reporting bugs

1. Check if the bug is already reported in [Issues](https://github.com/tikankika/question-forge/issues)
2. If not, create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behaviour
   - Environment (OS, Python/Node version, Claude Desktop version)

### Suggesting features

1. Open an issue with the `enhancement` label
2. Describe the use case and proposed solution
3. Reference relevant ADRs or RFCs if applicable

### Code contributions

#### Setup development environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/question-forge.git
cd question-forge

# Create a branch
git checkout -b feature/your-feature-name

# Install dependencies
cd packages/qf-pipeline
pip install -e ".[dev]"

cd ../qf-scaffolding
npm install
```

#### Development workflow

1. **Check existing ADRs** in `docs/adr/` for architectural context
2. **Create RFC** for significant changes (see `docs/rfcs/` for examples)
3. **Write tests** for new functionality
4. **Follow code style** (see below)
5. **Update documentation** if needed

#### Code style

**Python (qf-pipeline, qti-core):**
- Follow PEP 8
- Use type hints
- Docstrings for public functions

**TypeScript (qf-scaffolding):**
- Use TypeScript strict mode
- Explicit types (avoid `any`)
- JSDoc for public functions

#### Commit messages

Follow conventional commits:

```
type(scope): description

feat(m5): add self-learning format recognition
fix(parser): handle missing blanks field
docs(readme): update installation instructions
refactor(step3): simplify fix rule matching
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

#### Pull request process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Reference related issues in PR description
5. Request review

### Documentation contributions

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add examples
- Improve getting started guide
- Translate to other languages

## Architecture overview

Before contributing code, familiarise yourself with:

- **ADR-001**: Two-MCP architecture (qf-scaffolding + qf-pipeline)
- **ADR-014**: Shared session management
- **docs/rfcs/**: Design proposals and specifications
- **WORKFLOW.md**: Complete workflow documentation

## Communication

- **Issues**: Bug reports and feature requests
- **Discussions**: Questions and ideas
- **Pull Requests**: Code contributions

## Licence

By contributing, you agree that your contributions will be licensed under PolyForm Noncommercial 1.0.0 (see [LICENSE](LICENSE)).

---

Thank you for helping improve QuestionForge!
