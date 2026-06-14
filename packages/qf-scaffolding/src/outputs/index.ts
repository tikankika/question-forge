/**
 * Methodology Outputs Index
 *
 * Central registry for all M1-M4 output types.
 * Each output type has:
 * - Zod schema for validation
 * - YAML frontmatter generator
 * - Markdown body generator
 * - Filename generator
 */

import { learningObjectivesOutput } from './learning_objectives.js';
import { misconceptionsOutput } from './misconceptions.js';
import { emphasisPatternsOutput } from './emphasis_patterns.js';
import { examplesOutput } from './examples.js';
import { materialAnalysisOutput } from './material_analysis.js';

// Re-export types
export type { OutputMetadata } from './learning_objectives.js';
export type { LearningObjectivesData } from './learning_objectives.js';
export type { MisconceptionsData } from './misconceptions.js';
export type { EmphasisPatternsData } from './emphasis_patterns.js';
export type { ExamplesData } from './examples.js';
export type { MaterialAnalysisData } from './material_analysis.js';

/**
 * Output handler interface - all output types implement this
 */
export interface OutputHandler<T = unknown> {
  type: string;
  schema: import('zod').ZodType<T>;
  generateFrontmatter: (data: T, metadata: import('./learning_objectives.js').OutputMetadata) => string;
  generateMarkdown: (data: T) => string;
  generateFileContent: (data: T, metadata: import('./learning_objectives.js').OutputMetadata) => string;
  filename: (module: string) => string;
}

/**
 * Registry of all output handlers
 *
 * Phase 1: learning_objectives, misconceptions ✅
 * Phase 2: emphasis_patterns, examples, material_analysis ✅
 * Phase 3: blueprint, gap_analysis, generation_log, qa_report, detailed_feedback
 */
export const OUTPUT_HANDLERS = {
  // Phase 1 (M1 core)
  learning_objectives: learningObjectivesOutput,
  misconceptions: misconceptionsOutput,
  // Phase 2 (M1 completion)
  emphasis_patterns: emphasisPatternsOutput,
  examples: examplesOutput,
  material_analysis: materialAnalysisOutput,
  // Phase 3 (M2, M3, M4)
  // blueprint: blueprintOutput,
  // gap_analysis: gapAnalysisOutput,
  // generation_log: generationLogOutput,
  // qa_report: qaReportOutput,
  // detailed_feedback: detailedFeedbackOutput,
} as const;

/**
 * Output type union - all valid output types
 */
export type OutputType = keyof typeof OUTPUT_HANDLERS;

/**
 * Get output handler by type
 * @throws Error if output type is not registered
 */
export function getOutputHandler(type: string): OutputHandler {
  const handler = OUTPUT_HANDLERS[type as OutputType];
  if (!handler) {
    const validTypes = Object.keys(OUTPUT_HANDLERS).join(', ');
    throw new Error(`Unknown output type: ${type}. Valid types: ${validTypes}`);
  }
  return handler as OutputHandler;
}

/**
 * Check if output type is valid
 */
export function isValidOutputType(type: string): type is OutputType {
  return type in OUTPUT_HANDLERS;
}

/**
 * Stage to output type mapping
 * Maps (module, stage) → output type (if any)
 *
 * M1 Stages:
 * - Stage 0: material_analysis (DOCUMENTATION)
 * - Stage 2: emphasis_patterns (MANDATORY)
 * - Stage 3: examples (MANDATORY)
 * - Stage 4: misconceptions (MANDATORY)
 * - Stage 5: learning_objectives (MANDATORY)
 */
export const STAGE_OUTPUT_MAP: Record<string, Record<number, OutputType>> = {
  m1: {
    0: 'material_analysis',
    2: 'emphasis_patterns',
    3: 'examples',
    4: 'misconceptions',
    5: 'learning_objectives'
  },
  m2: {
    // 7: 'blueprint', // Phase 3
  },
  m3: {
    // N/A: 'generation_log', // Phase 3
  },
  m4: {
    // N/A: 'qa_report', // Phase 3
    // N/A: 'detailed_feedback', // Phase 3
  }
};

/**
 * Get expected output type for a stage
 * @returns Output type or undefined if stage has no output
 */
export function getStageOutputType(module: string, stage: number): OutputType | undefined {
  return STAGE_OUTPUT_MAP[module]?.[stage];
}

/**
 * Check if a stage requires an output
 */
export function stageRequiresOutput(module: string, stage: number): boolean {
  return getStageOutputType(module, stage) !== undefined;
}
