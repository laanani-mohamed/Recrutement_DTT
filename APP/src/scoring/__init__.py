# src/scoring/__init__.py
# Package de scoring de CV vs Job Description via LLM
from src.scoring.main_scoring import score_cv, PROVIDERS

__all__ = ["score_cv", "PROVIDERS"]
