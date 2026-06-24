/**
 * Tests for course_vault utilities — detecting a teaching-suite course root
 * when a QF project runs nested inside a course vault.
 */

import { describe, test, expect, beforeEach, afterEach } from "vitest";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";

import { detectCourseRoot } from "../course_vault.js";

let root: string;

beforeEach(() => {
  root = mkdtempSync(join(tmpdir(), "qf-vault-"));
});

afterEach(() => {
  rmSync(root, { recursive: true, force: true });
});

function mk(...segs: string[]): string {
  const p = join(root, ...segs);
  mkdirSync(p, { recursive: true });
  return p;
}

describe("detectCourseRoot", () => {
  test("finds the course root from a nested QF project (Exams/Formativa/<name>)", () => {
    const course = mk("Courses", "Biologi", "BIOG200x_2026_v4");
    writeFileSync(join(course, "project_state.json"), "{}");
    const project = mk("Courses", "Biologi", "BIOG200x_2026_v4", "Exams", "Formativa", "tema2_quiz");

    expect(detectCourseRoot(project)).toBe(course);
  });

  test("returns null when no ancestor is a course folder (standalone QF)", () => {
    const project = mk("standalone_project");
    // standalone QF projects have session.yaml, not project_state.json
    writeFileSync(join(project, "session.yaml"), "session: {}");

    expect(detectCourseRoot(project)).toBeNull();
  });

  test("returns the project path itself when it is the course root", () => {
    const course = mk("Courses", "X", "course1");
    writeFileSync(join(course, "project_state.json"), "{}");

    expect(detectCourseRoot(course)).toBe(course);
  });

  test("returns the nearest ancestor marker", () => {
    const outer = mk("Courses", "outer");
    writeFileSync(join(outer, "project_state.json"), "{}");
    const inner = mk("Courses", "outer", "inner_course");
    writeFileSync(join(inner, "project_state.json"), "{}");
    const project = mk("Courses", "outer", "inner_course", "Exams", "q");

    expect(detectCourseRoot(project)).toBe(inner);
  });

  test("respects maxDepth (does not find a marker beyond the bound)", () => {
    const course = mk("a");
    writeFileSync(join(course, "project_state.json"), "{}");
    const deep = mk("a", "b", "c", "d", "e");

    expect(detectCourseRoot(deep, 2)).toBeNull(); // marker is 4 levels up, bound is 2
    expect(detectCourseRoot(deep, 8)).toBe(course);
  });
});
