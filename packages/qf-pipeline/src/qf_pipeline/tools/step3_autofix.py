"""
Step 3: Auto-Fix Iteration Engine

Automatically fixes mechanical errors in QFMD markdown files.
Runs validation → fix → validation loop until valid or max rounds.

Self-Learning Features:
- Logs iterations to logs/step3_iterations.jsonl
- Reads/writes fix rules from logs/step3_fix_rules.json
- Updates rule confidence based on success rate

Usage:
    # As MCP tool
    step3_autofix({project_path: "...", input_file: "questions/draft.md"})

    # As CLI
    python -m qf_pipeline.tools.step3_autofix input.md [--project-path /path]

RFC-013: Pipeline Architecture v2.1
"""

import json
import re
import sys
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils.timestamp import get_timestamp

# Import validator from qti-core
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "qti-core"))
from src.parser.markdown_parser import MarkdownQuizParser


@dataclass
class FixRule:
    """A rule for auto-fixing a specific error type."""
    rule_id: str
    error_pattern: str  # Regex or string to match in error message
    fix_function: str   # Name of fix function
    confidence: float   # 0.0 - 1.0
    description: str
    success_count: int = 0
    applied_count: int = 0
    created_at: str = ""
    last_used: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'FixRule':
        """Create from dictionary."""
        return cls(**data)

    def update_stats(self, success: bool):
        """Update statistics after applying rule."""
        self.applied_count += 1
        if success:
            self.success_count += 1
        self.last_used = get_timestamp()
        # Recalculate confidence based on success rate
        if self.applied_count >= 5:  # Only adjust after 5 uses
            self.confidence = min(0.99, self.success_count / self.applied_count)


@dataclass
class FixResult:
    """Result of applying a fix."""
    success: bool
    rule_id: str
    error_message: str
    fix_applied: str
    lines_changed: int = 0


@dataclass
class Step3Result:
    """Final result of Step 3 iteration."""
    status: str  # "valid", "needs_m5", "needs_step1", "max_rounds", "error"
    rounds: int
    fixes_applied: List[FixResult] = field(default_factory=list)
    remaining_errors: List[Dict] = field(default_factory=list)
    message: str = ""
    session_id: str = ""


# Built-in fix rules (used if no learned rules exist)
DEFAULT_FIX_RULES = [
    FixRule(
        rule_id="STEP3_001",
        error_pattern="\\^type has colon",
        fix_function="fix_metadata_colon",
        confidence=0.95,
        description="Remove colon from ^type field",
        created_at="2026-01-26T00:00:00Z"
    ),
    FixRule(
        rule_id="STEP3_002",
        error_pattern="\\^identifier has colon",
        fix_function="fix_metadata_colon",
        confidence=0.95,
        description="Remove colon from ^identifier field",
        created_at="2026-01-26T00:00:00Z"
    ),
    FixRule(
        rule_id="STEP3_003",
        error_pattern="\\^points has colon",
        fix_function="fix_metadata_colon",
        confidence=0.95,
        description="Remove colon from ^points field",
        created_at="2026-01-26T00:00:00Z"
    ),
    FixRule(
        rule_id="STEP3_004",
        error_pattern="multiple_response.*requires correct.?answers",
        fix_function="fix_answer_to_correct_answers",
        confidence=0.95,
        description="Rename @field: answer to @field: correct_answers for multiple_response",
        created_at="2026-01-27T00:00:00Z"
    ),
    FixRule(
        rule_id="STEP3_005",
        error_pattern="multiple_response.*requires.*correct_answers.*found.*answer",
        fix_function="fix_answer_to_correct_answers",
        confidence=0.95,
        description="Rename @field: answer to @field: correct_answers for multiple_response",
        created_at="2026-01-27T00:00:00Z"
    ),
]


# =============================================================================
# Fix Rules Persistence (logs/step3_fix_rules.json)
# =============================================================================

