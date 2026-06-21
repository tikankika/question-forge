/**
 * read_materials — curriculum (Läroplan) in shared mode. Curriculum lives in the
 * Obsidian vault root above the course folder and is addressed with `curriculum:`.
 */

import { describe, test, expect, beforeEach, afterEach } from "vitest";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";

import { readMaterials } from "../read_materials.js";

let vaultRoot: string;
let project: string;

beforeEach(() => {
  vaultRoot = mkdtempSync(join(tmpdir(), "qf-courses-"));
  mkdirSync(join(vaultRoot, ".obsidian"), { recursive: true });
  writeFileSync(join(vaultRoot, "Laroplan_utdrag.txt"), "kunskapskrav: fotosyntes");
  writeFileSync(join(vaultRoot, "notes.md"), "not curriculum");
  const courseRoot = join(vaultRoot, "Biologi", "BIOG200x");
  mkdirSync(courseRoot, { recursive: true });
  writeFileSync(join(courseRoot, "project_state.json"), "{}");
  project = join(courseRoot, "Exams", "Formativa", "q1");
  mkdirSync(project, { recursive: true });
});
afterEach(() => {
  rmSync(vaultRoot, { recursive: true, force: true });
});

describe("read_materials — curriculum", () => {
  test("LIST surfaces curriculum as a curriculum:-prefixed entry", async () => {
    const res = await readMaterials({ project_path: project });
    const names = (res.files ?? []).map((f) => f.filename);
    expect(names).toContain("curriculum:Laroplan_utdrag.txt");
    expect(names).not.toContain("curriculum:notes.md");
  });

  test("READ reads the curriculum file in place", async () => {
    const res = await readMaterials({
      project_path: project,
      filename: "curriculum:Laroplan_utdrag.txt",
    });
    expect(res.success).toBe(true);
    expect(res.material?.text_content).toContain("kunskapskrav");
  });

  test("READ denies a non-curriculum or traversal name", async () => {
    expect((await readMaterials({ project_path: project, filename: "curriculum:notes.md" })).success).toBe(false);
    expect((await readMaterials({ project_path: project, filename: "curriculum:../x.pdf" })).success).toBe(false);
  });
});
