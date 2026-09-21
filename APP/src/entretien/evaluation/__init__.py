"""Phase POST : évaluation des réponses d'un entretien mené, contre leur barème."""

from src.entretien.evaluation.main_evaluation import PROVIDERS, evaluate_interview

__all__ = ["evaluate_interview", "PROVIDERS"]
