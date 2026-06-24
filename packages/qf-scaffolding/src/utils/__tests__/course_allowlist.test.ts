/**
 * Tests for the course-material allowlist (classifyCourseFile) — the consolidated
 * step-2 rule from ADR_qf_ts_material_flow:
 *   1. Data/Transkript/*_anonymized* → allow (edusafe stamp)
 *   2. Data/** (raw transcripts, Labbdata, Elevreflektioner) → deny
 *   3. .md in the role-gated zone (Student_Materials) → allow only safe frontmatter role
 *      (recap caught; content/student_summary denied — same folder, broken-key fix)
 *   4. clearly-safe content zones (Lesson_Plans, Styrdokument, Material/Klart…) → allow
 *      files including binaries (pptx/pdf have no frontmatter)
 *   5. everything else → deny (default-deny)
 */

import { describe, test, expect, beforeEach, afterEach } from "vitest";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";

import { classifyCourseFile } from "../course_vault.js";

let course: string;

beforeEach(() => {
  course = mkdtempSync(join(tmpdir(), "qf-course-"));
});
afterEach(() => {
  rmSync(course, { recursive: true, force: true });
});

/** Create a file (with optional content) under the course root and return its abs path. */
function file(rel: string, content = ""): string {
  const p = join(course, rel);
  mkdirSync(join(p, ".."), { recursive: true });
  writeFileSync(p, content);
  return p;
}

const fm = (type: string) => `---\ntype: ${type}\n---\n\nbody\n`;

async function admits(rel: string, content = ""): Promise<boolean> {
  const p = file(rel, content);
  return (await classifyCourseFile(course, p)).admit;
}

describe("classifyCourseFile — clearly-safe content zones", () => {
  test("Lesson_Plans md is admitted", async () => {
    expect(await admits("Lesson_Plans/lesson3.md", fm("lesson_plan"))).toBe(true);
  });
  test("Styrdokument pdf (binary, no frontmatter) is admitted", async () => {
    expect(await admits("Styrdokument/kunskapskrav.pdf")).toBe(true);
  });
  test("Material/Klart pptx (binary) is admitted", async () => {
    expect(await admits("Material/Klart/Presentationer/fotosyntes.pptx")).toBe(true);
  });
  test("Material/Sammanfattningar md is admitted", async () => {
    expect(await admits("Material/Sammanfattningar/v11.md")).toBe(true);
  });
  test("Material/WIP draft is denied (not a finished/safe zone)", async () => {
    expect(await admits("Material/WIP/draft.md")).toBe(false);
  });
});

describe("classifyCourseFile — Data/ transcript rule", () => {
  test("anonymized transcript is admitted", async () => {
    expect(await admits("Data/Transkript/260311_lesson_2_anonymized.txt")).toBe(true);
  });
  test("raw transcript is denied", async () => {
    expect(await admits("Data/Transkript/biog200x_lesson_2026-04-20_1.txt")).toBe(false);
  });
  test("Elevreflektioner is denied", async () => {
    expect(await admits("Data/Elevreflektioner/svar.md", fm("student_feedback"))).toBe(false);
  });
  test("Labbdata is denied", async () => {
    expect(await admits("Data/Labbdata/run.csv")).toBe(false);
  });
});

describe("classifyCourseFile — role-gated zone (Student_Materials)", () => {
  test("recap md is admitted (best 'what was taught' source despite the folder)", async () => {
    expect(await admits("Student_Materials/recap_v11.md", fm("recap"))).toBe(true);
  });
  test("content md is denied (student-facing, same folder)", async () => {
    expect(await admits("Student_Materials/handout.md", fm("content"))).toBe(false);
  });
  test("student_summary md is denied", async () => {
    expect(await admits("Student_Materials/Student_Summaries/s.md", fm("student_summary"))).toBe(false);
  });
  test("md without a safe role is denied", async () => {
    expect(await admits("Student_Materials/note.md")).toBe(false);
  });
  test("binary in role-gated zone is denied (role unverifiable)", async () => {
    expect(await admits("Student_Materials/poster.pdf")).toBe(false);
  });
});

describe("classifyCourseFile — default-deny + traversal", () => {
  test("unknown zone is denied", async () => {
    expect(await admits("Reflections/Bryggor/b.md", fm("reflection"))).toBe(false);
  });
  test("Ideas/Memos denied", async () => {
    expect(await admits("Ideas/idea.md")).toBe(false);
  });
  test("path outside the course root is denied", async () => {
    const outside = join(course, "..", "escape.md");
    expect((await classifyCourseFile(course, outside)).admit).toBe(false);
  });
});
