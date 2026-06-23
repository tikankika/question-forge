"""Course-vault detection for the qf-pipeline (Python) side.

Mirrors the TypeScript ``detectCourseRoot`` (qf-scaffolding ``course_vault.ts``).
Per ADR_qf_ts_material_flow Decision 5 the cross-language contract is the RULE,
not shared code: *walk up to the nearest ``project_state.json``*. Two
implementations, one spec — kept in sync via the ADR, deliberately not a shared
package.

Used by the copy-shutdown: when a QF project is nested inside a teaching-suite
course vault, material is read in place (no copy), so the pipeline references
in-vault files instead of duplicating them.
"""

from pathlib import Path
from typing import Optional

#: The teaching-suite course-folder marker (present in older and newer vaults).
COURSE_MARKER = "project_state.json"


def detect_course_root(project_path: str, max_depth: int = 8) -> Optional[str]:
    """Return the nearest ancestor course root, or ``None`` for standalone QF.

    Walks up from ``project_path`` looking for ``project_state.json``. Bounded:
    never returns the home directory or above, stops at the filesystem root, and
    never walks more than ``max_depth`` levels up.
    """
    home = Path.home().resolve()
    current = Path(project_path).resolve()

    for _ in range(max_depth + 1):
        if current == home:
            break  # never treat home (or above) as a course root
        if (current / COURSE_MARKER).exists():
            return str(current)
        parent = current.parent
        if parent == current:
            break  # filesystem root
        current = parent

    return None


def course_relpath(path, course_root: str) -> Optional[str]:
    """POSIX path of ``path`` relative to ``course_root``, or ``None`` when
    ``path`` lies outside the course vault.

    The single in-vault test shared by the copy-shutdown call sites (the
    pipeline's ``step0_add_file`` and ``create_session``): an inside-vault file
    is referenced in place; an outside file is copied.
    """
    try:
        return Path(path).resolve().relative_to(Path(course_root).resolve()).as_posix()
    except ValueError:
        return None
