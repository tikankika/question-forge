#!/usr/bin/env node

/**
 * QF-Scaffolding MCP Server
 *
 * MCP server for M1-M5 methodology guidance with output creation.
 *
 * Tools:
 * - load_stage: Load methodology content for a stage
 * - complete_stage: Complete a stage with optional output creation
 * - read_materials: Read instructional materials from materials/ (RFC-004)
 * - read_reference: Read reference documents from project root (RFC-004)
 * - m5_simple_*: Simple M5 tools for manual QFMD creation (Claude does transformation)
 *
 * This server provides methodology guidance for creating assessment questions
 * through a structured, pedagogical process.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { loadStage, loadStageSchema, getModuleName, getToolHintsForStage, formatToolHints } from "./tools/load_stage.js";
import { completeStage, completeStageSchema } from "./tools/complete_stage.js";
import { readMaterials, readMaterialsSchema } from "./tools/read_materials.js";
import { readReference, readReferenceSchema } from "./tools/read_reference.js";
import { saveM1Progress, saveM1ProgressSchema } from "./tools/save_m1_progress.js";
import { writeM1Stage, writeM1StageSchema } from "./tools/write_m1_stage.js";
import {
  readProjectFile,
  readProjectFileSchema,
  writeProjectFile,
  writeProjectFileSchema,
} from "./tools/project_files.js";
import { getStageOutputType } from "./outputs/index.js";
// M5 Simple Tools (manual mode - Claude does transformation)
import {
  m5SimpleStart,
  m5SimpleStartSchema,
  m5SimpleCurrent,
  m5SimpleCreate,
  m5SimpleCreateSchema,
  m5SimpleSkip,
  m5SimpleSkipSchema,
  m5SimpleFinish,
  m5SimpleStatus,
} from "./tools/m5_simple_tools.js";

// Server version
const VERSION = "0.6.0"; // Removed complex M5 tools, keeping only m5_simple_* (manual mode)

// Create MCP server
const server = new Server(
  {
    name: "qf-scaffolding",
    version: VERSION,
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Tool definitions
const TOOLS: Tool[] = [
  {
    name: "load_stage",
    description:
      `Load a methodology stage from QuestionForge modules. ` +
      `Supports: M1 (Material Analysis), M2 (Assessment Design), M3 (Question Generation), M4 (Quality Assurance). ` +
      `Returns the complete markdown content plus progress info. ` +
      `Use this to guide the teacher through the complete question generation workflow.`,
    inputSchema: {
      type: "object",
      properties: {
        module: {
          type: "string",
          enum: ["m1", "m2", "m3", "m4"],
          description:
            "Module to load from. " +
            "m1=Material Analysis (8 stages), " +
            "m2=Assessment Design (9 stages), " +
            "m3=Question Generation (5 stages), " +
            "m4=Quality Assurance (6 stages).",
        },
        stage: {
          type: "number",
          minimum: 0,
          maximum: 8,
          description:
            "Stage index (0-based). " +
            "M1: 0-7, M2: 0-8, M3: 0-4, M4: 0-5. " +
            "Stage 0 is always Introduction. Last stage is always reference material. " +
            "Middle stages are dialogue-driven with teacher approval gates.",
        },
        project_path: {
          type: "string",
          description:
            "Optional: Absolute path to project folder. " +
            "If provided, stage loads are logged to logs/session.jsonl (RFC-001).",
        },
      },
      required: ["module", "stage"],
    },
  },
  {
    name: "complete_stage",
    description:
      `Complete a methodology stage with optional output creation. ` +
      `Call this when teacher approves a stage and is ready to move on. ` +
      `For stages that produce outputs (learning objectives, misconceptions, etc.), ` +
      `include the output data and it will be validated, formatted, and saved to preparation/.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        module: {
          type: "string",
          enum: ["m1", "m2", "m3", "m4"],
          description: "Module being completed.",
        },
        stage: {
          type: "number",
          minimum: 0,
          maximum: 8,
          description: "Stage index being completed.",
        },
        output: {
          type: "object",
          description:
            "Optional output to create. Include for stages with methodology outputs. " +
            "Type must be: learning_objectives, misconceptions (more in Phase 2).",
          properties: {
            type: {
              type: "string",
              description: "Output type (e.g., 'learning_objectives', 'misconceptions').",
            },
            data: {
              type: "object",
              description: "Structured data for the output (validated against schema).",
            },
          },
          required: ["type", "data"],
        },
        overwrite: {
          type: "boolean",
          description: "Set to true to overwrite existing output file.",
          default: false,
        },
      },
      required: ["project_path", "module", "stage"],
    },
  },
  {
    name: "read_materials",
    description:
      `⚠️ PRIMÄRT för att LISTA filer i materials/ (filename=null). ` +
      `För PDF-analys: Be användaren LADDA UPP filen till chatten istället - Claude.ai har bättre PDF-läsning! ` +
      `Read mode (filename="X.pdf") är endast FALLBACK om användaren inte kan ladda upp.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        filename: {
          type: ["string", "null"],
          description:
            "null/omit = LIST mode (returnerar filnamn). " +
            "'X.pdf' = READ mode (FALLBACK - be användaren ladda upp istället!).",
        },
        file_pattern: {
          type: "string",
          description:
            "DEPRECATED: Use filename instead. " +
            "Optional glob pattern to filter files in list mode.",
        },
        extract_text: {
          type: "boolean",
          description:
            "Extract text content from files. Default: true. " +
            "Only applies in read mode.",
          default: true,
        },
      },
      required: ["project_path"],
    },
  },
  {
    name: "read_reference",
    description:
      `Read reference documents from the project root (syllabus, grading criteria, etc.). ` +
      `These are typically saved by step0_start from URLs. ` +
      `Use this to access course context for M1 Material Analysis.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        filename: {
          type: "string",
          description:
            "Specific filename to read (e.g., 'kursplan.md'). " +
            "If omitted, all reference documents are returned.",
        },
      },
      required: ["project_path"],
    },
  },
  {
    name: "save_m1_progress",
    description:
      `Save M1 (Material Analysis) progress to preparation/m1_analysis.md. ` +
      `Three actions: (1) add_material - progressive saves during Stage 0 after each PDF; ` +
      `(2) save_stage - saves completed stage output (Stage 0-5); ` +
      `(3) finalize_m1 - marks M1 complete, ready for M2. ` +
      `All stages save to ONE document that grows progressively.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        stage: {
          type: "number",
          minimum: 0,
          maximum: 5,
          description:
            "M1 stage number (0-5). Required for add_material and save_stage actions.",
        },
        action: {
          type: "string",
          enum: ["add_material", "save_stage", "finalize_m1"],
          description:
            "add_material = save after each PDF in Stage 0; " +
            "save_stage = save completed stage output; " +
            "finalize_m1 = mark M1 complete.",
        },
        data: {
          type: "object",
          description:
            "Data to save. Structure depends on action: " +
            "add_material needs {material: {...}}; " +
            "save_stage needs {stage_output: {...}}; " +
            "finalize_m1 needs {final_summary: {...}}.",
          properties: {
            material: {
              type: "object",
              description: "Material analysis data (for add_material action).",
            },
            stage_output: {
              type: "object",
              description: "Stage output data (for save_stage action).",
            },
            final_summary: {
              type: "object",
              description: "Final summary data (for finalize_m1 action).",
            },
          },
        },
      },
      required: ["project_path", "action", "data"],
    },
  },
  {
    name: "write_m1_stage",
    description:
      `Write content directly to an M1 stage file. ` +
      `Each stage gets its own file (m1_stage0_materials.md, m1_stage1_validation.md, etc.). ` +
      `What you write = what gets saved. No transformation. ` +
      `Safe: Won't overwrite existing files unless overwrite=true. ` +
      `Progress is tracked automatically in m1_progress.yaml.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        stage: {
          type: "number",
          minimum: 0,
          maximum: 5,
          description:
            "M1 stage number (0-5). " +
            "0=Materials, 1=Validation, 2=Emphasis, 3=Examples, 4=Misconceptions, 5=Objectives.",
        },
        content: {
          type: "string",
          description:
            "Raw markdown content to write. This is saved EXACTLY as provided. " +
            "Include all analysis, examples, misconceptions, etc. in markdown format.",
        },
        overwrite: {
          type: "boolean",
          description: "Set to true to overwrite existing stage file. Default: false (safe).",
          default: false,
        },
      },
      required: ["project_path", "stage", "content"],
    },
  },
  {
    name: "read_project_file",
    description:
      `Read any file within the project directory. ` +
      `Use this when you need to read files outside of materials/. ` +
      `For example: questions in questions/, outputs in output/, etc. ` +
      `Security: Only allows reading files within the project directory.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        relative_path: {
          type: "string",
          description:
            "Path relative to project folder. Examples: " +
            "'output/questions.md', 'questions/draft.md', 'session.yaml'",
        },
      },
      required: ["project_path", "relative_path"],
    },
  },
  {
    name: "write_project_file",
    description:
      `Write any file within the project directory. ` +
      `Use this when you need to create or update files outside standard folders. ` +
      `Creates parent directories automatically. ` +
      `Security: Only allows writing files within the project directory.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        relative_path: {
          type: "string",
          description:
            "Path relative to project folder. Examples: " +
            "'output/questions.md', 'questions/draft.md'",
        },
        content: {
          type: "string",
          description: "Content to write to the file.",
        },
        create_dirs: {
          type: "boolean",
          description: "Create parent directories if they don't exist. Default: true.",
          default: true,
        },
        overwrite: {
          type: "boolean",
          description: "Overwrite if file exists. Default: true.",
          default: true,
        },
      },
      required: ["project_path", "relative_path", "content"],
    },
  },
  // ========== M5 SIMPLE TOOLS (Manual Mode - RECOMMENDED) ==========
  // Old complex M5 tools archived to _archive/m5_complex_2026-02-01/
  {
    name: "m5_simple_start",
    description:
      `🆕 REKOMMENDERAD: Starta enkel M5-session (manuellt läge). ` +
      `Splittar fil vid "---", visar varje block för läraren. ` +
      `Ingen auto-parsing - läraren skapar QFMD själv.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        source_file: {
          type: "string",
          description: "Relative path to source file. Default: questions/m3_output.md",
        },
        output_file: {
          type: "string",
          description: "Relative path for output. Default: questions/m5_output.md",
        },
        separator: {
          type: "string",
          description: "Block separator. Default: ---",
        },
      },
      required: ["project_path"],
    },
  },
  {
    name: "m5_simple_current",
    description: "Visa aktuellt block i enkel M5-session.",
    inputSchema: {
      type: "object",
      properties: {},
      required: [],
    },
  },
  {
    name: "m5_simple_create",
    description:
      `Skapa QFMD för aktuellt block. ` +
      `Läraren skriver QFMD-innehållet direkt.`,
    inputSchema: {
      type: "object",
      properties: {
        qfmd: {
          type: "string",
          description: "QFMD-innehåll för denna fråga",
        },
      },
      required: ["qfmd"],
    },
  },
  {
    name: "m5_simple_skip",
    description: "Hoppa över aktuellt block.",
    inputSchema: {
      type: "object",
      properties: {
        reason: {
          type: "string",
          description: "Anledning till att hoppa över (valfritt)",
        },
      },
      required: [],
    },
  },
  {
    name: "m5_simple_finish",
    description: "Avsluta enkel M5-session och visa sammanfattning.",
    inputSchema: {
      type: "object",
      properties: {},
      required: [],
    },
  },
  {
    name: "m5_simple_status",
    description: "Visa status för enkel M5-session.",
    inputSchema: {
      type: "object",
      properties: {},
      required: [],
    },
  },
];

// Handle tools/list request
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: TOOLS };
});

// Handle tools/call request
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "load_stage") {
    try {
      // Validate input
      const validatedInput = loadStageSchema.parse(args);

      // Load the stage
      const result = await loadStage(validatedInput);

      if (result.success && result.content) {
        // Format response with stage info and content
        const moduleName = result.stage?.module ? getModuleName(result.stage.module) : "Unknown";

        // RFC-007: Gate after load_stage - require user approval before proceeding
        const stopGate = [
          `🛑 **STOP - VÄNTA PÅ GODKÄNNANDE**`,
          ``,
          `Metodologin för denna stage visas nedan.`,
          ``,
          `**INSTRUKTION FÖR CLAUDE:**`,
          `1. Presentera en KORT sammanfattning av vad denna stage innebär`,
          `2. Fråga: "Ska vi börja med denna stage?"`,
          `3. VÄNTA på att läraren säger "ok", "ja", "fortsätt" eller liknande`,
          `4. Anropa INGA verktyg förrän läraren godkänt`,
          ``,
          `---`,
          ``,
        ].join("\n");

        // Special warning for M1 Stage 0 (RFC-007: User-driven workflow)
        const m1Stage0Warning = (validatedInput.module === "m1" && validatedInput.stage === 0)
          ? `⚠️ **VIKTIGT: ONE FILE AT A TIME!** Följ "QUICK START FOR TEACHERS" nedan. Analysera EN fil, presentera, vänta på feedback, spara. ALDRIG flera filer samtidigt!\n\n`
          : "";

        const header = [
          stopGate,
          `# ${result.stage?.name}`,
          ``,
          m1Stage0Warning,
          `**Modul:** ${moduleName}`,
          `**Stage:** ${result.stage?.index} av ${result.progress?.totalStages}`,
          `**Estimerad tid:** ${result.stage?.estimatedTime}`,
          result.stage?.requiresApproval === true ? `**Kräver godkännande:** Ja` :
          result.stage?.requiresApproval === "conditional" ? `**Kräver godkännande:** Villkorligt (auto-pass)` :
          `**Kräver godkännande:** Nej`,
          ``,
          `---`,
          ``,
        ].join("\n");

        // Get tool hints for this stage
        const toolHints = getToolHintsForStage(
          validatedInput.module,
          validatedInput.stage
        );
        const toolHintsSection = formatToolHints(toolHints);

        const footer = [
          ``,
          `---`,
          ``,
          `**Progress:** Stage ${(result.progress?.currentStage ?? 0) + 1}/${result.progress?.totalStages}`,
          result.progress?.remaining && result.progress.remaining.length > 0
            ? `**Återstår:** ${result.progress.remaining.join(" → ")}`
            : `**Status:** ${moduleName} komplett!`,
          ``,
          `**Nästa:** ${result.nextAction}`,
        ].join("\n");

        return {
          content: [
            {
              type: "text",
              text: header + result.content + toolHintsSection + footer,
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `Error: ${result.error}`,
            },
          ],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [
          {
            type: "text",
            text: `Validation error: ${errorMessage}`,
          },
        ],
        isError: true,
      };
    }
  }

  // Handle complete_stage
  if (name === "complete_stage") {
    try {
      // Validate input
      const validatedInput = completeStageSchema.parse(args);

      // Complete the stage
      const result = await completeStage(validatedInput);

      if (result.success) {
        // Check if output was expected for this stage
        const expectedOutput = getStageOutputType(validatedInput.module, validatedInput.stage);
        const outputNote = result.output_filepath
          ? `\n\n**Output created:** \`${result.output_filepath}\``
          : expectedOutput
          ? `\n\n**Note:** Stage ${validatedInput.stage} typically produces ${expectedOutput} output. Consider providing output data.`
          : '';

        return {
          content: [
            {
              type: "text",
              text: `✅ Stage ${validatedInput.stage} completed for ${validatedInput.module.toUpperCase()}.${outputNote}`,
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `Error completing stage: ${result.error}`,
            },
          ],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [
          {
            type: "text",
            text: `Validation error: ${errorMessage}`,
          },
        ],
        isError: true,
      };
    }
  }

  // Handle read_materials (RFC-004: updated with list/read modes)
  if (name === "read_materials") {
    try {
      // Validate input
      const validatedInput = readMaterialsSchema.parse(args);

      // Read materials
      const result = await readMaterials(validatedInput);

      if (result.success) {
        const lines: string[] = [];

        if (result.mode === "list") {
          // List mode response
          lines.push(`# Materials in materials/`);
          lines.push(``);
          lines.push(`**Mode:** List (file metadata only)`);
          lines.push(`**Total files:** ${result.total_files}`);
          lines.push(``);

          if (result.files && result.files.length > 0) {
            lines.push(`| # | Filename | Type | Size |`);
            lines.push(`|---|----------|------|------|`);
            result.files.forEach((f, i) => {
              lines.push(`| ${i + 1} | ${f.filename} | ${f.content_type} | ${f.size_bytes.toLocaleString()} bytes |`);
            });
            lines.push(``);
            lines.push(`*Use read_materials(filename="X.pdf") to read a specific file.*`);
          } else {
            lines.push(`*No materials found in materials/*`);
          }
        } else {
          // Read mode response
          lines.push(`# Material: ${result.material?.filename}`);
          lines.push(``);
          lines.push(`**Mode:** Read (single file)`);
          lines.push(`**Type:** ${result.material?.content_type}`);
          lines.push(`**Size:** ${result.material?.size_bytes?.toLocaleString()} bytes`);
          if (result.total_chars) {
            lines.push(`**Characters:** ${result.total_chars.toLocaleString()}`);
          }
          lines.push(``);

          if (result.material?.error) {
            lines.push(`**Error:** ${result.material.error}`);
          } else if (result.material?.text_content) {
            lines.push(`---`);
            lines.push(``);
            lines.push(result.material.text_content);
          }
        }

        return {
          content: [
            {
              type: "text",
              text: lines.join("\n"),
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `Error: ${result.error}`,
            },
          ],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [
          {
            type: "text",
            text: `Validation error: ${errorMessage}`,
          },
        ],
        isError: true,
      };
    }
  }

  // Handle read_reference
  if (name === "read_reference") {
    try {
      // Validate input
      const validatedInput = readReferenceSchema.parse(args);

      // Read references
      const result = await readReference(validatedInput);

      if (result.success) {
        // Format response
        const lines: string[] = [
          `# Reference Documents`,
          ``,
          `**Total documents:** ${result.references.length}`,
          ``,
        ];

        if (result.references.length === 0) {
          lines.push(`*No reference documents found in project root.*`);
        } else {
          for (const ref of result.references) {
            lines.push(`## ${ref.filename}`);
            if (ref.source_url) {
              lines.push(`- **Source URL:** ${ref.source_url}`);
            }
            lines.push(``);
            lines.push(ref.content);
            lines.push(``);
          }
        }

        return {
          content: [
            {
              type: "text",
              text: lines.filter(l => l !== '').join("\n"),
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `Error: ${result.error}`,
            },
          ],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [
          {
            type: "text",
            text: `Validation error: ${errorMessage}`,
          },
        ],
        isError: true,
      };
    }
  }

  // Handle save_m1_progress (RFC-004: new tool)
  if (name === "save_m1_progress") {
    try {
      // Validate input
      const validatedInput = saveM1ProgressSchema.parse(args);

      // Save progress
      const result = await saveM1Progress(validatedInput);

      if (result.success) {
        const lines: string[] = [];
        const action = validatedInput.action;

        if (action === "add_material") {
          lines.push(`✅ Material saved to m1_analysis.md`);
          lines.push(``);
          lines.push(`**Materials analyzed:** ${result.materials_analyzed}/${result.total_materials}`);
        } else if (action === "save_stage") {
          lines.push(`✅ Stage ${validatedInput.stage} saved to m1_analysis.md`);
          lines.push(``);
          lines.push(`**Stages completed:** ${result.stages_completed.join(", ")}`);
        } else if (action === "finalize_m1") {
          lines.push(`🎉 M1 Complete!`);
          lines.push(``);
          lines.push(`**All stages completed:** ${result.stages_completed.join(", ")}`);
          lines.push(`**Ready for M2:** Yes`);
        }

        lines.push(``);
        lines.push(`**Document:** ${result.document_path}`);

        return {
          content: [
            {
              type: "text",
              text: lines.join("\n"),
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `Error saving M1 progress: ${result.error}`,
            },
          ],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [
          {
            type: "text",
            text: `Validation error: ${errorMessage}`,
          },
        ],
        isError: true,
      };
    }
  }

  // Handle write_m1_stage
  if (name === "write_m1_stage") {
    try {
      // Validate input
      const validatedInput = writeM1StageSchema.parse(args);

      // Write stage
      const result = await writeM1Stage(validatedInput);

      if (result.success) {
        const lines: string[] = [];
        lines.push(`✅ Stage ${validatedInput.stage} written to ${result.file_path}`);
        lines.push(``);
        lines.push(`**Stage:** ${result.stage_name}`);
        lines.push(`**Characters:** ${result.char_count?.toLocaleString()}`);
        lines.push(``);
        lines.push(`**Progress:**`);
        lines.push(`- Completed: ${result.progress?.completed.join(", ") || "none"}`);
        lines.push(`- Pending: ${result.progress?.pending.join(", ") || "none"}`);
        lines.push(`- Status: ${result.progress?.status}`);

        return {
          content: [
            {
              type: "text",
              text: lines.join("\n"),
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `Error writing stage: ${result.error}`,
            },
          ],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [
          {
            type: "text",
            text: `Validation error: ${errorMessage}`,
          },
        ],
        isError: true,
      };
    }
  }

  // Handle read_project_file
  if (name === "read_project_file") {
    try {
      const validatedInput = readProjectFileSchema.parse(args);
      const result = await readProjectFile(validatedInput);

      if (result.success && result.content) {
        const lines: string[] = [];
        lines.push(`# File: ${result.relative_path}`);
        lines.push(``);
        lines.push(`**Size:** ${result.size_bytes?.toLocaleString()} bytes`);
        lines.push(`**Path:** ${result.file_path}`);
        lines.push(``);
        lines.push(`---`);
        lines.push(``);
        lines.push(result.content);

        return {
          content: [
            {
              type: "text",
              text: lines.join("\n"),
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `Error reading file: ${result.error}`,
            },
          ],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [
          {
            type: "text",
            text: `Validation error: ${errorMessage}`,
          },
        ],
        isError: true,
      };
    }
  }

  // Handle write_project_file
  if (name === "write_project_file") {
    try {
      const validatedInput = writeProjectFileSchema.parse(args);
      const result = await writeProjectFile(validatedInput);

      if (result.success) {
        const lines: string[] = [];
        lines.push(`✅ File written: ${result.relative_path}`);
        lines.push(``);
        lines.push(`**Bytes written:** ${result.bytes_written?.toLocaleString()}`);
        lines.push(`**Full path:** ${result.file_path}`);
        if (result.created_dirs) {
          lines.push(`**Created directories:** Yes`);
        }

        return {
          content: [
            {
              type: "text",
              text: lines.join("\n"),
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `Error writing file: ${result.error}`,
            },
          ],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [
          {
            type: "text",
            text: `Validation error: ${errorMessage}`,
          },
        ],
        isError: true,
      };
    }
  }

  // ========== M5 SIMPLE HANDLERS (Manual Mode) ==========
  // Old complex M5 handlers archived to _archive/m5_complex_2026-02-01/

  // Handle m5_simple_start
  if (name === "m5_simple_start") {
    try {
      const validatedInput = m5SimpleStartSchema.parse(args);
      const result = await m5SimpleStart(validatedInput);

      if (result.success) {
        const lines: string[] = [];
        lines.push(`# M5 Enkel Session Startad`);
        lines.push(``);
        lines.push(`**Frågor:** ${result.total_blocks}`);
        lines.push(`**Källa:** ${result.source_file}`);
        lines.push(`**Output:** ${result.output_file}`);
        lines.push(``);
        lines.push(`---`);
        lines.push(``);
        lines.push(`## Block 1 av ${result.total_blocks}`);
        lines.push(``);
        lines.push("```markdown");
        lines.push(result.current_block.content);
        lines.push("```");
        lines.push(``);
        lines.push(result.instructions);

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      } else {
        return {
          content: [{ type: "text", text: `Error: ${result.error}` }],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Handle m5_simple_current
  if (name === "m5_simple_current") {
    try {
      const result = await m5SimpleCurrent();

      if (result.success && result.current_block) {
        const lines: string[] = [];
        lines.push(`## Block ${result.current_block.index} av ${result.current_block.total}`);
        lines.push(``);
        if (result.progress) {
          lines.push(`**Progress:** ${result.progress.approved} godkända, ${result.progress.skipped} hoppade över, ${result.progress.remaining} kvar`);
          lines.push(``);
        }
        lines.push("```markdown");
        lines.push(result.current_block.content);
        lines.push("```");

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      } else {
        return {
          content: [{ type: "text", text: `Error: ${result.error}` }],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Handle m5_simple_create
  if (name === "m5_simple_create") {
    try {
      const validatedInput = m5SimpleCreateSchema.parse(args);
      const result = await m5SimpleCreate(validatedInput);

      if (result.success) {
        const lines: string[] = [];
        lines.push(`✅ **Fråga ${result.question_number} skriven till fil**`);
        lines.push(``);

        if (result.progress) {
          lines.push(`**Progress:** ${result.progress.approved} godkända, ${result.progress.skipped} hoppade över, ${result.progress.remaining} kvar`);
          lines.push(``);
        }

        if (result.session_complete) {
          lines.push(`🎉 **Session klar!** Kör m5_simple_finish för sammanfattning.`);
        } else if (result.next_block) {
          lines.push(`---`);
          lines.push(``);
          lines.push(`## Block ${result.next_block.index} av ${result.next_block.total}`);
          lines.push(``);
          lines.push("```markdown");
          lines.push(result.next_block.content);
          lines.push("```");
        }

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      } else {
        return {
          content: [{ type: "text", text: `Error: ${result.error}` }],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Handle m5_simple_skip
  if (name === "m5_simple_skip") {
    try {
      const validatedInput = m5SimpleSkipSchema.parse(args);
      const result = await m5SimpleSkip(validatedInput);

      if (result.success) {
        const lines: string[] = [];
        lines.push(`⏭️ **Hoppade över block ${result.skipped_block}**`);
        if (result.reason) {
          lines.push(`Anledning: ${result.reason}`);
        }
        lines.push(``);

        if (result.progress) {
          lines.push(`**Progress:** ${result.progress.approved} godkända, ${result.progress.skipped} hoppade över, ${result.progress.remaining} kvar`);
          lines.push(``);
        }

        if (result.session_complete) {
          lines.push(`🎉 **Session klar!** Kör m5_simple_finish för sammanfattning.`);
        } else if (result.next_block) {
          lines.push(`---`);
          lines.push(``);
          lines.push(`## Block ${result.next_block.index} av ${result.next_block.total}`);
          lines.push(``);
          lines.push("```markdown");
          lines.push(result.next_block.content);
          lines.push("```");
        }

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      } else {
        return {
          content: [{ type: "text", text: `Error skipping block` }],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Handle m5_simple_finish
  if (name === "m5_simple_finish") {
    try {
      const result = await m5SimpleFinish();

      if (result.success && result.summary) {
        const lines: string[] = [];
        lines.push(`# M5 Enkel Session Avslutad`);
        lines.push(``);
        lines.push(`## Sammanfattning`);
        lines.push(``);
        lines.push(`| Metric | Antal |`);
        lines.push(`|--------|-------|`);
        lines.push(`| Total block | ${result.summary.total_blocks} |`);
        lines.push(`| Godkända | ${result.summary.approved} |`);
        lines.push(`| Hoppade över | ${result.summary.skipped} |`);
        lines.push(``);
        lines.push(`**Output fil:** ${result.summary.output_file}`);
        lines.push(`**Full path:** ${result.summary.output_path}`);
        lines.push(``);
        lines.push(`---`);
        lines.push(``);
        lines.push(`**Nästa steg:** Kör \`step2_validate\` för att validera QFMD.`);

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      } else {
        return {
          content: [{ type: "text", text: `Error: ${result.error}` }],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Handle m5_simple_status
  if (name === "m5_simple_status") {
    try {
      const result = await m5SimpleStatus();

      const lines: string[] = [];
      lines.push(`# M5 Enkel Session Status`);
      lines.push(``);

      if (!result.active) {
        lines.push(`**Status:** Ingen aktiv session`);
        lines.push(``);
        lines.push(`*Kör m5_simple_start för att börja.*`);
      } else {
        lines.push(`**Källa:** ${result.source_file}`);
        lines.push(`**Output:** ${result.output_file}`);
        lines.push(``);
        if (result.progress) {
          lines.push(`## Progress`);
          lines.push(``);
          lines.push(`| Status | Antal |`);
          lines.push(`|--------|-------|`);
          lines.push(`| Nuvarande | ${result.progress.current} av ${result.progress.total} |`);
          lines.push(`| Godkända | ${result.progress.approved} |`);
          lines.push(`| Hoppade över | ${result.progress.skipped} |`);
          lines.push(`| Kvar | ${result.progress.remaining} |`);
        }
      }

      return {
        content: [{ type: "text", text: lines.join("\n") }],
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Unknown tool
  return {
    content: [
      {
        type: "text",
        text: `Unknown tool: ${name}. Available tools: load_stage, complete_stage, read_materials, read_reference, save_m1_progress, write_m1_stage, read_project_file, write_project_file, m5_simple_start, m5_simple_current, m5_simple_create, m5_simple_skip, m5_simple_finish, m5_simple_status`,
      },
    ],
    isError: true,
  };
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`QF-Scaffolding MCP Server v${VERSION} running (M1-M4 + M5 Simple)`);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
