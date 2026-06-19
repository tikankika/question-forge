"""Session management for qf-pipeline.

Handles project structure creation, session state via session.yaml,
and workflow tracking.
"""

import logging
import shutil
import uuid
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .methodology import ensure_central_methodology
from .sources import create_empty_sources_yaml, update_sources_yaml
from .logger import log_event
from .timestamp import get_timestamp

logger = logging.getLogger(__name__)


# Entry point configuration for shared session
# Named after the module they start with (M1-M4) or "pipeline" for direct export
# ADR-015: Added "setup" for flexible project initialization
ENTRY_POINT_REQUIREMENTS = {
    "setup": {
        "requires_source_file": False,
        "requires_materials_folder": False,
        "next_module": None,  # Determined by step0_analyze
        "description": "Create empty project, add files later",
        "next_steps": ["step0_add_file", "step0_analyze"],
        "skips": []
    },
    "m1": {
        "requires_source_file": False,
        "requires_materials_folder": True,
        "next_module": "m1",
        "description": "Start from teaching materials → Content Analysis",
        "next_steps": ["M1", "M2", "M3", "M4", "Pipeline"],
        "skips": []
    },
    "m2": {
        "requires_source_file": True,
        "requires_materials_folder": False,
        "next_module": "m2",
        "description": "Start from learning objectives → Assessment Planning",
        "next_steps": ["M2", "M3", "M4", "Pipeline"],
        "skips": ["M1"]
    },
    "m3": {
        "requires_source_file": True,
        "requires_materials_folder": False,
        "next_module": "m3",
        "description": "Start from blueprint → Question Generation",
        "next_steps": ["M3", "M4", "Pipeline"],
        "skips": ["M1", "M2"]
    },
    "m4": {
        "requires_source_file": True,
        "requires_materials_folder": False,
        "next_module": "m4",
        "description": "Start from questions for QA → Quality Assurance",
        "next_steps": ["M4", "Pipeline"],
        "skips": ["M1", "M2", "M3"]
    },
    "pipeline": {
        "requires_source_file": True,
        "requires_materials_folder": False,
        "next_module": None,  # → Pipeline directly
        "description": "Validate and export finished questions directly",
        "next_steps": ["Step1", "Step2", "Step3", "Step4"],
        "skips": ["M1", "M2", "M3", "M4"]
    }
}


def validate_entry_point(
    entry_point: str,
    source_file: Optional[str],
    materials_folder: Optional[str] = None
) -> None:
    """Validate entry point and source_file/materials_folder combination.

    Args:
        entry_point: One of "setup", "m1", "m2", "m3", "m4", "pipeline"
        source_file: Path to source file (required for m2/m3/m4/pipeline)
        materials_folder: Path to materials folder (required for m1)

    Raises:
        ValueError: If entry_point is invalid or requirements not met
    """
    if entry_point not in ENTRY_POINT_REQUIREMENTS:
        valid_options = list(ENTRY_POINT_REQUIREMENTS.keys())
        raise ValueError(
            f"Invalid entry point: '{entry_point}'. "
            f"Valid options: {valid_options}"
        )

    config = ENTRY_POINT_REQUIREMENTS[entry_point]

    # ADR-015: "setup" entry point requires nothing, but accepts files
    if entry_point == "setup":
        if source_file:
            logger.info(f"ADR-015: source_file provided with setup - will copy to questions/")
        if materials_folder:
            logger.info(f"ADR-015: materials_folder provided with setup - will copy to materials/")
        return  # No requirements for setup, but files are welcomed

    # m1 requires materials_folder
    if entry_point == "m1":
        if not materials_folder:
            raise ValueError(
                f"Entry point 'm1' requires materials_folder.\n"
                f"Description: {config['description']}\n"
                f"Expected workflow: {' → '.join(config['next_steps'])}\n"
                f"Tip: Use entry_point='setup' to create project first, then add files."
            )
        if source_file:
            # source_file for m1 is treated as a reference document (e.g., syllabus)
            # It will be saved to project root, not questions/
            logger.info(
                f"source_file provided for 'm1' entry point - "
                f"will be saved as reference document in project root."
            )
    # Other entry points require source_file
    elif config["requires_source_file"] and not source_file:
        raise ValueError(
            f"Entry point '{entry_point}' requires source_file.\n"
            f"Description: {config['description']}\n"
            f"Expected workflow: {' → '.join(config['next_steps'])}\n"
            f"Tip: Use entry_point='setup' to create project first, then add files."
        )

    # Warn if materials_folder provided for non-m1
    if materials_folder and entry_point != "m1":
        logger.warning(
            f"materials_folder provided for '{entry_point}' entry point - "
            f"will be ignored. This parameter is only used for 'm1'."
        )


