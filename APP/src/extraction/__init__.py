# src/extraction/__init__.py
# Rend le dossier extraction importable comme package Python
from src.extraction.main_extraction import extract_text, METHODS

__all__ = ["extract_text", "METHODS"]
