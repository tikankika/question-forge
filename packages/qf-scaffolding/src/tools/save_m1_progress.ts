/**
 * save_m1_progress tool for qf-scaffolding MCP
 *
 * Progressive saving tool for M1 (Material Analysis).
 * All M1 stages save to a single document: preparation/m1_analysis.md
 *
 * RFC-004: Phase 2 - Progressive Saving
 *
 * Three actions:
 * - add_material: Progressive saves during Stage 0 (after each PDF)
 * - save_stage: Saves completed stage output (Stage 0-5)
 * - finalize_m1: Marks M1 complete, ready for M2
 */

import { z } from "zod";
import { readFile, writeFile, mkdir } from "fs/promises";
import { join, dirname } from "path";
import { existsSync } from "fs";
import { logEvent, logError } from "../utils/logger.js";
import { STAGE_NAMES } from "../utils/m1_constants.js";
import * as yaml from "yaml";

// Material analysis data (for add_material action)
// SIMPLIFIED: Just filename + raw markdown content
// What Claude presents = what gets saved (no transformation)
const MaterialDataSchema = z.object({
  filename: z.string(),
  content: z.string(), // Raw markdown - saved exactly as provided
});

// Stage output data (for save_stage action)
const StageOutputSchema = z.object({
  stage_name: z.string(),
  content: z.string(), // Markdown content for this stage
  teacher_approved: z.boolean().optional(),
});

// Final summary data (for finalize_m1 action)
const FinalSummarySchema = z.object({
  total_materials: z.number(),
  learning_objectives_count: z.number(),
  ready_for_m2: z.boolean(),
  summary: z.string().optional(),
});

// Input schema for save_m1_progress tool
export const saveM1ProgressSchema = z.object({
  project_path: z.string(),
  stage: z.number().min(0).max(5).optional(), // Which M1 stage (0-5)
  action: z.enum(["add_material", "save_stage", "finalize_m1"]),
  data: z.object({
    material: MaterialDataSchema.optional(),
    stage_output: StageOutputSchema.optional(),
    final_summary: FinalSummarySchema.optional(),
  }),
});

export type SaveM1ProgressInput = z.infer<typeof saveM1ProgressSchema>;

// Result type
export interface SaveM1ProgressResult {
  success: boolean;
  current_stage: number;
  stages_completed: number[];
  materials_analyzed?: number;
  total_materials?: number;
  document_path: string;
  error?: string;
}

// Document frontmatter type
interface M1Frontmatter {
  qf_type: string;
  qf_version: string;
  created: string;
  updated: string;
  session_id: string;
  status: "in_progress" | "complete";
  current_stage: number;
  stages_completed: number[];
  materials_analyzed: number;
  total_materials: number;
}

// STAGE_NAMES imported from ../utils/m1_constants.js

/**
 * Parse YAML frontmatter from markdown document
 */
function parseFrontmatter(content: string): {
  frontmatter: M1Frontmatter | null;
  body: string;
} {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) {
    return { frontmatter: null, body: content };
  }

  try {
    const frontmatter = yaml.parse(match[1]) as M1Frontmatter;
    return { frontmatter, body: match[2] };
  } catch {
    return { frontmatter: null, body: content };
  }
}

/**
 * Generate YAML frontmatter string
 */
function generateFrontmatter(fm: M1Frontmatter): string {
  return `---\n${yaml.stringify(fm)}---\n`;
}

/**
 * Create initial document structure
 */
function createInitialDocument(sessionId: string): string {
  const now = new Date().toISOString();
  const frontmatter: M1Frontmatter = {
    qf_type: "m1_analysis",
    qf_version: "1.0",
    created: now,
    updated: now,
    session_id: sessionId,
    status: "in_progress",
    current_stage: 0,
    stages_completed: [],
    materials_analyzed: 0,
    total_materials: 0,
  };

  const body = `
# M1: Material Analysis

## Stage 0: Material Analysis
*In Progress*

`;

  return generateFrontmatter(frontmatter) + body;
}

/**
 * Format material analysis as markdown
 * SIMPLIFIED: Just adds header, passes content through as-is
 */
function formatMaterialMarkdown(
  material: z.infer<typeof MaterialDataSchema>,
  index: number,
  total: number
): string {
  // Header + raw content (no transformation)
  return `### Material ${index}/${total}: ${material.filename}\n\n${material.content}\n`;
}

/**
 * Read session.yaml to get session_id
 */
