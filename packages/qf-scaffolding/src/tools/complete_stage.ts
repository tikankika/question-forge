/**
 * complete_stage tool for qf-scaffolding MCP
 *
 * Extended to handle methodology output creation.
 * When a stage is completed with an output:
 * 1. Validates output data against schema
 * 2. Generates YAML frontmatter + Markdown file
 * 3. Writes to preparation/
 * 4. Updates session.yaml
 * 5. Logs stage_complete event
 */

import { z } from 'zod';
import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';
import { getOutputHandler, isValidOutputType, type OutputType } from '../outputs/index.js';
import { logStageEvent, logEvent, logError } from '../utils/logger.js';

/**
 * Input schema for complete_stage tool
 */
export const completeStageSchema = z.object({
  project_path: z.string(),
  module: z.enum(['m1', 'm2', 'm3', 'm4']),
  stage: z.number().min(0).max(8),
  output: z.object({
    type: z.string(),
    data: z.unknown()
  }).optional(),
  overwrite: z.boolean().optional().default(false)
});

export type CompleteStageInput = z.infer<typeof completeStageSchema>;

/**
 * Result type for complete_stage
 */
export interface CompleteStageResult {
  success: boolean;
  stage_completed: boolean;
  output_filepath?: string;
  error?: string;
}

/**
 * Session YAML structure (partial - relevant fields only)
 */
interface SessionYaml {
  session?: {
    id?: string;
    created?: string;
    updated?: string;
  };
  methodology?: {
    [module: string]: {
      status?: string;
      completed_stages?: number[];
      outputs?: {
        [outputType: string]: string;
      };
    };
  };
}

/**
 * Read session.yaml from project
 */
function readSession(projectPath: string): SessionYaml {
  const sessionPath = path.join(projectPath, 'session.yaml');
  if (!fs.existsSync(sessionPath)) {
    return { session: { id: 'unknown' }, methodology: {} };
  }
  const content = fs.readFileSync(sessionPath, 'utf-8');
  return yaml.load(content, { schema: yaml.JSON_SCHEMA }) as SessionYaml || { session: { id: 'unknown' }, methodology: {} };
}

/**
 * Write session.yaml to project
 */
function writeSession(projectPath: string, session: SessionYaml): void {
  const sessionPath = path.join(projectPath, 'session.yaml');
  const content = yaml.dump(session, { lineWidth: -1 });
  fs.writeFileSync(sessionPath, content, 'utf-8');
}

/**
 * Get session ID from session.yaml
 */
function getSessionId(projectPath: string): string {
  const session = readSession(projectPath);
  return session.session?.id || 'unknown';
}

/**
 * Complete a methodology stage with optional output creation
 */
export async function completeStage(input: CompleteStageInput): Promise<CompleteStageResult> {
  const { project_path, module, stage, output, overwrite } = input;
  const startTime = Date.now();

  // Log tool_start
  logEvent(
    project_path,
    '',
    'complete_stage',
    'tool_start',
    'info',
    { module, stage, has_output: !!output }
  );

  try {
    // Read current session
    const session = readSession(project_path);
    const sessionId = session.session?.id || 'unknown';

    // Ensure methodology structure exists
    if (!session.methodology) {
      session.methodology = {};
    }
    if (!session.methodology[module]) {
      session.methodology[module] = {
        status: 'in_progress',
        completed_stages: [],
        outputs: {}
      };
    }

    let outputFilepath: string | undefined;

    // Handle output if provided
    if (output) {
      // Validate output type
      if (!isValidOutputType(output.type)) {
        const error = `Invalid output type: ${output.type}`;
        logError(project_path, 'complete_stage', 'ValidationError', error);
        return { success: false, stage_completed: false, error };
      }

      const handler = getOutputHandler(output.type);

      // Check if output already exists (unless overwrite is true)
      const existingOutput = session.methodology[module].outputs?.[output.type];
      if (existingOutput && !overwrite) {
        const error = `Output ${output.type} already exists. Set overwrite: true to replace.`;
        logError(project_path, 'complete_stage', 'OutputExistsError', error);
        return { success: false, stage_completed: false, error };
      }

      // Validate data against schema
      let validatedData: unknown;
      try {
        validatedData = handler.schema.parse(output.data);
      } catch (validationError) {
        const error = validationError instanceof Error
          ? validationError.message
          : 'Data validation failed';
        logError(project_path, 'complete_stage', 'SchemaValidationError', error, {
          output_type: output.type
        });
        return { success: false, stage_completed: false, error: `Schema validation failed: ${error}` };
      }

      // Generate file content
      const fileContent = handler.generateFileContent(validatedData, {
        module,
        stage,
        sessionId
      });

      // Ensure preparation directory exists
      const methodologyDir = path.join(project_path, 'preparation');
      if (!fs.existsSync(methodologyDir)) {
        fs.mkdirSync(methodologyDir, { recursive: true });
      }

      // Write file
      const filename = handler.filename(module);
      outputFilepath = path.join(methodologyDir, filename);
      fs.writeFileSync(outputFilepath, fileContent, 'utf-8');

      // Update session.yaml with output reference
      if (!session.methodology[module].outputs) {
        session.methodology[module].outputs = {};
      }
      session.methodology[module].outputs[output.type] = `preparation/${filename}`;
    }

    // Mark stage as completed
    if (!session.methodology[module].completed_stages) {
      session.methodology[module].completed_stages = [];
    }
    if (!session.methodology[module].completed_stages.includes(stage)) {
      session.methodology[module].completed_stages.push(stage);
      session.methodology[module].completed_stages.sort((a, b) => a - b);
    }

    // Update session timestamp
    if (session.session) {
      session.session.updated = new Date().toISOString();
    }

    // Write session.yaml
    writeSession(project_path, session);

    // Log stage_complete event
    logStageEvent(project_path, module, stage, 'stage_complete', {
      output_created: !!outputFilepath,
      output_type: output?.type,
      output_filepath: outputFilepath
    });

    // Log tool_end
    logEvent(
      project_path,
      '',
      'complete_stage',
      'tool_end',
      'info',
      {
        success: true,
        module,
        stage,
        output_created: !!outputFilepath
      },
      Date.now() - startTime
    );

    return {
      success: true,
      stage_completed: true,
      output_filepath: outputFilepath
    };

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';

    logError(project_path, 'complete_stage', 'UnknownError', errorMessage, {
      module,
      stage,
      stack: error instanceof Error ? error.stack : undefined
    });

    return {
      success: false,
      stage_completed: false,
      error: errorMessage
    };
  }
}

/**
 * Get current stage progress for a module
 */
export function getModuleProgress(projectPath: string, module: string): {
  completed_stages: number[];
  outputs: Record<string, string>;
} {
  const session = readSession(projectPath);
  const moduleData = session.methodology?.[module];

  return {
    completed_stages: moduleData?.completed_stages || [],
    outputs: moduleData?.outputs || {}
  };
}
