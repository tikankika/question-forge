/**
 * Unit tests for misconceptions output
 */

import { describe, test, expect } from 'vitest';
import {
  MisconceptionsSchema,
  generateFrontmatter,
  generateMarkdown,
  generateFileContent,
  misconceptionsOutput,
  type MisconceptionsData
} from '../misconceptions.js';

// Valid test data with all severities
const validTestData: MisconceptionsData = {
  misconceptions: [
    {
      id: "M1",
      topic: "Mitochondria function",
      misconception: "Mitochondria create energy from nothing",
      correct: "Mitochondria convert chemical energy (glucose → ATP)",
      evidence: [
        { source: "Formative quiz week 3", frequency: "8/15 students" },
        { source: "Lab 2 discussion", frequency: "Common verbal error" }
      ],
      severity: "high",
      rationale: "Fundamental misunderstanding of energy transformation",
      teaching_strategy: "Emphasize conversion not creation, use analogy",
      distractor_example: "Mitokondrier skapar energi"
    },
    {
      id: "M2",
      topic: "Cell walls",
      misconception: "All cells have cell walls",
      correct: "Only plant cells and prokaryotes have cell walls",
      evidence: [
        { source: "Homework assignment 1", frequency: "5/15 students" }
      ],
      severity: "medium",
      rationale: "Overgeneralization from plant cell focus",
      teaching_strategy: "Explicitly contrast animal vs plant cells",
      distractor_example: "Alla celler har cellvägg"
    },
    {
      id: "M3",
      topic: "DNA location",
      misconception: "DNA is only in the nucleus",
      correct: "DNA is primarily in nucleus, but also in mitochondria",
      evidence: [
        { source: "Class discussion week 5", frequency: "3/15 students" }
      ],
      severity: "low",
      rationale: "Incomplete understanding, not fundamentally wrong",
      teaching_strategy: "Mention mitochondrial DNA explicitly",
      distractor_example: "DNA finns bara i cellkärnan"
    }
  ]
};

// Minimal valid data
const minimalTestData: MisconceptionsData = {
  misconceptions: []
};

// Single misconception data
const singleMisconceptionData: MisconceptionsData = {
  misconceptions: [
    {
      id: "M1",
      topic: "Test topic",
      misconception: "Test misconception",
      correct: "Test correct answer",
      evidence: [{ source: "Test source", frequency: "50%" }],
      severity: "high",
      rationale: "Test rationale",
      teaching_strategy: "Test strategy",
      distractor_example: "Test distractor"
    }
  ]
};

const testMetadata = {
  module: "m1",
  stage: 4,
  sessionId: "test-session-456"
};

describe('MisconceptionsSchema', () => {
  test('validates correct data', () => {
    expect(() => {
      MisconceptionsSchema.parse(validTestData);
    }).not.toThrow();
  });

  test('validates empty misconceptions array', () => {
    expect(() => {
      MisconceptionsSchema.parse(minimalTestData);
    }).not.toThrow();
  });

  test('validates single misconception', () => {
    expect(() => {
      MisconceptionsSchema.parse(singleMisconceptionData);
    }).not.toThrow();
  });

  test('validates all severity levels', () => {
    ['high', 'medium', 'low'].forEach(severity => {
      const data = {
        misconceptions: [{
          ...validTestData.misconceptions[0],
          severity
        }]
      };
      expect(() => {
        MisconceptionsSchema.parse(data);
      }).not.toThrow();
    });
  });

  test('rejects invalid severity level', () => {
    const invalid = {
      misconceptions: [{
        ...validTestData.misconceptions[0],
        severity: 'critical' // not a valid enum value
      }]
    };
    expect(() => {
      MisconceptionsSchema.parse(invalid);
    }).toThrow();
  });

  test('rejects missing required fields', () => {
    const invalid = {
      misconceptions: [{
        id: "M1",
        topic: "Test"
        // missing other required fields
      }]
    };
    expect(() => {
      MisconceptionsSchema.parse(invalid);
    }).toThrow();
  });

  test('rejects invalid evidence array', () => {
    const invalid = {
      misconceptions: [{
        ...validTestData.misconceptions[0],
        evidence: "not an array"
      }]
    };
    expect(() => {
      MisconceptionsSchema.parse(invalid);
    }).toThrow();
  });
});

