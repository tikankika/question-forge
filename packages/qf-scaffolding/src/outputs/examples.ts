/**
 * Examples Output (M1 Stage 3)
 *
 * Generates YAML frontmatter and Markdown body for m1_examples.md
 * Based on SPEC_M1_M4_OUTPUTS_FULL.md specification.
 */

import { z } from 'zod';
import * as yaml from 'js-yaml';
import type { OutputMetadata } from './learning_objectives.js';

// Question potential schema
const QuestionPotentialSchema = z.object({
  bloom_levels: z.array(z.string()),
  question_types: z.array(z.string()),
  example_stem: z.string().optional()
});

// Single example schema
const ExampleItemSchema = z.object({
  id: z.string(),
  title: z.string(),
  source: z.string(),
  topic: z.string(),
  learning_objective: z.string().optional(),
  context: z.string(),
  visual: z.boolean().optional(),
  hands_on: z.boolean().optional(),
  usage_count: z.number(),
  contexts: z.array(z.string()),
  effectiveness: z.enum(['low', 'medium', 'high', 'very_high']),
  student_familiarity: z.enum(['low', 'medium', 'high', 'very_high']),
  question_potential: QuestionPotentialSchema
});

// Complete examples data schema
export const ExamplesSchema = z.object({
  materials_reviewed: z.string().optional(),
  examples: z.array(ExampleItemSchema)
});

export type ExamplesData = z.infer<typeof ExamplesSchema>;
export type ExampleItem = z.infer<typeof ExampleItemSchema>;

/**
 * Generate YAML frontmatter for examples
 */
export function generateFrontmatter(
  data: ExamplesData,
  metadata: OutputMetadata
): string {
  const frontmatterData = {
    module: metadata.module,
    stage: metadata.stage,
    output_type: 'examples',
    created: new Date().toISOString(),
    session_id: metadata.sessionId,
    examples: data.examples
  };

  return yaml.dump(frontmatterData, { lineWidth: -1 });
}

/**
 * Format effectiveness/familiarity level for display
 */
function formatLevel(level: string): string {
  return level.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

/**
 * Format a single example for Markdown output
 */
function formatExample(example: ExampleItem, index: number): string {
  const visualIndicator = example.visual ? '📊 Visual' : '';
  const handsOnIndicator = example.hands_on ? '🔬 Hands-On' : '';
  const indicators = [visualIndicator, handsOnIndicator].filter(Boolean).join(' | ');

  const contextsFormatted = example.contexts.map((ctx, i) =>
    `${i + 1}. **${ctx}**`
  ).join('\n');

  const bloomLevels = example.question_potential.bloom_levels.join(', ');
  const questionTypes = example.question_potential.question_types.join(', ');

  return `## Example ${index + 1}: ${example.title}

**Source:** ${example.source}
**Topic:** ${example.topic}
${example.learning_objective ? `**Learning Objective:** ${example.learning_objective}` : ''}
${indicators ? `**Type:** ${indicators}` : ''}

### Context
${example.context}

### Usage Across Course (${example.usage_count} times)
${contextsFormatted}

### Effectiveness Assessment
- **Student Familiarity:** ${formatLevel(example.student_familiarity)} (${example.usage_count} exposures)
- **Effectiveness:** ${formatLevel(example.effectiveness)}
${example.visual ? '- **Visual Impact:** High (visual/diagram component)' : ''}
${example.hands_on ? '- **Hands-On Component:** High (personal experience)' : ''}

### Question Potential

**Suitable Bloom Levels:** ${bloomLevels}

**Question Types:**
${example.question_potential.question_types.map(t => `- ${t}`).join('\n')}

${example.question_potential.example_stem ? `**Example Question Stem:**
> "${example.question_potential.example_stem}"` : ''}

**Why This Example Works:**
- Familiar to students (seen ${example.usage_count}x)
${example.visual ? '- Visual memory aid' : ''}
${example.hands_on ? '- Personal hands-on experience' : ''}
- Clear context for question stems`;
}

/**
 * Generate Markdown body for examples
 */
export function generateMarkdown(data: ExamplesData): string {
  const date = new Date().toISOString().split('T')[0];

  // Format examples
  const examplesContent = data.examples.length > 0
    ? data.examples.map((ex, i) => formatExample(ex, i)).join('\n\n---\n\n')
    : '*No examples cataloged.*';

  // Group examples by type
  const visualExamples = data.examples.filter(e => e.visual);
  const handsOnExamples = data.examples.filter(e => e.hands_on);
  const highFamiliarity = data.examples.filter(e =>
    e.student_familiarity === 'very_high' || e.student_familiarity === 'high'
  );

  // Build summary table
  const summaryRows = data.examples.map(ex => {
    const sourceType = ex.hands_on ? 'Lab' : 'Lecture';
    const bloomAbbrev = ex.question_potential.bloom_levels.map(b => b.substring(0, 3)).join(', ');
    return `| ${ex.id} | ${sourceType} | ${ex.usage_count} | ${formatLevel(ex.student_familiarity)} | ${bloomAbbrev} |`;
  }).join('\n');

  return `# M1 Instructional Examples Catalog

**Analysis Date:** ${date}
**Materials Reviewed:** ${data.materials_reviewed || 'See material_analysis.md'}
**Total Examples Cataloged:** ${data.examples.length} (high-value examples only)

---

${examplesContent}

---

## Example Usage Guidelines for M3

### High Familiarity Examples${highFamiliarity.length > 0 ? ` (${highFamiliarity.map(e => e.id).join(', ')})` : ''}
**Use for:**
- Remember/Understand questions
- Foundation questions
- All students will recognize reference

**Question Stems:**
- "Som vi såg i [source]..."
- "I [context], vilket..."
- "Baserat på [example]..."

### Hands-On Examples${handsOnExamples.length > 0 ? ` (${handsOnExamples.map(e => e.id).join(', ')})` : ''}
**Use for:**
- Apply/Analyze questions
- Scenario-based questions
- Questions requiring data interpretation

**Question Stems:**
- "I [lab], ni observerade... Om [variable], vad händer?"
- "Baserat på er lab-data..."
- "Förutsäg resultatet om..."

### Visual Examples${visualExamples.length > 0 ? ` (${visualExamples.map(e => e.id).join(', ')})` : ''}
**Benefits:**
- Strong visual memory
- Good for diagram-based questions
- Multiple retrieval cues

---

## Summary Statistics

| Example | Source Type | Usage Count | Familiarity | Bloom Levels |
|---------|------------|-------------|-------------|--------------|
${summaryRows || '| - | - | - | - | - |'}

---

**Next Step:** M3 uses these examples to create contextually-grounded question stems that students will find familiar and valid.`;
}

/**
 * Generate complete file content (YAML frontmatter + Markdown body)
 */
export function generateFileContent(
  data: ExamplesData,
  metadata: OutputMetadata
): string {
  const frontmatter = generateFrontmatter(data, metadata);
  const markdown = generateMarkdown(data);
  return `---\n${frontmatter}---\n\n${markdown}`;
}

/**
 * Export for complete_stage integration
 */
export const examplesOutput = {
  type: 'examples' as const,
  schema: ExamplesSchema,
  generateFrontmatter,
  generateMarkdown,
  generateFileContent,
  filename: (module: string) => `${module}_examples.md`
};
