/**
 * M5 Simple Tools - Manual Mode
 *
 * Simplified M5 workflow:
 * 1. Split file by "---"
 * 2. Show each block to teacher
 * 3. Teacher creates/confirms QFMD
 * 4. Write to output
 *
 * No auto-detection, no pattern learning - just simple human-in-the-loop.
 */

import { z } from "zod";
import * as fs from "fs";
import * as path from "path";
import { isPathWithinBase } from "../utils/path_security.js";
import { fileURLToPath } from "url";

// ============================================================================
// M5 Methodology Path
// ============================================================================

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const M5_METHODOLOGY_PATH = path.resolve(
  __dirname,
  "../../../../methodology/m5"
);

/**
 * Read FORMAT_REFERENCE.md and return instructions for Claude Desktop
 */
function getM5Instructions(totalBlocks: number, sourceFile: string): string {
  const formatRefPath = path.join(M5_METHODOLOGY_PATH, "FORMAT_REFERENCE.md");

  let formatReference = "";
  try {
    if (fs.existsSync(formatRefPath)) {
      formatReference = fs.readFileSync(formatRefPath, "utf-8");
    } else {
      formatReference = `**VARNING:** FORMAT_REFERENCE.md hittades inte på ${formatRefPath}`;
    }
  } catch (err) {
    formatReference = `**FEL:** Kunde inte läsa FORMAT_REFERENCE.md: ${err}`;
  }

  return `
## M5 Manuell Session Startad

**${totalBlocks} frågor** hittades i ${sourceFile}.

### Workflow:

1. **Läs** råinnehållet för varje block
2. **Följ FORMAT_REFERENCE nedan** för korrekt QFMD-struktur
3. **Skapa QFMD** med m5_simple_create({ qfmd: "..." })
4. Eller **hoppa över** med m5_simple_skip()

### Efter M5:

Kör \`step2_validate\` för att verifiera formatet.

---

# FORMAT REFERENCE

${formatReference}
`;
}

// ============================================================================
// Simple Session State (in-memory)
// ============================================================================

interface SimpleSession {
  projectPath: string;
  sourceFile: string;
  outputFile: string;
  blocks: string[];
  currentIndex: number;
  approved: number;
  skipped: number;
  startedAt: string;
}

let currentSession: SimpleSession | null = null;

// ============================================================================
// Schemas
// ============================================================================

export const m5SimpleStartSchema = z.object({
  project_path: z.string().describe("Absolute path to the project folder"),
  source_file: z
    .string()
    .optional()
    .describe("Relative path to source file. Default: questions/m3_output.md"),
  output_file: z
    .string()
    .optional()
    .describe("Relative path for output. Default: questions/m5_output.md"),
  separator: z
    .string()
    .optional()
    .describe("Block separator. Default: ---"),
});

export const m5SimpleCreateSchema = z.object({
  qfmd: z.string().describe("The QFMD content for this question"),
});

export const m5SimpleSkipSchema = z.object({
  reason: z.string().optional().describe("Why skipping this block"),
});

// ============================================================================
// Tool: m5_simple_start
// ============================================================================

export interface M5SimpleStartResult {
  success: boolean;
  error?: string;
  total_blocks: number;
  source_file: string;
  output_file: string;
  current_block: {
    index: number;
    total: number;
    content: string;
  };
  instructions: string;
}

