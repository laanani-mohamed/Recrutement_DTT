# src/convert_json/__init__.py
# Package de conversion des CVs en JSON via LLM
# Contient les providers : Groq, Gemini, OpenRouter
from src.convert_json.main_convert_json import convert_cv, classify_cv, PROVIDERS

__all__ = ["convert_cv", "classify_cv", "PROVIDERS"]
