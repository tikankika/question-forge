/**
 * course_vault — detect when a QF project runs nested inside a teaching-suite
 * course vault, so QF can read course material in place instead of requiring it
 * copied into <project>/materials/.
 *
 * Design source: internal ADR_qf_ts_material_flow.md. Standalone QF (no course
 * vault) is unaffected — detectCourseRoot returns null and callers fall back to
 * the existing <project>/materials/ behaviour.
 */

import { existsSync } from "fs";
import { dirname, join, resolve } from "path";
import { homedir } from "os";

/** The teaching-suite course-folder marker. Present in both older and newer
 * vaults (unlike `_config/course_context.md`, which older vaults lack). */
export const COURSE_MARKER = "project_state.json";

/**
 * Walk up from `projectPath` looking for the course marker. Returns the absolute
 * course-root path, or null when no ancestor (within bounds) is a course folder.
 *
 * Bounded: never treats the home directory or above as a course root, stops at
 * the filesystem root, and never walks more than `maxDepth` levels up.
 */
export function detectCourseRoot(projectPath: string, maxDepth = 8): string | null {
  const home = resolve(homedir());
  let dir = resolve(projectPath);

  for (let i = 0; i <= maxDepth; i++) {
    if (dir === home) break; // never treat home (or above) as a course root
    if (existsSync(join(dir, COURSE_MARKER))) return dir;
    const parent = dirname(dir);
    if (parent === dir) break; // filesystem root
    dir = parent;
  }
  return null;
}