async function getSessionId(projectPath: string): Promise<string> {
  try {
    const sessionPath = join(projectPath, "session.yaml");
    const content = await readFile(sessionPath, "utf-8");
    const session = yaml.parse(content);
    return session?.session?.id || "unknown";
  } catch {
    return "unknown";
  }
}

/**
 * Update session.yaml with M1 progress
 */
async function updateSessionYaml(
  projectPath: string,
  currentStage: number,
  stagesCompleted: number[],
  materialsAnalyzed: number,
  totalMaterials: number,
  isComplete: boolean
): Promise<void> {
  const sessionPath = join(projectPath, "session.yaml");

  try {
    let session: Record<string, unknown> = {};

    if (existsSync(sessionPath)) {
      const content = await readFile(sessionPath, "utf-8");
      session = yaml.parse(content) || {};
    }

    // Update methodology.m1 section
    if (!session.methodology) {
      session.methodology = {};
    }

    const methodology = session.methodology as Record<string, unknown>;
    methodology.m1 = {
      status: isComplete ? "complete" : "in_progress",
      current_stage: currentStage,
      stages_completed: stagesCompleted,
      output: "preparation/m1_analysis.md",
      materials_analyzed: materialsAnalyzed,
      total_materials: totalMaterials,
      last_updated: new Date().toISOString(),
    };

    await writeFile(sessionPath, yaml.stringify(session), "utf-8");
  } catch (error) {
    // Log but don't fail - session.yaml update is secondary
    console.error("Failed to update session.yaml:", error);
  }
}

/**
 * Save M1 progress to m1_analysis.md
 */
