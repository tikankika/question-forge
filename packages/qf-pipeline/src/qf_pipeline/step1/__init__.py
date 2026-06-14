"""Step 1: Minimal Safety Net

Vision A Implementation (2026-01-28):
- Step 1 is used ONLY when Step 3 auto-fix fails
- Most files go: M5 → Step 2 → Step 3 → Step 4 (Step 1 skipped)
- Step 1 handles: unknown errors, Step 3 failures, structural issues

Archived modules (3200+ lines) removed in v0.1.2 cleanup.
Kept modules (~520 lines): frontmatter, parser, decision_logger
"""

# Kept: Frontmatter management
from .frontmatter import (
    add_frontmatter,
    update_frontmatter,
    remove_frontmatter,
    parse_frontmatter,
    has_frontmatter,
    create_progress_dict,
    update_progress,
)

# Kept: Question parsing
from .parser import (
    parse_file,
    ParsedQuestion,
)

# Kept: Decision logging
from .decision_logger import (
    log_decision,
    log_session_start,
    log_session_complete,
    log_navigation,
)

__all__ = [
    # Frontmatter
    'add_frontmatter',
    'update_frontmatter',
    'remove_frontmatter',
    'parse_frontmatter',
    'has_frontmatter',
    'create_progress_dict',
    'update_progress',
    # Parsing
    'parse_file',
    'ParsedQuestion',
    # Decision logging
    'log_decision',
    'log_session_start',
    'log_session_complete',
    'log_navigation',
]

# Previously archived modules (removed in v0.1.2):
# analyzer, detector, patterns, prompts, session, structural_issues, transformer, step1_tools
