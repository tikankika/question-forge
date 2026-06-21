/**
 * read_materials tool for qf-scaffolding MCP
 *
 * Reads instructional materials from the project's materials/ folder.
 * Supports PDF text extraction, markdown, and text files.
 *
 * RFC-004: Phase 2 - Updated with filename parameter
 *
 * Two modes:
 * - List mode (filename=null/undefined): Returns file list with metadata, NO content
 * - Read mode (filename="X.pdf"): Returns content of ONE specific file
 */

import { z } from "zod";
import { existsSync } from "fs";
import { readFile, readdir, stat } from "fs/promises";
import { join, extname, basename } from "path";
import { PDFParse } from "pdf-parse";
import { logEvent, logError } from "../utils/logger.js";
import { isPathWithinBase } from "../utils/path_security.js";
import {
  detectCourseRoot,
  listCourseMaterials,
  classifyCourseFile,
} from "../utils/course_vault.js";

/** Prefix that identifies a course-vault file in shared mode (read in place). */
const COURSE_PREFIX = "course:";

// Input schema for read_materials tool
export const readMaterialsSchema = z.object({
  project_path: z.string(),
  filename: z.string().nullable().optional(), // NEW: null/undefined → list, "X.pdf" → read one
  file_pattern: z.string().optional(), // DEPRECATED: kept for backwards compatibility
  extract_text: z.boolean().optional().default(true), // Extract text from PDFs
});

export type ReadMaterialsInput = z.infer<typeof readMaterialsSchema>;

// File info type (for list mode - no content)
export interface FileInfo {
  filename: string;
  size_bytes: number;
  content_type: "pdf" | "md" | "txt" | "pptx" | "other";
  /** "project" = <project>/materials/; "course" = read-in-place from the
   * course vault (filename is prefixed `course:`). Absent ⇒ project (legacy). */
  source?: "project" | "course";
}

// Material info type (for read mode - with content)
export interface MaterialInfo {
  filename: string;
  path: string;
  content_type: "pdf" | "md" | "txt" | "pptx" | "other";
  size_bytes: number;
  text_content?: string;
  error?: string;
}

// Result type for read_materials (supports both modes)
export interface ReadMaterialsResult {
  success: boolean;
  mode: "list" | "read";

  // List mode result
  files?: FileInfo[];

  // Read mode result
  material?: MaterialInfo;

  // Common fields
  total_files: number;
  total_chars?: number;
  error?: string;

  // Legacy field (for backwards compatibility)
  materials?: MaterialInfo[];
}

/**
 * Determine content type from file extension
 */
function getContentType(filename: string): MaterialInfo["content_type"] {
  const ext = extname(filename).toLowerCase();
  switch (ext) {
    case ".pdf":
      return "pdf";
    case ".md":
    case ".markdown":
      return "md";
    case ".txt":
      return "txt";
    case ".pptx":
      return "pptx";
    default:
      return "other";
  }
}

/**
 * Check if filename matches pattern
 * Supports simple glob patterns: *.pdf, lecture*, *analysis*
 */
function matchesPattern(filename: string, pattern?: string): boolean {
  if (!pattern) return true;

  // Convert glob pattern to regex
  const regexPattern = pattern
    .replace(/\./g, "\\.") // Escape dots
    .replace(/\*/g, ".*"); // * becomes .*

  const regex = new RegExp(`^${regexPattern}$`, "i");
  return regex.test(filename);
}

/**
 * Extract text from PDF file using pdf-parse library
 */
async function extractPdfText(filePath: string): Promise<string> {
  const buffer = await readFile(filePath);
  const pdfParser = new PDFParse({ data: buffer });
  const textResult = await pdfParser.getText();
  await pdfParser.destroy();
  return textResult.text;
}

/**
 * Read a single material file (with text extraction)
 */
async function readMaterial(
  filePath: string,
  filename: string,
  extractText: boolean
): Promise<MaterialInfo> {
  const contentType = getContentType(filename);
  const stats = await stat(filePath);

  const material: MaterialInfo = {
    filename,
    path: filePath,
    content_type: contentType,
    size_bytes: stats.size,
  };

  if (extractText) {
    try {
      switch (contentType) {
        case "pdf":
          material.text_content = await extractPdfText(filePath);
          break;
        case "md":
        case "txt":
          material.text_content = await readFile(filePath, "utf-8");
          break;
        case "pptx":
          material.error = "PPTX extraction not yet implemented";
          break;
        default:
          material.error = `Cannot extract text from ${contentType} files`;
      }
    } catch (error) {
      material.error =
        error instanceof Error ? error.message : "Unknown extraction error";
    }
  }

  return material;
}

/**
 * Read an allowlisted course-vault file in place (shared mode). The course path
 * is validated by classifyCourseFile (default-deny: traversal, Data/ raw, and
 * unsafe roles are rejected), so no file outside the safe zones is read.
 */
async function readCourseFile(
  projectPath: string,
  courseRoot: string | null,
  filename: string,
  extractText: boolean,
  startTime: number
): Promise<ReadMaterialsResult> {
  if (!courseRoot) {
    return {
      success: false,
      mode: "read",
      total_files: 0,
      error: "Not inside a course vault — 'course:' paths require shared mode",
    };
  }

  const rel = filename.slice(COURSE_PREFIX.length);
  const abs = join(courseRoot, rel);

  const decision = await classifyCourseFile(courseRoot, abs);
  if (!decision.admit) {
    return {
      success: false,
      mode: "read",
      total_files: 0,
      error: `Allowlist error: "${rel}" is not readable (${decision.reason})`,
    };
  }

  try {
    await stat(abs);
  } catch {
    return { success: false, mode: "read", total_files: 0, error: `File not found: ${rel}` };
  }

  const material = await readMaterial(abs, basename(rel), extractText);
  const totalChars = material.text_content?.length ?? 0;
  logEvent(
    projectPath,
    "",
    "read_materials",
    "tool_end",
    "info",
    { success: true, mode: "read", filename, source: "course", total_chars: totalChars },
    Date.now() - startTime
  );
  return { success: true, mode: "read", material, total_files: 1, total_chars: totalChars };
}

