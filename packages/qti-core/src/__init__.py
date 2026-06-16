"""
QTI Generator for Inspera

Convert markdown quiz files to QTI 2.2 packages for Inspera Assessment Platform.
"""

__version__ = "0.2.4"
__author__ = "Niklas Karlsson"

# Make subpackages easily importable
from src.parser import MarkdownQuizParser
from src.generator import XMLGenerator
from src.packager import QTIPackager

__all__ = [
    'MarkdownQuizParser',
    'XMLGenerator',
    'QTIPackager',
]
