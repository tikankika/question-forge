/**
 * Unit tests for learning_objectives output
 */

import { describe, test, expect } from 'vitest';
import {
  LearningObjectivesSchema,
  generateFrontmatter,
  generateMarkdown,
  generateFileContent,
  learningObjectivesOutput,
  type LearningObjectivesData
} from '../learning_objectives.js';

// Valid test data
const validTestData: LearningObjectivesData = {
  course: "Celler och Virus",
  instructor: "Example Instructor",
  tier1: [
    {
      id: "LO1.1",
      text: "Describe the basic structure of prokaryotic and eukaryotic cells",
      bloom: "Remember",
      rationale: "Fundamental concept, 30% of instruction time"
    },
    {
      id: "LO1.2",
      text: "Explain the function of mitochondria in cellular respiration",
      bloom: "Understand",
      rationale: "Explicitly stated as 'critical for exam'"
    }
  ],
  tier2: [
    {
      id: "LO2.1",
      text: "Analyze how cell membrane structure relates to function",
      bloom: "Analyze",
      rationale: "Important for lab work, moderate emphasis"
    }
  ],
  tier3: [
    {
      id: "LO3.1",
      text: "Describe the endosymbiotic theory",
      bloom: "Remember",
      rationale: "Background knowledge, mentioned once"
    }
  ],
  tier4_excluded: [
    "Advanced molecular genetics (explicitly out of scope)",
    "Detailed biochemical pathways (covered in BI2002)"
  ]
};

// Minimal valid test data
const minimalTestData: LearningObjectivesData = {
  course: "Test Course",
  tier1: [],
  tier2: [],
  tier3: [],
  tier4_excluded: []
};

const testMetadata = {
  module: "m1",
  stage: 5,
  sessionId: "test-session-123"
};

describe('LearningObjectivesSchema', () => {
  test('validates correct data', () => {
    expect(() => {
      LearningObjectivesSchema.parse(validTestData);
    }).not.toThrow();
  });

  test('validates minimal data (empty arrays)', () => {
    expect(() => {
      LearningObjectivesSchema.parse(minimalTestData);
    }).not.toThrow();
  });

  test('accepts optional instructor field', () => {
    const dataWithoutInstructor = { ...validTestData };
    delete (dataWithoutInstructor as any).instructor;

    expect(() => {
      LearningObjectivesSchema.parse(dataWithoutInstructor);
    }).not.toThrow();
  });

  test('rejects invalid tier1 (not an array)', () => {
    const invalid = { ...validTestData, tier1: "not an array" };
    expect(() => {
      LearningObjectivesSchema.parse(invalid);
    }).toThrow();
  });

  test('rejects missing required fields in tier1 items', () => {
    const invalid = {
      ...validTestData,
      tier1: [{ id: "LO1.1", text: "Test" }] // missing bloom and rationale
    };
    expect(() => {
      LearningObjectivesSchema.parse(invalid);
    }).toThrow();
  });

  test('rejects missing course field', () => {
    const invalid = { ...validTestData };
    delete (invalid as any).course;

    expect(() => {
      LearningObjectivesSchema.parse(invalid);
    }).toThrow();
  });
});

describe('generateFrontmatter', () => {
  test('generates valid YAML with all fields', () => {
    const yaml = generateFrontmatter(validTestData, testMetadata);

    expect(yaml).toContain('module: m1');
    expect(yaml).toContain('stage: 5');
    expect(yaml).toContain('output_type: learning_objectives');
    expect(yaml).toContain('session_id: test-session-123');
    expect(yaml).toContain('course: Celler och Virus');
    expect(yaml).toContain('instructor: Example Instructor');
  });

  test('includes created timestamp', () => {
    const yaml = generateFrontmatter(validTestData, testMetadata);

    // Should contain ISO timestamp (js-yaml quotes strings with colons)
    expect(yaml).toMatch(/created: '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);
  });

  test('includes learning_objectives structure', () => {
    const yaml = generateFrontmatter(validTestData, testMetadata);

    expect(yaml).toContain('learning_objectives:');
    expect(yaml).toContain('tier1:');
    expect(yaml).toContain('tier2:');
    expect(yaml).toContain('tier3:');
    expect(yaml).toContain('tier4_excluded:');
  });
});

describe('generateMarkdown', () => {
  test('generates Markdown with correct structure', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('# M1 Learning Objectives');
    expect(md).toContain('**Course:** Celler och Virus');
    expect(md).toContain('**Instructor:** Example Instructor');
    expect(md).toContain('## Tier 1: Core Concepts');
    expect(md).toContain('## Tier 2: Important');
    expect(md).toContain('## Tier 3: Useful Background');
    expect(md).toContain('## Tier 4: Excluded from Assessment');
  });

  test('includes learning objective details', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('**LO1.1**');
    expect(md).toContain('(Remember)');
    expect(md).toContain('Describe the basic structure');
    expect(md).toContain('*Rationale:*');
  });

  test('includes tier4 excluded items', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('- Advanced molecular genetics');
    expect(md).toContain('- Detailed biochemical pathways');
  });

  test('handles empty tiers gracefully', () => {
    const md = generateMarkdown(minimalTestData);

    expect(md).toContain('*No Tier 1 objectives defined.*');
    expect(md).toContain('*No Tier 2 objectives defined.*');
    expect(md).toContain('*No excluded topics.*');
  });

  test('handles missing instructor', () => {
    const dataWithoutInstructor = { ...validTestData };
    delete (dataWithoutInstructor as any).instructor;

    const md = generateMarkdown(dataWithoutInstructor);
    expect(md).toContain('**Instructor:** N/A');
  });

  test('includes next step guidance', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('**Next Step:**');
    expect(md).toContain('M2 Assessment Design');
  });
});

describe('generateFileContent', () => {
  test('combines YAML frontmatter and Markdown body', () => {
    const content = generateFileContent(validTestData, testMetadata);

    // Should start with YAML delimiter
    expect(content.startsWith('---\n')).toBe(true);

    // Should have closing YAML delimiter
    expect(content).toContain('---\n\n#');

    // Should contain both parts
    expect(content).toContain('module: m1');
    expect(content).toContain('# M1 Learning Objectives');
  });
});

describe('learningObjectivesOutput', () => {
  test('has correct type', () => {
    expect(learningObjectivesOutput.type).toBe('learning_objectives');
  });

  test('generates correct filename', () => {
    expect(learningObjectivesOutput.filename('m1')).toBe('m1_learning_objectives.md');
  });

  test('exposes schema', () => {
    expect(learningObjectivesOutput.schema).toBeDefined();
    expect(typeof learningObjectivesOutput.schema.parse).toBe('function');
  });
});