/**
 * Read instructional materials from project's materials/ folder
 *
 * Two modes:
 * - filename=null/undefined: List all files (metadata only, no content)
 * - filename="X.pdf": Read and extract text from ONE specific file
 */
export async function readMaterials(
  input: z.input<typeof readMaterialsSchema>
): Promise<ReadMaterialsResult> {
  const { project_path, filename, file_pattern, extract_text = true } = input;
  const startTime = Date.now();

  // Determine mode
  const isListMode = filename === null || filename === undefined;
  const mode = isListMode ? "list" : "read";

  // Log tool_start (TIER 1)
  logEvent(project_path, "", "read_materials", "tool_start", "info", {
    mode,
    filename: filename ?? null,
    file_pattern,
    extract_text,
  });

  const materialsPath = join(project_path, "materials");
  const courseRoot = detectCourseRoot(project_path);

  try {
    // Shared course-vault mode: read an allowlisted course file in place.
    if (!isListMode && filename && filename.startsWith(COURSE_PREFIX)) {
      return await readCourseFile(project_path, courseRoot, filename, extract_text, startTime);
    }

    // Project materials/ folder. Standalone: it must exist. Shared mode: a
    // missing folder is fine — course material is read in place instead.
    const haveProjectMaterials = existsSync(materialsPath);
    if (!haveProjectMaterials && !courseRoot) {
      const error = `Materials folder not found: ${materialsPath}`;
      logEvent(
        project_path,
        "",
        "read_materials",
        "tool_end",
        "warn",
        { success: false, error, mode },
        Date.now() - startTime
      );
      return { success: false, mode, total_files: 0, error };
    }

    // ========== LIST MODE ==========
    if (isListMode) {
      const files: FileInfo[] = [];

      const allFiles = haveProjectMaterials ? await readdir(materialsPath) : [];
      for (const fname of allFiles) {
        const filePath = join(materialsPath, fname);
        const fileStats = await stat(filePath);

        // Skip directories
        if (fileStats.isDirectory()) continue;

        // Apply pattern filter if provided (backwards compatibility)
        if (file_pattern && !matchesPattern(fname, file_pattern)) continue;

        files.push({
          filename: fname,
          size_bytes: fileStats.size,
          content_type: getContentType(fname),
          source: "project",
        });
      }

      // Shared mode: also surface allowlisted course material (read in place,
      // no copy). Entries are `course:`-prefixed and marked source "course".
      if (courseRoot) {
        for (const cm of await listCourseMaterials(courseRoot)) {
          files.push({
            filename: COURSE_PREFIX + cm.relPath,
            size_bytes: cm.size_bytes,
            content_type: cm.content_type,
            source: "course",
          });
        }
      }

      // Sort by filename
      files.sort((a, b) => a.filename.localeCompare(b.filename));

      logEvent(
        project_path,
        "",
        "read_materials",
        "tool_end",
        "info",
        {
          success: true,
          mode: "list",
          total_files: files.length,
          content_types: files.reduce(
            (acc, f) => {
              acc[f.content_type] = (acc[f.content_type] || 0) + 1;
              return acc;
            },
            {} as Record<string, number>
          ),
        },
        Date.now() - startTime
      );

      return {
        success: true,
        mode: "list",
        files,
        total_files: files.length,
      };
    }

    // ========== READ MODE ==========
    const filePath = join(materialsPath, filename);

    // Security: prevent path traversal
    if (!isPathWithinBase(materialsPath, filePath)) {
      return {
        success: false,
        mode: "read",
        total_files: 0,
        error: `Security error: path "${filename}" resolves outside materials directory`,
      };
    }

    // Check if file exists
    try {
      await stat(filePath);
    } catch {
      const error = `File not found: ${filename}`;
      logEvent(
        project_path,
        "",
        "read_materials",
        "tool_end",
        "warn",
        { success: false, error, mode: "read", filename },
        Date.now() - startTime
      );
      return { success: false, mode: "read", total_files: 0, error };
    }

    // Read the specific file
    const material = await readMaterial(filePath, filename, extract_text);
    const totalChars = material.text_content?.length ?? 0;

    logEvent(
      project_path,
      "",
      "read_materials",
      "tool_end",
      "info",
      {
        success: true,
        mode: "read",
        filename,
        content_type: material.content_type,
        size_bytes: material.size_bytes,
        total_chars: totalChars,
        has_error: !!material.error,
      },
      Date.now() - startTime
    );

    return {
      success: true,
      mode: "read",
      material,
      total_files: 1,
      total_chars: totalChars,
    };
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    const errorStack = error instanceof Error ? error.stack : undefined;

    // Log tool_error (TIER 1)
    logError(
      project_path,
      "read_materials",
      error instanceof Error ? error.constructor.name : "UnknownError",
      errorMessage,
      { stack: errorStack, mode, filename }
    );

    return {
      success: false,
      mode,
      total_files: 0,
      error: `Failed to read materials: ${errorMessage}`,
    };
  }
}
