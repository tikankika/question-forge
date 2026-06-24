/**
 * Tests for read_materials in SHARED course-vault mode — when the QF project is
 * nested inside a teaching-suite course folder, read_materials additionally
 * surfaces (LIST) and reads (READ) allowlisted course material in place,
 * without copying. Standalone behaviour is covered by the characterisation tests.
 */

import { describe, test, expect, beforeEach, afterEach } from "vitest";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";

import { readMaterials } from "../read_materials.js";

let courseRoot: string;
let project: string;

function write(base: string, rel: string, content = ""): void {
  const p = join(base, rel);
  mkdirSync(join(p, ".."), { recursive: true });
  writeFileSync(p, content);
}
const fm = (type: string) => `---\ntype: ${type}\n---\nbody\n`;

beforeEach(() => {
  courseRoot = mkdtempSync(join(tmpdir(), "qf-vault-"));
  // teaching-suite course marker
  writeFileSync(join(courseRoot, "project_state.json"), "{}");
  // nested QF project
  project = join(courseRoot, "Exams", "Formativa", "tema2_quiz");
  mkdirSync(project, { recursive: true });

  // course materials (some admitted, some denied)
  write(courseRoot, "Lesson_Plans/l3.md", fm("lesson_plan"));
  write(courseRoot, "Material/Klart/Presentationer/foto.pptx", "binary");
  write(courseRoot, "Data/Transkript/260311_lesson_2_anonymized.txt", "[SPEAKER_00]");
  write(courseRoot, "Data/Transkript/raw_2026-04-20.txt", "raw"); // denied
  write(courseRoot, "Reflections/Bryggor/b.md", fm("reflection")); // denied
});
afterEach(() => {
  rmSync(courseRoot, { recursive: true, force: true });
});

describe("read_materials shared mode — LIST", () => {
  test("includes allowlisted course material (source-marked), excludes denied", async () => {
    write(project, "materials/own.pdf", "own"); // project's own copied material

    const res = await readMaterials({ project_path: project });

    expect(res.success).toBe(true);
    expect(res.mode).toBe("list");
    const names = (res.files ?? []).map((f) => f.filename).sort();
    expect(names).toContain("own.pdf"); // project file still listed
    expect(names).toContain("course:Lesson_Plans/l3.md");
    expect(names).toContain("course:Material/Klart/Presentationer/foto.pptx");
    expect(names).toContain("course:Data/Transkript/260311_lesson_2_anonymized.txt");
    // denied never appear
    expect(names).not.toContain("course:Data/Transkript/raw_2026-04-20.txt");
    expect(names.some((n) => n.includes("Reflections"))).toBe(false);
  });

  test("works even when the project has no materials/ folder (no copy)", async () => {
    // no project/materials at all
    const res = await readMaterials({ project_path: project });

    expect(res.success).toBe(true);
    expect(res.mode).toBe("list");
    const names = (res.files ?? []).map((f) => f.filename);
    expect(names).toContain("course:Lesson_Plans/l3.md");
  });

  test("course entries are marked source=course", async () => {
    const res = await readMaterials({ project_path: project });
    const courseEntry = (res.files ?? []).find((f) => f.filename.startsWith("course:"));
    expect(courseEntry?.source).toBe("course");
  });
});

describe("read_materials shared mode — READ in place", () => {
  test("reads an admitted course file in place", async () => {
    write(courseRoot, "Lesson_Plans/l3.md", fm("lesson_plan") + "TAUGHT: photosynthesis");

    const res = await readMaterials({
      project_path: project,
      filename: "course:Lesson_Plans/l3.md",
    });

    expect(res.success).toBe(true);
    expect(res.mode).toBe("read");
    expect(res.material?.text_content).toContain("photosynthesis");
  });

  test("denies a raw transcript (allowlist)", async () => {
    const res = await readMaterials({
      project_path: project,
      filename: "course:Data/Transkript/raw_2026-04-20.txt",
    });
    expect(res.success).toBe(false);
  });

  test("denies path traversal via course: prefix", async () => {
    const res = await readMaterials({
      project_path: project,
      filename: "course:../escape.md",
    });
    expect(res.success).toBe(false);
  });
});
