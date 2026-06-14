/**
 * write_m1_stage tool for qf-scaffolding MCP
 *
 * Direct file writing for M1 stages - what Claude writes = what gets saved.
 * Each stage gets its own file, preventing accidental overwrites.
 *
 * Files created:
 * - m1_stage0_materials.md
 * - m1_stage1_validation.md
 * - m1_stage2_emphasis.md
 * - m1_stage3_examples.md
 * - m1_stage4_misconceptions.md
 * - m1_stage5_objectives.md
 * - m1_progress.yaml (auto-updated)
 */

import { z } from "zod";
import { readFile, writeFile, mkdir } from "fs/promises";
import { join } from "path";
import { existsSync } from "fs";
import * as yaml from "yaml";
import { STAGE_NAMES } from "../utils/m1_constants.js";

// Stage file names
const STAGE_FILES: Record<number, string> = {
  0: "m1_stage0_materials.md",
  1: "m1_stage1_validation.md",
  2: "m1_stage2_emphasis.md",
  3: "m1_stage3_examples.md",
  4: "m1_stage4_misconceptions.md",
  5: "m1_stage5_objectives.md",
};

// Input schema
export const writeM1StageSchema = z.object({
  project_path: z.string(),
  stage: z.number().min(0).max(5),
  content: z.string().min(1), // Raw markdown content
  overwrite: z.boolean().default(false),
});

export type WriteM1StageInput = z.infer<typeof writeM1StageSchema>;

// Progress file structure
interface M1Progress {
  version: string;
  created: string;
  updated: string;
  status: "not_started" | "in_progress" | "complete";
  stages: {
    [key: number]: {
      status: "pending" | "complete";
      file: string;
      completed_at?: string;
      char_count?: number;
    };
  };
}

// Result type
export interface WriteM1StageResult {
  success: boolean;
  file_path?: string;
  stage_name?: string;
  char_count?: number;
  progress?: {
    completed: number[];
    pending: number[];
    status: string;
  };
  error?: string;
}

/**
 * Read or create m1_progress.yaml
 */
async function getProgress(methodologyDir: string): Promise<M1Progress> {
  const progressPath = join(methodologyDir, "m1_progress.yaml");

  if (existsSync(progressPath)) {
    const content = await readFile(progressPath, "utf-8");
    return yaml.parse(content) as M1Progress;
  }

  // Create initial progress
  const now = new Date().toISOString();
  const progress: M1Progress = {
    version: "1.0",
    created: now,
    updated: now,
    status: "not_started",
    stages: {},
  };

  // Initialize all stages as pending
  for (let i = 0; i <= 5; i++) {
    progress.stages[i] = {
      status: "pending",
      file: STAGE_FILES[i],
    };
  }

  return progress;
}

/**
 * Save m1_progress.yaml
 */
async function saveProgress(
  methodologyDir: string,
  progress: M1Progress
): Promise<void> {
  const progressPath = join(methodologyDir, "m1_progress.yaml");
  progress.updated = new Date().toISOString();
  await writeFile(progressPath, yaml.stringify(progress), "utf-8");
}

/**
 * Write content to a specific M1 stage file
 */
export async function writeM1Stage(
  input: WriteM1StageInput
): Promise<WriteM1StageResult> {
  const { project_path, stage, content, overwrite } = input;

  // Validate stage
  if (!STAGE_FILES[stage]) {
    return {
      success: false,
      error: `Invalid stage: ${stage}. Valid stages: 0-5`,
    };
  }

  const methodologyDir = join(project_path, "preparation");
  const filePath = join(methodologyDir, STAGE_FILES[stage]);
  const stageName = STAGE_NAMES[stage];

  try {
    // Ensure directory exists
    if (!existsSync(methodologyDir)) {
      await mkdir(methodologyDir, { recursive: true });
    }

    // Check if file already exists
    if (existsSync(filePath) && !overwrite) {
      return {
        success: false,
        error: `File already exists: ${STAGE_FILES[stage]}. Use overwrite=true to replace.`,
      };
    }

    // Add header to content
    const now = new Date().toISOString();
    const header = [
      `---`,
      `stage: ${stage}`,
      `name: "${stageName}"`,
      `created: ${now}`,
      `---`,
      ``,
    ].join("\n");

    const fullContent = header + content;

    // Write file
    await writeFile(filePath, fullContent, "utf-8");

    // Update progress
    const progress = await getProgress(methodologyDir);
    progress.stages[stage] = {
      status: "complete",
      file: STAGE_FILES[stage],
      completed_at: now,
      char_count: content.length,
    };

    // Update overall status
    const completedStages = Object.entries(progress.stages)
      .filter(([_, s]) => s.status === "complete")
      .map(([k, _]) => parseInt(k));
    const pendingStages = Object.entries(progress.stages)
      .filter(([_, s]) => s.status === "pending")
      .map(([k, _]) => parseInt(k));

    if (completedStages.length === 0) {
      progress.status = "not_started";
    } else if (completedStages.length === 6) {
      progress.status = "complete";
    } else {
      progress.status = "in_progress";
    }

    await saveProgress(methodologyDir, progress);

    return {
      success: true,
      file_path: filePath,
      stage_name: stageName,
      char_count: content.length,
      progress: {
        completed: completedStages.sort((a, b) => a - b),
        pending: pendingStages.sort((a, b) => a - b),
        status: progress.status,
      },
    };
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    return {
      success: false,
      error: `Failed to write stage ${stage}: ${errorMessage}`,
    };
  }
}

