/**
 * Unit tests for material_analysis output
 */

import { describe, test, expect } from 'vitest';
import {
  MaterialAnalysisSchema,
  generateFrontmatter,
  generateMarkdown,
  generateFileContent,
  materialAnalysisOutput,
  type MaterialAnalysisData
} from '../material_analysis.js';

// Valid test data
const validTestData: MaterialAnalysisData = {
  analysis_duration: 90,
  analyst: "Claude Sonnet 4",
  materials_analyzed: {
    lectures: [
      {
        title: "Lecture 1: Introduction to Cells",
        date: "2025-09-15",
        duration: 90,
        slides: 45,
        transcript: true,
        topics: ["Cell types", "prokaryotic vs eukaryotic"]
      },
      {
        title: "Lecture 2: Mitochondria and Energy",
        date: "2025-09-22",
        duration: 60,
        slides: 30,
        transcript: true,
        topics: ["Cellular respiration", "ATP production"]
      }
    ],
    labs: [
      {
        title: "Lab 1: Cell Observation",
        date: "2025-09-20",
        handout_pages: 8,
        practical: true,
        activities: ["Microscopy", "diffusion demonstration"]
      }
    ],
    readings: [
      {
        title: "Campbell Biology Ch. 3-4",
        pages: 45,
        required: true,
        topics: ["Cell structure", "organelles"]
      }
    ]
  },
  completeness: {
    all_lectures: true,
    all_labs: true,
    all_readings: true,
    missing: ["Guest lecture (scheduled 2026-02-05)"]
  },
  quality_assessment: {
    lecture_clarity: "high",
    lecture_consistency: "high",
    emphasis_signals: "very_high",
    lab_connection: "good",
    reading_alignment: "strong"
  }
};

// Minimal valid data
const minimalTestData: MaterialAnalysisData = {
  materials_analyzed: {
    lectures: [],
    labs: [],
    readings: []
  },
  completeness: {
    all_lectures: true,
    all_labs: true,
    all_readings: true
  }
};

const testMetadata = {
  module: "m1",
  stage: 0,
  sessionId: "test-session-ma"
};

describe('MaterialAnalysisSchema', () => {
  test('validates correct data', () => {
    expect(() => {
      MaterialAnalysisSchema.parse(validTestData);
    }).not.toThrow();
  });

  test('validates minimal data', () => {
    expect(() => {
      MaterialAnalysisSchema.parse(minimalTestData);
    }).not.toThrow();
  });

  test('validates all quality levels', () => {
    ['low', 'medium', 'high'].forEach(level => {
      const data: MaterialAnalysisData = {
        ...minimalTestData,
        quality_assessment: {
          lecture_clarity: level as any
        }
      };
      expect(() => MaterialAnalysisSchema.parse(data)).not.toThrow();
    });
  });

  test('validates lab connection levels', () => {
    ['weak', 'good', 'strong'].forEach(level => {
      const data: MaterialAnalysisData = {
        ...minimalTestData,
        quality_assessment: {
          lab_connection: level as any
        }
      };
      expect(() => MaterialAnalysisSchema.parse(data)).not.toThrow();
    });
  });

  test('accepts optional fields', () => {
    const dataWithOptional: MaterialAnalysisData = {
      materials_analyzed: {
        lectures: [{
          title: "Test Lecture"
          // No date, duration, slides, transcript, topics
        }],
        labs: [{
          title: "Test Lab"
          // No date, handout_pages, practical, activities
        }],
        readings: [{
          title: "Test Reading"
          // No pages, required, topics
        }]
      },
      completeness: {
        all_lectures: true,
        all_labs: true,
        all_readings: true
        // No missing
      }
      // No analysis_duration, analyst, quality_assessment
    };
    expect(() => MaterialAnalysisSchema.parse(dataWithOptional)).not.toThrow();
  });

  test('rejects invalid quality level', () => {
    const invalid = {
      ...minimalTestData,
      quality_assessment: {
        lecture_clarity: "invalid"
      }
    };
    expect(() => MaterialAnalysisSchema.parse(invalid)).toThrow();
  });
});

