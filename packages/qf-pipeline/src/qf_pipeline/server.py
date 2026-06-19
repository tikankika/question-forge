"""QuestionForge Pipeline MCP Server.

Provides tools for validating markdown questions and exporting to QTI format.
Includes session management for project-based workflows.

Tool naming convention (ADR-007):
  stepN_ = Step N in pipeline (consistent with Assessment_suite phaseN_)

  step0_* = Session Management
  step2_* = Validator
  step4_* = Export

  Cross-step utilities have no prefix (list_types)
"""

import asyncio
import json
import logging
import subprocess
import time
import traceback
from pathlib import Path
from typing import List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .wrappers import (
    # Parser - used by step1_* tools
    parse_markdown,
    parse_file,
    # Generator - used by list_types
    get_supported_types,
    # Validator - used by step2_validate_content
    validate_markdown,
    # Errors
    WrapperError,
    # NOTE: RFC-012 - These are now OBSOLETE (replaced by subprocess):
    # - generate_all_xml, create_qti_package (step4_export uses scripts)
    # - validate_file, validate_resources, copy_resources (subprocess)
)
from .tools import (
    start_session_tool,
    get_session_status_tool,
    load_session_tool,
    get_current_session,
    # Step 0 tools - ADR-015 Flexible Project Initialization
    step0_add_file,
    step0_analyze,
    # Project file tools
    read_project_file,
    write_project_file,
)
from .utils.logger import log_action, log_event

logger = logging.getLogger(__name__)

# Sibling qti-core package (…/packages/qti-core), used by step2/step4 subprocesses
QTI_CORE_PATH = Path(__file__).parent.parent.parent.parent / "qti-core"

# Create server instance
server = Server("qf-pipeline")