class SessionManager:
    """Manages QF pipeline sessions with project structure and state.

    Project structure (RFC-013 v2.1):
        project_name/
        ├── materials/          ← Input (lectures, slides) - M1 reads
        ├── methodology/        ← Method guides (copied in Step 0)
        ├── preparation/        ← M1 + M2 output (foundation for questions)
        ├── questions/          ← Questions (M3 creates, M4/M5 edit)
        │   └── history/        ← Automatic backups per step
        ├── pipeline/           ← Step 1-3 working area
        │   └── history/        ← Backups
        ├── output/             ← Step 4 final output
        │   └── qti/            ← QTI packages (.zip)
        ├── logs/               ← Session logs
        └── session.yaml        ← Metadata and state
    """

    FOLDERS = [
        "materials",           # Input (lectures, slides) - M1 reads
        "methodology",         # Method guides (copied in Step 0)
        "preparation",         # M1 + M2 output (foundation for questions)
        "questions",           # Questions (M3 creates, M4/M5 edit)
        "questions/history",   # Automatic backups per step
        "pipeline",            # Step 1-3 working area
        "pipeline/history",    # Backups
        "output",              # Final output
        "output/qti",          # QTI packages
        "logs",                # Session logs (shared by both MCPs)
    ]
    SESSION_FILE = "session.yaml"

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize session manager.

        Args:
            project_path: Path to existing project (for loading session)
        """
        self._project_path: Optional[Path] = project_path
        self._session_data: Optional[dict] = None

        if project_path:
            self._load_session()

    @property
    def project_path(self) -> Optional[Path]:
        """Get current project path."""
        return self._project_path

    @property
    def session_id(self) -> Optional[str]:
        """Get current session ID."""
        if self._session_data:
            return self._session_data.get("session", {}).get("id")
        return None

    @property
    def questions_file(self) -> Optional[Path]:
        """Get path to questions file."""
        if self._project_path and self._session_data:
            questions_path = self._session_data.get("questions", {}).get("path")
            if questions_path:
                return self._project_path / questions_path
        return None

    @property
    def working_file(self) -> Optional[Path]:
        """Get path to working file (alias for questions_file for backward compat)."""
        return self.questions_file

    @property
    def source_file(self) -> Optional[Path]:
        """Get path to source file copy."""
        if self._project_path and self._session_data:
            copied_to = self._session_data.get("source", {}).get("copied_to")
            if copied_to:
                return self._project_path / copied_to
        return None

    @property
    def output_folder(self) -> Optional[Path]:
        """Get path to output folder."""
        if self._project_path:
            return self._project_path / "output"
        return None

    @property
    def questions_folder(self) -> Optional[Path]:
        """Get path to questions folder."""
        if self._project_path:
            return self._project_path / "questions"
        return None

    @property
    def pipeline_folder(self) -> Optional[Path]:
        """Get path to pipeline working folder."""
        if self._project_path:
            return self._project_path / "pipeline"
        return None

    def create_session(
        self,
        output_folder: str,
        source_file: Optional[str] = None,
        project_name: Optional[str] = None,
        entry_point: str = "pipeline",
        materials_folder: Optional[str] = None,
        initial_sources: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create a new session with project structure.

        Args:
            output_folder: Directory where project will be created
            source_file: Path to source file (required for m2/m3/m4/pipeline)
            project_name: Optional project name (auto-generated if not provided)
            entry_point: One of "m1", "m2", "m3", "m4", "pipeline"
            materials_folder: Path to folder with instructional materials (required for m1)
            initial_sources: Optional list of initial sources for sources.yaml
                Each source should have: path, type (optional), location (optional)

        Returns:
            dict with success status, paths, and next_module
        """
        output_base = Path(output_folder).resolve()

        # Validate entry point and source_file/materials_folder combination
        try:
            validate_entry_point(entry_point, source_file, materials_folder)
        except ValueError as e:
            return {
                "success": False,
                "error": {
                    "type": "validation_error",
                    "message": str(e)
                }
            }

        # Get entry point config
        ep_config = ENTRY_POINT_REQUIREMENTS[entry_point]

        # Handle source file if provided
        source_path = None
        if source_file:
            source_path = Path(source_file).resolve()

            # Validate source file exists
            if not source_path.exists():
                return {
                    "success": False,
                    "error": {
                        "type": "file_not_found",
                        "message": f"Source file not found: {source_file}"
                    }
                }

            if not source_path.is_file():
                return {
                    "success": False,
                    "error": {
                        "type": "invalid_path",
                        "message": f"Source path is not a file: {source_file}"
                    }
                }

        # Generate project name if not provided
        if not project_name:
            if source_path:
                project_name = source_path.stem  # filename without extension
            else:
                # For materials entry point, generate timestamp-based name
                project_name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create project directory
        # Avoid duplicate folders if output_folder already ends with project_name
        if output_base.name == project_name:
            project_path = output_base
        else:
            project_path = output_base / project_name

        try:
            # Create output base if needed
            output_base.mkdir(parents=True, exist_ok=True)

            # Create project structure
            project_path.mkdir(parents=True, exist_ok=True)
            for folder in self.FOLDERS:
                folder_path = project_path / folder
                folder_path.mkdir(exist_ok=True)

                # Add README for materials folder ONLY if no materials_folder provided
                # (otherwise user's own README might be in materials_folder)
                if folder == "materials" and not materials_folder:
                    readme_path = folder_path / "README.md"
                    readme_path.write_text(
                        "# Teaching Materials\n\n"
                        "Upload all materials from your teaching here:\n"
                        "- Presentations (PDF, PPTX)\n"
                        "- Lecture notes\n"
                        "- Transcripts from recordings\n"
                        "- Textbooks/articles used\n",
                        encoding="utf-8"
                    )

            # Copy materials if provided (for m1 entry point)
            materials_copied = 0
            if materials_folder:
                materials_src = Path(materials_folder)
                materials_dest = project_path / "materials"

                logger.info(f"Copying materials from {materials_src} to {materials_dest}")

                # Define junk files to ignore
                def ignore_junk(directory, files):
                    """Ignore junk files and hidden files."""
                    ignored = []
                    for f in files:
                        # Ignore hidden files (except .md files which might be intentional)
                        if f.startswith('.') and not f.endswith('.md'):
                            ignored.append(f)
                        # Ignore OS junk
                        elif f in ('Thumbs.db', 'desktop.ini', 'ehthumbs.db'):
                            ignored.append(f)
                        # Ignore Office temp files
                        elif f.startswith('~$'):
                            ignored.append(f)
                        # Ignore Python cache
                        elif f == '__pycache__' or f.endswith('.pyc'):
                            ignored.append(f)
                    return ignored

                # Copy entire tree (including subdirectories)
                shutil.copytree(
                    materials_src,
                    materials_dest,
                    dirs_exist_ok=True,  # Merge with existing (materials/ already exists)
                    ignore=ignore_junk
                )

                # Walk the copied tree once: count now, reuse the list below
                material_files = [p for p in materials_dest.rglob('*') if p.is_file()]
                materials_copied += len(material_files)

                logger.info(f"Copied {materials_copied} files to materials/")

            # ADR-016: ensure the central methodology snapshot exists at
            # <QF_WORKSPACE>/methodology/ (shared across all course projects).
            methodology_result = ensure_central_methodology()
            logger.info(
                f"Central methodology: {methodology_result['action']} "
                f"({methodology_result.get('message', '')})"
            )

            # Initialize sources.yaml
            if initial_sources:
                sources_result = update_sources_yaml(
                    project_path,
                    initial_sources,
                    updated_by="qf-pipeline:step0_start",
                    append=False
                )
                logger.info(f"Initialized sources.yaml with {sources_result.get('sources_added', 0)} sources")
            else:
                create_empty_sources_yaml(project_path, created_by="qf-pipeline:step0_start")
                logger.info("Created empty sources.yaml")

            # Register copied materials in sources.yaml
            if materials_copied > 0:
                materials_sources = []
                for item in material_files:
                    ext = item.suffix.lower()
                    file_type = {
                        '.pdf': 'lecture_slides',
                        '.pptx': 'lecture_slides',
                        '.ppt': 'lecture_slides',
                        '.docx': 'document',
                        '.doc': 'document',
                        '.txt': 'text',
                        '.md': 'markdown',
                        '.mp4': 'video',
                        '.mp3': 'audio',
                        '.wav': 'audio',
                    }.get(ext, 'unknown')

                    materials_sources.append({
                        "path": f"materials/{item.relative_to(materials_dest)}",
                        "type": file_type,
                        "location": "local",
                        "metadata": {
                            "original_path": str(materials_src / item.relative_to(materials_dest)),
                            "copied_at": get_timestamp(),
                        }
                    })

                if materials_sources:
                    result = update_sources_yaml(
                        project_path,
                        materials_sources,
                        updated_by="qf-pipeline:step0_start",
                        append=True
                    )
                    logger.info(f"Registered {result.get('sources_added', 0)} materials in sources.yaml")

            # Copy source file if provided
            questions_dest = None
            reference_doc = None
            if source_path:
                if entry_point == "m1":
                    # For m1: save source_file as reference document in project root
                    # (e.g., syllabus/kursplan)
                    reference_doc = project_path / source_path.name
                    shutil.copy2(source_path, reference_doc)
                    logger.info(f"Saved reference document: {reference_doc}")
                    # Register reference doc in sources.yaml
                    update_sources_yaml(
                        project_path,
                        [{
                            "path": source_path.name,
                            "type": "syllabus",
                            "location": "fetched" if "fetched" in str(source_path) else "local",
                            "metadata": {
                                "original_path": str(source_path),
                                "copied_at": get_timestamp(),
                            }
                        }],
                        updated_by="qf-pipeline:step0_start",
                        append=True
                    )
                    logger.info(f"Registered reference document in sources.yaml")
                else:
                    # For m2/m3/m4/pipeline: copy to questions/
                    # Use original filename or 'questions.md' as default
                    questions_dest = project_path / "questions" / source_path.name
                    shutil.copy2(source_path, questions_dest)
                    logger.info(f"Copied questions to: {questions_dest}")

                    # Register questions file in sources.yaml
                    update_sources_yaml(
                        project_path,
                        [{
                            "path": f"questions/{source_path.name}",
                            "type": "questions",
                            "location": "local",
                            "metadata": {
                                "original_path": str(source_path),
                                "copied_at": get_timestamp(),
                            }
                        }],
                        updated_by="qf-pipeline:step0_start",
                        append=True
                    )
                    logger.info(f"Registered questions file in sources.yaml")

            # Generate session ID
            session_id = str(uuid.uuid4())

            # Create session data with methodology section
            # For m1, source is a reference document; for others, it's the questions file
            if entry_point == "m1" and reference_doc:
                source_data = {
                    "original_path": str(source_path) if source_path else None,
                    "filename": source_path.name if source_path else None,
                    "copied_to": None,  # Not in questions/ for m1
                    "reference_doc": source_path.name if reference_doc else None,
                }
                questions_data = {
                    "path": None,  # M3 will create this
                    "last_validated": None,
                    "validation_status": "not_validated",
                    "question_count": None,
                }
            else:
                source_data = {
                    "original_path": str(source_path) if source_path else None,
                    "filename": source_path.name if source_path else None,
                    "copied_to": f"questions/{source_path.name}" if questions_dest else None,
                }
                questions_data = {
                    "path": f"questions/{source_path.name}" if questions_dest else None,
                    "last_validated": None,
                    "validation_status": "not_validated",
                    "question_count": None,
                }

            self._session_data = {
                "session": {
                    "id": session_id,
                    "created": get_timestamp(),
                    "updated": get_timestamp(),
                },
                "source": source_data,
                "questions": questions_data,  # Renamed from "working"
                "exports": [],
                # Methodology section for shared session
                "methodology": {
                    "entry_point": entry_point,
                    "active_module": ep_config["next_module"],
                    "m1": {"status": "not_started", "loaded_stages": [], "outputs": {}},
                    "m2": {"status": "not_started", "loaded_stages": [], "outputs": {}},
                    "m3": {"status": "not_started", "loaded_stages": [], "outputs": {}},
                    "m4": {"status": "not_started", "loaded_stages": [], "outputs": {}},
                }
            }

            self._project_path = project_path
            self._save_session()

            # Log session creation (RFC-001 compliant)
            log_event(
                project_path=project_path,
                session_id=session_id,
                tool="step0_start",
                event="session_start",
                level="info",
                data={"entry_point": entry_point}
            )
            log_event(
                project_path=project_path,
                session_id=session_id,
                tool="step0_start",
                event="session_created",
                level="info",
                data={
                    "methodology_files": methodology_result.get("files_copied", 0),
                    "sources_count": len(initial_sources) if initial_sources else 0,
                    "materials_copied": materials_copied
                }
            )

            # Build response
            response = {
                "success": True,
                "session_id": session_id,
                "project_path": str(project_path),
                "output_folder": str(project_path / "output"),
                "questions_folder": str(project_path / "questions"),
                "pipeline_folder": str(project_path / "pipeline"),
                "entry_point": entry_point,
                "next_module": ep_config["next_module"],
                "pipeline_ready": entry_point == "pipeline",
                "methodology_copied": methodology_result.get("files_copied", 0),
                "sources_initialized": len(initial_sources) if initial_sources else 0,
                "materials_copied": materials_copied,
            }

            # Add file paths if source was provided
            if entry_point == "m1" and materials_folder:
                # m1 entry point with materials
                response["questions_file"] = None
                response["materials_folder"] = str(project_path / "materials")

                if reference_doc:
                    # Reference document (e.g., syllabus) was also provided
                    response["reference_doc"] = str(reference_doc)
                    response["message"] = (
                        f"Session started with entry point '{entry_point}'. "
                        f"{materials_copied} files copied to materials/. "
                        f"Reference document saved: {source_path.name}. "
                        f"Next step: {ep_config['next_module']} (qf-scaffolding)"
                    )
                else:
                    response["message"] = (
                        f"Session started with entry point '{entry_point}'. "
                        f"{materials_copied} files copied to materials/ (folder structure preserved). "
                        f"Next step: {ep_config['next_module']} (qf-scaffolding)"
                    )
            elif source_path and questions_dest:
                # m2/m3/m4/pipeline with source file
                response["questions_file"] = str(questions_dest)
                response["message"] = f"Session started. Working with: {source_path.name}"
            else:
                response["questions_file"] = None
                response["message"] = (
                    f"Session started with entry point '{entry_point}'. "
                    f"Next step: {ep_config['next_module']} (qf-scaffolding)"
                )

            return response

        except PermissionError as e:
            return {
                "success": False,
                "error": {
                    "type": "permission_error",
                    "message": f"Cannot write to directory: {e}"
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "type": type(e).__name__,
                    "message": str(e)
                }
            }

    def get_status(self) -> dict:
        """Get current session status.

        Returns:
            dict with session status and paths
        """
        if not self._session_data or not self._project_path:
            return {
                "active": False,
                "message": "No active session"
            }

        questions_data = self._session_data.get("questions", {})
        exports = self._session_data.get("exports", [])

        return {
            "active": True,
            "session_id": self.session_id,
            "project_path": str(self._project_path),
            "questions_file": str(self.questions_file) if self.questions_file else None,
            "questions_folder": str(self.questions_folder) if self.questions_folder else None,
            "pipeline_folder": str(self.pipeline_folder) if self.pipeline_folder else None,
            "output_folder": str(self.output_folder) if self.output_folder else None,
            "validation_status": questions_data.get("validation_status", "not_validated"),
            "question_count": questions_data.get("question_count"),
            "last_validated": questions_data.get("last_validated"),
            "last_export": exports[-1].get("output_file") if exports else None,
            "export_count": len(exports)
        }

    def update_validation(self, is_valid: bool, question_count: int) -> None:
        """Update validation status in session.

        Args:
            is_valid: Whether validation passed
            question_count: Number of questions found
        """
        if self._session_data:
            self._session_data["questions"]["last_validated"] = get_timestamp()
            self._session_data["questions"]["validation_status"] = "valid" if is_valid else "invalid"
            self._session_data["questions"]["question_count"] = question_count
            self._session_data["session"]["updated"] = get_timestamp()
            self._save_session()

    def log_export(self, output_file: str, questions_exported: int) -> None:
        """Log an export to session.

        Args:
            output_file: Path to exported file (relative to project)
            questions_exported: Number of questions exported
        """
        if self._session_data:
            self._session_data["exports"].append({
                "timestamp": get_timestamp(),
                "output_file": output_file,
                "questions_exported": questions_exported
            })
            self._session_data["session"]["updated"] = get_timestamp()
            self._save_session()

    def end_session(self) -> dict:
        """End current session.

        Returns:
            dict with session summary
        """
        if not self._session_data or not self._project_path:
            return {
                "success": False,
                "error": {
                    "type": "no_session",
                    "message": "No active session to end"
                }
            }

        exports = self._session_data.get("exports", [])
        session_id = self.session_id
        project_path = self._project_path
        validation_status = self._session_data.get("questions", {}).get("validation_status", "unknown")
        question_count = self._session_data.get("questions", {}).get("question_count", 0)

        # Log session_end (TIER 2)
        log_event(
            project_path=project_path,
            session_id=session_id,
            tool="session_manager",
            event="session_end",
            level="info",
            data={
                "export_count": len(exports),
                "validation_status": validation_status,
                "question_count": question_count,
            }
        )

        # Clear session state
        project_path_str = str(project_path)
        self._session_data = None
        self._project_path = None

        return {
            "success": True,
            "exports_created": [e.get("output_file") for e in exports],
            "project_path": project_path_str,
            "message": f"Session ended. {len(exports)} export(s) created."
        }

    def _load_session(self) -> None:
        """Load session data from session.yaml."""
        if not self._project_path:
            return

        session_file = self._project_path / self.SESSION_FILE
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                self._session_data = yaml.safe_load(f)

    def _save_session(self) -> None:
        """Save session data to session.yaml."""
        if not self._project_path or not self._session_data:
            return

        session_file = self._project_path / self.SESSION_FILE
        with open(session_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(
                self._session_data,
                f,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False
            )

    @classmethod
    def load_from_path(cls, project_path: str) -> "SessionManager":
        """Load session from existing project path.

        Args:
            project_path: Path to project directory

        Returns:
            SessionManager instance with loaded session
        """
        path = Path(project_path).resolve()
        if not (path / cls.SESSION_FILE).exists():
            raise FileNotFoundError(f"No session found at {project_path}")
        return cls(path)
