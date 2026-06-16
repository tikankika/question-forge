/**
 * read_reference tool for qf-scaffolding MCP
 *
 * Reads reference documents (syllabus, grading criteria) from project root.
 * These documents are typically saved by step0_start from URLs.
 *
 * RFC-004: Phase 1 - Core Read Tools
 */

import { z } from "zod";
import { readFile, readdir, stat } from "fs/promises";
import { join, extname } from "path";
import { logEvent, logError } from "../utils/logger.js";
import { isPathWithinBase } from "../utils/path_security.js";

// Input schema for read_reference tool
export const readReferenceSchema = z.object({
  project_path: z.string(),
  filename: z.string().optional(), // Specific file, or all reference docs if omitted
});

export type ReadReferenceInput = z.infer<typeof readReferenceSchema>;

// Reference document info
export interface ReferenceInfo {
  filename: string;
  content: string;
  source_url?: string; // If fetched from URL (stored in companion .url file)
}

// Result type for read_reference
export interface ReadReferenceResult {
  success: boolean;
  references: ReferenceInfo[];
  error?: string;
}

// Reference document extensions
const REFERENCE_EXTENSIONS = [".md", ".txt", ".html"];

/**
 * Check if a file is a reference document
 */
function isReferenceDoc(filename: string): boolean {
  const ext = extname(filename).toLowerCase();
  return REFERENCE_EXTENSIONS.includes(ext);
}

/**
 * Read a single reference document
 */
async function readReferenceDoc(
  projectPath: string,
  filename: string
): Promise<ReferenceInfo> {
  const filePath = join(projectPath, filename);

  // Security: prevent path traversal
  if (!isPathWithinBase(projectPath, filePath)) {
    throw new Error(`Security error: path "${filename}" resolves outside project directory`);
  }

  const content = await readFile(filePath, "utf-8");

  // Check for companion .url file with source URL
  const urlFilePath = filePath + ".url";
  let sourceUrl: string | undefined;

  try {
    const urlContent = await readFile(urlFilePath, "utf-8");
    sourceUrl = urlContent.trim();
  } catch {
    // No URL file, that's fine
  }

  return {
    filename,
    content,
    source_url: sourceUrl,
  };
}

/**
 * Read reference documents from project root
 */
export async function readReference(
  input: ReadReferenceInput
): Promise<ReadReferenceResult> {
  const { project_path, filename } = input;
  const startTime = Date.now();

  // Log tool_start (TIER 1)
  logEvent(project_path, "", "read_reference", "tool_start", "info", {
    filename: filename || "all",
  });

  try {
    // Check if project path exists
    try {
      await stat(project_path);
    } catch {
      const error = `Project path not found: ${project_path}`;
      logEvent(
        project_path,
        "",
        "read_reference",
        "tool_end",
        "warn",
        { success: false, error },
        Date.now() - startTime
      );
      return { success: false, references: [], error };
    }

    const references: ReferenceInfo[] = [];

    if (filename) {
      // Read specific file
      try {
        const reference = await readReferenceDoc(project_path, filename);
        references.push(reference);
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "Unknown error";
        const errorText = `Failed to read reference '${filename}': ${errorMessage}`;
        logEvent(
          project_path,
          "",
          "read_reference",
          "tool_end",
          "warn",
          { success: false, error: errorText },
          Date.now() - startTime
        );
        return { success: false, references: [], error: errorText };
      }
    } else {
      // Read all reference documents from project root
      const files = await readdir(project_path);

      for (const file of files) {
        // Skip directories
        const filePath = join(project_path, file);
        const fileStats = await stat(filePath);
        if (fileStats.isDirectory()) continue;

        // Skip non-reference files
        if (!isReferenceDoc(file)) continue;

        // Skip .url companion files
        if (file.endsWith(".url")) continue;

        try {
          const reference = await readReferenceDoc(project_path, file);
          references.push(reference);
        } catch {
          // Skip files that can't be read
        }
      }
    }

    // Log tool_end with success (TIER 1)
    logEvent(
      project_path,
      "",
      "read_reference",
      "tool_end",
      "info",
      {
        success: true,
        files_read: references.length,
        filenames: references.map((r) => r.filename),
      },
      Date.now() - startTime
    );

    return {
      success: true,
      references,
    };
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    const errorStack = error instanceof Error ? error.stack : undefined;

    // Log tool_error (TIER 1)
    logError(
      project_path,
      "read_reference",
      error instanceof Error ? error.constructor.name : "UnknownError",
      errorMessage,
      { stack: errorStack }
    );

    return {
      success: false,
      references: [],
      error: `Failed to read references: ${errorMessage}`,
    };
  }
}