async def _auto_load_session(file_path: str):
    """Try to load a session from the project structure around file_path."""
    input_path = Path(file_path).resolve()
    if input_path.parent.name in ("pipeline", "questions"):
        project_path = input_path.parent.parent
        session_file = project_path / "session.yaml"
        if session_file.exists():
            result = await load_session_tool(str(project_path))
            if result.get("success"):
                return get_current_session()
    return None


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools."""
    return [
        # System
        Tool(
            name="init",
            description=(
                "CALL THIS FIRST! Returns M1/M2/M3/M4/Pipeline entry point routing. "
                "Ask user: 'What do you have?' "
                "M1=Material, M2=Learning objectives, M3=Blueprint, M4=Questions for QA, Pipeline=Direct export. "
                "Then use step0_start with correct entry_point."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        # Step 0: Session Management
        Tool(
            name="step0_start",
            description=(
                "Start a new session OR load existing. "
                "For new: provide output_folder + entry_point. "
                "ADR-015: Use entry_point='setup' to create empty project, then add files with step0_add_file. "
                "source_file can be a local path OR a URL (auto-fetched as .md). "
                "For existing: provide project_path."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "output_folder": {
                        "type": "string",
                        "description": "NEW SESSION: Directory where project will be created",
                    },
                    "source_file": {
                        "type": "string",
                        "description": "NEW SESSION: Path OR URL to source (required for m2/m3/m4/pipeline, optional for setup). URLs auto-fetched to .md",
                    },
                    "project_name": {
                        "type": "string",
                        "description": "NEW SESSION: Optional project name (auto-generated if not provided)",
                    },
                    "entry_point": {
                        "type": "string",
                        "description": (
                            "NEW SESSION: Entry point - "
                            "'setup' (empty project, ADR-015), "
                            "'m1' (material), 'm2' (learning objectives), 'm3' (blueprint), 'm4' (QA), 'pipeline' (direct). "
                            "Default: 'pipeline'"
                        ),
                        "enum": ["setup", "m1", "m2", "m3", "m4", "pipeline"],
                    },
                    "materials_folder": {
                        "type": "string",
                        "description": "NEW SESSION: Path to folder containing instructional materials (required for entry_point m1). Entire folder structure copied to materials/ (junk files filtered).",
                    },
                    "project_path": {
                        "type": "string",
                        "description": "LOAD SESSION: Path to existing project directory",
                    },
                },
            },
        ),
        Tool(
            name="step0_add_file",
            description=(
                "ADR-015: Add a file to an existing project. "
                "Can be called multiple times. "
                "Auto-detects file type and places in correct folder. "
                "Returns conversion hints if file needs MarkItDown."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to project directory",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to file to add (local path)",
                    },
                    "file_type": {
                        "type": "string",
                        "description": "File type hint: 'auto', 'questions', 'materials', 'resources', 'blueprint'. Default: 'auto'",
                        "enum": ["auto", "questions", "materials", "resources", "blueprint"],
                    },
                    "target_folder": {
                        "type": "string",
                        "description": "Target folder: 'auto', 'questions', 'materials', 'questions/resources'. Default: 'auto'",
                    },
                },
                "required": ["project_path", "file_path"],
            },
        ),
        Tool(
            name="step0_analyze",
            description=(
                "ADR-015: Analyze project contents and recommend workflow. "
                "Call after adding files with step0_add_file. "
                "Returns recommended entry point based on what files exist."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to project directory",
                    },
                },
                "required": ["project_path"],
            },
        ),
        Tool(
            name="step0_status",
            description="Get status of current session including validation status and exports",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        # Step 2: Validator
        Tool(
            name="step2_validate",
            description="Validate markdown file. If session active: uses working_file by default.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to markdown file (optional if session active)",
                    },
                },
            },
        ),
        Tool(
            name="step2_validate_content",
            description="Validate markdown content string directly (for testing snippets)",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Markdown content to validate",
                    },
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="step2_read",
            description=(
                "Read the working file content for inspection/fixing. "
                "Use when validation fails and you need to see the file. "
                "Requires active session."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "max_lines": {
                        "type": "integer",
                        "description": "Maximum lines to return (default: all)",
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Start from this line (1-indexed, default: 1)",
                    },
                },
            },
        ),
        # Step 3: Auto-Fix
        Tool(
            name="step3_autofix",
            description=(
                "Auto-fix mechanical errors in markdown. "
                "Runs validation → fix → validation loop until valid or max rounds. "
                "Fixes: colon in metadata (^type: → ^type), field positioning. "
                "Returns 'valid', 'needs_m5' (pedagogical errors), or 'max_rounds'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to markdown file",
                    },
                    "content": {
                        "type": "string",
                        "description": "Or provide content directly (instead of file_path)",
                    },
                    "max_rounds": {
                        "type": "integer",
                        "description": "Maximum fix iterations (default: 10)",
                        "default": 10,
                    },
                    "save": {
                        "type": "boolean",
                        "description": "Save fixed content to file (default: true)",
                        "default": True,
                    },
                },
            },
        ),
        # Pipeline Router (between Step 2 and Step 3/1/M5)
        Tool(
            name="pipeline_route",
            description=(
                "Route Step 2 validation errors to appropriate handler. "
                "MECHANICAL errors → Step 3 (auto-fix). "
                "STRUCTURAL errors → Step 1 (teacher decision). "
                "PEDAGOGICAL errors → M5 (content authoring). "
                "No errors → Step 4 (export)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to markdown file to validate and route",
                    },
                    "errors": {
                        "type": "array",
                        "description": "Or provide errors directly from Step 2",
                        "items": {"type": "object"},
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Include error details in output (default: true)",
                        "default": True,
                    },
                },
            },
        ),
        # Step 4: Export
        Tool(
            name="step4_export",
            description="Export to QTI package. If session active: uses questions/ and output/. Or provide paths directly.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to markdown file (optional if session active)",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path for output ZIP file (optional if session active)",
                    },
                    "output_name": {
                        "type": "string",
                        "description": "Name for output ZIP and Inspera (e.g., 'Ma2b_Prov_VT2025'). Default: project folder name.",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code (sv/en)",
                        "default": "sv",
                    },
                },
            },
        ),
        # Step 1: Minimal Safety Net (Vision A - 2026-01-28)
        # Most files: M5 → Step 2 → Step 3 → Step 4 (Step 1 skipped)
        # Step 1 only when: Step 3 fails, unknown errors, structural issues needing human
        Tool(
            name="step1_review",
            description=(
                "Review structural errors that router sent to Step 1. "
                "Shows questions with errors and available actions. "
                "Use when pipeline_route returns 'step1'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to markdown file",
                    },
                    "errors": {
                        "type": "array",
                        "description": "Structural errors from pipeline_route",
                        "items": {"type": "object"},
                    },
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="step1_manual_fix",
            description=(
                "Apply manual fix when Step 3 auto-fix fails. "
                "Teacher provides corrected question content."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to markdown file",
                    },
                    "question_id": {
                        "type": "string",
                        "description": "Question to fix (e.g., 'Q001')",
                    },
                    "new_content": {
                        "type": "string",
                        "description": "Corrected question content",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Optional reason for the fix",
                    },
                },
                "required": ["file_path", "question_id", "new_content"],
            },
        ),
        Tool(
            name="step1_delete",
            description=(
                "Delete a question from the file. "
                "Use when question is unsalvageable or duplicate."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to markdown file",
                    },
                    "question_id": {
                        "type": "string",
                        "description": "Question to delete",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Optional reason for deletion",
                    },
                },
                "required": ["file_path", "question_id"],
            },
        ),
        Tool(
            name="step1_skip",
            description="Skip a question for now. Question remains in file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question_id": {
                        "type": "string",
                        "description": "Question to skip",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Optional reason for skipping",
                    },
                },
                "required": ["question_id"],
            },
        ),
        # Cross-step utility
        Tool(
            name="list_types",
            description="List supported question types",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="list_projects",
            description="List configured project folders with status. Shows available projects for quick selection.",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_files": {
                        "type": "boolean",
                        "description": "Also count markdown files in each folder",
                        "default": False
                    }
                }
            },
        ),
        # Project file tools (read/write anywhere in project)
        Tool(
            name="read_project_file",
            description="Read any file within a project directory. Security: prevents path traversal outside project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Root project directory",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "Path relative to project_path, e.g. 'output/questions.md'",
                    },
                },
                "required": ["project_path", "relative_path"],
            },
        ),
        Tool(
            name="write_project_file",
            description="Write any file within a project directory. Creates parent dirs by default. Security: prevents path traversal.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Root project directory",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "Path relative to project_path",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write",
                    },
                    "create_dirs": {
                        "type": "boolean",
                        "description": "Create parent directories if needed (default: true)",
                        "default": True,
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Overwrite if file exists (default: true)",
                        "default": True,
                    },
                },
                "required": ["project_path", "relative_path", "content"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "init":
            return await handle_init()
        elif name == "step0_start":
            return await handle_step0_start(arguments)
        elif name == "step0_add_file":
            return await handle_step0_add_file(arguments)
        elif name == "step0_analyze":
            return await handle_step0_analyze(arguments)
        elif name == "step0_status":
            return await handle_step0_status(arguments)
        elif name == "step2_validate":
            return await handle_step2_validate(arguments)
        elif name == "step2_validate_content":
            return await handle_step2_validate_content(arguments)
        elif name == "step2_read":
            return await handle_step2_read(arguments)
        elif name == "step3_autofix":
            return await handle_step3_autofix(arguments)
        elif name == "pipeline_route":
            return await handle_pipeline_route(arguments)
        elif name == "step4_export":
            return await handle_step4_export(arguments)
        elif name == "list_types":
            return await handle_list_types()
        elif name == "list_projects":
            return await handle_list_projects(arguments)
        # Project file tools
        elif name == "read_project_file":
            return await handle_read_project_file(arguments)
        elif name == "write_project_file":
            return await handle_write_project_file(arguments)
        # Step 1: Minimal Safety Net (Vision A)
        elif name == "step1_review":
            return await handle_step1_review(arguments)
        elif name == "step1_manual_fix":
            return await handle_step1_manual_fix(arguments)
        elif name == "step1_delete":
            return await handle_step1_delete(arguments)
        elif name == "step1_skip":
            return await handle_step1_skip(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except WrapperError as e:
        return [TextContent(type="text", text=f"Error: {e}")]
    except FileNotFoundError as e:
        return [TextContent(type="text", text=f"File not found: {e}")]
    except PermissionError as e:
        return [TextContent(type="text", text=f"Permission denied: {e}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {type(e).__name__}: {e}")]


# =============================================================================
# System: Init
# =============================================================================

async def handle_init() -> List[TextContent]:
    """Handle init tool call - return critical instructions with simplified ADR-015 flow."""
    instructions = """# QuestionForge - Getting Started

## RECOMMENDED WORKFLOW (ADR-015)

```
┌────────────────────────────────────────────────────────────────┐
│  1. CREATE PROJECT                                             │
│     step0_start(output_folder="...", entry_point="setup")      │
│                              ↓                                 │
│  2. ADD FILES                                                  │
│     step0_add_file(project_path="...", file_path="...")        │
│     (can be called multiple times)                             │
│                              ↓                                 │
│  3. GET RECOMMENDATION                                         │
│     step0_analyze(project_path="...")                          │
│     → The system suggests the right path based on your files   │
└────────────────────────────────────────────────────────────────┘
```

