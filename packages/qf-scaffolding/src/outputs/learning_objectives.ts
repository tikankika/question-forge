/**
 * Learning Objectives Output (M1 Stage 5)
 *
 * Generates YAML frontmatter and Markdown body for m1_learning_objectives.md
 * Based on SPEC_M1_M4_OUTPUTS_FULL.md specification.
 */

import { z } from 'zod';
import * as yaml from 'js-yaml';

// Schema for learning objective item
const LearningObjectiveItemSchema = z.object({
  id: z.string(),
  text: z.string(),
  bloom: z.string(),
  rationale: z.string()
});

// Schema for complete learning objectives data
export const LearningObjectivesSchema = z.object({
  course: z.string(),
  instructor: z.string().optional(),
  tier1: z.array(LearningObjectiveItemSchema),
  tier2: z.array(LearningObjectiveItemSchema),
  tier3: z.array(LearningObjectiveItemSchema),
  tier4_excluded: z.array(z.string())
});

export type LearningObjectivesData = z.infer<typeof LearningObjectivesSchema>;

export interface OutputMetadata {
  module: string;
  stage: number;
  sessionId: string;
}

/**
 * Generate YAML frontmatter for learning objectives
 */
export function generateFrontmatter(
  data: LearningObjectivesData,
  metadata: OutputMetadata
): string {
  const frontmatterData = {
    module: metadata.module,
    stage: metadata.stage,
    output_type: 'learning_objectives',
    created: new Date().toISOString(),
    session_id: metadata.sessionId,
    course: data.course,
    instructor: data.instructor,
    learning_objectives: {
      tier1: data.tier1,
      tier2: data.tier2,
      tier3: data.tier3,
      tier4_excluded: data.tier4_excluded
    }
  };

  return yaml.dump(frontmatterData, { lineWidth: -1 });
}

/**
 * Generate Markdown body for learning objectives
 */
export function generateMarkdown(data: LearningObjectivesData): string {
  const date = new Date().toISOString().split('T')[0];

  const tier1Content = data.tier1.length > 0
    ? data.tier1.map(lo =>
        `- **${lo.id}** (${lo.bloom}): ${lo.text}\n  - *Rationale:* ${lo.rationale}`
      ).join('\n\n')
    : '*No Tier 1 objectives defined.*';

  const tier2Content = data.tier2.length > 0
    ? data.tier2.map(lo =>
        `- **${lo.id}** (${lo.bloom}): ${lo.text}\n  - *Rationale:* ${lo.rationale}`
      ).join('\n\n')
    : '*No Tier 2 objectives defined.*';

  const tier3Content = data.tier3.length > 0
    ? data.tier3.map(lo =>
        `- **${lo.id}** (${lo.bloom}): ${lo.text}\n  - *Rationale:* ${lo.rationale}`
      ).join('\n\n')
    : '*No Tier 3 objectives defined.*';

  const tier4Content = data.tier4_excluded.length > 0
    ? data.tier4_excluded.map(item => `- ${item}`).join('\n')
    : '*No excluded topics.*';

  return `# M1 Learning Objectives

**Course:** ${data.course}
**Instructor:** ${data.instructor || 'N/A'}
**Date:** ${date}

## Tier 1: Core Concepts (Must Assess)

These concepts received the highest emphasis and are critical for assessment.

${tier1Content}

## Tier 2: Important (Should Assess)

${tier2Content}

## Tier 3: Useful Background (Could Assess)

${tier3Content}

## Tier 4: Excluded from Assessment

${tier4Content}

---

**Next Step:** Use these learning objectives in M2 Assessment Design to create blueprint.`;
}

/**
 * Generate complete file content (YAML frontmatter + Markdown body)
 */
export function generateFileContent(
  data: LearningObjectivesData,
  metadata: OutputMetadata
): string {
  const frontmatter = generateFrontmatter(data, metadata);
  const markdown = generateMarkdown(data);
  return `---\n${frontmatter}---\n\n${markdown}`;
}

/**
 * Export for complete_stage integration
 */
export const learningObjectivesOutput = {
  type: 'learning_objectives' as const,
  schema: LearningObjectivesSchema,
  generateFrontmatter,
  generateMarkdown,
  generateFileContent,
  filename: (module: string) => `${module}_learning_objectives.md`
};
