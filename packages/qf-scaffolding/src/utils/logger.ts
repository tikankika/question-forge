/**
 * Unified logging for qf-scaffolding (RFC-001 compliant)
 *
 * All logs go to logs/session.jsonl (shared with qf-pipeline).
 */

import * as fs from "fs";
import * as path from "path";
import * as yaml from "js-yaml";

// Schema version per RFC-001
const SCHEMA_VERSION = 1;

// Log levels
export type LogLevel = "debug" | "info" | "warn" | "error";

// Log entry structure per RFC-001
interface LogEntry {
  ts: string;
  v: number;
  session_id: string;
  mcp: string;
  tool: string;
  event: string;
  level: LogLevel;
  data?: Record<string, unknown>;
  duration_ms?: number;
  parent_id?: string;
}

// Session YAML structure
interface SessionYaml {
  session?: {
    id?: string;
    created?: string;
    updated?: string;
  };
}

/**
 * Read session_id from session.yaml
 */
function readSessionId(projectPath: string): string {
  try {
    const sessionYamlPath = path.join(projectPath, "session.yaml");
    if (fs.existsSync(sessionYamlPath)) {
      const content = fs.readFileSync(sessionYamlPath, "utf-8");
      const data = yaml.load(content, { schema: yaml.JSON_SCHEMA }) as SessionYaml;
      return data?.session?.id || "unknown";
    }
  } catch {
    // Ignore errors, return unknown
  }
  return "unknown";
}

/**
 * Log event to logs/session.jsonl (RFC-001 compliant)
 *
 * Thread-safe with synchronous writes.
 * If sessionId is empty, it will be auto-read from session.yaml.
 */
export function logEvent(
  projectPath: string,
  sessionId: string,
  tool: string,
  event: string,
  level: LogLevel = "info",
  data?: Record<string, unknown>,
  durationMs?: number,
  parentId?: string
): void {
  if (!projectPath) {
    return;
  }

  // Auto-read session_id if not provided
  const effectiveSessionId = sessionId || readSessionId(projectPath);

  // Ensure logs directory exists
  const logsDir = path.join(projectPath, "logs");
  if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
  }

  // Build log entry per RFC-001 schema
  const logEntry: LogEntry = {
    ts: new Date().toISOString(),
    v: SCHEMA_VERSION,
    session_id: effectiveSessionId,
    mcp: "qf-scaffolding",
    tool,
    event,
    level,
  };

  // Add optional fields
  if (data) {
    logEntry.data = data;
  }
  if (durationMs !== undefined) {
    logEntry.duration_ms = durationMs;
  }
  if (parentId) {
    logEntry.parent_id = parentId;
  }

  // Append to session.jsonl (shared log)
  const logFile = path.join(logsDir, "session.jsonl");
  fs.appendFileSync(logFile, JSON.stringify(logEntry) + "\n", "utf-8");
}

/**
 * Log action (backward-compatible wrapper)
 *
 * Automatically reads session_id from session.yaml.
 */
export function logAction(
  projectPath: string,
  tool: string,
  message: string,
  data?: Record<string, unknown>,
  level: LogLevel = "info"
): void {
  if (!projectPath) {
    return;
  }

  // Auto-read session_id from session.yaml
  const sessionId = readSessionId(projectPath);

  logEvent(projectPath, sessionId, tool, message, level, data);
}

/**
 * Log stage event (helper for M1-M4 stages)
 */
export function logStageEvent(
  projectPath: string,
  module: string,
  stage: number,
  event: "stage_start" | "stage_complete" | "stage_skip",
  data?: Record<string, unknown>
): void {
  const sessionId = readSessionId(projectPath);

  logEvent(
    projectPath,
    sessionId,
    `${module}_stage${stage}`,
    event,
    "info",
    {
      module,
      stage,
      ...data,
    }
  );
}

/**
 * Log user decision (for ML training)
 */
export function logUserDecision(
  projectPath: string,
  tool: string,
  decisionType: string,
  optionsPresented: unknown[],
  userChoice: unknown,
  rationale?: string
): void {
  const sessionId = readSessionId(projectPath);

  logEvent(
    projectPath,
    sessionId,
    tool,
    "user_decision",
    "info",
    {
      decision_type: decisionType,
      options_presented: optionsPresented,
      user_choice: userChoice,
      ...(rationale && { rationale }),
    }
  );
}

/**
 * Log error with context
 */
export function logError(
  projectPath: string,
  tool: string,
  errorType: string,
  errorMessage: string,
  context?: Record<string, unknown>
): void {
  const sessionId = readSessionId(projectPath);

  logEvent(
    projectPath,
    sessionId,
    tool,
    "tool_error",
    "error",
    {
      error_type: errorType,
      error_message: errorMessage,
      ...context,
    }
  );
}

/**
 * Get session state from logs (for resumption)
 */
export function getSessionState(projectPath: string): {
  status: string;
  total_events?: number;
  last_activity?: string;
  error_count?: number;
} {
  const logFile = path.join(projectPath, "logs", "session.jsonl");

  if (!fs.existsSync(logFile)) {
    return { status: "no_session" };
  }

  try {
    const content = fs.readFileSync(logFile, "utf-8");
    const lines = content.trim().split("\n").filter(Boolean);
    const events = lines.map((line) => JSON.parse(line) as LogEntry);

    if (events.length === 0) {
      return { status: "empty", total_events: 0 };
    }

    const errors = events.filter((e) => e.level === "error");

    return {
      status: "resumable",
      total_events: events.length,
      last_activity: events[events.length - 1]?.ts,
      error_count: errors.length,
    };
  } catch {
    return { status: "error" };
  }
}
