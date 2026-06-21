/**
 * course_vault — detect when a QF project runs nested inside a teaching-suite
 * course vault, so QF can read course material in place instead of requiring it
 * copied into <project>/materials/.
 *
 * Design source: internal ADR_qf_ts_material_flow.md. Standalone QF (no course
 * vault) is unaffected — detectCourseRoot returns null and callers fall back to
 * the existing <project>/materials/ behaviour.
 */

import { existsSync, readFileSync } from "fs";
import { basename, dirname, join, relative, resolve } from "path";
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

// ── Material allowlist (ADR_qf_ts_material_flow, consolidated step-2 rule) ──────

/** Clearly-safe content zones: teacher-authored subject content. All files
 * (markdown AND binaries — pptx/pdf have no frontmatter) are admitted here. */
export const SAFE_ZONES = [
  "Lesson_Plans",
  "Styrdokument",
  "Syllabus",
  "Material/Klart",
  "Material/Sammanfattningar",
  "Material/Resurser",
  "Material/Uppgifter",
];

/** Mixed zones where safe and unsafe roles co-exist (e.g. recap vs content):
 * admit only markdown whose frontmatter `type` is a safe role. */
export const ROLE_GATED_ZONES = ["Student_Materials"];

/** Raw lesson recordings live here; admit ONLY edusafe-anonymised transcripts. */
export const TRANSCRIPT_ZONE = "Data/Transkript";

/** Frontmatter `type` roles that represent "what was taught" (PII-safe). */
export const SAFE_ROLES = new Set([
  "material",
  "lesson_plan",
  "lesson_summary",
  "recap",
  "syllabus",
]);

export interface CourseFileDecision {
  admit: boolean;
  reason: string;
}

/** POSIX-style path of `absPath` relative to `courseRoot`, or null when the
 * target is outside the course root (including `../` traversal). */
function relUnder(courseRoot: string, absPath: string): string | null {
  const rel = relative(resolve(courseRoot), resolve(absPath)).split("\\").join("/");
  if (rel === "" || rel.startsWith("../") || rel === ".." || rel.startsWith("/")) {
    return null;
  }
  return rel;
}

function inZone(rel: string, zone: string): boolean {
  return rel === zone || rel.startsWith(zone + "/");
}

/** Read a markdown file's YAML-frontmatter `type`, or null if absent/unreadable. */
function readFrontmatterType(absPath: string): string | null {
  try {
    const txt = readFileSync(absPath, "utf8");
    const block = /^---\s*\n([\s\S]*?)\n---/.exec(txt);
    if (!block) return null;
    const m = /^type:\s*['"]?([\w-]+)/m.exec(block[1]);
    return m ? m[1] : null;
  } catch {
    return null;
  }
}

/**
 * Decide whether a course-vault file may be read by QF (default-deny).
 *
 * Rules (ADR_qf_ts_material_flow §Decision 4):
 *  1. Data/Transkript/*_anonymized* → allow (edusafe stamp); rest of Data/ → deny.
 *  2. Role-gated zones (Student_Materials) → allow only .md with a safe frontmatter role.
 *  3. Clearly-safe content zones → allow all files (incl. binaries).
 *  4. Everything else (incl. ../ escapes) → deny.
 */
export async function classifyCourseFile(
  courseRoot: string,
  absPath: string
): Promise<CourseFileDecision> {
  const rel = relUnder(courseRoot, absPath);
  if (rel === null) return { admit: false, reason: "outside course root" };

  // 1. Data/ — student-data zone; only anonymised transcripts escape the deny.
  if (rel === "Data" || rel.startsWith("Data/")) {
    if (inZone(rel, TRANSCRIPT_ZONE) && /_anonymized/i.test(basename(absPath))) {
      return { admit: true, reason: "anonymised transcript" };
    }
    return { admit: false, reason: "Data/ student-data zone" };
  }

  // 2. Role-gated zone — markdown with a safe role only (catches recap).
  if (ROLE_GATED_ZONES.some((z) => inZone(rel, z))) {
    if (!rel.toLowerCase().endsWith(".md")) {
      return { admit: false, reason: "role-gated zone: non-markdown" };
    }
    const role = readFrontmatterType(absPath);
    if (role && SAFE_ROLES.has(role)) {
      return { admit: true, reason: `safe role: ${role}` };
    }
    return { admit: false, reason: `role not safe: ${role ?? "none"}` };
  }

  // 3. Clearly-safe content zones — all files.
  if (SAFE_ZONES.some((z) => inZone(rel, z))) {
    return { admit: true, reason: "safe content zone" };
  }

  // 4. Default-deny.
  return { admit: false, reason: "default-deny (not in an allowed zone)" };
}
