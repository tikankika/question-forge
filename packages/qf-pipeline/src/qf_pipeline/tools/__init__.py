"""MCP tools for qf-pipeline."""

from .session import (
    start_session_tool,
    get_session_status_tool,
    end_session_tool,
    load_session_tool,
    get_current_session,
    set_current_session,
)

from .step0_tools import (
    step0_add_file,
    step0_analyze,
)

from .step1_tools import (
    step1_review,
    step1_manual_fix,
    step1_delete,
    step1_skip,
)

from .project_files import (
    read_project_file,
    write_project_file,
)

from .pipeline_router import (
    route_errors,
    RouteDecision,
    CategorizedError,
    ErrorCategory,
    format_route_decision,
)

__all__ = [
    # Session tools (Step 0)
    "start_session_tool",
    "get_session_status_tool",
    "end_session_tool",
    "load_session_tool",
    "get_current_session",
    "set_current_session",
    # Step 0 tools - ADR-015 Flexible Project Initialization
    "step0_add_file",
    "step0_analyze",
    # Step 1 tools (Vision A)
    "step1_review",
    "step1_manual_fix",
    "step1_delete",
    "step1_skip",
    # Project file tools
    "read_project_file",
    "write_project_file",
    # Pipeline router
    "route_errors",
    "RouteDecision",
    "CategorizedError",
    "ErrorCategory",
    "format_route_decision",
]
