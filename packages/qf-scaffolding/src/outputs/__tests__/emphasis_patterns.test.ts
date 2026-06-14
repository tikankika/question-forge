/**
 * Unit tests for emphasis_patterns output
 */

import { describe, test, expect } from 'vitest';
import {
  EmphasisPatternsSchema,
  generateFrontmatter,
  generateMarkdown,
  generateFileContent,
  emphasisPatternsOutput,
  type EmphasisPatternsData
} from '../emphasis_patterns.js';

// Valid test data
const validTestData: EmphasisPatternsData = {
  materials_analyzed: "8 lectures, 3 labs, 4 reading chapters",
  total_instruction_time: "12 hours",
  tier1: [
    {
      topic: "Mitochondria function",
      signals: [
        {
          type: "explicit",
          count: 6,
          examples: ["Detta är VIKTIGT för tentan", "Kom ihåg till examen"]
        },
        {
          type: "time",
          percentage: 30,
          context: "3 of 8 lectures focused primarily on this"
        },
        {
          type: "repetition",
          count: 5,
          context: "Repeated in different contexts"
        }
      ],
      rationale: "Highest combination of explicit, time, and repetition signals"
    }
  ],
  tier2: [
    {
      topic: "Membrane transport",
      signals: [
        {
          type: "time",
          percentage: 15,
          context: "Dedicated lab session"
        },
        {
          type: "practical",
          context: "Hands-on lab focus"
        }
      ],
      rationale: "Practical application focus, moderate emphasis"
    }
  ],
  tier3: [
    {
      topic: "Endosymbiotic theory",
      signals: [
        {
          type: "explicit",
          count: 1,
          examples: ["Interesting background, won't be on exam"]
        }
      ],
      rationale: "Explicitly marked as non-critical"
    }
  ],
  tier4: [
    {
      topic: "Advanced molecular genetics",
      signals: [
        {
          type: "explicit",
          count: 1,
          examples: ["Out of scope for this course"]
        }
      ],
      rationale: "Explicitly excluded from scope"
    }
  ]
};

// Minimal valid data
const minimalTestData: EmphasisPatternsData = {
  tier1: [],
  tier2: [],
  tier3: [],
  tier4: []
};

const testMetadata = {
  module: "m1",
  stage: 2,
  sessionId: "test-session-ep"
};

describe('EmphasisPatternsSchema', () => {
  test('validates correct data', () => {
    expect(() => {
      EmphasisPatternsSchema.parse(validTestData);
    }).not.toThrow();
  });

  test('validates minimal data (empty tiers)', () => {
    expect(() => {
      EmphasisPatternsSchema.parse(minimalTestData);
    }).not.toThrow();
  });

  test('validates all signal types', () => {
    const signalTypes = ['explicit', 'time', 'repetition', 'foundational', 'visual', 'practical'];
    signalTypes.forEach(type => {
      const data: EmphasisPatternsData = {
        ...minimalTestData,
        tier1: [{
          topic: "Test",
          signals: [{ type: type as any }],
          rationale: "Test"
        }]
      };
      expect(() => EmphasisPatternsSchema.parse(data)).not.toThrow();
    });
  });

  test('rejects invalid signal type', () => {
    const invalid = {
      ...minimalTestData,
      tier1: [{
        topic: "Test",
        signals: [{ type: "invalid_type" }],
        rationale: "Test"
      }]
    };
    expect(() => EmphasisPatternsSchema.parse(invalid)).toThrow();
  });
});

describe('generateFrontmatter', () => {
  test('generates valid YAML', () => {
    const yaml = generateFrontmatter(validTestData, testMetadata);

    expect(yaml).toContain('module: m1');
    expect(yaml).toContain('stage: 2');
    expect(yaml).toContain('output_type: emphasis_patterns');
    expect(yaml).toContain('session_id: test-session-ep');
  });

  test('includes emphasis_analysis structure', () => {
    const yaml = generateFrontmatter(validTestData, testMetadata);

    expect(yaml).toContain('emphasis_analysis:');
    expect(yaml).toContain('tier1:');
    expect(yaml).toContain('tier2:');
    expect(yaml).toContain('tier3:');
    expect(yaml).toContain('tier4:');
  });
});

describe('generateMarkdown', () => {
  test('generates Markdown with correct structure', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('# M1 Emphasis Patterns Analysis');
    expect(md).toContain('## Tier 1: Critical Emphasis');
    expect(md).toContain('## Tier 2: Important');
    expect(md).toContain('## Tier 3: Useful Background');
    expect(md).toContain('## Tier 4: Excluded');
  });

  test('includes topic details', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('### Mitochondria function');
    expect(md).toContain('**Explicit priority:**');
    expect(md).toContain('**Time allocation:**');
    expect(md).toContain('**Rationale:**');
  });

  test('includes summary table', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('## Summary Statistics');
    expect(md).toContain('| Tier | Topics');
  });

  test('handles empty tiers', () => {
    const md = generateMarkdown(minimalTestData);

    expect(md).toContain('*No Tier 1 topics identified.*');
    expect(md).toContain('*No Tier 2 topics identified.*');
  });

  test('includes next step guidance', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('**Next Step:**');
    expect(md).toContain('M2');
  });
});

describe('generateFileContent', () => {
  test('combines YAML frontmatter and Markdown body', () => {
    const content = generateFileContent(validTestData, testMetadata);

    expect(content.startsWith('---\n')).toBe(true);
    expect(content).toContain('---\n\n#');
    expect(content).toContain('module: m1');
    expect(content).toContain('# M1 Emphasis Patterns Analysis');
  });
});

describe('emphasisPatternsOutput', () => {
  test('has correct type', () => {
    expect(emphasisPatternsOutput.type).toBe('emphasis_patterns');
  });

  test('generates correct filename', () => {
    expect(emphasisPatternsOutput.filename('m1')).toBe('m1_emphasis_patterns.md');
  });
});
