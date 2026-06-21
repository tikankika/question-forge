/**
 * Tests for curriculum (Läroplan/styrdokument) handling — these documents live
 * in the Obsidian vault root, ONE+ level above the course folder, so they need a
 * separate addressing (`curriculum:` prefix) from under-course `course:` paths.
 * Step 7 of read-materials-in-place (ADR_qf_ts_material_flow): Läroplan = allow.
 */

import { describe, test, expect, beforeEach, afterEach } from "vitest";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";

import {
  detectVaultRoot,
  listCurriculum,
  classifyCurriculumFile,
} from "../course_vault.js";

let vaultRoot: string;
let courseRoot: string;

beforeEach(() => {
  vaultRoot = mkdtempSync(join(tmpdir(), "qf-courses-"));
  mkdirSync(join(vaultRoot, ".obsidian"), { recursive: true }); // vault marker
  // curriculum at the vault root
  writeFileSync(join(vaultRoot, "Laroplan for gymnasieskolan.pdf"), "curriculum");
  // non-curriculum top-level files
  writeFileSync(join(vaultRoot, "COSEAQ_framework.md"), "framework");
  writeFileSync(join(vaultRoot, "random.txt"), "x");
  // a course folder under the vault root
  courseRoot = join(vaultRoot, "Biologi", "BIOG200x_2026_v4");
  mkdirSync(courseRoot, { recursive: true });
  writeFileSync(join(courseRoot, "project_state.json"), "{}");
});
afterEach(() => {
  rmSync(vaultRoot, { recursive: true, force: true });
});

describe("detectVaultRoot", () => {
  test("walks up from the course root to the .obsidian vault root", () => {
    expect(detectVaultRoot(courseRoot)).toBe(vaultRoot);
  });
  test("returns null when there is no vault root", () => {
    const lone = mkdtempSync(join(tmpdir(), "qf-novault-"));
    expect(detectVaultRoot(lone)).toBeNull();
    rmSync(lone, { recursive: true, force: true });
  });
});

describe("listCurriculum", () => {
  test("lists only curriculum documents at the vault root", async () => {
    const got = (await listCurriculum(courseRoot)).map((m) => m.relPath);
    expect(got).toEqual(["Laroplan for gymnasieskolan.pdf"]);
  });
  test("does not recurse into sibling course folders", async () => {
    // a curriculum-named file inside another course must NOT appear
    const other = join(vaultRoot, "Annat", "kurs");
    mkdirSync(other, { recursive: true });
    writeFileSync(join(other, "laroplan_kopia.pdf"), "x");
    const got = (await listCurriculum(courseRoot)).map((m) => m.relPath);
    expect(got).toEqual(["Laroplan for gymnasieskolan.pdf"]);
  });
});

describe("classifyCurriculumFile", () => {
  test("admits the curriculum pdf by name", () => {
    const d = classifyCurriculumFile(courseRoot, "Laroplan for gymnasieskolan.pdf");
    expect(d.admit).toBe(true);
    expect(d.absPath).toBe(join(vaultRoot, "Laroplan for gymnasieskolan.pdf"));
  });
  test("rejects a non-curriculum file", () => {
    expect(classifyCurriculumFile(courseRoot, "COSEAQ_framework.md").admit).toBe(false);
  });
  test("rejects path separators / traversal", () => {
    expect(classifyCurriculumFile(courseRoot, "../secret.pdf").admit).toBe(false);
    expect(classifyCurriculumFile(courseRoot, "sub/laroplan.pdf").admit).toBe(false);
  });
  test("rejects a curriculum-named file that does not exist", () => {
    expect(classifyCurriculumFile(courseRoot, "laroplan_missing.pdf").admit).toBe(false);
  });
});