## QUICK START

**Ask the teacher:**
1. "Where should the project be saved?" → output_folder
2. "What should the project be called?" → project_name (optional)

**Create:**
```
step0_start(
    output_folder="/path/to/projects",
    project_name="MyExam",
    entry_point="setup"
)
```

**Add files:**
```
step0_add_file(
    project_path="/path/to/MyExam",
    file_path="/path/to/exam.docx"
)
```
→ If the file is Word/Excel/PDF: the system indicates that MarkItDown is needed

**Analyse:**
```
step0_analyze(project_path="/path/to/MyExam")
```
→ Returns: "Recommends: M5 → Pipeline" (or other based on content)

## FILE TYPES

| File type | What happens |
|-----------|--------------|
| .md | Copied directly, analysed for QFMD format |
| .docx/.xlsx/.pdf | Copied, flagged for MarkItDown conversion |
| .png/.jpg/.mp3 | Copied to questions/resources/ |

## POSSIBLE RECOMMENDATIONS

| Status | Meaning | Next step |
|--------|---------|-----------|
| `empty` | No files | step0_add_file() |
| `needs_conversion` | docx/pdf needs conversion | MarkItDown MCP |
| `needs_m5` | Markdown but not QFMD | m5_start() |
| `ready_for_pipeline` | QFMD format, ready | step2_validate() |
| `needs_m1` | Materials only | load_stage(m1, 0) |

## ALTERNATIVE WORKFLOW (if you know exactly what you have)

| What you have | entry_point | Requires |
|---------------|-------------|----------|
| Material | "m1" | materials_folder |
| Learning objectives | "m2" | source_file |
| Blueprint | "m3" | source_file |
| Questions for QA | "m4" | source_file |
| Finished QFMD | "pipeline" | source_file |

## TOOLS

**Step 0 (Session):**
- init, step0_start, step0_add_file, step0_analyze, step0_status

**Methodology (qf-scaffolding):**
- load_stage, module_status