describe('generateFrontmatter', () => {
  test('generates valid YAML', () => {
    const yaml = generateFrontmatter(validTestData, testMetadata);

    expect(yaml).toContain('module: m1');
    expect(yaml).toContain('stage: 0');
    expect(yaml).toContain('output_type: material_analysis');
    expect(yaml).toContain('session_id: test-session-ma');
    expect(yaml).toContain('analysis_duration: 90');
  });

  test('includes materials_analyzed structure', () => {
    const yaml = generateFrontmatter(validTestData, testMetadata);

    expect(yaml).toContain('materials_analyzed:');
    expect(yaml).toContain('lectures:');
    expect(yaml).toContain('labs:');
    expect(yaml).toContain('readings:');
  });

  test('includes completeness check', () => {
    const yaml = generateFrontmatter(validTestData, testMetadata);

    expect(yaml).toContain('completeness:');
    expect(yaml).toContain('all_lectures: true');
  });
});

describe('generateMarkdown', () => {
  test('generates Markdown with correct structure', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('# M1 Material Analysis');
    expect(md).toContain('## Materials Analyzed');
    expect(md).toContain('### Lectures');
    expect(md).toContain('### Labs');
    expect(md).toContain('### Readings');
    expect(md).toContain('## Completeness Check');
    expect(md).toContain('## Summary');
  });

  test('includes lecture details', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('**Lecture 1: Introduction to Cells**');
    expect(md).toContain('- Date: 2025-09-15');
    expect(md).toContain('- Duration: 90 minutes');
    expect(md).toContain('- Slides: 45');
    expect(md).toContain('- Transcript: ✅ Available');
  });

  test('includes lab details', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('**Lab 1: Cell Observation**');
    expect(md).toContain('- Handout: 8 pages');
    expect(md).toContain('- Practical: ✅ Yes');
  });

  test('includes reading details', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('**Campbell Biology Ch. 3-4**');
    expect(md).toContain('- Pages: 45');
    expect(md).toContain('- Required: ✅ Yes');
  });

  test('includes completeness indicators', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('✅ **All scheduled lectures analyzed**');
    expect(md).toContain('⚠️ **Missing:**');
  });

  test('includes quality assessment when provided', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('## Material Quality Assessment');
    expect(md).toContain('- **Clarity:** High');
    expect(md).toContain('- **Consistency:** High');
  });

  test('handles empty materials', () => {
    const md = generateMarkdown(minimalTestData);

    expect(md).toContain('*No lectures analyzed.*');
    expect(md).toContain('*No labs analyzed.*');
    expect(md).toContain('*No readings analyzed.*');
  });

  test('calculates total instruction time', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('**Estimated Lecture Time:**');
    expect(md).toContain('2.5 hours'); // 90 + 60 = 150 minutes = 2.5 hours
  });

  test('includes next step guidance', () => {
    const md = generateMarkdown(validTestData);

    expect(md).toContain('**Next Step:**');
    expect(md).toContain('Stages 1-5');
  });
});

describe('generateFileContent', () => {
  test('combines YAML frontmatter and Markdown body', () => {
    const content = generateFileContent(validTestData, testMetadata);

    expect(content.startsWith('---\n')).toBe(true);
    expect(content).toContain('---\n\n#');
    expect(content).toContain('module: m1');
    expect(content).toContain('# M1 Material Analysis');
  });
});

describe('materialAnalysisOutput', () => {
  test('has correct type', () => {
    expect(materialAnalysisOutput.type).toBe('material_analysis');
  });

  test('generates correct filename', () => {
    expect(materialAnalysisOutput.filename('m1')).toBe('m1_material_analysis.md');
  });
});
