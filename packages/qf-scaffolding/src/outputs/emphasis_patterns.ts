/**
 * Emphasis Patterns Output (M1 Stage 2)
 *
 * Generates YAML frontmatter and Markdown body for m1_emphasis_patterns.md
 * Based on SPEC_M1_M4_OUTPUTS_FULL.md specification.
 */

import { z } from 'zod';
import * as yaml from 'js-yaml';
import type { OutputMetadata } from './learning_objectives.js';

// Signal schema - flexible to support different signal types
const SignalSchema = z.object({
  type: z.enum(['explicit', 'time', 'repetition', 'foundational', 'visual', 'practical']),
  count: z.number().optional(),
  percentage: z.number().optional(),
  examples: z.array(z.string()).optional(),
  context: z.string().optional(),
  evidence: z.string().optional()
});

// Topic emphasis schema
const TopicEmphasisSchema = z.object({
  topic: z.string(),
  signals: z.array(SignalSchema),
  rationale: z.string()
});

// Complete emphasis patterns data schema
export const EmphasisPatternsSchema = z.object({
  materials_analyzed: z.string().optional(),
  total_instruction_time: z.string().optional(),
  tier1: z.array(TopicEmphasisSchema),
  tier2: z.array(TopicEmphasisSchema),
  tier3: z.array(TopicEmphasisSchema),
  tier4: z.array(TopicEmphasisSchema)
});

export type EmphasisPatternsData = z.infer<typeof EmphasisPatternsSchema>;
export type TopicEmphasis = z.infer<typeof TopicEmphasisSchema>;
export type Signal = z.infer<typeof SignalSchema>;

/**
 * Generate YAML frontmatter for emphasis patterns
 */
export function generateFrontmatter(
  data: EmphasisPatternsData,
  metadata: OutputMetadata
): string {
  const frontmatterData = {
    module: metadata.module,
    stage: metadata.stage,
    output_type: 'emphasis_patterns',
    created: new Date().toISOString(),
    session_id: metadata.sessionId,
    emphasis_analysis: {
      tier1: data.tier1,
      tier2: data.tier2,
      tier3: data.tier3,
      tier4: data.tier4
    }
  };

  return yaml.dump(frontmatterData, { lineWidth: -1 });
}

/**
 * Format a signal for Markdown output
 */
function formatSignal(signal: Signal): string {
  const parts: string[] = [];

  switch (signal.type) {
    case 'explicit':
      parts.push(`**Explicit priority:** ${signal.count || 0} mentions`);
      if (signal.examples && signal.examples.length > 0) {
        parts.push(...signal.examples.map(ex => `  - "${ex}"`));
      }
      break;
    case 'time':
      parts.push(`**Time allocation:** ${signal.percentage || 0}% of instruction`);
      if (signal.context) {
        parts.push(`  - ${signal.context}`);
      }
      break;
    case 'repetition':
      parts.push(`**Repetition:** ${signal.count || 0} contexts`);
      if (signal.context) {
        parts.push(`  - ${signal.context}`);
      }
      break;
    case 'foundational':
      parts.push(`**Foundational:** ${signal.evidence || 'Required for subsequent topics'}`);
      break;
    case 'visual':
      parts.push(`**Visual emphasis:** ${signal.context || 'Diagrams and visual aids'}`);
      break;
    case 'practical':
      parts.push(`**Practical application:** ${signal.context || 'Hands-on component'}`);
      break;
  }

  return parts.join('\n');
}

/**
 * Format a topic for Markdown output
 */
function formatTopic(topic: TopicEmphasis): string {
  const signalsFormatted = topic.signals.map(formatSignal).join('\n\n');

  return `### ${topic.topic}

**Emphasis Signals:**
${signalsFormatted}

**Rationale:** ${topic.rationale}`;
}

/**
 * Generate Markdown body for emphasis patterns
 */
export function generateMarkdown(data: EmphasisPatternsData): string {
  const date = new Date().toISOString().split('T')[0];

  // Format tier sections
  const tier1Content = data.tier1.length > 0
    ? data.tier1.map(formatTopic).join('\n\n---\n\n')
    : '*No Tier 1 topics identified.*';

  const tier2Content = data.tier2.length > 0
    ? data.tier2.map(formatTopic).join('\n\n---\n\n')
    : '*No Tier 2 topics identified.*';

  const tier3Content = data.tier3.length > 0
    ? data.tier3.map(formatTopic).join('\n\n---\n\n')
    : '*No Tier 3 topics identified.*';

  const tier4Content = data.tier4.length > 0
    ? data.tier4.map(formatTopic).join('\n\n---\n\n')
    : '*No Tier 4 (excluded) topics identified.*';

  // Calculate summary statistics
  const totalTopics = data.tier1.length + data.tier2.length + data.tier3.length + data.tier4.length;

  // Build summary table rows
  const summaryRows = [
    `| 1    | ${data.tier1.length}      | High          | High         |`,
    `| 2    | ${data.tier2.length}      | Medium        | Medium       |`,
    `| 3    | ${data.tier3.length}      | Low           | Low          |`,
    `| 4    | ${data.tier4.length}      | Excluded      | N/A          |`
  ].join('\n');

  return `# M1 Emphasis Patterns Analysis

**Analysis Date:** ${date}
**Materials Analyzed:** ${data.materials_analyzed || 'See material_analysis.md'}
**Total Instruction Time:** ${data.total_instruction_time || 'N/A'}

## Tier 1: Critical Emphasis (Must Assess)

${tier1Content}

---

## Tier 2: Important (Should Assess)

${tier2Content}

---

## Tier 3: Useful Background (Could Assess)

${tier3Content}

---

## Tier 4: Excluded

${tier4Content}

---

## Summary Statistics

| Tier | Topics | Explicit Signals | Repetition |
|------|--------|------------------|------------|
${summaryRows}

**Total Topics Analyzed:** ${totalTopics}

---

**Next Step:** M2 uses these tiers to prioritize blueprint question distribution.`;
}

/**
 * Generate complete file content (YAML frontmatter + Markdown body)
 */
export function generateFileContent(
  data: EmphasisPatternsData,
  metadata: OutputMetadata
): string {
  const frontmatter = generateFrontmatter(data, metadata);
  const markdown = generateMarkdown(data);
  return `---\n${frontmatter}---\n\n${markdown}`;
}

/**
 * Export for complete_stage integration
 */
export const emphasisPatternsOutput = {
  type: 'emphasis_patterns' as const,
  schema: EmphasisPatternsSchema,
  generateFrontmatter,
  generateMarkdown,
  generateFileContent,
  filename: (module: string) => `${module}_emphasis_patterns.md`
};
