"""Archived wrappers - RFC-012.

These wrappers are DEPRECATED and kept only for backwards compatibility.
New code should use subprocess to call qti-core scripts directly.

Archived 2026-01-24:
- validator.py - replaced by subprocess → step1_validate.py
- generator.py - replaced by subprocess → step4_generate_xml.py
- packager.py - replaced by subprocess → step5_create_zip.py
- resources.py - replaced by subprocess → step3_copy_resources.py
"""
