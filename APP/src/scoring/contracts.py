"""Contrats de données pour le scoring CV / fiche de poste.

Principe directeur : le LLM ne calcule jamais le score final. Il statue
exigence par exigence, avec citation à l'appui ; le score est ensuite calculé
en Python, déterministe et auditable — jamais haluciné par le modèle.
"""

from typing import Literal

from pydantic import BaseModel, Field

from src.shared.contracts import JobSpec

__all__ = ["Statut", "POIDS_STATUT", "POIDS_CATEGORIE", "RequirementVerdict", "ScoreCard", "JobSpec"]

Statut = Literal["satisfait", "partiel", "absent"]
Categorie = Literal["must_have", "nice_to_have"]

# Poids utilisés par ScoreCard.calculer_score() — jamais choisis par le LLM.
POIDS_STATUT: dict[str, float] = {"satisfait": 1.0, "partiel": 0.5, "absent": 0.0}
POIDS_CATEGORIE: dict[str, float] = {"must_have": 3.0, "nice_to_have": 1.0}


class RequirementVerdict(BaseModel):
    """Verdict du LLM sur UNE exigence du poste, jamais un score global."""

    requirement_id: str
    requirement: str
    categorie: Categorie
    raisonnement: str = ""
    status: Statut
    evidence: str = ""
    evidence_verifiee: bool = False
    source_field: Literal[
        "experience", "formation", "competences", "certifications", "aucun"
    ] = "aucun"


class ScoreCard(BaseModel):
    """Évaluation complète d'un CV face à un poste, exigence par exigence."""

    candidat: str
    poste: str
    job: JobSpec
    verdicts: list[RequirementVerdict] = Field(default_factory=list)
    score_global: float = 0.0
    points_forts: list[str] = Field(default_factory=list)
    lacunes: list[str] = Field(default_factory=list)
    recommandation: str = ""
    provider: str = ""
    genere_le: str = ""
    version_contrat: str = "1.0"

    def calculer_score(self) -> float:
        """Score 0-100, pondéré must_have > nice_to_have. Calcul Python pur."""
        if not self.verdicts:
            return 0.0
        total_poids = sum(POIDS_CATEGORIE[v.categorie] for v in self.verdicts)
        if total_poids == 0:
            return 0.0
        somme = sum(
            POIDS_CATEGORIE[v.categorie] * POIDS_STATUT[v.status] for v in self.verdicts
        )
        return round(100 * somme / total_poids, 1)