def load_fix_rules(project_path: Optional[Path]) -> List[FixRule]:
    """
    Load fix rules from project's logs/step3_fix_rules.json.
    Falls back to DEFAULT_FIX_RULES if file doesn't exist.

    IMPORTANT: Always merges with DEFAULT_FIX_RULES to ensure new rules
    are available even if cached file exists (self-learning preserves
    learned confidence values for existing rules).
    """
    # Start with default rules (always include latest)
    default_rules = {r.rule_id: FixRule(**asdict(r)) for r in DEFAULT_FIX_RULES}

    if not project_path:
        return list(default_rules.values())

    rules_file = project_path / "logs" / "step3_fix_rules.json"

    if not rules_file.exists():
        # Initialize with default rules
        save_fix_rules(project_path, list(default_rules.values()))
        return list(default_rules.values())

    try:
        with open(rules_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Load cached rules and merge with defaults
        for rule_data in data.get('rules', []):
            rule = FixRule.from_dict(rule_data)
            if rule.rule_id in default_rules:
                # Keep learned confidence/counts from cached rule
                default_rules[rule.rule_id] = rule
            else:
                # Keep custom/graduated rules from cache
                default_rules[rule.rule_id] = rule

        return list(default_rules.values())

    except Exception as e:
        print(f"Warning: Could not load fix rules: {e}")
        return list(default_rules.values())


def save_fix_rules(project_path: Path, rules: List[FixRule]):
    """Save fix rules to project's logs/step3_fix_rules.json."""
    logs_dir = project_path / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    rules_file = logs_dir / "step3_fix_rules.json"

    data = {
        "version": "1.0",
        "updated_at": get_timestamp(),
        "rules": [r.to_dict() for r in rules]
    }

    with open(rules_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# =============================================================================
# Iterations Log (logs/step3_iterations.jsonl)
# =============================================================================

def log_iteration(
    project_path: Path,
    session_id: str,
    round_num: int,
    error: Dict,
    rule: FixRule,
    result: FixResult,
    file_path: str
):
    """
    Append iteration to logs/step3_iterations.jsonl.
    JSONL format: one JSON object per line.
    """
    logs_dir = project_path / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = logs_dir / "step3_iterations.jsonl"

    entry = {
        "ts": get_timestamp(),
        "v": 1,
        "session_id": session_id,
        "round": round_num,
        "file": file_path,
        "error": {
            "question_id": error.get('question_id', 'UNKNOWN'),
            "field": error.get('field', ''),
            "message": error.get('message', '')
        },
        "rule": {
            "rule_id": rule.rule_id,
            "confidence": rule.confidence,
            "description": rule.description
        },
        "result": {
            "success": result.success,
            "lines_changed": result.lines_changed
        }
    }

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def log_session_result(
    project_path: Path,
    session_id: str,
    result: 'Step3Result',
    file_path: str
):
    """Log final session result."""
    logs_dir = project_path / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = logs_dir / "step3_iterations.jsonl"

    entry = {
        "ts": get_timestamp(),
        "v": 1,
        "session_id": session_id,
        "event": "session_complete",
        "file": file_path,
        "result": {
            "status": result.status,
            "rounds": result.rounds,
            "fixes_applied": len(result.fixes_applied),
            "remaining_errors": len(result.remaining_errors)
        }
    }

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


# =============================================================================
# Step 3 Auto-Fix Engine
# =============================================================================

class Step3AutoFix:
    """
    Auto-fix mechanical errors through iteration.

    Workflow:
    1. Validate markdown
    2. Categorize errors (mechanical vs pedagogical)
    3. If mechanical: fix 1 error → save → loop
    4. If pedagogical: return "needs M5"
    5. If valid: return "ready for Step 4"
    6. Max rounds protection

    Self-Learning:
    - Loads rules from step3_fix_rules.json
    - Updates rule confidence after each fix
    - Logs iterations to step3_iterations.jsonl
    """

    def __init__(
        self,
        content: str,
        max_rounds: int = 10,
        project_path: Optional[Path] = None,
        file_path: str = ""
    ):
        self.content = content
        self.max_rounds = max_rounds
        self.project_path = project_path
        self.file_path = file_path
        self.session_id = str(uuid.uuid4())[:8]

        # Load rules (from file if project_path, else defaults)
        self.fix_rules = load_fix_rules(project_path)
        self.iteration_log: List[Dict] = []

    def run(self) -> Step3Result:
        """
        Run the auto-fix iteration loop.

        Returns:
            Step3Result with status and details
        """
        fixes_applied = []

        for round_num in range(self.max_rounds):
            # Validate current content
            validation = self._validate()

            # Check if valid
            if validation['valid']:
                result = Step3Result(
                    status="valid",
                    rounds=round_num,
                    fixes_applied=fixes_applied,
                    message=f"✅ Valid after {round_num} fix(es)",
                    session_id=self.session_id
                )
                self._finalize(result)
                return result

            # Categorize errors
            errors = validation['errors']
            mechanical, pedagogical = self._categorize_errors(errors)

            # If only pedagogical errors remain, exit to M5
            if not mechanical and pedagogical:
                result = Step3Result(
                    status="needs_m5",
                    rounds=round_num,
                    fixes_applied=fixes_applied,
                    remaining_errors=pedagogical,
                    message=f"❌ {len(pedagogical)} pedagogical error(s) - needs M5",
                    session_id=self.session_id
                )
                self._finalize(result)
                return result

            # If no errors but not valid (shouldn't happen)
            if not mechanical and not pedagogical:
                result = Step3Result(
                    status="error",
                    rounds=round_num,
                    fixes_applied=fixes_applied,
                    message="Unexpected state: no errors but not valid",
                    session_id=self.session_id
                )
                self._finalize(result)
                return result

            # Pick one mechanical error to fix (highest confidence rule first)
            error, rule = self._pick_best_fix(mechanical)

            if not rule:
                # No rule for any mechanical error
                result = Step3Result(
                    status="needs_step1",
                    rounds=round_num,
                    fixes_applied=fixes_applied,
                    remaining_errors=mechanical,
                    message=f"❌ No fix rule for: {mechanical[0].get('message', 'unknown')}",
                    session_id=self.session_id
                )
                self._finalize(result)
                return result

            # Apply fix
            fix_result = self._apply_fix(error, rule)

            # Update rule stats
            rule.update_stats(fix_result.success)

            if fix_result.success:
                fixes_applied.append(fix_result)

                # Log iteration
                if self.project_path:
                    log_iteration(
                        self.project_path,
                        self.session_id,
                        round_num,
                        error,
                        rule,
                        fix_result,
                        self.file_path
                    )

                self._log_iteration_internal(round_num, error, rule, fix_result)
            else:
                # Fix failed - continue to next round (might pick different error)
                pass

        # Max rounds reached
        final_validation = self._validate()
        result = Step3Result(
            status="max_rounds",
            rounds=self.max_rounds,
            fixes_applied=fixes_applied,
            remaining_errors=final_validation.get('errors', []),
            message=f"⚠️ Max rounds ({self.max_rounds}) reached",
            session_id=self.session_id
        )
        self._finalize(result)
        return result

    def _finalize(self, result: Step3Result):
        """Save rules and log final result."""
        # Save updated rules (with new confidence scores)
        if self.project_path:
            save_fix_rules(self.project_path, self.fix_rules)
            log_session_result(
                self.project_path,
                self.session_id,
                result,
                self.file_path
            )

    def _validate(self) -> Dict[str, Any]:
        """Validate current content using markdown_parser."""
        parser = MarkdownQuizParser(self.content)
        return parser.validate()

    def _categorize_errors(
        self,
        errors: List[Dict]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Categorize errors into mechanical vs pedagogical.

        Mechanical (auto-fixable):
        - Colon in metadata fields
        - Field not at start of line
        - Field name corrections (answer → correct_answers)

        Pedagogical (needs human):
        - Missing required CONTENT (not just field rename)
        - Missing options, blanks, etc.

        RFC-013 Appendix A: Error Routing & Categorization
        """
        mechanical = []
        pedagogical = []

        for error in errors:
            msg = error.get('message', '').lower()

            # Mechanical errors (can auto-fix)
            if 'has colon' in msg:
                mechanical.append(error)
            elif 'not at start of line' in msg:
                mechanical.append(error)
            # Field rename: multiple_response requires correct_answers (not answer)
            elif 'multiple_response' in msg and 'requires correct' in msg:
                mechanical.append(error)
            elif 'requires correct_answers' in msg:
                mechanical.append(error)
            # Pedagogical errors (need human to provide content)
            elif 'missing' in msg and 'content' in msg:
                pedagogical.append(error)
            elif 'empty' in msg:
                pedagogical.append(error)
            elif 'no correct' in msg and 'marked' in msg:
                pedagogical.append(error)
            # Other "requires" that aren't field renames
            elif 'requires' in msg:
                pedagogical.append(error)
            elif 'missing' in msg:
                pedagogical.append(error)
            else:
                # Unknown - treat as pedagogical (safer)
                pedagogical.append(error)

        return mechanical, pedagogical

    def _pick_best_fix(
        self,
        mechanical_errors: List[Dict]
    ) -> Tuple[Optional[Dict], Optional[FixRule]]:
        """
        Pick the best error/rule combination.
        Prioritizes highest confidence rules.
        """
        best_error = None
        best_rule = None
        best_confidence = 0.0

        for error in mechanical_errors:
            rule = self._match_rule(error)
            if rule and rule.confidence >= best_confidence:
                best_error = error
                best_rule = rule
                best_confidence = rule.confidence

        return best_error, best_rule

    def _match_rule(self, error: Dict) -> Optional[FixRule]:
        """Find the best fix rule matching this error (highest confidence)."""
        msg = error.get('message', '')
        best_rule = None
        best_confidence = -1.0

        for rule in self.fix_rules:
            if re.search(rule.error_pattern, msg, re.IGNORECASE):
                if rule.confidence > best_confidence:
                    best_rule = rule
                    best_confidence = rule.confidence

        return best_rule

    def _apply_fix(self, error: Dict, rule: FixRule) -> FixResult:
        """Apply a fix rule to the content."""
        fix_func = getattr(self, f'_{rule.fix_function}', None)

        if not fix_func:
            return FixResult(
                success=False,
                rule_id=rule.rule_id,
                error_message=error.get('message', ''),
                fix_applied=f"Fix function not found: {rule.fix_function}"
            )

        try:
            lines_changed = fix_func(error)

            return FixResult(
                success=lines_changed > 0,
                rule_id=rule.rule_id,
                error_message=error.get('message', ''),
                fix_applied=rule.description,
                lines_changed=lines_changed
            )
        except Exception as e:
            return FixResult(
                success=False,
                rule_id=rule.rule_id,
                error_message=error.get('message', ''),
                fix_applied=f"Error: {str(e)}"
            )

    def _fix_metadata_colon(self, error: Dict) -> int:
        """
        Fix: Remove colon from metadata field.

        ^type: value → ^type value
        ^identifier: Q001 → ^identifier Q001
        ^points: 1 → ^points 1
        """
        msg = error.get('message', '')

        # Determine which field
        if 'type' in msg.lower():
            pattern = r'(\^type):\s*'
        elif 'identifier' in msg.lower():
            pattern = r'(\^identifier):\s*'
        elif 'points' in msg.lower():
            pattern = r'(\^points):\s*'
        else:
            return 0

        # Replace in content
        new_content, count = re.subn(pattern, r'\1 ', self.content)

        if count > 0:
            self.content = new_content
            return count

        return 0

    def _fix_answer_to_correct_answers(self, error: Dict) -> int:
        """
        Fix: Rename @field: answer to @field: correct_answers for multiple_response.

        This fixes the case where M5 generated:
            @field: answer
            A, C, E
            @end_field

        But multiple_response requires:
            @field: correct_answers
            A, C, E
            @end_field

        The content stays the same - only the field name changes.

        Strategy:
        1. Find the question by ^identifier (full ID like COURSE_B_MR_Q002)
        2. Or by short ID (Q002) in header
        3. Within that question, find @field: answer
        4. Replace with @field: correct_answers
        """
        question_id = error.get('question_id', '')

        if not question_id:
            # Try to fix all multiple_response questions with @field: answer
            return self._fix_answer_to_correct_answers_global()

        # Extract short ID (e.g., "Q002" from "COURSE_B_MR_Q002")
        import re
        short_id_match = re.search(r'(Q\d+)', question_id)
        short_id = short_id_match.group(1) if short_id_match else question_id

        # Find the question section in content
        lines = self.content.split('\n')
        in_target_question = False
        question_start = -1
        question_end = -1
        changes = 0

        for i, line in enumerate(lines):
            # Check if this is the start of our target question
            # Match by: # Q002 ... OR ^identifier COURSE_B_MR_Q002
            if line.startswith('# ') and short_id in line:
                in_target_question = True
                question_start = i
                continue

            if line.strip().startswith('^identifier') and question_id in line:
                in_target_question = True
                if question_start < 0:
                    question_start = i
                continue

            # Check if we've reached the next question or end
            if in_target_question and line.startswith('# ') and short_id not in line:
                question_end = i
                break

            if in_target_question and line.strip() == '---':
                # Could be end of question
                if question_start >= 0:
                    question_end = i
                    break

        # If we found the question section, do targeted replacement
        if question_start >= 0:
            end_idx = question_end if question_end > 0 else len(lines)

            for i in range(question_start, end_idx):
                if lines[i].strip() == '@field: answer':
                    lines[i] = '@field: correct_answers'
                    changes += 1

            if changes > 0:
                self.content = '\n'.join(lines)

        # If targeted fix didn't work, try global
        if changes == 0:
            return self._fix_answer_to_correct_answers_global()

        return changes

    def _fix_answer_to_correct_answers_global(self) -> int:
        """
        Fallback: Fix @field: answer → @field: correct_answers globally
        for all multiple_response questions.

        Uses a more careful approach:
        1. Find each question with ^type multiple_response
        2. Within that question, replace @field: answer
        """
        lines = self.content.split('\n')
        changes = 0
        in_multiple_response = False

        for i, line in enumerate(lines):
            # Detect multiple_response question
            if line.strip().startswith('^type') and 'multiple_response' in line:
                in_multiple_response = True
                continue

            # Detect new question (reset)
            if line.startswith('# ') or line.strip() == '---':
                in_multiple_response = False
                continue

            # Fix within multiple_response question
            if in_multiple_response and lines[i].strip() == '@field: answer':
                lines[i] = lines[i].replace('@field: answer', '@field: correct_answers')
                changes += 1

        if changes > 0:
            self.content = '\n'.join(lines)

        return changes

    def _log_iteration_internal(
        self,
        round_num: int,
        error: Dict,
        rule: FixRule,
        result: FixResult
    ):
        """Log iteration internally (for return value)."""
        self.iteration_log.append({
            'timestamp': get_timestamp(),
            'round': round_num,
            'error': {
                'question_id': error.get('question_id', 'UNKNOWN'),
                'message': error.get('message', '')
            },
            'rule_id': rule.rule_id,
            'success': result.success,
            'lines_changed': result.lines_changed
        })

    def get_fixed_content(self) -> str:
        """Return the fixed content."""
        return self.content

    def get_iteration_log(self) -> List[Dict]:
        """Return the iteration log."""
        return self.iteration_log


# =============================================================================
# Public API
# =============================================================================

def autofix_file(
    input_path: Path,
    output_path: Optional[Path] = None,
    max_rounds: int = 10,
    project_path: Optional[Path] = None
) -> Step3Result:
    """
    Auto-fix a markdown file.

    Args:
        input_path: Path to input markdown file
        output_path: Path to save fixed file (default: overwrite input)
        max_rounds: Maximum fix iterations
        project_path: Project root for logging (optional)

    Returns:
        Step3Result with status and details
    """
    # Read input
    content = input_path.read_text(encoding='utf-8')

    # Determine project_path if not provided
    if not project_path:
        # Try to find project root (has session.yaml)
        for parent in input_path.parents:
            if (parent / "session.yaml").exists():
                project_path = parent
                break

    # Run auto-fix
    fixer = Step3AutoFix(
        content,
        max_rounds=max_rounds,
        project_path=project_path,
        file_path=str(input_path)
    )
    result = fixer.run()

    # Save if fixes were applied
    if result.fixes_applied:
        save_path = output_path or input_path
        save_path.write_text(fixer.get_fixed_content(), encoding='utf-8')
        result.message += f"\n📄 Saved to: {save_path}"

    return result


def autofix_content(
    content: str,
    max_rounds: int = 10,
    project_path: Optional[Path] = None
) -> Tuple[Step3Result, str]:
    """
    Auto-fix markdown content string.

    Args:
        content: Markdown content
        max_rounds: Maximum fix iterations
        project_path: Project root for logging (optional)

    Returns:
        (Step3Result, fixed_content)
    """
    fixer = Step3AutoFix(
        content,
        max_rounds=max_rounds,
        project_path=project_path,
        file_path="<content>"
    )
    result = fixer.run()
    return result, fixer.get_fixed_content()


# =============================================================================
# CLI
# =============================================================================

def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m qf_pipeline.tools.step3_autofix <input.md> [--project-path PATH] [--max-rounds N]")
        sys.exit(2)

    input_path = Path(sys.argv[1])

    # Parse arguments
    max_rounds = 10
    project_path = None

    if '--max-rounds' in sys.argv:
        idx = sys.argv.index('--max-rounds')
        if idx + 1 < len(sys.argv):
            max_rounds = int(sys.argv[idx + 1])

    if '--project-path' in sys.argv:
        idx = sys.argv.index('--project-path')
        if idx + 1 < len(sys.argv):
            project_path = Path(sys.argv[idx + 1])

    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(2)

    print(f"Step 3 Auto-Fix: {input_path}")
    print(f"Max rounds: {max_rounds}")
    if project_path:
        print(f"Project path: {project_path}")
    print("=" * 60)

    result = autofix_file(input_path, max_rounds=max_rounds, project_path=project_path)

    print(f"\nSession: {result.session_id}")
    print(f"Status: {result.status}")
    print(f"Rounds: {result.rounds}")
    print(f"Fixes applied: {len(result.fixes_applied)}")

    if result.fixes_applied:
        print("\nFixes:")
        for fix in result.fixes_applied:
            print(f"  - [{fix.rule_id}] {fix.fix_applied}")

    if result.remaining_errors:
        print(f"\nRemaining errors: {len(result.remaining_errors)}")
        for err in result.remaining_errors[:5]:  # Show first 5
            print(f"  - {err.get('message', 'Unknown')}")

    print(f"\n{result.message}")

    # Exit code
    if result.status == "valid":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