export async function m5SimpleStart(
  input: z.infer<typeof m5SimpleStartSchema>
): Promise<M5SimpleStartResult> {
  const projectPath = input.project_path;
  const sourceFile = input.source_file || "questions/m3_output.md";
  const outputFile = input.output_file || "questions/m5_output.md";
  const separator = input.separator || "---";

  const sourcePath = path.join(projectPath, sourceFile);
  const outputPath = path.join(projectPath, outputFile);

  // Security: prevent path traversal
  if (!isPathWithinBase(projectPath, sourcePath) || !isPathWithinBase(projectPath, outputPath)) {
    return {
      success: false,
      error: "Security error: file paths must not escape the project directory",
      total_blocks: 0,
      source_file: sourceFile,
      output_file: outputFile,
      current_block: { index: 0, total: 0, content: "" },
      instructions: "",
    };
  }

  // Check file exists
  if (!fs.existsSync(sourcePath)) {
    return {
      success: false,
      error: `Fil finns inte: ${sourceFile}`,
      total_blocks: 0,
      source_file: sourceFile,
      output_file: outputFile,
      current_block: { index: 0, total: 0, content: "" },
      instructions: "",
    };
  }

  // Read and split
  const content = fs.readFileSync(sourcePath, "utf-8");
  const blocks = content
    .split(new RegExp(`\\n${separator}\\n`))
    .map((b) => b.trim())
    .filter((b) => b.length > 0);

  if (blocks.length === 0) {
    return {
      success: false,
      error: `Inga block hittades. Kontrollera att filen använder "${separator}" som separator.`,
      total_blocks: 0,
      source_file: sourceFile,
      output_file: outputFile,
      current_block: { index: 0, total: 0, content: "" },
      instructions: "",
    };
  }

  // Clear output file if exists
  if (fs.existsSync(outputPath)) {
    const backupPath = outputPath.replace(".md", `_backup_${Date.now()}.md`);
    fs.renameSync(outputPath, backupPath);
  }

  // Create session
  currentSession = {
    projectPath,
    sourceFile,
    outputFile,
    blocks,
    currentIndex: 0,
    approved: 0,
    skipped: 0,
    startedAt: new Date().toISOString(),
  };

  return {
    success: true,
    total_blocks: blocks.length,
    source_file: sourceFile,
    output_file: outputFile,
    current_block: {
      index: 1,
      total: blocks.length,
      content: blocks[0],
    },
    instructions: getM5Instructions(blocks.length, sourceFile),
  };
}

// ============================================================================
// Tool: m5_simple_current
// ============================================================================

export interface M5SimpleCurrentResult {
  success: boolean;
  error?: string;
  current_block?: {
    index: number;
    total: number;
    content: string;
  };
  progress?: {
    approved: number;
    skipped: number;
    remaining: number;
  };
}

export async function m5SimpleCurrent(): Promise<M5SimpleCurrentResult> {
  if (!currentSession) {
    return {
      success: false,
      error: "Ingen aktiv session. Kör m5_simple_start först.",
    };
  }

  const { blocks, currentIndex, approved, skipped } = currentSession;

  if (currentIndex >= blocks.length) {
    return {
      success: false,
      error: "Alla block är bearbetade. Kör m5_simple_finish.",
    };
  }

  return {
    success: true,
    current_block: {
      index: currentIndex + 1,
      total: blocks.length,
      content: blocks[currentIndex],
    },
    progress: {
      approved,
      skipped,
      remaining: blocks.length - currentIndex,
    },
  };
}

// ============================================================================
// Tool: m5_simple_create
// ============================================================================

export interface M5SimpleCreateResult {
  success: boolean;
  error?: string;
  written: boolean;
  question_number?: number;
  next_block?: {
    index: number;
    total: number;
    content: string;
  };
  session_complete?: boolean;
  progress?: {
    approved: number;
    skipped: number;
    remaining: number;
  };
}

export async function m5SimpleCreate(
  input: z.infer<typeof m5SimpleCreateSchema>
): Promise<M5SimpleCreateResult> {
  if (!currentSession) {
    return {
      success: false,
      error: "Ingen aktiv session. Kör m5_simple_start först.",
      written: false,
    };
  }

  const qfmd = input.qfmd.trim();

  // Basic validation
  if (!qfmd.includes("^type") && !qfmd.includes("@field:")) {
    return {
      success: false,
      error: "Ogiltig QFMD: Saknar ^type eller @field: struktur.",
      written: false,
    };
  }

  // Write to output file
  const outputPath = path.join(
    currentSession.projectPath,
    currentSession.outputFile
  );

  // Ensure directory exists
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Append with separator
  const fileExists = fs.existsSync(outputPath);
  const separator = fileExists ? "\n\n---\n\n" : "";
  const header = fileExists
    ? ""
    : `<!-- QFMD Generated by M5 Simple -->\n<!-- ${new Date().toISOString()} -->\n\n`;

  fs.appendFileSync(outputPath, header + separator + qfmd + "\n", "utf-8");

  // Advance session
  const questionNumber = currentSession.currentIndex + 1;
  currentSession.approved++;
  currentSession.currentIndex++;

  // Check if done
  if (currentSession.currentIndex >= currentSession.blocks.length) {
    return {
      success: true,
      written: true,
      question_number: questionNumber,
      session_complete: true,
      progress: {
        approved: currentSession.approved,
        skipped: currentSession.skipped,
        remaining: 0,
      },
    };
  }

  // Return next block
  return {
    success: true,
    written: true,
    question_number: questionNumber,
    next_block: {
      index: currentSession.currentIndex + 1,
      total: currentSession.blocks.length,
      content: currentSession.blocks[currentSession.currentIndex],
    },
    progress: {
      approved: currentSession.approved,
      skipped: currentSession.skipped,
      remaining:
        currentSession.blocks.length - currentSession.currentIndex,
    },
  };
}

