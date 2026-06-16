/**
 * Unit tests for examples output
 */

import { describe, test, expect } from 'vitest';
import {
  ExamplesSchema,
  generateFrontmatter,
  generateMarkdown,
  generateFileContent,
  examplesOutput,
  type ExamplesData
} from '../examples.js';

// Valid test data
const validTestData: ExamplesData = {
  materials_reviewed: "8 lectures, 3 labs, assigned readings",
  examples: [
    {
      id: "EX1",
      title: "Red Blood Cell Diagram",
      source: "Lecture 1, Slide 12",
      topic: "Cell structure - animal cells",
      learning_objective: "LO1.1",
      context: "Compared to plant cell to show structural differences",
      visual: true,
      usage_count: 3,
      contexts: [
        "Lecture 1: Introduction to cell types",
        "Lab 1: Microscopy observation",
        "Lecture 4: Review before quiz"
      ],
      effectiveness: "high",
      student_familiarity: "very_high",
      question_potential: {
        bloom_levels: ["Remember", "Understand"],
        question_types: ["multiple_choice", "labeling"],
        example_stem: "Som vi såg i Lecture 1, vilken struktur saknar röda blodkroppar?"
      }
    },
    {
      id: "EX2",
      title: "Membrane Transport Lab Demonstration",
      source: "Lab 1, Practical Exercise",
      topic: "Membrane transport - diffusion",
      learning_objective: "LO2.1",
      context: "Hands-on demonstration with dye diffusion",
      visual: true,
      hands_on: true,
      usage_count: 2,
      contexts: [
        "Lab 1: Practical demonstration",
        "Lecture 3: Theoretical explanation"
      ],
      effectiveness: "very_high",
      student_familiarity: "high",
      question_potential: {
        bloom_levels: ["Apply", "Analyze"],
        question_types: ["scenario_based", "prediction"],
        example_stem: "I Lab 1 observerade vi färgdiffusion. Om koncentrationen ökas, vad händer?"
      }
    }
  ]
};

// Minimal valid data
const minimalTestData: ExamplesData = {
  examples: []
};

// Single example data
const singleExampleData: ExamplesData = {
  examples: [
    {
      id: "EX1",
      title: "Test Example",
      source: "Test Source",
      topic: "Test Topic",
      context: "Test context",
      usage_count: 1,
      contexts: ["Context 1"],
      effectiveness: "medium",
      student_familiarity: "medium",
      question_potential: {
        bloom_levels: ["Remember"],
        question_types: ["multiple_choice"]
      }
    }
  ]
};

const testMetadata = {
  module: "m1",
  stage: 3,
  sessionId: "test-session-ex"
};

describe('ExamplesSchema', () => {
  test('validates correct data', () => {
    expect(() => {
      ExamplesSchema.parse(validTestData);
    }).not.toThrow();
  });

  test('validates minimal data (empty examples)', () => {
    expect(() => {
      ExamplesSchema.parse(minimalTestData);
    }).not.toThrow();
  });

  test('validates single example', () => {
    expect(() => {
      ExamplesSchema.parse(singleExampleData);
    }).not.toThrow();
  });

  test('validates all effectiveness levels', () => {
    ['low', 'medium', 'high', 'very_high'].forEach(level => {
      const data: ExamplesData = {
        examples: [{
          ...singleExampleData.examples[0],
          effectiveness: level as any
        }]
      };
      expect(() => ExamplesSchema.parse(data)).not.toThrow();
    });
  });

  test('validates all familiarity levels', () => {
    ['low', 'medium', 'high', 'very_high'].forEach(level => {
      const data: ExamplesData = {
        examples: [{
          ...singleExampleData.examples[0],
          student_familiarity: level as any
        }]
      };
      expect(() => ExamplesSchema.parse(data)).not.toThrow();
    });
  });

  test('rejects invalid effectiveness level', () => {
    const invalid = {
      examples: [{
        ...singleExampleData.examples[0],
        effectiveness: "invalid"
      }]
    };
    expect(() => ExamplesSchema.parse(invalid)).toThrow();
  });

  test('accepts optional fields', () => {
    const dataWithOptional: ExamplesData = {
      examples: [{
        id: "EX1",
        title: "Test",
        source: "Source",
        topic: "Topic",
        context: "Context",
        usage_count: 1,
        contexts: [],
        effectiveness: "high",
        student_familiarity: "high",
        question_potential: {
          bloom_levels: [],
          question_types: []
        }
        // No learning_objective, visual, hands_on
      }]
    };
    expect(() => ExamplesSchema.parse(dataWithOptional)).not.toThrow();
  });
});

describe('generateFrontmatter', () => {
  test('generates valid YAML', () => {
    const yaml = generateFrontmatter(validTestData, testMetadata);

    expect(yaml).toContain('module: m1');
    expect(yaml).toContain('stage: 3');
    expect(yaml).toContain('output_type: examples');
    expect(yaml).toContain('session_id: test-session-ex');
  });

  test('includes examples array', () => {
    const yaml = generateFrontmatter(validTestData, testMetadata);

    expect(yaml).toContain('examples:');
    expect(yaml).toContain('id: EX1');
    expect(yaml).toContain('title: Red Blood Cell Diagram');
  });
});

describe('generateMarkdown', () => {
  test('generates Markdown with correct structure', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('# M1 Instructional Examples Catalog');
    expect(md).toContain('**Total Examples Cataloged:** 2');
    expect(md).toContain('## Example Usage Guidelines for M3');
    expect(md).toContain('## Summary Statistics');
  });

  test('includes example details', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('## Example 1: Red Blood Cell Diagram');
    expect(md).toContain('**Source:** Lecture 1, Slide 12');
    expect(md).toContain('### Context');
    expect(md).toContain('### Usage Across Course');
    expect(md).toContain('### Effectiveness Assessment');
    expect(md).toContain('### Question Potential');
  });

  test('shows visual and hands-on indicators', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('📊 Visual');
    expect(md).toContain('🔬 Hands-On');
  });

  test('includes question potential details', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('**Suitable Bloom Levels:**');
    expect(md).toContain('**Question Types:**');
    expect(md).toContain('**Example Question Stem:**');
  });

  test('includes summary table', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('| Example | Source Type | Usage Count');
    expect(md).toContain('| EX1 |');
    expect(md).toContain('| EX2 |');
  });

  test('handles empty examples', () => {
    const md = generateMarkdown(minimalTestData);

    expect(md).toContain('*No examples cataloged.*');
  });

  test('includes next step guidance', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('**Next Step:**');
    expect(md).toContain('M3');
  });
});

describe('generateFileContent', () => {
  test('combines YAML frontmatter and Markdown body', () => {
    const content = generateFileContent(validTestData, testMetadata);

    expect(content.startsWith('---\n')).toBe(true);
    expect(content).toContain('---\n\n#');
    expect(content).toContain('module: m1');
    expect(content).toContain('# M1 Instructional Examples Catalog');
  });
});

describe('examplesOutput', () => {
  test('has correct type', () => {
    expect(examplesOutput.type).toBe('examples');
  });

  test('generates correct filename', () => {
    expect(examplesOutput.filename('m1')).toBe('m1_examples.md');
  });
});