export async function saveM1Progress(
  input: SaveM1ProgressInput
): Promise<SaveM1ProgressResult> {
  const { project_path, stage, action, data } = input;
  const startTime = Date.now();

  const documentPath = join(project_path, "preparation", "m1_analysis.md");

  // Log tool_start
  logEvent(project_path, "", "save_m1_progress", "tool_start", "info", {
    action,
    stage,
  });

  try {
    // Ensure directory exists
    const dir = dirname(documentPath);
    if (!existsSync(dir)) {
      await mkdir(dir, { recursive: true });
    }

    // Read existing document or create new
    let content: string;
    let frontmatter: M1Frontmatter;
    let body: string;

    if (existsSync(documentPath)) {
      content = await readFile(documentPath, "utf-8");
      const parsed = parseFrontmatter(content);

      if (parsed.frontmatter) {
        frontmatter = parsed.frontmatter;
        body = parsed.body;
      } else {
        // Document exists but has no frontmatter - treat as new
        const sessionId = await getSessionId(project_path);
        content = createInitialDocument(sessionId);
        const parsed2 = parseFrontmatter(content);
        frontmatter = parsed2.frontmatter!;
        body = parsed2.body;
      }
    } else {
      // Create new document
      const sessionId = await getSessionId(project_path);
      content = createInitialDocument(sessionId);
      const parsed = parseFrontmatter(content);
      frontmatter = parsed.frontmatter!;
      body = parsed.body;
    }

    // Handle action
    switch (action) {
      case "add_material": {
        if (!data.material) {
          throw new Error("add_material action requires data.material");
        }
        if (stage !== 0 && stage !== undefined) {
          throw new Error("add_material action is only valid for stage 0");
        }

        // Increment materials count
        frontmatter.materials_analyzed += 1;
        if (frontmatter.total_materials < frontmatter.materials_analyzed) {
          frontmatter.total_materials = frontmatter.materials_analyzed;
        }

        // Format and append material
        const materialMd = formatMaterialMarkdown(
          data.material,
          frontmatter.materials_analyzed,
          frontmatter.total_materials
        );

        // Find the Stage 0 section and append material
        const stage0Header = "## Stage 0: Material Analysis";
        const stage1Header = "## Stage 1:";

        const stage0Index = body.indexOf(stage0Header);
        const stage1Index = body.indexOf(stage1Header);

        if (stage0Index !== -1) {
          if (stage1Index !== -1 && stage1Index > stage0Index) {
            // Insert before Stage 1
            body =
              body.slice(0, stage1Index) +
              materialMd +
              "\n" +
              body.slice(stage1Index);
          } else {
            // Append at end
            body = body + materialMd;
          }
        } else {
          // No Stage 0 section - append
          body = body + "\n" + stage0Header + "\n*In Progress*\n\n" + materialMd;
        }

        break;
      }

      case "save_stage": {
        if (!data.stage_output) {
          throw new Error("save_stage action requires data.stage_output");
        }
        if (stage === undefined) {
          throw new Error("save_stage action requires stage parameter");
        }

        const stageNum = stage;
        const stageName = STAGE_NAMES[stageNum] || `Stage ${stageNum}`;
        const now = new Date().toISOString();

        // Mark stage as completed
        if (!frontmatter.stages_completed.includes(stageNum)) {
          frontmatter.stages_completed.push(stageNum);
          frontmatter.stages_completed.sort((a, b) => a - b);
        }

        // Update current stage
        frontmatter.current_stage = Math.max(
          frontmatter.current_stage,
          stageNum + 1
        );

        // Find or create stage section
        const stageHeader = `## Stage ${stageNum}: ${stageName}`;
        const nextStageHeader = `## Stage ${stageNum + 1}:`;

        // Build stage content
        const stageContent = `${stageHeader} ✅
*Completed: ${now}*

${data.stage_output.content}

---

`;

        // Replace existing stage section or append
        const stageIndex = body.indexOf(`## Stage ${stageNum}:`);
        const nextIndex = body.indexOf(nextStageHeader);

        if (stageIndex !== -1) {
          // Find end of current stage section
          let endIndex = nextIndex !== -1 ? nextIndex : body.length;

          // Also check for horizontal rule as section separator
          const hrIndex = body.indexOf("\n---\n", stageIndex + stageHeader.length);
          if (hrIndex !== -1 && hrIndex < endIndex) {
            endIndex = hrIndex + 5; // Include the ---\n
          }

          body = body.slice(0, stageIndex) + stageContent + body.slice(endIndex);
        } else {
          // Append new stage section
          body = body + "\n" + stageContent;
        }

        break;
      }

      case "finalize_m1": {
        if (!data.final_summary) {
          throw new Error("finalize_m1 action requires data.final_summary");
        }

        // Mark M1 as complete
        frontmatter.status = "complete";
        frontmatter.current_stage = 5;

        // Add final summary section
        const finalSection = `
## M1 Final Summary ✅
*Finalized: ${new Date().toISOString()}*

- **Total Materials Analyzed:** ${data.final_summary.total_materials}
- **Learning Objectives:** ${data.final_summary.learning_objectives_count}
- **Ready for M2:** ${data.final_summary.ready_for_m2 ? "Yes" : "No"}

${data.final_summary.summary || ""}

---
*M1 Complete - Proceed to M2 (Assessment Design)*
`;

        // Append or replace final summary
        const finalIndex = body.indexOf("## M1 Final Summary");
        if (finalIndex !== -1) {
          body = body.slice(0, finalIndex) + finalSection;
        } else {
          body = body + "\n" + finalSection;
        }

        break;
      }
    }

    // Update frontmatter timestamp
    frontmatter.updated = new Date().toISOString();

    // Write updated document
    const newContent = generateFrontmatter(frontmatter) + body;
    await writeFile(documentPath, newContent, "utf-8");

    // Update session.yaml
    await updateSessionYaml(
      project_path,
      frontmatter.current_stage,
      frontmatter.stages_completed,
      frontmatter.materials_analyzed,
      frontmatter.total_materials,
      frontmatter.status === "complete"
    );

    // Log success
    logEvent(
      project_path,
      "",
      "save_m1_progress",
      "tool_end",
      "info",
      {
        success: true,
        action,
        stage,
        current_stage: frontmatter.current_stage,
        stages_completed: frontmatter.stages_completed,
        materials_analyzed: frontmatter.materials_analyzed,
      },
      Date.now() - startTime
    );

    return {
      success: true,
      current_stage: frontmatter.current_stage,
      stages_completed: frontmatter.stages_completed,
      materials_analyzed: frontmatter.materials_analyzed,
      total_materials: frontmatter.total_materials,
      document_path: documentPath,
    };
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    const errorStack = error instanceof Error ? error.stack : undefined;

    logError(
      project_path,
      "save_m1_progress",
      error instanceof Error ? error.constructor.name : "UnknownError",
      errorMessage,
      { stack: errorStack, action, stage }
    );

    return {
      success: false,
      current_stage: stage ?? 0,
      stages_completed: [],
      document_path: documentPath,
      error: `Failed to save M1 progress: ${errorMessage}`,
    };
  }
}
