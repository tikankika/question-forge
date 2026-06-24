/**
 * Tests for listCourseMaterials — recursive walk of a course vault that returns
 * only allowlisted "what was taught" files (delegates to classifyCourseFile).
 */

import { describe, test, expect, beforeEach, afterEach } from "vitest";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";

import { listCourseMaterials } from "../course_vault.js";

let course: string;

beforeEach(() => {
  course = mkdtempSync(join(tmpdir(), "qf-list-"));
});
afterEach(() => {
  rmSync(course, { recursive: true, force: true });
});

function file(rel: string, content = ""): void {
  const p = join(course, rel);
  mkdirSync(join(p, ".."), { recursive: true });
  writeFileSync(p, content);
}

const fm = (type: string) => `---\ntype: ${type}\n---\nbody\n`;

describe("listCourseMaterials", () => {
  test("returns allowlisted files across zones, excludes denied ones", async () => {
    // admitted
    file("Lesson_Plans/l3.md", fm("lesson_plan"));
    file("Material/Klart/Presentationer/fotosyntes.pptx", "binary");
    file("Styrdokument/krav.pdf", "binary");
    file("Student_Materials/recap_v11.md", fm("recap"));
    file("Data/Transkript/260311_lesson_2_anonymized.txt", "[SPEAKER_00] ...");
    // denied
    file("Data/Transkript/biog200x_lesson_2026-04-20_1.txt", "raw");
    file("Data/Elevreflektioner/svar.md", fm("student_feedback"));
    file("Student_Materials/handout.md", fm("content"));
    file("Reflections/Bryggor/b.md", fm("reflection"));
    file("Ideas/idea.md", "");

    const got = (await listCourseMaterials(course)).map((m) => m.relPath).sort();

    expect(got).toEqual(
      [
        "Data/Transkript/260311_lesson_2_anonymized.txt",
        "Lesson_Plans/l3.md",
        "Material/Klart/Presentationer/fotosyntes.pptx",
        "Student_Materials/recap_v11.md",
        "Styrdokument/krav.pdf",
      ].sort()
    );
  });

  test("recurses into nested safe-zone subfolders", async () => {
    file("Material/Klart/Övningar/set1/uppg.md", fm("material"));
    const got = (await listCourseMaterials(course)).map((m) => m.relPath);
    expect(got).toContain("Material/Klart/Övningar/set1/uppg.md");
  });

  test("reports content_type and size", async () => {
    file("Styrdokument/krav.pdf", "abcd");
    const [m] = await listCourseMaterials(course);
    expect(m.content_type).toBe("pdf");
    expect(m.size_bytes).toBe(4);
  });

  test("empty course (no safe zones) yields no materials", async () => {
    file("Ideas/x.md", "");
    expect(await listCourseMaterials(course)).toEqual([]);
  });
});
