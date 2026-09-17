"""Contrats de données partagés par les phases préparation, entretien et évaluation."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from src.shared.contracts import JobSpec

__all__ = [
    "SECTIONS",
    "LIBELLES_SECTION",
    "QUOTA_PAR_SECTION",
    "RubricItem",
    "Question",
    "JobSpec",
    "InterviewBrief",
    "QuestionPlan",
]

Section = Literal["intro", "comportemental", "technique", "mise_en_situation", "cloture"]

SECTIONS: tuple[Section, ...] = (
    "intro",
    "comportemental",
    "technique",
    "mise_en_situation",
    "cloture",
)

LIBELLES_SECTION: dict[str, str] = {
    "intro": "Ouverture & parcours",
    "comportemental": "Comportemental (STAR)",
    "technique": "Technique",
    "mise_en_situation": "Mise en situation",
    "cloture": "Clôture & motivation",
}

QUOTA_PAR_SECTION: dict[str, int] = {
    "intro": 1,
    "comportemental": 3,
    "technique": 4,
    "mise_en_situation": 2,
    "cloture": 1,
}


class RubricItem(BaseModel):
    """Un critère observable du barème de notation d'une question."""

    criterion: str
    weight: float = Field(default=1.0, ge=0)
    description: str = ""


class Question(BaseModel):
    """Une question d'entretien, indissociable de son barème et de ses relances."""

    id: str = ""
    section: Section
    target_competency: str
    difficulty: int = Field(default=3, ge=1, le=5)
    question: str
    ancrage_cv: str = ""
    ancrage_verifie: bool = False
    rubric: list[RubricItem] = Field(min_length=2)
    followups: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _normalise_poids(self) -> "Question":
        # Exiger une somme de 1.0 dans le prompt échoue sur les modèles gratuits : on renormalise ici.
        total = sum(item.weight for item in self.rubric)
        poids_egal = round(1 / len(self.rubric), 4)
        for item in self.rubric:
            item.weight = round(item.weight / total, 4) if total > 0 else poids_egal
        return self


class InterviewBrief(BaseModel):
    """Ce que le planificateur doit savoir avant de rédiger les questions."""

    job: JobSpec
    probe_targets: list[str] = Field(default_factory=list)
    points_forts: list[str] = Field(default_factory=list)


class QuestionPlan(BaseModel):
    """Plan d'entretien complet, prêt à être déroulé sans nouvel appel LLM."""

    candidat: str
    poste: str
    brief: InterviewBrief
    questions: list[Question] = Field(default_factory=list)
    sections_echouees: list[str] = Field(default_factory=list)
    erreurs: dict[str, str] = Field(default_factory=dict)
    provider: str
    genere_le: str
    version_contrat: str = "1.0"

    def par_section(self, section: str) -> list[Question]:
        return [q for q in self.questions if q.section == section]
