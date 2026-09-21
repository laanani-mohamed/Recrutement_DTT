"""Contrats de données partagés par les modules entretien et scoring."""

from typing import Literal

from pydantic import BaseModel, Field


class JobSpec(BaseModel):
    """Fiche de poste structurée en exigences."""

    titre: str = "Poste"
    must_have: list[str] = Field(default_factory=list)
    nice_to_have: list[str] = Field(default_factory=list)


# Vocabulaire de statut partagé par le scoring (RequirementVerdict) et l'évaluation
# d'entretien (CriterionVerdict) : un LLM statue, jamais une note — le score est
# toujours calculé en Python à partir de ces poids, jamais halluciné par le modèle.
Statut = Literal["satisfait", "partiel", "absent"]
POIDS_STATUT: dict[str, float] = {"satisfait": 1.0, "partiel": 0.5, "absent": 0.0}
