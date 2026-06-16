# M5 - QFMD Formatting

## Purpose

M5 (Question Formatting) is a **manual preparatory step** between question generation and the technical pipeline. It takes the unformatted question text produced in M3 (Question Generation) — usually after M4 (Quality Assurance) approval — and helps the teacher format it into QFMD (QuestionForge Markdown), the structured markdown format the pipeline's validator (`step2_validate`) reads before QTI export.

## Why M5 is needed

```
M3 output (unformatted)
        │
        ▼
┌─────────────────────────────┐
│  M5 (manual step)           │
│  • Shows raw text to teacher│
│  • Teacher + the connected  │
│    AI assistant             │
│    format it into QFMD      │
│  • Writes to file           │
└─────────────────────────────┘
        │
        ▼
step2_validate (can now read it)
```

**M5 cannot call the parser** (different MCP servers). M5 therefore needs its own documentation of the correct format.

## Workflow

### 1. Start a session
```
m5_simple_start({ project_path: "/path/to/project" })
```
Reads `questions/m3_output.md`, splits on `---`, shows the first block.

### 2. For each block

1. **Read the raw content** that M5 shows
2. **Consult FORMAT_REFERENCE.md** for the correct format (it covers the core types; for other types use the validated fixtures in `packages/qti-core/tests/fixtures/v65/` as templates)
3. **Create QFMD** following the template or fixture for the right question type
4. **Save** with `m5_simple_create({ qfmd: "..." })`

Or skip with `m5_simple_skip()`.

### 3. Finish
```
m5_simple_finish()
```

### 4. Validate
```
step2_validate({ project_path: "..." })
```
If errors → fix and re-run.

## Tools

| Tool | Description |
|------|-------------|
| `m5_simple_start` | Start a session, show the first block |
| `m5_simple_current` | Show the current block again |
| `m5_simple_create` | Save QFMD for the current block |
| `m5_simple_skip` | Skip the current block |
| `m5_simple_status` | Show progress |
| `m5_simple_finish` | Finish and show a summary |

## Important

See **FORMAT_REFERENCE.md** for the exact format of the core question types, and the fixtures in `packages/qti-core/tests/fixtures/v65/` for all others.

**Language note:** write your question content in the language of your teaching material — the examples in these documents are illustrative, not a language requirement.
