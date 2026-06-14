/**
 * Misconceptions Output (M1 Stage 4)
 *
 * Generates YAML frontmatter and Markdown body for m1_misconceptions.md
 * Based on SPEC_M1_M4_OUTPUTS_FULL.md specification.
 */

import { z } from 'zod';
import * as yaml from 'js-yaml';
import type { OutputMetadata } from './learning_objectives.js';

// Evidence item schema
const EvidenceItemSchema = z.object({
  source: z.string(),
  frequency: z.string()
});

// Single misconception schema
const MisconceptionItemSchema = z.object({
  id: z.string(),
  topic: z.string(),
  misconception: z.string(),
  correct: z.string(),
  evidence: z.array(EvidenceItemSchema),
  severity: z.enum(['high', 'medium', 'low']),
  rationale: z.string(),
  teaching_strategy: z.string(),
  distractor_example: z.string()
});

// Complete misconceptions data schema
export const MisconceptionsSchema = z.object({
  misconceptions: z.array(MisconceptionItemSchema)
});

export type MisconceptionsData = z.infer<typeof MisconceptionsSchema>;
export type MisconceptionItem = z.infer<typeof MisconceptionItemSchema>;

/**
 * Generate YAML frontmatter for misconceptions
 */
export function generateFrontmatter(
  data: MisconceptionsData,
  metadata: OutputMetadata
): string {
  const frontmatterData = {
    module: metadata.module,
    stage: metadata.stage,
    output_type: 'misconceptions',
    created: new Date().toISOString(),
    session_id: metadata.sessionId,
    misconceptions: data.misconceptions
  };

  return yaml.dump(frontmatterData, { lineWidth: -1 });
}

/**
 * Generate detailed markdown for a single misconception
 */
function renderMisconception(m: MisconceptionItem, detailed: boolean): string {
  const evidenceList = m.evidence
    .map(e => `- ${e.source}: **${e.frequency}**`)
    .join('\n');

  const severityStars = m.severity === 'high' ? '⭐⭐⭐⭐⭐' :
                        m.severity === 'medium' ? '⭐⭐⭐⭐' : '⭐⭐⭐';

  if (detailed) {
    return `### ${m.id}: "${m.misconception}"

**Misconception:** ${m.misconception}
**Correct Understanding:** ${m.correct}

**Evidence:**
${evidenceList}

**Severity:** ${m.severity.toUpperCase()}
**Rationale:** ${m.rationale}

**Teaching Strategy Used:**
${m.teaching_strategy}

**Distractor Potential:** ${severityStars}
**Example Distractor:** "${m.distractor_example}"`;
  } else {
    return `### ${m.id}: "${m.misconception}"

**Correct Understanding:** ${m.correct}

**Evidence:**
${evidenceList}

**Severity:** ${m.severity.toUpperCase()}
**Distractor Potential:** ${severityStars}`;
  }
}

/**
 * Generate Markdown body for misconceptions
 */
export function generateMarkdown(data: MisconceptionsData): string {
  const date = new Date().toISOString().split('T')[0];

  // Group by severity
  const high = data.misconceptions.filter(m => m.severity === 'high');
  const medium = data.misconceptions.filter(m => m.severity === 'medium');
  const low = data.misconceptions.filter(m => m.severity === 'low');

  // Generate sections
  const highSection = high.length > 0
    ? high.map(m => renderMisconception(m, true)).join('\n\n---\n\n')
    : '*No high severity misconceptions identified.*';

  const mediumSection = medium.length > 0
    ? medium.map(m => renderMisconception(m, false)).join('\n\n---\n\n')
    : '*No medium severity misconceptions identified.*';

  const lowSection = low.length > 0
    ? low.map(m => renderMisconception(m, false)).join('\n\n---\n\n')
    : '*No low severity misconceptions identified.*';

  // Summary table
  const summaryRows = data.misconceptions.map(m => {
    const stars = m.severity === 'high' ? '⭐⭐⭐⭐⭐' :
                  m.severity === 'medium' ? '⭐⭐⭐⭐' : '⭐⭐⭐';
    const freq = m.evidence[0]?.frequency || 'N/A';
    return `| ${m.id} | ${m.topic} | ${m.misconception.substring(0, 30)}... | ${freq} | ${m.severity.charAt(0).toUpperCase() + m.severity.slice(1)} | ${stars} |`;
  }).join('\n');

  return `# M1 Common Student Misconceptions

**Analysis Date:** ${date}

---

## HIGH SEVERITY Misconceptions

These represent fundamental misunderstandings that must be addressed.

${highSection}

---

## MEDIUM SEVERITY Misconceptions

${mediumSection}

---

## LOW SEVERITY Misconceptions

${lowSection}

---

## Misconception Summary Table

| ID | Topic | Misconception | Frequency | Severity | Distractor ⭐ |
|----|-------|---------------|-----------|----------|-------------|
${summaryRows}

---

## Usage Guidelines for M3 (Question Generation)

**For HIGH severity misconceptions:**
- Use in Remember/Understand questions
- Can be primary distractor
- Explicitly address in feedback

**For MEDIUM severity misconceptions:**
- Use in Understand/Apply questions
- Good secondary distractor
- Include in partial credit feedback

**For LOW severity misconceptions:**
- Use in Apply/Analyze questions
- Optional distractor
- Brief mention in feedback sufficient

---

**Next Step:** M3 uses these documented misconceptions to create realistic, pedagogically-grounded distractors.`;
}

/**
 * Generate complete file content (YAML frontmatter + Markdown body)
 */
export function generateFileContent(
  data: MisconceptionsData,
  metadata: OutputMetadata
): string {
  const frontmatter = generateFrontmatter(data, metadata);
  const markdown = generateMarkdown(data);
  return `---\n${frontmatter}---\n\n${markdown}`;
}

/**
 * Export for complete_stage integration
 */
export const misconceptionsOutput = {
  type: 'misconceptions' as const,
  schema: MisconceptionsSchema,
  generateFrontmatter,
  generateMarkdown,
  generateFileContent,
  filename: (module: string) => `${module}_misconceptions.md`
};
