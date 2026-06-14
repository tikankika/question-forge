/**
 * Material Analysis Output (M1 Stage 0)
 *
 * Generates YAML frontmatter and Markdown body for m1_material_analysis.md
 * Based on SPEC_M1_M4_OUTPUTS_FULL.md specification.
 *
 * This is a DOCUMENTATION output - audit trail of what was analyzed.
 */

import { z } from 'zod';
import * as yaml from 'js-yaml';
import type { OutputMetadata } from './learning_objectives.js';

// Lecture material schema
const LectureMaterialSchema = z.object({
  title: z.string(),
  date: z.string().optional(),
  duration: z.number().optional(), // minutes
  slides: z.number().optional(),
  transcript: z.boolean().optional(),
  topics: z.array(z.string()).optional()
});

// Lab material schema
const LabMaterialSchema = z.object({
  title: z.string(),
  date: z.string().optional(),
  handout_pages: z.number().optional(),
  practical: z.boolean().optional(),
  activities: z.array(z.string()).optional()
});

// Reading material schema
const ReadingMaterialSchema = z.object({
  title: z.string(),
  pages: z.number().optional(),
  required: z.boolean().optional(),
  topics: z.array(z.string()).optional()
});

// Completeness check schema
const CompletenessSchema = z.object({
  all_lectures: z.boolean(),
  all_labs: z.boolean(),
  all_readings: z.boolean(),
  missing: z.array(z.string()).optional()
});

// Complete material analysis data schema
export const MaterialAnalysisSchema = z.object({
  analysis_duration: z.number().optional(), // minutes spent analyzing
  analyst: z.string().optional(),
  materials_analyzed: z.object({
    lectures: z.array(LectureMaterialSchema),
    labs: z.array(LabMaterialSchema),
    readings: z.array(ReadingMaterialSchema)
  }),
  completeness: CompletenessSchema,
  quality_assessment: z.object({
    lecture_clarity: z.enum(['low', 'medium', 'high']).optional(),
    lecture_consistency: z.enum(['low', 'medium', 'high']).optional(),
    emphasis_signals: z.enum(['low', 'medium', 'high', 'very_high']).optional(),
    lab_connection: z.enum(['weak', 'good', 'strong']).optional(),
    reading_alignment: z.enum(['weak', 'good', 'strong']).optional()
  }).optional()
});

export type MaterialAnalysisData = z.infer<typeof MaterialAnalysisSchema>;

/**
 * Generate YAML frontmatter for material analysis
 */
export function generateFrontmatter(
  data: MaterialAnalysisData,
  metadata: OutputMetadata
): string {
  const frontmatterData = {
    module: metadata.module,
    stage: metadata.stage,
    output_type: 'material_analysis',
    created: new Date().toISOString(),
    session_id: metadata.sessionId,
    analysis_duration: data.analysis_duration,
    materials_analyzed: data.materials_analyzed,
    completeness: data.completeness
  };

  return yaml.dump(frontmatterData, { lineWidth: -1 });
}

/**
 * Format a lecture for Markdown output
 */
function formatLecture(lecture: z.infer<typeof LectureMaterialSchema>, index: number): string {
  const parts = [
    `${index + 1}. **${lecture.title}**`
  ];

  if (lecture.date) parts.push(`   - Date: ${lecture.date}`);
  if (lecture.duration) parts.push(`   - Duration: ${lecture.duration} minutes`);
  if (lecture.slides) parts.push(`   - Slides: ${lecture.slides}`);
  if (lecture.transcript !== undefined) {
    parts.push(`   - Transcript: ${lecture.transcript ? '✅ Available' : '❌ Not available'}`);
  }
  if (lecture.topics && lecture.topics.length > 0) {
    parts.push(`   - Topics: ${lecture.topics.join(', ')}`);
  }

  return parts.join('\n');
}

/**
 * Format a lab for Markdown output
 */
function formatLab(lab: z.infer<typeof LabMaterialSchema>, index: number): string {
  const parts = [
    `${index + 1}. **${lab.title}**`
  ];

  if (lab.date) parts.push(`   - Date: ${lab.date}`);
  if (lab.handout_pages) parts.push(`   - Handout: ${lab.handout_pages} pages`);
  if (lab.practical !== undefined) {
    parts.push(`   - Practical: ${lab.practical ? '✅ Yes' : '❌ No'}`);
  }
  if (lab.activities && lab.activities.length > 0) {
    parts.push(`   - Activities: ${lab.activities.join(', ')}`);
  }

  return parts.join('\n');
}

/**
 * Format a reading for Markdown output
 */