describe('generateFrontmatter', () => {
  test('generates valid YAML with all fields', () => {
    const yaml = generateFrontmatter(validTestData, testMetadata);

    expect(yaml).toContain('module: m1');
    expect(yaml).toContain('stage: 4');
    expect(yaml).toContain('output_type: misconceptions');
    expect(yaml).toContain('session_id: test-session-456');
  });

  test('includes created timestamp', () => {
    const yaml = generateFrontmatter(validTestData, testMetadata);
    // js-yaml quotes strings with colons
    expect(yaml).toMatch(/created: '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);
  });

  test('includes misconceptions array', () => {
    const yaml = generateFrontmatter(validTestData, testMetadata);

    expect(yaml).toContain('misconceptions:');
    expect(yaml).toContain('id: M1');
    expect(yaml).toContain('severity: high');
  });
});

describe('generateMarkdown', () => {
  test('generates Markdown with correct structure', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('# M1 Common Student Misconceptions');
    expect(md).toContain('## HIGH SEVERITY Misconceptions');
    expect(md).toContain('## MEDIUM SEVERITY Misconceptions');
    expect(md).toContain('## LOW SEVERITY Misconceptions');
  });

  test('includes misconception details for high severity', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('### M1: "Mitochondria create energy from nothing"');
    expect(md).toContain('**Misconception:** Mitochondria create energy');
    expect(md).toContain('**Correct Understanding:**');
    expect(md).toContain('**Evidence:**');
    expect(md).toContain('**Teaching Strategy Used:**');
    expect(md).toContain('**Distractor Potential:** ⭐⭐⭐⭐⭐');
  });

  test('includes evidence items', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('- Formative quiz week 3: **8/15 students**');
    expect(md).toContain('- Lab 2 discussion: **Common verbal error**');
  });

  test('includes summary table', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('## Misconception Summary Table');
    expect(md).toContain('| ID | Topic | Misconception | Frequency | Severity | Distractor');
    expect(md).toContain('| M1 | Mitochondria function');
  });

  test('includes usage guidelines', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('## Usage Guidelines for M3');
    expect(md).toContain('**For HIGH severity misconceptions:**');
    expect(md).toContain('**For MEDIUM severity misconceptions:**');
    expect(md).toContain('**For LOW severity misconceptions:**');
  });

  test('includes next step guidance', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('**Next Step:**');
    expect(md).toContain('M3 uses these documented misconceptions');
  });

  test('handles empty misconceptions array', () => {
    const md = generateMarkdown(minimalTestData);

    expect(md).toContain('*No high severity misconceptions identified.*');
    expect(md).toContain('*No medium severity misconceptions identified.*');
    expect(md).toContain('*No low severity misconceptions identified.*');
  });

  test('assigns correct star ratings by severity', () => {
    const md = generateMarkdown(validTestData);

    // High severity gets 5 stars
    expect(md).toContain('⭐⭐⭐⭐⭐');
    // Medium severity gets 4 stars
    expect(md).toContain('⭐⭐⭐⭐');
    // Low severity gets 3 stars
    expect(md).toContain('⭐⭐⭐');
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
    expect(content).toContain('# M1 Common Student Misconceptions');
  });
});

describe('misconceptionsOutput', () => {
  test('has correct type', () => {
    expect(misconceptionsOutput.type).toBe('misconceptions');
  });

  test('generates correct filename', () => {
    expect(misconceptionsOutput.filename('m1')).toBe('m1_misconceptions.md');
  });

  test('exposes schema', () => {
    expect(misconceptionsOutput.schema).toBeDefined();
    expect(typeof misconceptionsOutput.schema.parse).toBe('function');
  });
});