**Pipeline:**
- step2_validate, step3_autofix, step4_export
"""
    return [TextContent(type="text", text=instructions)]


# =============================================================================
# Step 0: Session Management
# =============================================================================

async def handle_step0_start(arguments: dict) -> List[TextContent]:
    """Handle step0_start - create new session OR load existing."""

    # Load existing session
    if arguments.get("project_path"):
        result = await load_session_tool(arguments["project_path"])
        if result.get("success"):
            # Log session_resume (TIER 2)
            log_event(
                project_path=Path(result['project_path']),
                session_id=result['session_id'],
                tool="step0_start",
                event="session_resume",
                level="info",
                data={
                    "resumed_at": result.get('validation_status', 'unknown'),
                    "working_file": result.get('working_file'),
                    "export_count": result.get('export_count', 0),
                }
            )
            return [TextContent(
                type="text",
                text=f"Session loaded!\n"
                     f"  ID: {result['session_id']}\n"
                     f"  Project: {result['project_path']}\n"
                     f"  Working file: {result.get('working_file', 'N/A')}\n"
                     f"  Validation: {result.get('validation_status', 'unknown')}"
            )]
        else:
            error = result.get("error", {})
            return [TextContent(
                type="text",
                text=f"Could not load session: {error.get('message')}"
            )]

    # Create new session - requires output_folder
    if not arguments.get("output_folder"):
        return [TextContent(
            type="text",
            text=(
                "Error: output_folder required for new session.\n\n"
                "Usage:\n"
                "  - New session: output_folder + entry_point (+ source_file for m2/m3/m4/pipeline)\n"
                "  - Load existing: project_path\n\n"
                "Entry points:\n"
                "  - m1: Start from instructional materials (Content Analysis)\n"
                "  - m2: Start from learning objectives (Assessment Design)\n"
                "  - m3: Start from blueprint (Question Generation)\n"
                "  - m4: Start from questions for QA (Quality Assurance)\n"
                "  - pipeline: Validate and export directly [default]"
            )
        )]

    # Get entry_point (default to "pipeline")
    entry_point = arguments.get("entry_point", "pipeline")

    # Validate materials_folder for m1 entry point
    materials_folder = arguments.get("materials_folder")

    if entry_point == "m1":
        if not materials_folder:
            return [TextContent(
                type="text",
                text=(
                    "Error: materials_folder required for entry point 'm1'.\n\n"
                    "Entry point m1 (Content Analysis) starts from instructional materials.\n"
                    "Provide path to folder containing:\n"
                    "  - Presentations (PDF, PPTX)\n"
                    "  - Lecture notes\n"
                    "  - Transcripts\n"
                    "  - Textbooks/articles\n\n"
                    "Example:\n"
                    "  materials_folder='/path/to/course/materials'"
                )
            )]

        # Validate materials_folder exists and is directory
        materials_path = Path(materials_folder)
        if not materials_path.exists():
            return [TextContent(
                type="text",
                text=f"Error: materials_folder does not exist: {materials_folder}"
            )]

        if not materials_path.is_dir():
            return [TextContent(
                type="text",
                text=f"Error: materials_folder is not a directory: {materials_folder}"
            )]

    # If materials_folder provided for non-m1 entry point, warn but continue
    if materials_folder and entry_point != "m1":
        logger.warning(
            f"materials_folder provided for '{entry_point}' entry point - "
            f"will be ignored. This parameter is only used for 'm1'."
        )
        materials_folder = None  # Clear it

    result = await start_session_tool(
        output_folder=arguments["output_folder"],
        source_file=arguments.get("source_file"),
        project_name=arguments.get("project_name"),
        entry_point=entry_point,
        materials_folder=materials_folder
    )

    if result.get("success"):
        log_action(
            Path(result['project_path']),
            "step0_start",
            f"Session created: {result['session_id']} (entry_point: {entry_point})",
            data={
                "session_id": result['session_id'],
                "source_file": arguments.get("source_file"),
                "project_path": result['project_path'],
                "entry_point": entry_point,
                "next_module": result.get('next_module'),
                "action": "create",
            }
        )

        # Build next steps guidance based on entry_point
        if result.get('pipeline_ready'):
            next_steps = (
                "Next step (Pipeline):\n"
                "  1. step2_validate: Validate the working file\n"
                "  2. step4_export: Export to QTI"
            )
        else:
            next_module = result.get('next_module')
            if next_module:
                next_steps = (
                    f"Next step (qf-scaffolding):\n"
                    f"  1. list_modules: Show available modules\n"
                    f"  2. load_stage({next_module}, 0): Start with {next_module.upper()}"
                )
            else:
                # entry_point="setup" - ADR-015 flexible initialization
                # Check if source_file was already provided
                if result.get('questions_file') or arguments.get('source_file'):
                    # File was provided with setup - confirm it was added
                    next_steps = (
                        "═══════════════════════════════════════════════════════\n"
                        "FILE ADDED! Are there more files?\n"
                        "═══════════════════════════════════════════════════════\n\n"
                        "TEACHING MATERIALS?\n"
                        "   (Lectures, slides, transcripts)\n\n"
                        "RESOURCES (images, audio, video)?\n"
                        "   (Figures, diagrams, audio clips for questions)\n\n"
                        "MORE TESTS/QUESTIONS?\n"
                        "   (More Word/Excel/PDF files)\n\n"
                        "───────────────────────────────────────────────────────\n"
                        "If YES - add more files:\n"
                        f"  step0_add_file(project_path=\"{result['project_path']}\", file_path=\"...\")\n\n"
                        "If NO - analyse and continue:\n"
                        f"  step0_analyze(project_path=\"{result['project_path']}\")\n"
                        "  → The system recommends the right workflow"
                    )
                else:
                    # Empty project created
                    next_steps = (
                        "═══════════════════════════════════════════════════════\n"
                        "ASK THE TEACHER: Which files should be added?\n"
                        "═══════════════════════════════════════════════════════\n\n"
                        "TESTS/QUESTIONS to convert?\n"
                        "   (Word, Excel, PDF with existing questions)\n\n"
                        "TEACHING MATERIALS?\n"
                        "   (Lectures, slides, transcripts)\n\n"
                        "RESOURCES (images, audio, video)?\n"
                        "   (Figures, diagrams, audio clips for questions)\n\n"
                        "───────────────────────────────────────────────────────\n"
                        "For each file, use:\n"
                        f"  step0_add_file(project_path=\"{result['project_path']}\", file_path=\"...\")\n\n"
                        "When all files are added:\n"
                        f"  step0_analyze(project_path=\"{result['project_path']}\")\n"
                        "  → The system recommends the right workflow"
                    )

        # Build response text
        response_text = (
            f"Session started!\n"
            f"  Session ID: {result['session_id']}\n"
            f"  Project: {result['project_path']}\n"
            f"  Entry point: {entry_point}\n"
        )

        if result.get('questions_file'):
            response_text += f"  Question file: {result['questions_file']}\n"

        if result.get('materials_copied'):
            response_text += f"  Materials: {result['materials_copied']} files copied to materials/\n"

        response_text += f"  Output: {result['output_folder']}\n\n{next_steps}"

        return [TextContent(type="text", text=response_text)]
    else:
        error = result.get("error", {})
        return [TextContent(
            type="text",
            text=f"Could not start session:\n"
                 f"  Type: {error.get('type')}\n"
                 f"  Message: {error.get('message')}"
        )]


async def handle_step0_status(arguments: dict) -> List[TextContent]:
    """Handle step0_status - get session status."""
    result = await get_session_status_tool()

    if result.get("active"):
        return [TextContent(
            type="text",
            text=f"Session active\n"
                 f"  ID: {result['session_id']}\n"
                 f"  Project: {result['project_path']}\n"
                 f"  Working file: {result.get('questions_file', 'N/A')}\n"
                 f"  Validation: {result['validation_status']} ({result.get('question_count', '?')} questions)\n"
                 f"  Exports: {result['export_count']}"
        )]
    else:
        return [TextContent(
            type="text",
            text="No active session. Use step0_start to begin."
        )]


async def handle_step0_add_file(arguments: dict) -> List[TextContent]:
    """Handle step0_add_file - add file to existing project (ADR-015)."""
    project_path = arguments.get("project_path")
    file_path = arguments.get("file_path")

    if not project_path:
        return [TextContent(
            type="text",
            text="Error: project_path required. Provide path to the project folder."
        )]

    if not file_path:
        return [TextContent(
            type="text",
            text="Error: file_path required. Provide path to the file to add."
        )]

    result = await step0_add_file(
        project_path=project_path,
        file_path=file_path,
        file_type=arguments.get("file_type", "auto"),
        target_folder=arguments.get("target_folder", "auto"),
    )

    if result.get("success"):
        file_info = result.get("file_added", {})
        lines = [
            "FILE ADDED",
            "",
            f"Original: {file_info.get('original')}",
            f"Copied to: {file_info.get('copied_to')}",
            f"File type: {file_info.get('file_type')}",
            "",
        ]

        if result.get("needs_conversion"):
            lines.append("CONVERSION REQUIRED")
            lines.append(result.get("conversion_hint", ""))
            lines.append("")

        # Ask about more files
        lines.append("───────────────────────────────────────────────────────")
        lines.append("MORE FILES TO ADD?")
        lines.append("───────────────────────────────────────────────────────")
        lines.append("")
        lines.append("Teaching materials? (slides, lectures)")
        lines.append("Resources? (images, audio, video for questions)")
        lines.append("More tests/questions?")
        lines.append("")
        lines.append("If YES: Use step0_add_file again")
        lines.append("If NO: Run step0_analyze to continue")

        return [TextContent(type="text", text="\n".join(lines))]
    else:
        error = result.get("error", {})
        return [TextContent(
            type="text",
            text=f"Error: {error.get('message', 'Unknown error')}"
        )]


async def handle_step0_analyze(arguments: dict) -> List[TextContent]:
    """Handle step0_analyze - analyse project and recommend workflow (ADR-015)."""
    project_path = arguments.get("project_path")

    if not project_path:
        return [TextContent(
            type="text",
            text="Error: project_path required. Provide path to the project folder."
        )]

    result = await step0_analyze(project_path=project_path)

    if result.get("success"):
        analysis = result.get("analysis", {})
        recommendation = result.get("recommendation", {})

        lines = [
            "=" * 50,
            "PROJECT ANALYSIS (ADR-015)",
            "=" * 50,
            "",
            f"Project: {result.get('project_path')}",
            "",
            "CONTENTS:",
            f"  Materials: {analysis.get('materials_count', 0)} files",
            f"  Questions: {analysis.get('questions_count', 0)} files",
            f"  Resources: {analysis.get('resources_count', 0)} files",
            "",
        ]

        # Show questions details if any
        if analysis.get("questions"):
            lines.append("QUESTION FILES:")
            for q in analysis.get("questions", []):
                estimated = q.get("estimated_questions")
                est_str = f" (~{estimated} questions)" if estimated else ""
                conv_str = " needs conversion" if q.get("needs_conversion") else ""
                lines.append(f"  - {q.get('name')}{est_str}{conv_str}")
            lines.append("")

        # Show recommendation
        lines.append("-" * 50)
        lines.append("RECOMMENDATION")
        lines.append("-" * 50)
        lines.append("")
        lines.append(f"Status: {recommendation.get('status', 'unknown')}")
        lines.append(f"Message: {recommendation.get('message', '')}")
        lines.append("")

        if recommendation.get("recommended_flow"):
            lines.append(f"Recommended workflow: {recommendation.get('recommended_flow')}")

        if recommendation.get("next_command"):
            lines.append(f"Next command: {recommendation.get('next_command')}")

        if recommendation.get("alternatives"):
            lines.append("")
            lines.append("Alternatives:")
            for alt in recommendation.get("alternatives", []):
                lines.append(f"  - {alt}")

        if recommendation.get("files_to_convert"):
            lines.append("")
            lines.append("Files that need conversion:")
            for f in recommendation.get("files_to_convert", []):
                lines.append(f"  - {f}")

        return [TextContent(type="text", text="\n".join(lines))]
    else:
        error = result.get("error", {})
        return [TextContent(
            type="text",
            text=f"Error: {error.get('message', 'Unknown error')}"
        )]


# =============================================================================
# Step 2: Validator
# =============================================================================

async def handle_step2_validate(arguments: dict) -> List[TextContent]:
    """
    Handle step2_validate - validate markdown file using subprocess.

    RFC-012: Run step1_validate.py script instead of wrapper to guarantee
    consistency with manual terminal workflow.
    """
    session = get_current_session()
    start_time = time.time()

    # Determine file path
    if arguments.get("file_path"):
        file_path = arguments["file_path"]
    elif session and session.working_file:
        file_path = str(session.working_file)
    else:
        return [TextContent(
            type="text",
            text="Provide file_path or start a session first (step0_start)"
        )]

    # Validate file exists
    if not Path(file_path).exists():
        return [TextContent(
            type="text",
            text=f"File not found: {file_path}"
        )]

    # Auto-load session from project if not already active
    if not session:
        session = await _auto_load_session(file_path)

    # Path to qti-core
    qti_core_path = QTI_CORE_PATH
    if not qti_core_path.exists():
        return [TextContent(
            type="text",
            text=f"qti-core not found at: {qti_core_path}"
        )]

    # Log tool_start (TIER 1)
    if session:
        log_event(
            project_path=session.project_path,
            session_id=session.session_id,
            tool="step2_validate",
            event="tool_start",
            level="info",
            data={"file": file_path, "method": "subprocess"}
        )

    try:
        # Run step1_validate.py via subprocess (RFC-012)
        result = subprocess.run(
            ['python3', 'scripts/step1_validate.py', str(file_path), '--verbose'],
            cwd=qti_core_path,
            capture_output=True,
            text=True,
            timeout=60
        )

        duration_ms = int((time.time() - start_time) * 1000)

        # Parse validation status from exit code
        is_valid = (result.returncode == 0)

        # Try to extract question count from output
        question_count = 0
        for line in result.stdout.split('\n'):
            if 'Total Questions:' in line:
                try:
                    question_count = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass

        # Log tool_end (TIER 1)
        if session:
            log_event(
                project_path=session.project_path,
                session_id=session.session_id,
                tool="step2_validate",
                event="tool_end",
                level="info",
                data={
                    "success": True,
                    "valid": is_valid,
                    "question_count": question_count,
                    "exit_code": result.returncode,
                },
                duration_ms=duration_ms
            )

        # Update session if active
        if session:
            session.update_validation(is_valid, question_count)

            # Log validation_complete (TIER 2) when validation passes
            if is_valid:
                log_event(
                    project_path=session.project_path,
                    session_id=session.session_id,
                    tool="step2_validate",
                    event="validation_complete",
                    level="info",
                    data={
                        "valid": True,
                        "question_count": question_count
                    }
                )

        # Combine stdout and stderr for output
        output = result.stdout
        if result.stderr:
            output += f"\n\nStderr:\n{result.stderr}"

        # Save report to session folder if active
        if session:
            report_path = session.project_path / "validation_report.txt"
            try:
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(output)
                output += f"\n\nReport saved to: {report_path}"
            except Exception as e:
                output += f"\n\n(Could not save report: {e})"

        return [TextContent(type="text", text=output)]

    except subprocess.TimeoutExpired:
        return [TextContent(
            type="text",
            text="Validation timeout (>60s). File may be too large."
        )]

    except Exception as e:
        # Log tool_error (TIER 1)
        if session:
            log_event(
                project_path=session.project_path,
                session_id=session.session_id,
                tool="step2_validate",
                event="tool_error",
                level="error",
                data={
                    "error_type": type(e).__name__,
                    "message": str(e),
                    "stacktrace": traceback.format_exc(),
                    "context": {"file": file_path}
                }
            )
        raise


async def handle_step2_validate_content(arguments: dict) -> List[TextContent]:
    """Handle step2_validate_content - validate markdown content string."""
    content = arguments.get("content")
    if not content:
        return [TextContent(type="text", text="Error: content required")]

    result = validate_markdown(content)

    if result["valid"]:
        return [TextContent(type="text", text="Content is valid")]

    issues_text = "\n".join(
        f"  [{i['level']}] {i['message']}" for i in result["issues"]
    )
    return [TextContent(type="text", text=f"Invalid content:\n{issues_text}")]


async def handle_step2_read(arguments: dict) -> List[TextContent]:
    """Handle step2_read - read working file content."""
    session = get_current_session()

    if not session or not session.working_file:
        return [TextContent(
            type="text",
            text="Error: No active session. Run step0_start first."
        )]

    working_file = Path(session.working_file)

    if not working_file.exists():
        return [TextContent(
            type="text",
            text=f"Error: Working file not found: {working_file}"
        )]

    try:
        with open(working_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        start_line = arguments.get('start_line', 1) - 1
        max_lines = arguments.get('max_lines')

        if start_line < 0:
            start_line = 0

        if max_lines:
            selected_lines = lines[start_line:start_line + max_lines]
        else:
            selected_lines = lines[start_line:]

        content = ''.join(selected_lines)
        line_count = len(selected_lines)
        total_lines = len(lines)

        header = f"File: {working_file.name}\n"
        header += f"Showing lines {start_line + 1}-{start_line + line_count} of {total_lines}\n"
        header += "-" * 40 + "\n"

        log_action(
            session.project_path,
            "step2_read",
            f"Read lines {start_line + 1}-{start_line + line_count}",
            data={
                "start_line": start_line + 1,
                "lines_read": line_count,
                "total_lines": total_lines,
            }
        )

        return [TextContent(type="text", text=header + content)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: Could not read the file: {e}"
        )]


# =============================================================================
# Step 3: Auto-Fix
# =============================================================================

async def handle_step3_autofix(arguments: dict) -> List[TextContent]:
    """
    Handle step3_autofix - auto-fix mechanical errors.

    Runs validation → fix → validation loop until valid or max rounds.
    """
    from .tools.step3_autofix import autofix_file, autofix_content, Step3Result

    file_path = arguments.get('file_path')
    content = arguments.get('content')
    max_rounds = arguments.get('max_rounds', 10)
    save = arguments.get('save', True)

    # Check for active session
    session = get_current_session()
    project_path = None

    # Auto-load session from project if not already active
    if not session and file_path:
        session = await _auto_load_session(file_path)

    if session:
        project_path = session.project_path
        # If no file_path, use session's questions file
        if not file_path and not content:
            questions_dir = project_path / "questions"
            if questions_dir.exists():
                md_files = list(questions_dir.glob("*.md"))
                if md_files:
                    file_path = str(md_files[0])

    # Need either file_path or content
    if not file_path and not content:
        return [TextContent(
            type="text",
            text="Error: Provide file_path or content"
        )]

    try:
        if content:
            # Fix content string
            result, fixed_content = autofix_content(
                content,
                max_rounds=max_rounds,
                project_path=project_path
            )

            # Build response
            lines = [
                "# Step 3: Auto-Fix Result",
                "",
                f"**Status:** {result.status}",
                f"**Rounds:** {result.rounds}",
                f"**Fixes applied:** {len(result.fixes_applied)}",
                "",
            ]

            if result.fixes_applied:
                lines.append("## Fixes Applied")
                for fix in result.fixes_applied:
                    lines.append(f"- [{fix.rule_id}] {fix.fix_applied}")
                lines.append("")

            if result.remaining_errors:
                lines.append(f"## Remaining Errors ({len(result.remaining_errors)})")
                for err in result.remaining_errors[:10]:
                    q_id = err.get('question_id', '?')
                    msg = err.get('message', 'Unknown')
                    lines.append(f"- [{q_id}] {msg}")
                lines.append("")

            lines.append(f"**Message:** {result.message}")

            # If valid and caller wants the content back
            if result.status == "valid":
                lines.append("")
                lines.append("---")
                lines.append("")
                lines.append("## Fixed Content")
                lines.append("```markdown")
                lines.append(fixed_content[:2000] + ("..." if len(fixed_content) > 2000 else ""))
                lines.append("```")

            return [TextContent(type="text", text="\n".join(lines))]

        else:
            # Fix file
            input_path = Path(file_path)

            if not input_path.exists():
                return [TextContent(
                    type="text",
                    text=f"Error: File not found: {file_path}"
                )]

            result = autofix_file(
                input_path,
                output_path=input_path if save else None,
                max_rounds=max_rounds,
                project_path=project_path
            )

            # Log summary if session active (detailed logs in step3_iterations.jsonl)
            if project_path:
                log_event(
                    str(project_path),
                    session.session_id if session else "",
                    "step3_autofix",
                    "autofix_complete",
                    "info",
                    {
                        "status": result.status,
                        "rounds": result.rounds,
                        "fixes_applied": len(result.fixes_applied),
                        "remaining_errors": len(result.remaining_errors),
                    }
                )

            # Build response
            lines = [
                "# Step 3: Auto-Fix Result",
                "",
                f"**File:** {input_path.name}",
                f"**Status:** {result.status}",
                f"**Rounds:** {result.rounds}",
                f"**Fixes applied:** {len(result.fixes_applied)}",
                "",
            ]

            if result.fixes_applied:
                lines.append("## Fixes Applied")
                for fix in result.fixes_applied:
                    lines.append(f"- [{fix.rule_id}] {fix.fix_applied}")
                lines.append("")

            if result.remaining_errors:
                lines.append(f"## Remaining Errors ({len(result.remaining_errors)})")
                for err in result.remaining_errors[:10]:
                    q_id = err.get('question_id', '?')
                    msg = err.get('message', 'Unknown')
                    lines.append(f"- [{q_id}] {msg}")
                lines.append("")

            lines.append(f"**Message:** {result.message}")

            # Next step suggestion
            if result.status == "valid":
                lines.append("")
                lines.append("---")
                lines.append("**Next:** `step4_export` to create QTI package")
            elif result.status == "needs_m5":
                lines.append("")
                lines.append("---")
                lines.append("**Next:** Return to M5 to fix pedagogical errors")
            elif result.status == "needs_step1":
                lines.append("")
                lines.append("---")
                lines.append("**Next:** Use `step1_*` tools to fix structural errors")

            return [TextContent(type="text", text="\n".join(lines))]

    except Exception as e:
        logger.error(f"Step 3 error: {traceback.format_exc()}")
        return [TextContent(type="text", text=f"Step 3 error: {type(e).__name__}: {str(e)}")]


# =============================================================================
# Pipeline Router
# =============================================================================

async def handle_pipeline_route(arguments: dict) -> List[TextContent]:
    """
    Route Step 2 validation errors to appropriate handler.

    RFC-013 Appendix A: Error Routing & Categorization
    - MECHANICAL errors → Step 3 (auto-fix)
    - STRUCTURAL errors → Step 1 (teacher decision)
    - PEDAGOGICAL errors → M5 (content authoring)
    - No errors → Step 4 (export)
    """
    from .tools.pipeline_router import handle_pipeline_route as router_handler

    try:
        result = await router_handler(arguments)

        # Format output
        output_text = result.get('formatted_output', '')

        return [TextContent(type="text", text=output_text)]

    except Exception as e:
        logger.error(f"Router error: {traceback.format_exc()}")
        return [TextContent(type="text", text=f"Router error: {type(e).__name__}: {str(e)}")]


# =============================================================================
# Step 4: Export
# =============================================================================

async def handle_step4_export(arguments: dict) -> List[TextContent]:
    """
    Handle step4_export - export to QTI package using ALL 5 scripts sequentially.

    RFC-012: Run actual scripts instead of wrappers to guarantee:
    1. apply_resource_mapping() is called (fixes critical image path bug)
    2. Consistency with manual terminal workflow
    3. Scripts = source of truth
    """
    session = get_current_session()
    start_time = time.time()

    # Determine file path
    if arguments.get("file_path"):
        file_path = arguments["file_path"]
    elif session and session.working_file:
        file_path = str(session.working_file)
    else:
        return [TextContent(
            type="text",
            text="Provide file_path or start a session first (step0_start)"
        )]

    # Validate input file exists
    if not Path(file_path).exists():
        return [TextContent(
            type="text",
            text=f"File not found: {file_path}"
        )]

    # Auto-load session from project if not already active
    if not session:
        session = await _auto_load_session(file_path)

    language = arguments.get("language", "sv")
    output_name = arguments.get("output_name")

    # Path to qti-core
    qti_core_path = QTI_CORE_PATH
    if not qti_core_path.exists():
        return [TextContent(
            type="text",
            text=f"qti-core not found at: {qti_core_path}"
        )]

    # Determine output name with fallback chain:
    # 1. Explicit output_name parameter
    # 2. Project folder name (if session active)
    # 3. Input file stem (original behaviour)
    if output_name:
        quiz_name = output_name
    elif session and session.project_path:
        # Use project folder name (e.g., "Ma2b_Prov_VT2025")
        quiz_name = Path(session.project_path).name
    else:
        # Fallback to file stem
        quiz_name = Path(file_path).stem

    # Output directory - use session's output folder or fallback to qti-core/output
    output_dir = Path(session.output_folder) if session and session.output_folder else qti_core_path / "output"

    # Quiz directory (where step2 creates the structure)
    quiz_dir = output_dir / quiz_name

    # Log tool_start (TIER 1)
    if session:
        log_event(
            project_path=session.project_path,
            session_id=session.session_id,
            tool="step4_export",
            event="tool_start",
            level="info",
            data={
                "file": file_path,
                "output_dir": str(output_dir),
                "output_name": quiz_name,
                "language": language,
                "method": "subprocess"
            }
        )

    # Scripts to run sequentially
    # NOTE: step3/4/5 need explicit --quiz-dir because they can't auto-detect
    # when output is outside qti-core/output/ (which is where they look by default)
    scripts = [
        {
            'name': 'step1_validate.py',
            'args': [str(file_path), '--verbose'],
            'description': 'Validates markdown format',
            'timeout': 60
        },
        {
            'name': 'step2_create_folder.py',
            'args': [str(file_path), '--output-dir', str(output_dir), '--output-name', quiz_name],
            'description': 'Creates output structure',
            'timeout': 30
        },
        {
            'name': 'step3_copy_resources.py',
            'args': ['--markdown-file', str(file_path), '--quiz-dir', str(quiz_dir), '--verbose'],
            'description': 'Copies and renames resources',
            'timeout': 60
        },
        {
            'name': 'step4_generate_xml.py',
            'args': ['--markdown-file', str(file_path), '--quiz-dir', str(quiz_dir), '--language', language, '--verbose'],
            'description': 'Generates QTI XML files (+ apply_resource_mapping)',
            'timeout': 120
        },
        {
            'name': 'step5_create_zip.py',
            'args': ['--quiz-dir', str(quiz_dir), '--output-name', f"{quiz_name}.zip", '--verbose'],
            'description': 'Creates QTI package (ZIP)',
            'timeout': 60
        }
    ]

    # Collect output
    all_output = []
    all_output.append("=" * 70)
    all_output.append("QTI EXPORT - SUBPROCESS APPROACH (RFC-012)")
    all_output.append("=" * 70)
    all_output.append(f"Source: {file_path}")
    all_output.append(f"Output: {output_dir}")
    all_output.append(f"Output name: {quiz_name}")
    all_output.append(f"Language: {language}")
    all_output.append("")

    # Run each script
    for i, script in enumerate(scripts, 1):
        all_output.append(f"\n{'=' * 70}")
        all_output.append(f"STEP {i}/5: {script['name']}")
        all_output.append(f"{script['description']}")
        all_output.append(f"{'=' * 70}\n")

        try:
            result = subprocess.run(
                ['python3', f"scripts/{script['name']}"] + script['args'],
                cwd=qti_core_path,
                capture_output=True,
                text=True,
                timeout=script['timeout']
            )

            # Append output
            all_output.append(result.stdout)

            # Check for errors
            if result.returncode != 0:
                all_output.append(f"\nERROR in {script['name']}!")
                all_output.append(f"\nStderr:\n{result.stderr}")

                # Log error
                if session:
                    log_action(
                        session.project_path,
                        "step4_export",
                        f"Error in {script['name']}: exit {result.returncode}"
                    )

                return [TextContent(type="text", text="\n".join(all_output))]

            all_output.append(f"✓ {script['name']} completed!\n")

        except subprocess.TimeoutExpired:
            all_output.append(f"\nTIMEOUT in {script['name']} (>{script['timeout']}s)!")
            return [TextContent(type="text", text="\n".join(all_output))]

        except Exception as e:
            all_output.append(f"\nEXCEPTION in {script['name']}: {str(e)}")
            return [TextContent(type="text", text="\n".join(all_output))]

    duration_ms = int((time.time() - start_time) * 1000)

    # Success - update session state
    question_count = 0
    zip_path = ""
    try:
        # Read package_info.json to get ZIP path
        package_info_path = quiz_dir / ".workflow" / "package_info.json"

        if package_info_path.exists():
            with open(package_info_path) as f:
                package_info = json.load(f)

            zip_path = package_info.get('zip_path', str(output_dir / f"{quiz_name}.zip"))

            # Try to get question count from xml_files.json
            xml_files_path = quiz_dir / ".workflow" / "xml_files.json"
            if xml_files_path.exists():
                with open(xml_files_path) as f:
                    xml_info = json.load(f)
                question_count = xml_info.get('xml_count', 0)

            # Update session
            if session:
                session.log_export(zip_path, question_count)

                # Log tool_end (TIER 1)
                log_event(
                    project_path=session.project_path,
                    session_id=session.session_id,
                    tool="step4_export",
                    event="tool_end",
                    level="info",
                    data={
                        "success": True,
                        "question_count": question_count,
                        "output_file": zip_path,
                    },
                    duration_ms=duration_ms
                )

                # Log export_complete (TIER 2)
                log_event(
                    project_path=session.project_path,
                    session_id=session.session_id,
                    tool="step4_export",
                    event="export_complete",
                    level="info",
                    data={
                        "output_file": zip_path,
                        "question_count": question_count,
                        "format": "QTI 2.2"
                    }
                )

    except Exception as e:
        all_output.append(f"\n⚠️  Warning: Could not update session state: {e}")

    # Final summary
    all_output.append("\n" + "=" * 70)
    all_output.append("EXPORT COMPLETE!")
    all_output.append("=" * 70)
    all_output.append(f"\nZIP: {zip_path}")
    all_output.append(f"Questions: {question_count}")
    all_output.append(f"\nVerify: {quiz_dir}")

    return [TextContent(type="text", text="\n".join(all_output))]


# =============================================================================
# Cross-step Utilities
# =============================================================================

async def handle_list_types() -> List[TextContent]:
    """Handle list_types - list supported question types."""
    types = get_supported_types()
    return [TextContent(
        type="text",
        text=f"Question types ({len(types)}):\n" + "\n".join(f"  - {t}" for t in types)
    )]


async def handle_list_projects(arguments: dict) -> List[TextContent]:
    """Handle list_projects - list configured project folders."""
    from .utils.config import list_projects, ConfigError

    include_files = arguments.get("include_files", False)

    try:
        result = list_projects(include_files=include_files)
    except ConfigError as e:
        return [TextContent(type="text", text=f"Configuration error: {e}")]

    lines = [f"Projects ({result['count']}):\n"]

    for p in result['projects']:
        status = "+" if p['exists'] else "-"
        lines.append(f"  {p['index']}. [{status}] {p['name']}")
        lines.append(f"     Path: {p['path']}")
        if p['description']:
            lines.append(f"     {p['description']}")
        if include_files and p.get('md_file_count') is not None:
            lines.append(f"     Files: {p['md_file_count']} markdown")
        lines.append("")

    if result['default_output_dir']:
        lines.append(f"Default output: {result['default_output_dir']}")

    lines.append(f"\nConfig: {result['config_path']}")
    lines.append("\nTip: Use step0_start with source_file from the desired folder.")

    return [TextContent(type="text", text="\n".join(lines))]


# =============================================================================
# Project File Tools (read/write anywhere in project)
# =============================================================================

async def handle_read_project_file(arguments: dict) -> List[TextContent]:
    """Handle read_project_file - read any file within project."""
    project_path = arguments.get("project_path")
    relative_path = arguments.get("relative_path")

    if not project_path or not relative_path:
        return [TextContent(
            type="text",
            text="Error: Both project_path and relative_path are required"
        )]

    result = await read_project_file(project_path, relative_path)

    if not result.get("success"):
        return [TextContent(
            type="text",
            text=f"Error: {result.get('error', 'Unknown error')}"
        )]

    # Format successful response
    lines = [
        f"File: {result['relative_path']}",
        f"Size: {result['size_bytes']} bytes",
        "-" * 40,
        result['content']
    ]

    return [TextContent(type="text", text="\n".join(lines))]


async def handle_write_project_file(arguments: dict) -> List[TextContent]:
    """Handle write_project_file - write any file within project."""
    project_path = arguments.get("project_path")
    relative_path = arguments.get("relative_path")
    content = arguments.get("content")
    create_dirs = arguments.get("create_dirs", True)
    overwrite = arguments.get("overwrite", True)

    if not project_path or not relative_path or content is None:
        return [TextContent(
            type="text",
            text="Error: project_path, relative_path, and content are required"
        )]

    result = await write_project_file(
        project_path,
        relative_path,
        content,
        create_dirs=create_dirs,
        overwrite=overwrite
    )

    if not result.get("success"):
        return [TextContent(
            type="text",
            text=f"Error: {result.get('error', 'Unknown error')}"
        )]

    # Format successful response
    msg = f"Wrote {result['bytes_written']} bytes to {result['relative_path']}"
    if result.get('created_dirs'):
        msg += " (created parent directories)"

    return [TextContent(type="text", text=msg)]


# =============================================================================
# Step 1: Minimal Safety Net (Vision A - 2026-01-28)
# =============================================================================

async def handle_step1_review(arguments: dict) -> List[TextContent]:
    """Handle step1_review - review structural errors from router."""
    from .tools.step1_tools import step1_review

    result = await step1_review(
        file_path=arguments.get("file_path", ""),
        errors=arguments.get("errors")
    )

    if not result.get("success"):
        return [TextContent(type="text", text=f"Error: {result.get('error')}")]

    lines = [
        "# Step 1: Review Structural Errors",
        "",
        f"**File:** {result['file']}",
        f"**Questions:** {result['total_questions']}",
        f"**With errors:** {len(result['questions_with_errors'])}",
        "",
    ]

    if result['questions_with_errors']:
        lines.append("## Questions Needing Attention")
        for q in result['questions_with_errors']:
            lines.append(f"\n### {q['question_id']}")
            for err in q['errors']:
                lines.append(f"- {err.get('message', 'Unknown error')}")
            if q.get('content_preview'):
                lines.append(f"\n```\n{q['content_preview']}\n```")

    lines.extend([
        "",
        "## Available Actions",
        "- `step1_manual_fix(file_path, question_id, new_content)` - Fix manually",
        "- `step1_delete(file_path, question_id)` - Remove question",
        "- `step1_skip(question_id)` - Skip for now",
    ])

    return [TextContent(type="text", text="\n".join(lines))]


async def handle_step1_manual_fix(arguments: dict) -> List[TextContent]:
    """Handle step1_manual_fix - apply manual fix."""
    from .tools.step1_tools import step1_manual_fix

    result = await step1_manual_fix(
        file_path=arguments.get("file_path", ""),
        question_id=arguments.get("question_id", ""),
        new_content=arguments.get("new_content", ""),
        reason=arguments.get("reason")
    )

    if not result.get("success"):
        return [TextContent(type="text", text=f"Error: {result.get('error')}")]

    return [TextContent(
        type="text",
        text=f"Fixed {result['question_id']}\nReason: {result.get('reason', 'N/A')}\n\nNext: Re-run step2_validate to check result."
    )]


async def handle_step1_delete(arguments: dict) -> List[TextContent]:
    """Handle step1_delete - delete question."""
    from .tools.step1_tools import step1_delete

    result = await step1_delete(
        file_path=arguments.get("file_path", ""),
        question_id=arguments.get("question_id", ""),
        reason=arguments.get("reason")
    )

    if not result.get("success"):
        return [TextContent(type="text", text=f"Error: {result.get('error')}")]

    return [TextContent(
        type="text",
        text=f"Deleted {result['question_id']}\nReason: {result.get('reason', 'N/A')}\n\nNext: Re-run step2_validate."
    )]


async def handle_step1_skip(arguments: dict) -> List[TextContent]:
    """Handle step1_skip - skip question."""
    from .tools.step1_tools import step1_skip

    result = await step1_skip(
        question_id=arguments.get("question_id", ""),
        reason=arguments.get("reason")
    )

    return [TextContent(
        type="text",
        text=f"Skipped {result['question_id']}\nReason: {result.get('reason', 'N/A')}\nNote: {result.get('note', '')}"
    )]


# =============================================================================
# Server Entry Point
# =============================================================================

async def run_server():
    """Run the MCP server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    """Run the MCP server."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
