/**
 * Security tests for qf-scaffolding.
 *
 * Verifies path traversal prevention, YAML safe deserialization,
 * and path_security utility correctness.
 */

import { describe, test, expect } from "vitest";
import { isPathWithinBase, resolveSecurePath } from "../utils/path_security.js";

// =============================================================================
// Path Security Utility
// =============================================================================

describe("isPathWithinBase", () => {
  test("allows paths within base directory", () => {
    expect(isPathWithinBase("/project", "/project/file.txt")).toBe(true);
    expect(isPathWithinBase("/project", "/project/sub/deep/file.txt")).toBe(true);
  });

  test("blocks path traversal via ../", () => {
    expect(isPathWithinBase("/project", "/project/../etc/passwd")).toBe(false);
    expect(isPathWithinBase("/project", "/etc/passwd")).toBe(false);
  });

  test("blocks deep traversal", () => {
    expect(isPathWithinBase("/project", "/project/sub/../../etc/passwd")).toBe(false);
  });

  test("blocks absolute path escape", () => {
    expect(isPathWithinBase("/project", "/other/path")).toBe(false);
  });

  test("blocks empty relative path (base itself)", () => {
    expect(isPathWithinBase("/project", "/project")).toBe(false);
  });
});

describe("resolveSecurePath", () => {
  test("resolves safe relative path", () => {
    const result = resolveSecurePath("/project", "sub/file.txt");
    expect(result).toBe("/project/sub/file.txt");
  });

  test("rejects traversal in user path", () => {
    const result = resolveSecurePath("/project", "../../../etc/passwd");
    expect(result).toBeNull();
  });

  test("rejects traversal with leading dot-dot", () => {
    const result = resolveSecurePath("/project", "../../escape");
    expect(result).toBeNull();
  });

  test("allows nested safe path", () => {
    const result = resolveSecurePath("/project", "materials/lecture.pdf");
    expect(result).toBe("/project/materials/lecture.pdf");
  });
});

// =============================================================================
// YAML Safe Schema
// =============================================================================

describe("YAML safe deserialization", () => {
  test("logger.ts uses JSON_SCHEMA (not DEFAULT_SCHEMA)", async () => {
    // Read the actual source file and verify it uses safe schema
    const fs = await import("fs");
    const path = await import("path");
    const loggerSource = fs.readFileSync(
      path.join(__dirname, "../utils/logger.ts"),
      "utf-8"
    );

    // Must contain explicit safe schema
    expect(loggerSource).toContain("schema: yaml.JSON_SCHEMA");
    // Must NOT contain bare yaml.load without schema
    const bareLoads = loggerSource.match(/yaml\.load\(content\)(?!\s*,)/g);
    expect(bareLoads).toBeNull();
  });

  test("complete_stage.ts uses JSON_SCHEMA (not DEFAULT_SCHEMA)", async () => {
    const fs = await import("fs");
    const path = await import("path");
    const source = fs.readFileSync(
      path.join(__dirname, "../tools/complete_stage.ts"),
      "utf-8"
    );

    expect(source).toContain("schema: yaml.JSON_SCHEMA");
    const bareLoads = source.match(/yaml\.load\(content\)(?!\s*,)/g);
    expect(bareLoads).toBeNull();
  });
});

// =============================================================================
// Path Traversal Attack Vectors
// =============================================================================

describe("common attack vectors", () => {
  const attacks = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\config\\sam",
    "....//....//etc/passwd",
    "sub/../../../etc/passwd",
  ];

  test.each(attacks)("resolveSecurePath blocks: %s", (attack) => {
    const result = resolveSecurePath("/project", attack);
    expect(result).toBeNull();
  });
});
