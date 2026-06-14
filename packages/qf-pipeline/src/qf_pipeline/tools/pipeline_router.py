"""
Pipeline Router - Routes Step 2 validation errors to appropriate handler.

RFC-013 Appendix A: Error Routing & Categorization

Error Categories:
- MECHANICAL → Step 3 (auto-fix): Deterministic fixes, no human needed
- STRUCTURAL → Step 1 (teacher): Format issues needing human decision
- PEDAGOGICAL → M5 (content): Missing content that needs authoring

Usage:
    from qf_pipeline.tools.pipeline_router import route_errors, RouteDecision

    # After Step 2 validation
    decision = route_errors(step2_errors)

    if decision.route == "step3":
        # Run step3_autofix
    elif decision.route == "step1":
        # Teacher needs to fix structural issues
    elif decision.route == "m5":
        # Back to M5 for content
    else:  # "step4"
        # Ready for export!
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple
import re


class ErrorCategory(Enum):
    """Error categories for routing."""
    MECHANICAL = "mechanical"       # Step 3 auto-fixes
    STRUCTURAL = "structural"       # Step 1 teacher decision
    PEDAGOGICAL = "pedagogical"     # M5 content authoring


@dataclass
class CategorizedError:
    """An error with its category and metadata."""
    original: Dict                  # Original error from Step 2
    category: ErrorCategory
    question_id: str
    field: str
    message: str
    auto_fixable: bool
    fix_hint: Optional[str] = None


@dataclass
class RouteDecision:
    """Routing decision with details."""
    route: str                      # "step3", "step1", "m5", or "step4"
    reason: str                     # Why this route
    mechanical_errors: List[CategorizedError] = field(default_factory=list)
    structural_errors: List[CategorizedError] = field(default_factory=list)
    pedagogical_errors: List[CategorizedError] = field(default_factory=list)

    @property
    def total_errors(self) -> int:
        return len(self.mechanical_errors) + len(self.structural_errors) + len(self.pedagogical_errors)

    def summary(self) -> str:
        """Human-readable summary."""
        lines = [
            f"Route: {self.route.upper()}",
            f"Reason: {self.reason}",
            f"Total errors: {self.total_errors}",
            f"  - Mechanical (Step 3): {len(self.mechanical_errors)}",
            f"  - Structural (Step 1): {len(self.structural_errors)}",
            f"  - Pedagogical (M5): {len(self.pedagogical_errors)}",
        ]
        return "\n".join(lines)


# =============================================================================
# CATEGORIZATION PATTERNS
# =============================================================================

# MECHANICAL: Deterministic auto-fixes (Step 3)
MECHANICAL_PATTERNS = [
    # Metadata colon issues
    (r'has colon', 'Remove colon from metadata field'),
    (r'colon in.*metadata', 'Remove colon from metadata'),

    # Field positioning
    (r'not at start of line', 'Move field marker to line start'),

    # Field renames (deterministic)
    (r'multiple_response.*requires correct', 'Rename @field: answer to @field: correct_answers'),
    (r'requires correct_answers', 'Add or rename to @field: correct_answers'),

    # Syntax normalization
    (r'legacy.*syntax', 'Convert legacy syntax to current format'),
    (r'deprecated.*format', 'Update to current format'),
]

# STRUCTURAL: Need teacher decision (Step 1)
STRUCTURAL_PATTERNS = [
    # Separator issues
    (r'missing.*separator', 'Add question separator (---)'),
    (r'no separator', 'Add separator between questions'),

    # Malformed structure
    (r'malformed.*field', 'Fix field syntax'),
    (r'unclosed.*field', 'Close field block with @end_field'),
    (r'invalid.*field.*name', 'Check field name spelling'),

    # Duplicate/conflicting
    (r'duplicate.*field', 'Remove duplicate field'),
    (r'conflicting', 'Resolve conflict'),

    # Question structure
    (r'missing.*header', 'Add question header'),
    (r'invalid.*type', 'Fix question type'),
    (r'unknown.*type', 'Correct question type name'),
]

# PEDAGOGICAL: Need content authoring (M5)
PEDAGOGICAL_PATTERNS = [
    # Missing content
    (r'missing.*content', 'Add question content'),
    (r'empty.*question', 'Write question text'),
    (r'no.*text', 'Add question text'),

    # Missing options/answers (content, not field name)
    (r'requires options', 'Add answer options'),
    (r'missing.*options', 'Add answer options'),
    (r'no.*options', 'Create answer options'),

    # Correct answers not marked (content issue)
    (r'no correct.*marked', 'Mark correct answer(s) with [correct]'),
    (r'mark.*correct', 'Mark correct answer(s)'),

    # Missing pedagogical fields
    (r'missing.*feedback', 'Add feedback text'),
    (r'missing.*explanation', 'Add explanation'),
    (r'requires.*blanks', 'Define blank fields'),
    (r'missing.*blanks', 'Add blank definitions'),

    # Incomplete content
    (r'incomplete', 'Complete the content'),
    (r'empty', 'Add content'),
]


def categorize_error(error: Dict) -> CategorizedError:
    """
    Categorize a single error from Step 2 validation.

    Args:
        error: Dict with 'question_id', 'field', 'message' keys

    Returns:
        CategorizedError with category and metadata
    """
    msg = error.get('message', '').lower()
    question_id = error.get('question_id', 'unknown')
    field_name = error.get('field', 'unknown')

    # Check MECHANICAL patterns first (highest priority for auto-fix)
    for pattern, hint in MECHANICAL_PATTERNS:
        if re.search(pattern, msg, re.IGNORECASE):
            return CategorizedError(
                original=error,
                category=ErrorCategory.MECHANICAL,
                question_id=question_id,
                field=field_name,
                message=error.get('message', ''),
                auto_fixable=True,
                fix_hint=hint
            )

    # Check STRUCTURAL patterns
    for pattern, hint in STRUCTURAL_PATTERNS:
        if re.search(pattern, msg, re.IGNORECASE):
            return CategorizedError(
                original=error,
                category=ErrorCategory.STRUCTURAL,
                question_id=question_id,
                field=field_name,
                message=error.get('message', ''),
                auto_fixable=False,
                fix_hint=hint
            )

    # Check PEDAGOGICAL patterns
    for pattern, hint in PEDAGOGICAL_PATTERNS:
        if re.search(pattern, msg, re.IGNORECASE):
            return CategorizedError(
                original=error,
                category=ErrorCategory.PEDAGOGICAL,
                question_id=question_id,
                field=field_name,
                message=error.get('message', ''),
                auto_fixable=False,
                fix_hint=hint
            )

    # Default: Unknown errors go to STRUCTURAL (safer - needs human)
    return CategorizedError(
        original=error,
        category=ErrorCategory.STRUCTURAL,
        question_id=question_id,
        field=field_name,
        message=error.get('message', ''),
        auto_fixable=False,
        fix_hint='Unknown error - review manually'
    )


def route_errors(errors: List[Dict]) -> RouteDecision:
    """
    Route Step 2 validation errors to appropriate handler.

    Priority order:
    1. If ALL errors are MECHANICAL → Step 3 (auto-fix all)
    2. If any MECHANICAL errors → Step 3 first (fix what we can)
    3. If only STRUCTURAL errors → Step 1 (teacher decision)
    4. If only PEDAGOGICAL errors → M5 (content authoring)
    5. If no errors → Step 4 (export!)

    Args:
        errors: List of error dicts from Step 2 validation

    Returns:
        RouteDecision with route and categorized errors
    """
    if not errors:
        return RouteDecision(
            route="step4",
            reason="No errors - ready for export",
            mechanical_errors=[],
            structural_errors=[],
            pedagogical_errors=[]
        )

    # Categorize all errors
    mechanical = []
    structural = []
    pedagogical = []

    for error in errors:
        categorized = categorize_error(error)
        if categorized.category == ErrorCategory.MECHANICAL:
            mechanical.append(categorized)
        elif categorized.category == ErrorCategory.STRUCTURAL:
            structural.append(categorized)
        else:
            pedagogical.append(categorized)

    # Determine route based on priority
    if mechanical:
        # If we have mechanical errors, Step 3 first
        if structural or pedagogical:
            reason = f"Fix {len(mechanical)} mechanical errors first, then re-validate"
        else:
            reason = f"All {len(mechanical)} errors are auto-fixable"
        return RouteDecision(
            route="step3",
            reason=reason,
            mechanical_errors=mechanical,
            structural_errors=structural,
            pedagogical_errors=pedagogical
        )

    elif structural:
        # No mechanical, but structural issues
        if pedagogical:
            reason = f"Fix {len(structural)} structural issues first (teacher decision needed)"
        else:
            reason = f"All {len(structural)} errors need teacher decision"
        return RouteDecision(
            route="step1",
            reason=reason,
            mechanical_errors=mechanical,
            structural_errors=structural,
            pedagogical_errors=pedagogical
        )

    elif pedagogical:
        # Only pedagogical issues
        return RouteDecision(
            route="m5",
            reason=f"All {len(pedagogical)} errors need content authoring",
            mechanical_errors=mechanical,
            structural_errors=structural,
            pedagogical_errors=pedagogical
        )

    # Should not reach here, but just in case
    return RouteDecision(
        route="step4",
        reason="No actionable errors",
        mechanical_errors=[],
        structural_errors=[],
        pedagogical_errors=[]
    )


def format_route_decision(decision: RouteDecision, verbose: bool = True) -> str:
    """
    Format route decision for display.

    Args:
        decision: RouteDecision object
        verbose: If True, include error details

    Returns:
        Formatted string for display
    """
    lines = [
        "# Pipeline Routing Decision",
        "",
        f"**Route to:** `{decision.route}`",
        f"**Reason:** {decision.reason}",
        "",
        "## Error Summary",
        f"- Mechanical (→ Step 3): {len(decision.mechanical_errors)}",
        f"- Structural (→ Step 1): {len(decision.structural_errors)}",
        f"- Pedagogical (→ M5): {len(decision.pedagogical_errors)}",
        f"- **Total:** {decision.total_errors}",
    ]

    if verbose and decision.total_errors > 0:
        if decision.mechanical_errors:
            lines.extend([
                "",
                "## Mechanical Errors (Auto-fixable)",
            ])
            for err in decision.mechanical_errors:
                lines.append(f"- **{err.question_id}** [{err.field}]: {err.message}")
                if err.fix_hint:
                    lines.append(f"  - Fix: {err.fix_hint}")

        if decision.structural_errors:
            lines.extend([
                "",
                "## Structural Errors (Teacher Decision)",
            ])
            for err in decision.structural_errors:
                lines.append(f"- **{err.question_id}** [{err.field}]: {err.message}")
                if err.fix_hint:
                    lines.append(f"  - Hint: {err.fix_hint}")

        if decision.pedagogical_errors:
            lines.extend([
                "",
                "## Pedagogical Errors (Content Needed)",
            ])
            for err in decision.pedagogical_errors:
                lines.append(f"- **{err.question_id}** [{err.field}]: {err.message}")
                if err.fix_hint:
                    lines.append(f"  - Hint: {err.fix_hint}")

    # Add next steps
    lines.extend([
        "",
        "## Next Steps",
    ])

    if decision.route == "step3":
        lines.append("1. Run `step3_autofix` to fix mechanical errors")
        lines.append("2. Re-run `step2_validate` to check result")
        if decision.structural_errors or decision.pedagogical_errors:
            lines.append("3. After Step 3, other errors may need attention")

    elif decision.route == "step1":
        lines.append("1. Run `step1_start` to review structural issues")
        lines.append("2. Teacher approves/fixes each issue")
        lines.append("3. Run `step1_finish` when done")
        lines.append("4. Re-run `step2_validate` to confirm")

    elif decision.route == "m5":
        lines.append("1. Return to M5 for content authoring")
        lines.append("2. Add missing content (options, feedback, etc.)")
        lines.append("3. Re-run pipeline from Step 2")

    else:  # step4
        lines.append("1. Run `step4_export` to create QTI package")
        lines.append("2. Ready for LMS import!")

    return "\n".join(lines)


# =============================================================================
# MCP TOOL HANDLER
# =============================================================================

async def handle_pipeline_route(arguments: dict) -> dict:
    """
    MCP tool handler for pipeline_route.

    Args:
        arguments: Dict with 'errors' (list) or 'file_path' (str)

    Returns:
        Dict with route decision and formatted output
    """
    errors = arguments.get('errors', [])
    verbose = arguments.get('verbose', True)

    # If file_path provided, run validation first
    if arguments.get('file_path') and not errors:
        # Import here to avoid circular dependency
        from .step3_autofix import Step3AutoFixer

        file_path = arguments['file_path']
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        fixer = Step3AutoFixer(content)
        validation = fixer._validate()
        errors = validation.get('errors', [])

    # Route the errors
    decision = route_errors(errors)

    # Format output
    formatted = format_route_decision(decision, verbose=verbose)

    return {
        "route": decision.route,
        "reason": decision.reason,
        "total_errors": decision.total_errors,
        "mechanical_count": len(decision.mechanical_errors),
        "structural_count": len(decision.structural_errors),
        "pedagogical_count": len(decision.pedagogical_errors),
        "formatted_output": formatted,
        "errors": {
            "mechanical": [e.original for e in decision.mechanical_errors],
            "structural": [e.original for e in decision.structural_errors],
            "pedagogical": [e.original for e in decision.pedagogical_errors],
        }
    }
