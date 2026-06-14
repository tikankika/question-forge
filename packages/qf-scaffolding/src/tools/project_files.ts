/**
 * Project file tools for qf-scaffolding MCP
 *
 * General-purpose file read/write within project directory.
 * Allows Claude to access ANY file within the project, not just
 * specific folders like materials/ or questions/.
 *
 * Security: Only allows access within project_path (no path traversal)
 */

import { z } from "zod";
import { readFile, writeFile, mkdir, stat } from "fs/promises";
import { join, dirname, normalize, relative, isAbsolute } from "path";
import { existsSync } from "fs";
import { logEvent, logError } from "../utils/logger.js";

// ============================================
// READ PROJECT FILE
// ============================================

export const readProjectFileSchema = z.object({
  project_path: z.string(),
  relative_path: z.string(), // Path relative to project_path, e.g. "output/questions.md"
});

export type ReadProjectFileInput = z.infer<typeof readProjectFileSchema>;

export interface ReadProjectFileResult {
  success: boolean;
  file_path?: string;
  relative_path?: string;
  content?: string;
  size_bytes?: number;
  error?: string;
}

/**
 * Validate that the resolved path is within project_path (prevent path traversal)
 */
function isPathWithinProject(projectPath: string, targetPath: string): boolean {
  const normalizedProject = normalize(projectPath);
  const normalizedTarget = normalize(targetPath);
  const relativePath = relative(normalizedProject, normalizedTarget);

  // If relative path starts with ".." or is absolute, it's outside project
  return (
    !relativePath.startsWith("..") &&
    !isAbsolute(relativePath) &&
    relativePath !== ""
  );
}

/**
 * Read any file within the project directory
 */
export async function readProjectFile(
  input: ReadProjectFileInput
): Promise<ReadProjectFileResult> {
  const { project_path, relative_path } = input;

  // Build full path
  const fullPath = join(project_path, relative_path);

  // Security: Ensure path is within project
  if (!isPathWithinProject(project_path, fullPath)) {
    logError(
      project_path,
      "read_project_file",
      "PathTraversalAttempt",
      `Path "${relative_path}" resolves to "${fullPath}" which is outside project`,
      { relative_path, resolved: fullPath }
    );
    return {
      success: false,
      error: `Security error: Path "${relative_path}" resolves outside project directory.`,
    };
  }

  logEvent(project_path, "", "read_project_file", "tool_start", "info", {
    relative_path,
    full_path: fullPath,
  });

  try {
    // Check if file exists
    if (!existsSync(fullPath)) {
      return {
        success: false,
        relative_path,
        error: `File not found: ${relative_path}`,
      };
    }

    // Get file stats
    const stats = await stat(fullPath);

    if (stats.isDirectory()) {
      return {
        success: false,
        relative_path,
        error: `Path is a directory, not a file: ${relative_path}`,
      };
    }

    // Read file content
    const content = await readFile(fullPath, "utf-8");

    logEvent(project_path, "", "read_project_file", "tool_end", "info", {
      relative_path,
      size_bytes: stats.size,
      chars: content.length,
    });

    return {
      success: true,
      file_path: fullPath,
      relative_path,
      content,
      size_bytes: stats.size,
    };
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : "Unknown error";
    logError(
      project_path,
      "read_project_file",
      "ReadError",
      errorMsg,
      { relative_path }
    );

    return {
      success: false,
      relative_path,
      error: `Failed to read file: ${errorMsg}`,
    };
  }
}

// ============================================
// WRITE PROJECT FILE
// ============================================

export const writeProjectFileSchema = z.object({
  project_path: z.string(),
  relative_path: z.string(), // Path relative to project_path
  content: z.string(), // Content to write
  create_dirs: z.boolean().default(true), // Create parent directories if needed
  overwrite: z.boolean().default(true), // Overwrite if file exists
  append: z.boolean().default(false), // Append to end of file instead of replacing
});

export type WriteProjectFileInput = z.infer<typeof writeProjectFileSchema>;

export interface WriteProjectFileResult {
  success: boolean;
  file_path?: string;
  relative_path?: string;
  bytes_written?: number;
  created_dirs?: boolean;
  error?: string;
}

/**
 * Write any file within the project directory
 */
export async function writeProjectFile(
  input: WriteProjectFileInput
): Promise<WriteProjectFileResult> {
  const { project_path, relative_path, content, create_dirs, overwrite, append } = input;

  // Build full path
  const fullPath = join(project_path, relative_path);

  // Security: Ensure path is within project
  if (!isPathWithinProject(project_path, fullPath)) {
    logError(
      project_path,
      "write_project_file",
      "PathTraversalAttempt",
      `Path "${relative_path}" resolves to "${fullPath}" which is outside project`,
      { relative_path, resolved: fullPath }
    );
    return {
      success: false,
      error: `Security error: Path "${relative_path}" resolves outside project directory.`,
    };
  }

  logEvent(project_path, "", "write_project_file", "tool_start", "info", {
    relative_path,
    full_path: fullPath,
    content_length: content.length,
    create_dirs,
    overwrite,
    append,
  });

  try {
    // Check if file exists and overwrite is false
    if (existsSync(fullPath) && !overwrite) {
      return {
        success: false,
        relative_path,
        error: `File already exists: ${relative_path}. Set overwrite=true to replace.`,
      };
    }

    // Create parent directories if needed
    const parentDir = dirname(fullPath);
    let createdDirs = false;

    if (!existsSync(parentDir)) {
      if (create_dirs) {
        await mkdir(parentDir, { recursive: true });
        createdDirs = true;
      } else {
        return {
          success: false,
          relative_path,
          error: `Parent directory does not exist: ${dirname(relative_path)}. Set create_dirs=true to create.`,
        };
      }
    }

    // Determine final content (append mode or replace)
    let finalContent = content;
    const fileExisted = existsSync(fullPath);
    const didAppend = append && fileExisted;

    if (didAppend) {
      const existingContent = await readFile(fullPath, "utf-8");
      finalContent = existingContent + content;
    }

    // Write file
    await writeFile(fullPath, finalContent, "utf-8");

    logEvent(project_path, "", "write_project_file", "tool_end", "info", {
      relative_path,
      bytes_written: Buffer.byteLength(finalContent, "utf-8"),
      appended: didAppend,
      created_dirs: createdDirs,
    });

    return {
      success: true,
      file_path: fullPath,
      relative_path,
      bytes_written: Buffer.byteLength(finalContent, "utf-8"),
      created_dirs: createdDirs,
    };
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : "Unknown error";
    logError(
      project_path,
      "write_project_file",
      "WriteError",
      errorMsg,
      { relative_path }
    );

    return {
      success: false,
      relative_path,
      error: `Failed to write file: ${errorMsg}`,
    };
  }
}
