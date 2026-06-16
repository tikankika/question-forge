# qf-scaffolding

QuestionForge Scaffolding MCP - methodology guidance for modules M1-M4 and M5 question formatting, producing QFMD (QuestionForge Markdown) for the pipeline.

## Overview

qf-scaffolding provides pedagogical scaffolding for the question generation process. It guides teachers through the methodology stages while working alongside qf-pipeline for technical processing.

| Module | Purpose | Stages |
|--------|---------|--------|
| **M1** | Content Analysis | 6 stages (0-5) |
| **M2** | Assessment Planning | 7 stages |
| **M3** | Question Generation | 3 stages (3A-3C) |
| **M4** | Quality Assurance | 5 phases |
| **M5** | Question Formatting | Simple mode |

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn
- Active qf-pipeline session (shared session architecture)

### Installation

```bash
# Navigate to package
cd packages/qf-scaffolding

# Install dependencies
npm install

# Build TypeScript
npm run build

# Test
npm test
```

### Development

```bash
# Watch mode for development
npm run dev
```

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "qf-scaffolding": {
      "command": "node",
      "args": ["/path/to/packages/qf-scaffolding/build/index.js"]
    }
  }
}
```

Replace `/path/to` with actual paths.

**Note:** Both qf-pipeline and qf-scaffolding should be configured together for full functionality.

## MCP Tools

### Core Tools

| Tool | Description |
|------|-------------|
| `load_stage` | Load methodology for a specific stage |
| `complete_stage` | Mark stage as complete, advance to next |
| `read_materials` | List or read files from materials folder |
| `read_reference` | Read reference documents (curriculum, etc.) |

### M1-Specific Tools

| Tool | Description |
|------|-------------|
| `save_m1_progress` | Progressive saving to m1_analysis.md |
| `write_m1_stage` | Direct file writing per stage (separate files) |

### M5 Tools

| Tool | Description |
|------|-------------|
| `m5_simple_start` | Start an M5 formatting session over a question file |
| `m5_simple_current` | Show the current question block |
| `m5_simple_create` | Write the approved QFMD for the current block |
| `m5_simple_skip` | Skip the current block |
| `m5_simple_status` | Show session progress |
| `m5_simple_finish` | End the session and show a summary |

### Project Tools

| Tool | Description |
|------|-------------|
| `read_project_file` | Read a specific project file |
| `write_project_file` | Write a project file |

## Shared Session Architecture

qf-scaffolding shares sessions with qf-pipeline via `session.yaml`:

```yaml
# Pipeline section (managed by qf-pipeline)
session_id: "project_20260114"
source_file: "/path/to/questions.md"
# ...

# Methodology section (managed by qf-scaffolding)
methodology:
  entry_point: "m1"
  active_module: "m1"
  m1:
    status: "in_progress"
    loaded_stages: [0, 1]
    current_stage: 1
```

**Important:** Always start with `step0_start` (qf-pipeline) before using qf-scaffolding tools.

## Project Structure

```
qf-scaffolding/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts              # MCP server entry point
│   ├── tools/
│   │   ├── load_stage.ts     # Stage loading
│   │   ├── complete_stage.ts # Stage completion
│   │   ├── read_materials.ts # Material reading
│   │   ├── read_reference.ts # Reference reading
│   │   ├── save_m1_progress.ts
│   │   ├── write_m1_stage.ts
│   │   ├── m5_simple_tools.ts
│   │   └── project_files.ts
│   ├── outputs/              # Output formatters
│   │   ├── material_analysis.ts
│   │   ├── emphasis_patterns.ts
│   │   ├── examples.ts
│   │   ├── misconceptions.ts
│   │   └── learning_objectives.ts
│   └── utils/
│       └── logger.ts         # Structured logging
└── build/                    # Compiled JavaScript
```

## Methodology Files

The methodology files are stored in the project's `methodology/` folder:

```
methodology/
├── m1/
│   ├── m1_0_stage0_material_analysis.md
│   ├── m1_1_stage1_validation.md
│   └── ...
├── m2/
├── m3/
└── m4/
```

These are copied during `step0_start` from the QuestionForge methodology repository.

## Stage Gate Pattern

qf-scaffolding enforces stage gates to ensure teacher approval:

```typescript
// load_stage returns:
{
  document: { content: "..." },
  requires_approval: true,
  approval_prompt: "Stage 1 complete. Continue to Stage 2?"
}
```

Claude must wait for teacher confirmation before advancing stages.

## Testing

```bash
# Run all tests
npm test

# Watch mode
npm run test:watch
```

## Dependencies

- **@modelcontextprotocol/sdk**: MCP SDK for TypeScript
- **yaml** / **js-yaml**: YAML parsing for session files
- **zod**: Schema validation
- **pdf-parse**: PDF text extraction for materials

## Related Documentation

- [WORKFLOW.md](../../WORKFLOW.md) - Complete workflow documentation
- [Methodology guides](../../methodology/) - The M1-M5 methodology files

## Licence

PolyForm Noncommercial 1.0.0 - See [LICENSE](../../LICENSE)
