/**
 * Path security utilities — prevent path traversal attacks.
 */

import { normalize, relative, isAbsolute, join } from "path";

/**
 * Validate that the resolved path is within a base directory (prevent path traversal).
 * Returns false if the path escapes via ../ or is absolute.
 */
export function isPathWithinBase(basePath: string, targetPath: string): boolean {
  const normalizedBase = normalize(basePath);
  const normalizedTarget = normalize(targetPath);
  const rel = relative(normalizedBase, normalizedTarget);

  return !rel.startsWith("..") && !isAbsolute(rel) && rel !== "";
}

/**
 * Resolve a user-supplied path relative to a base directory, rejecting traversal.
 * Returns the resolved path or null if the path escapes the base.
 */
export function resolveSecurePath(basePath: string, userPath: string): string | null {
  const fullPath = join(basePath, userPath);
  return isPathWithinBase(basePath, fullPath) ? fullPath : null;
}