// ============================================================================
// Tool: m5_simple_skip
// ============================================================================

export interface M5SimpleSkipResult {
  success: boolean;
  skipped_block?: number;
  reason?: string;
  next_block?: {
    index: number;
    total: number;
    content: string;
  };
  session_complete?: boolean;
  progress?: {
    approved: number;
    skipped: number;
    remaining: number;
  };
}

export async function m5SimpleSkip(
  input: z.infer<typeof m5SimpleSkipSchema>
): Promise<M5SimpleSkipResult> {
  if (!currentSession) {
    return { success: false };
  }

  const skippedBlock = currentSession.currentIndex + 1;
  currentSession.skipped++;
  currentSession.currentIndex++;

  // Check if done
  if (currentSession.currentIndex >= currentSession.blocks.length) {
    return {
      success: true,
      skipped_block: skippedBlock,
      reason: input.reason,
      session_complete: true,
      progress: {
        approved: currentSession.approved,
        skipped: currentSession.skipped,
        remaining: 0,
      },
    };
  }

  return {
    success: true,
    skipped_block: skippedBlock,
    reason: input.reason,
    next_block: {
      index: currentSession.currentIndex + 1,
      total: currentSession.blocks.length,
      content: currentSession.blocks[currentSession.currentIndex],
    },
    progress: {
      approved: currentSession.approved,
      skipped: currentSession.skipped,
      remaining:
        currentSession.blocks.length - currentSession.currentIndex,
    },
  };
}

// ============================================================================
// Tool: m5_simple_finish
// ============================================================================

export interface M5SimpleFinishResult {
  success: boolean;
  error?: string;
  summary?: {
    total_blocks: number;
    approved: number;
    skipped: number;
    output_file: string;
    output_path: string;
  };
}

export async function m5SimpleFinish(): Promise<M5SimpleFinishResult> {
  if (!currentSession) {
    return {
      success: false,
      error: "Ingen aktiv session.",
    };
  }

  const summary = {
    total_blocks: currentSession.blocks.length,
    approved: currentSession.approved,
    skipped: currentSession.skipped,
    output_file: currentSession.outputFile,
    output_path: path.join(
      currentSession.projectPath,
      currentSession.outputFile
    ),
  };

  // Clear session
  currentSession = null;

  return {
    success: true,
    summary,
  };
}

// ============================================================================
// Tool: m5_simple_status
// ============================================================================

export interface M5SimpleStatusResult {
  active: boolean;
  source_file?: string;
  output_file?: string;
  progress?: {
    current: number;
    total: number;
    approved: number;
    skipped: number;
    remaining: number;
  };
}

export async function m5SimpleStatus(): Promise<M5SimpleStatusResult> {
  if (!currentSession) {
    return { active: false };
  }

  return {
    active: true,
    source_file: currentSession.sourceFile,
    output_file: currentSession.outputFile,
    progress: {
      current: currentSession.currentIndex + 1,
      total: currentSession.blocks.length,
      approved: currentSession.approved,
      skipped: currentSession.skipped,
      remaining:
        currentSession.blocks.length - currentSession.currentIndex,
    },
  };
}
