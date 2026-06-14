# QuestionForge Log Events

This document defines all standard event types used in QuestionForge logging.

## Event Naming Convention

Events use `snake_case` and follow the pattern: `{category}_{action}`

Examples:
- `session_start` - Session category, start action
- `tool_end` - Tool category, end action
- `user_decision` - User category, decision action

## Session Events

| Event | Level | When | Required Data |
|-------|-------|------|---------------|
| `session_start` | info | New session created | `entry_point`, `source_file` |
| `session_resume` | info | Existing session loaded | `previous_state` |
| `session_end` | info | Session completed | `summary` |

## Tool Events (qf-pipeline)

| Event | Level | When | Required Data |
|-------|-------|------|---------------|
| `tool_start` | info | Tool begins | `arguments` |
| `tool_end` | info | Tool completes | `success`, `result` |
| `tool_progress` | debug | Long operation update | `percent`, `current`, `total` |
| `tool_error` | error | Error occurred | `error_type`, `error_message` |

### Tool Names (qf-pipeline)

- `step0_start` - Create/load session
- `step0_status` - Get session status
- `step1_start` - Start guided build
- `step1_fix_auto` - Auto-fix problems
- `step1_fix_manual` - Manual fix
- `step2_validate` - Validate markdown
- `step2_read` - Read working file
- `step3_decide` - Decision tool
- `step4_export` - Export to QTI

## Module Events (qf-scaffolding)

| Event | Level | When | Required Data |
|-------|-------|------|---------------|
| `stage_start` | info | M1-M4 stage begins | `module`, `stage`, `stage_name` |
| `stage_complete` | info | Stage approved | `module`, `stage`, `outputs` |
| `stage_skip` | info | Stage skipped | `module`, `stage`, `reason` |

### Module Names

- `m1` - Content Analysis
- `m2` - Assessment Design
- `m3` - Question Generation
- `m4` - Quality Assurance

## User Events

| Event | Level | When | Required Data |
|-------|-------|------|---------------|
| `user_decision` | info | User made choice | `decision_type`, `options_presented`, `user_choice` |
| `user_input` | info | User provided text | `prompt_type`, `input_length` |
| `user_edit` | info | User modified content | `content_type`, `changes` |

### Decision Types

- `assessment_type` - Formative vs summative
- `question_count` - Number of questions
- `bloom_distribution` - Cognitive level distribution
- `question_types` - MC, fill-in, etc.
- `difficulty_distribution` - Easy/medium/hard

## Validation Events (qti-core)

| Event | Level | When | Required Data |
|-------|-------|------|---------------|
| `file_parsed` | info | Source file read | `path`, `lines`, `questions_found` |
| `question_validated` | debug | Single question checked | `question_id`, `valid`, `errors` |
| `validation_summary` | info | Batch complete | `total`, `valid`, `invalid` |
| `export_complete` | info | QTI package created | `output_path`, `format` |

## Log Levels

| Level | When to Use | Examples |
|-------|-------------|----------|
| `debug` | Detailed info for developers | Per-question validation, file reads |
| `info` | Normal operations | Session start, tool complete, user decisions |
| `warn` | Potential issues | Missing optional fields, deprecated usage |
| `error` | Failures | Validation errors, crashes, exceptions |

## Examples

See `examples/` directory for complete JSON examples:

- `session_start.json` - New session creation
- `user_decision.json` - User choice logging
- `validation_complete.json` - Successful validation
- `error_deep.json` - Detailed error with context
