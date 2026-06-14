# Getting Started with QuestionForge

This guide takes you from zero to your first QTI export in about 30 minutes.

## Prerequisites

### Required Software

| Software | Version | Check Command |
|----------|---------|---------------|
| Python | 3.10+ | `python3 --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Claude Desktop | Latest | Open app |

### Claude Desktop Configuration

QuestionForge uses MCP (Model Context Protocol) to integrate with Claude Desktop. You'll need to configure both MCP servers.

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/tikankika/question-forge.git
cd QuestionForge
```

### Step 2: Install qf-pipeline (Python)

```bash
cd packages/qf-pipeline

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package
pip install -e .

# Verify installation
python -c "from qf_pipeline import server; print('✅ qf-pipeline installed')"
```

### Step 3: Install qf-scaffolding (TypeScript)

```bash
cd ../qf-scaffolding

# Install dependencies
npm install

# Build
npm run build

# Verify installation
node -e "console.log('✅ qf-scaffolding installed')"
```

### Step 4: Install qti-core

```bash
cd ../qti-core

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from src.parser import MarkdownQuizParser; print('qti-core installed')"
```

### Step 5: Configure Claude Desktop

Edit your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the MCP servers:

```json
{
  "mcpServers": {
    "qf-pipeline": {
      "command": "python",
      "args": ["-m", "qf_pipeline.server"],
      "cwd": "/path/to/QuestionForge/packages/qf-pipeline",
      "env": {
        "PYTHONPATH": "/path/to/QuestionForge/packages/qti-core"
      }
    },
    "qf-scaffolding": {
      "command": "node",
      "args": ["dist/index.js"],
      "cwd": "/path/to/QuestionForge/packages/qf-scaffolding"
    }
  }
}
```

**Important:** Replace `/path/to/QuestionForge` with your actual path.

### Step 6: Restart Claude Desktop

Quit and reopen Claude Desktop. Verify the MCP servers are loaded by typing:

```
What tools do you have from qf-pipeline?
```

Claude should list tools like `step0_start`, `step2_validate`, `step4_export`, etc.

## Your First Project

### Option A: Quick Export (Existing Questions)

If you have questions in markdown format ready to export:

```
Create a QF project called "test_export" with entry point "pipeline" 
and this source file: /path/to/your/questions.md
```

Then:
```
Validate the questions with step2_validate
```

If valid:
```
Export to QTI with step4_export
```

### Option B: Full Workflow (From Materials)

If you want to create questions from teaching materials:

```
Create a QF project called "my_course" with entry point "m1"
and materials folder: /path/to/your/materials/
```

Claude will guide you through:
1. **M1**: Analysing your materials
2. **M2**: Designing the assessment
3. **M3**: Generating questions
4. **M4**: Quality assurance
5. **Pipeline**: Validation and export

## Project Structure

After creating a project, you'll see:

```
my_course/
├── materials/          # Your instructional materials
├── methodology/        # M1-M4 methodology guides (copied)
├── preparation/        # M1 + M2 outputs
├── questions/          # M3 creates questions here
├── pipeline/           # Working files for validation
├── output/qti/         # Final QTI package
├── logs/               # Session logs
├── session.yaml        # Project state
└── sources.yaml        # Tracked source files
```

## Common Commands

| Task | Command |
|------|---------|
| Create project | `step0_start` |
| Check status | `step0_status` |
| Add files | `step0_add_file` |
| Load methodology | `load_stage` |
| Validate | `step2_validate` |
| Auto-fix | `step3_autofix` |
| Export | `step4_export` |

## Troubleshooting

### MCP Not Loading

1. Check config file syntax (valid JSON?)
2. Verify paths are absolute
3. Check Claude Desktop logs: `~/Library/Logs/Claude/`

### Python Import Errors

1. Verify PYTHONPATH includes qti-core
2. Check virtual environment is activated
3. Run `pip install -e .` again

### TypeScript Build Errors

1. Run `npm install` to ensure dependencies
2. Delete `dist/` and run `npm run build` again
3. Check Node.js version (need 18+)

### Validation Fails

1. Check QFMD format (see `methodology/m5/FORMAT_REFERENCE.md`)
2. Common issues: colons in metadata, missing fields
3. Use `step3_autofix` for mechanical errors

## Next Steps

- Read [WORKFLOW.md](../WORKFLOW.md) for complete workflow documentation
- Explore [ADRs](adr/) for architecture decisions
- Check [RFCs](rfcs/) for feature specifications
- See `methodology/m5/FORMAT_REFERENCE.md` for QFMD format

## Getting Help

- Check existing [Issues](https://github.com/tikankika/question-forge/issues)
- Read the [FAQ](#faq) below
- Open a new issue if needed

---

## FAQ

### What is QFMD?

QFMD (QuestionForge Markdown) is the structured markdown format used for questions. Example:

```markdown
---
# Q001A
^question What is the main function of mitochondria?
^type multiple_choice_single
^identifier BIO_MC_001
^points 1
^labels cell-function, mitochondria

@field: options
A) Protein synthesis
B) Energy production (ATP)
C) Cell division
D) DNA storage
@end_field

@field: answer
B
@end_field
---
```

### What question types are supported?

15 types including:
- `multiple_choice_single`
- `multiple_response`
- `true_false`
- `text_entry`
- `inline_choice`
- `match`
- `hotspot`
- `essay`
- And more...

### Can I use existing questions?

Yes! Use entry point `pipeline` or `questions` to start with existing markdown questions. QuestionForge will validate and export them.

### What LMS platforms are supported?

Currently optimised for **Inspera**. The QTI 2.1 export follows Inspera's requirements. Other QTI-compatible platforms may work but are not tested.

---

*Happy question forging!*
