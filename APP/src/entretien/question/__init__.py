"""Phase de préparation : génération du plan d'entretien à partir du CV et du poste."""

from src.entretien.question.main_question import PROVIDERS, generate_question_plan

__all__ = ["generate_question_plan", "PROVIDERS"]
