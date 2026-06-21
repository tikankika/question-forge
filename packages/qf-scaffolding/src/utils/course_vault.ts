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
import { readdir, stat } from "fs/promises";
import { basename, dirname, extname, join, relative, resolve } from "path";
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
/** Walk up from `startPath` returning the first ancestor satisfying `hasMarker`.
 * Bounded: never returns the home directory or above, stops at the filesystem
 * root, and never walks more than `maxDepth` levels up. */
function walkUpFor(
  startPath: string,
  hasMarker: (dir: string) => boolean,
  maxDepth: number
): string | null {
  const home = resolve(homedir());
  let dir = resolve(startPath);
  for (let i = 0; i <= maxDepth; i++) {
    if (dir === home) break; // never treat home (or above) as a root
    if (hasMarker(dir)) return dir;
    const parent = dirname(dir);
    if (parent === dir) break; // filesystem root
    dir = parent;
  }
  return null;
}

export function detectCourseRoot(projectPath: string, maxDepth = 8): string | null {
  return walkUpFor(projectPath, (dir) => existsSync(join(dir, COURSE_MARKER)), maxDepth);
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

// ── Course material listing ────────────────────────────────────────────────

export type CourseContentType = "pdf" | "md" | "txt" | "pptx" | "other";

export interface CourseMaterial {
  /** POSIX path relative to the course root. */
  relPath: string;
  content_type: CourseContentType;
  size_bytes: number;
}

/** Zones that may contain admittable files — we only walk these, never the
 * whole vault (cheaper, and avoids touching process/student folders at all). */
const CANDIDATE_ZONES = [...SAFE_ZONES, ...ROLE_GATED_ZONES, TRANSCRIPT_ZONE];

function courseContentType(name: string): CourseContentType {
  switch (extname(name).toLowerCase()) {
    case ".pdf":
      return "pdf";
    case ".md":
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
 * Recursively list the allowlisted course materials under `courseRoot`.
 * Walks only the candidate zones and admits each file via classifyCourseFile,
 * so denied files (raw transcripts, student data, process notes) never appear.
 * Symlinks are skipped (defence-in-depth against escaping the vault).
 */
export async function listCourseMaterials(courseRoot: string): Promise<CourseMaterial[]> {
  const out: CourseMaterial[] = [];

  async function walk(dir: string): Promise<void> {
    let entries;
    try {
      entries = await readdir(dir, { withFileTypes: true });
    } catch {
      return; // zone absent in this vault
    }
    for (const entry of entries) {
      const abs = join(dir, entry.name);
      if (entry.isDirectory()) {
        await walk(abs);
      } else if (entry.isFile()) {
        const decision = await classifyCourseFile(courseRoot, abs);
        if (!decision.admit) continue;
        const rel = relUnder(courseRoot, abs);
        if (rel === null) continue;
        out.push({
          relPath: rel,
          content_type: courseContentType(entry.name),
          size_bytes: (await stat(abs)).size,
        });
      }
    }
  }

  for (const zone of CANDIDATE_ZONES) {
    await walk(join(courseRoot, zone));
  }
  out.sort((a, b) => a.relPath.localeCompare(b.relPath));
  return out;
}

// ── Curriculum (Läroplan / styrdokument) at the vault root ─────────────────────
// These live in the Obsidian vault root, above the course folder, so they use a
// separate `curriculum:` addressing rather than under-course `course:` paths.

/** Curriculum document name pattern (national curriculum / governing docs). */
export const CURRICULUM_PATTERN = /(l[äa]roplan|curriculum|styrdokument)/i;
const CURRICULUM_EXTS = new Set([".pdf", ".md", ".txt"]);

/** Walk up from the course root to the Obsidian vault root (the dir holding
 * `.obsidian/`). Bounded; returns null if no vault root is found. */
export function detectVaultRoot(courseRoot: string, maxDepth = 6): string | null {
  return walkUpFor(courseRoot, (dir) => existsSync(join(dir, ".obsidian")), maxDepth);
}

/** List curriculum documents at the vault root (top-level only — never recurses
 * into sibling course folders). relPath is the bare filename. */
export async function listCurriculum(courseRoot: string): Promise<CourseMaterial[]> {
  const vaultRoot = detectVaultRoot(courseRoot);
  if (!vaultRoot) return [];
  let entries;
  try {
    entries = await readdir(vaultRoot, { withFileTypes: true });
  } catch {
    return [];
  }
  const out: CourseMaterial[] = [];
  for (const entry of entries) {
    if (!entry.isFile()) continue; // top-level files only
    if (!CURRICULUM_PATTERN.test(entry.name)) continue;
    if (!CURRICULUM_EXTS.has(extname(entry.name).toLowerCase())) continue;
    const abs = join(vaultRoot, entry.name);
    out.push({
      relPath: entry.name,
      content_type: courseContentType(entry.name),
      size_bytes: (await stat(abs)).size,
    });
  }
  out.sort((a, b) => a.relPath.localeCompare(b.relPath));
  return out;
}

export interface CurriculumDecision {
  admit: boolean;
  absPath?: string;
  reason: string;
}

/** Validate a requested curriculum file (a bare vault-root filename). Rejects
 * path separators/traversal, non-curriculum names, and missing files. */
export function classifyCurriculumFile(courseRoot: string, name: string): CurriculumDecision {
  if (name.includes("/") || name.includes("\\") || name.includes("..")) {
    return { admit: false, reason: "curriculum must be a top-level vault-root filename" };
  }
  if (!CURRICULUM_PATTERN.test(name) || !CURRICULUM_EXTS.has(extname(name).toLowerCase())) {
    return { admit: false, reason: "not a curriculum document" };
  }
  const vaultRoot = detectVaultRoot(courseRoot);
  if (!vaultRoot) return { admit: false, reason: "no vault root" };
  const abs = join(vaultRoot, name);
  if (!existsSync(abs)) return { admit: false, reason: "not found" };
  return { admit: true, absPath: abs, reason: "curriculum" };
}