function formatReading(reading: z.infer<typeof ReadingMaterialSchema>, index: number): string {
  const parts = [
    `${index + 1}. **${reading.title}**`
  ];

  if (reading.pages) parts.push(`   - Pages: ${reading.pages}`);
  if (reading.required !== undefined) {
    parts.push(`   - Required: ${reading.required ? '✅ Yes' : '❌ No'}`);
  }
  if (reading.topics && reading.topics.length > 0) {
    parts.push(`   - Topics: ${reading.topics.join(', ')}`);
  }

  return parts.join('\n');
}

/**
 * Generate Markdown body for material analysis
 */
export function generateMarkdown(data: MaterialAnalysisData): string {
  const date = new Date().toISOString().split('T')[0];
  const { materials_analyzed, completeness, quality_assessment } = data;

  // Format materials
  const lecturesContent = materials_analyzed.lectures.length > 0
    ? materials_analyzed.lectures.map(formatLecture).join('\n\n')
    : '*No lectures analyzed.*';

  const labsContent = materials_analyzed.labs.length > 0
    ? materials_analyzed.labs.map(formatLab).join('\n\n')
    : '*No labs analyzed.*';

  const readingsContent = materials_analyzed.readings.length > 0
    ? materials_analyzed.readings.map(formatReading).join('\n\n')
    : '*No readings analyzed.*';

  // Completeness check
  const completenessChecks = [
    `${completeness.all_lectures ? '✅' : '❌'} **All scheduled lectures analyzed** (${materials_analyzed.lectures.length}/${materials_analyzed.lectures.length})`,
    `${completeness.all_labs ? '✅' : '❌'} **All lab materials analyzed** (${materials_analyzed.labs.length}/${materials_analyzed.labs.length})`,
    `${completeness.all_readings ? '✅' : '❌'} **All required readings analyzed** (${materials_analyzed.readings.length}/${materials_analyzed.readings.length})`
  ];

  if (completeness.missing && completeness.missing.length > 0) {
    completenessChecks.push(`⚠️ **Missing:** ${completeness.missing.join(', ')}`);
  }

  // Quality assessment (if provided)
  let qualitySection = '';
  if (quality_assessment) {
    const qa = quality_assessment;
    qualitySection = `
---

## Material Quality Assessment

### Lecture Materials
${qa.lecture_clarity ? `- **Clarity:** ${qa.lecture_clarity.charAt(0).toUpperCase() + qa.lecture_clarity.slice(1)}` : ''}
${qa.lecture_consistency ? `- **Consistency:** ${qa.lecture_consistency.charAt(0).toUpperCase() + qa.lecture_consistency.slice(1)}` : ''}
${qa.emphasis_signals ? `- **Emphasis Signals:** ${qa.emphasis_signals.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}` : ''}

### Lab Materials
${qa.lab_connection ? `- **Connection to Theory:** ${qa.lab_connection.charAt(0).toUpperCase() + qa.lab_connection.slice(1)}` : ''}

### Reading Materials
${qa.reading_alignment ? `- **Alignment with Lectures:** ${qa.reading_alignment.charAt(0).toUpperCase() + qa.reading_alignment.slice(1)}` : ''}
`;
  }

  // Calculate total instruction time
  const totalLectureMinutes = materials_analyzed.lectures.reduce((sum, l) => sum + (l.duration || 0), 0);
  const totalHours = Math.round(totalLectureMinutes / 60 * 10) / 10;

  return `# M1 Material Analysis

**Analysis Date:** ${date}
**Time Spent:** ${data.analysis_duration || 'N/A'} minutes
**Analyst:** ${data.analyst || 'Claude'}

---

## Materials Analyzed

### Lectures (${materials_analyzed.lectures.length} total)

${lecturesContent}

### Labs (${materials_analyzed.labs.length} total)

${labsContent}

### Readings (${materials_analyzed.readings.length} total)

${readingsContent}

---

## Completeness Check

${completenessChecks.join('\n')}
${qualitySection}
---

## Summary

- **Total Lectures:** ${materials_analyzed.lectures.length}
- **Total Labs:** ${materials_analyzed.labs.length}
- **Total Readings:** ${materials_analyzed.readings.length}
- **Estimated Lecture Time:** ${totalHours} hours

---

**Next Step:** Use this material base to proceed with Stages 1-5 of M1.`;
}

/**
 * Generate complete file content (YAML frontmatter + Markdown body)
 */
export function generateFileContent(
  data: MaterialAnalysisData,
  metadata: OutputMetadata
): string {
  const frontmatter = generateFrontmatter(data, metadata);
  const markdown = generateMarkdown(data);
  return `---\n${frontmatter}---\n\n${markdown}`;
}

/**
 * Export for complete_stage integration
 */
export const materialAnalysisOutput = {
  type: 'material_analysis' as const,
  schema: MaterialAnalysisSchema,
  generateFrontmatter,
  generateMarkdown,
  generateFileContent,
  filename: (module: string) => `${module}_material_analysis.md`
};
