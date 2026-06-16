# qf-pipeline

QuestionForge Pipeline MCP - validation and QTI export for Inspera.

## Setup

### Option 1: Using uv (Recommended)

```bash
# Install uv if not installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to package
cd packages/qf-pipeline

# Create virtual environment and install (incl. dev dependency group)
uv sync --group dev

# Test
uv run pytest tests/ -v
```

### Option 2: Using pip

```bash
# Python 3.10+ required
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest pytest-asyncio pytest-cov  # dev dependencies

# Test
pytest tests/ -v
```

> Note: dev dependencies are declared as a PEP 735 dependency group, not a
> `[dev]` extra — `pip install -e ".[dev]"` will not find them.

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "qf-pipeline": {
      "command": "/path/to/packages/qf-pipeline/.venv/bin/python",
      "args": ["-m", "qf_pipeline.server"],
      "env": {
        "PYTHONPATH": "/path/to/packages/qf-pipeline/src"
      }
    }
  }
}
```

Replace `/path/to` with actual paths.

## MCP Tools

The pipeline runs step 0 (project setup) → step 1 (guided build) → step 2 (validation) → step 3 (auto-fix) → step 4 (export), with mandatory teacher stops between steps.

| Tool | Description |
|------|-------------|
| `init` | Initialise or resume a pipeline session |
| `step0_start` | Start a project: create the folder structure and session |
| `step0_add_file` | Add a material/question file to the project |
| `step0_analyze` | Analyse project materials |
| `step0_status` | Show project status |
| `step1_review` | Review questions one by one (guided build) |
| `step1_manual_fix` | Apply a manual fix to the current question |
| `step1_delete` | Delete the current question |
| `step1_skip` | Skip the current question |
| `step2_validate` | Validate a question markdown file |
| `step2_validate_content` | Validate a markdown string |
| `step2_read` | Read validation results |
| `step3_autofix` | Auto-fix mechanical validation errors |
| `pipeline_route` | Recommend export shape (questions vs question set) |
| `step4_export` | Generate the QTI package |
| `list_types` | List the 16 supported question types |
| `list_projects` | List configured project folders |
| `read_project_file` | Read a project file |
| `write_project_file` | Write a project file |

## Testing Wrappers (without MCP)

The wrappers work independently of MCP:

```bash
cd packages/qf-pipeline
PYTHONPATH="src:$PYTHONPATH" python3 -m pytest tests/ -v
```

## Dependencies

- **qti-core**: resolved automatically as the sibling package `packages/qti-core` in the monorepo — no path configuration needed
- **Python**: 3.10+
- **mcp**: MCP SDK for Python

## Project Structure

```
qf-pipeline/
├── pyproject.toml
├── src/qf_pipeline/
│   ├── __init__.py
│   ├── server.py           # MCP server and tool registration
│   ├── specs/              # Question-type specs (YAML) + INDEX
│   ├── step1/              # Guided-build: parser, frontmatter, decision log
│   ├── tools/              # Tool implementations (step0/step1/step3, router, session, project files)
│   ├── utils/              # Config, logging, methodology loader, session manager
│   └── wrappers/           # qti-core integration (parser; _archived: previous generation)
└── tests/                  # pytest suite
```

## Licence

PolyForm Noncommercial 1.0.0 - See [LICENSE](../../LICENSE)
