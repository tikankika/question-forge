"""Wrapper for QTIPackager from QTI-Generator-for-Inspera.

Provides clean functions for creating IMS Content Packages (ZIP) with manifest.
"""

from pathlib import Path
from typing import List, Tuple

from .errors import PackagingError

# Import from QTI-Generator (path configured in __init__.py)
from src.packager.qti_packager import QTIPackager


def create_qti_package(
    questions_xml: List[Tuple[str, str]],
    metadata: dict,
    output_path: str,
    keep_folder: bool = True,
) -> dict:
    """Create QTI package from generated XML.

    Args:
        questions_xml: List of (identifier, xml_content) tuples.
        metadata: Package metadata dictionary.
        output_path: Path for output ZIP file.
        keep_folder: Whether to keep extracted folder. Defaults to True.

    Returns:
        Dictionary with:
        {
            'zip_path': str,      # Path to created ZIP
            'folder_path': str    # Path to extracted folder (if kept)
        }

    Raises:
        PackagingError: If package creation fails.
    """
    try:
        packager = QTIPackager()
        return packager.create_package(
            questions_xml=questions_xml,
            metadata=metadata,
            output_filename=output_path,
            keep_folder=keep_folder,
        )
    except Exception as e:
        raise PackagingError(f"Failed to create QTI package: {e}", source_error=e)


def validate_package(package_path: str) -> dict:
    """Validate existing QTI package.

    Args:
        package_path: Path to package directory or ZIP file.

    Returns:
        Dictionary with:
        {
            'valid': bool,
            'issues': list,
            'warnings': list
        }

    Raises:
        PackagingError: If validation fails.
    """
    try:
        packager = QTIPackager()
        return packager.validate_package(Path(package_path))
    except Exception as e:
        raise PackagingError(f"Failed to validate package: {e}", source_error=e)


def inspect_package(package_path: str) -> str:
    """Get tree view of package contents.

    Args:
        package_path: Path to package directory or ZIP file.

    Returns:
        Tree view string of package contents.

    Raises:
        PackagingError: If inspection fails.
    """
    try:
        packager = QTIPackager()
        return packager.get_package_tree(package_path)
    except Exception as e:
        raise PackagingError(f"Failed to inspect package: {e}", source_error=e)


def get_package_info(package_path: str) -> dict:
    """Get metadata and statistics about a package.

    Args:
        package_path: Path to package directory or ZIP file.

    Returns:
        Dictionary with package information.

    Raises:
        PackagingError: If inspection fails.
    """
    try:
        path = Path(package_path)

        # Count XML files
        if path.is_dir():
            xml_files = list(path.glob("**/*.xml"))
        else:
            # ZIP file - would need to extract first
            return {"path": str(path), "type": "zip", "note": "Extract to inspect"}

        return {
            "path": str(path),
            "type": "directory",
            "xml_count": len(xml_files),
            "has_manifest": (path / "imsmanifest.xml").exists(),
        }
    except Exception as e:
        raise PackagingError(f"Failed to get package info: {e}", source_error=e)
