/**
 * Characterisation tests for read_materials STANDALONE behaviour — locks the
 * current contract (list/read from <project>/materials/, path-traversal blocked,
 * missing-folder error) before the read-materials-in-place change. These must
 * stay green through steps 5-6 (standalone QF unchanged).
 *
 * Standalone = the project has no teaching-suite course root ancestor, so
 * detectCourseRoot returns null and read_materials behaves exactly as today.
 */

import { describe, test, expect, beforeEach, afterEach } from "vitest";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";

import { readMaterials } from "../read_materials.js";

let project: string;

beforeEach(() => {
  // mkdtemp under tmpdir → no project_state.json ancestor → standalone
  project = mkdtempSync(join(tmpdir(), "qf-standalone-"));
});
afterEach(() => {
  rmSync(project, { recursive: true, force: true });
});

function material(name: string, content = ""): void {
  const dir = join(project, "materials");
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, name), content);
}

describe("read_materials standalone — list mode", () => {
  test("lists files in <project>/materials/", async () => {
    material("a.md", "# A");
    material("b.txt", "btext");

    const res = await readMaterials({ project_path: project });

    expect(res.success).toBe(true);
    expect(res.mode).toBe("list");
    expect(res.total_files).toBe(2);
    expect(res.files?.map((f) => f.filename).sort()).toEqual(["a.md", "b.txt"]);
  });

  test("missing materials/ folder returns an error", async () => {
    const res = await readMaterials({ project_path: project });
    expect(res.success).toBe(false);
    expect(res.error).toContain("Materials folder not found");
  });
});

describe("read_materials standalone — read mode", () => {
  test("reads one file's text content from materials/", async () => {
    material("note.md", "# Hello\ncontent here");

    const res = await readMaterials({ project_path: project, filename: "note.md" });

    expect(res.success).toBe(true);
    expect(res.mode).toBe("read");
    expect(res.material?.filename).toBe("note.md");
    expect(res.material?.text_content).toContain("content here");
  });

  test("blocks path traversal outside materials/", async () => {
    material("ok.md", "ok");
    writeFileSync(join(project, "secret.md"), "secret");

    const res = await readMaterials({ project_path: project, filename: "../secret.md" });

    expect(res.success).toBe(false);
    expect(res.error).toContain("Security error");
  });
});
