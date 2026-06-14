# Contributing to QuestionForge

Thank you for your interest in contributing to QuestionForge!

## How to Contribute

### Reporting Bugs

1. Check if the bug is already reported in [Issues](https://github.com/tikankika/question-forge/issues)
2. If not, create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behaviour
   - Environment (OS, Python/Node version, Claude Desktop version)

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the use case and proposed solution
3. Reference relevant ADRs or RFCs if applicable

### Code Contributions

#### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/QuestionForge.git
cd QuestionForge

# Create a branch
git checkout -b feature/your-feature-name

# Install dependencies
cd packages/qf-pipeline
pip install -e ".[dev]"

cd ../qf-scaffolding
npm install
```

#### Development Workflow

1. **Check existing ADRs** in `docs/adr/` for architectural context
2. **Create RFC** for significant changes (see `docs/rfcs/` for examples)
3. **Write tests** for new functionality
4. **Follow code style** (see below)
5. **Update documentation** if needed

#### Code Style

**Python (qf-pipeline, qti-core):**
- Follow PEP 8
- Use type hints
- Docstrings for public functions

**TypeScript (qf-scaffolding):**
- Use TypeScript strict mode
- Explicit types (avoid `any`)
- JSDoc for public functions

#### Commit Messages

Follow conventional commits:

```
type(scope): description

feat(m5): add self-learning format recognition
fix(parser): handle missing blanks field
docs(readme): update installation instructions
refactor(step3): simplify fix rule matching
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

#### Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Reference related issues in PR description
5. Request review

### Documentation Contributions

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add examples
- Improve getting started guide
- Translate to other languages

## Architecture Overview

Before contributing code, familiarise yourself with:

- **ADR-001**: Two-MCP architecture (qf-scaffolding + qf-pipeline)
- **ADR-014**: Shared session management
- **docs/rfcs/**: Design proposals and specifications
- **WORKFLOW.md**: Complete workflow documentation

## Communication

- **Issues**: Bug reports and feature requests
- **Discussions**: Questions and ideas
- **Pull Requests**: Code contributions

## License

By contributing, you agree that your contributions will be licensed under CC BY-NC-SA 4.0.

---

Thank you for helping improve QuestionForge!
