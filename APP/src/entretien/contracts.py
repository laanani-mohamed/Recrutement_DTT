"""Contrats de données partagés par les phases préparation, entretien et évaluation."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from src.shared.contracts import POIDS_STATUT, JobSpec, Statut

__all__ = [
    "SECTIONS",
    "LIBELLES_SECTION",
    "QUOTA_PAR_SECTION",
    "RubricItem",
    "Question",
    "JobSpec",
    "InterviewBrief",
    "QuestionPlan",
    "AnswerRecord",
    "InterviewSession",
    "CriterionVerdict",
    "EvaluatedAnswer",
    "InterviewEvaluation",
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
    ancrage_poste: str = ""
    ancrage_poste_verifie: bool = False
    rubric: list[RubricItem] = Field(min_length=2)
    followups: list[str] = Field(default_factory=list)
    reponse_ideale: str = ""
    # Réponse de référence générée en PREP, au même appel que le barème : sert
    # d'ancre au jugement en POST — la recherche montre qu'une référence réduit
    # nettement la variance d'un juge LLM par rapport à un jugement à l'aveugle.

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


class AnswerRecord(BaseModel):
    """Une réponse du candidat, horodatée — à une question principale ou à une relance."""

    question_id: str
    reponse: str
    est_relance: bool = False
    horodatage: str = ""            # ISO-8601 complet — reformulé à l'affichage seulement
    duree_reponse_s: float = 0.0    # secondes entre la pose de la question et la soumission


class InterviewSession(BaseModel):
    """État de la conduite d'un entretien : progression dans le plan + réponses collectées.

    Aucune intelligence ici — la boucle live ne fait qu'avancer ce curseur.
    Toute la réflexion (questions, barèmes, relances) a déjà eu lieu en phase PREP.
    """

    plan: QuestionPlan
    cursor: int = 0
    relance_utilisee: bool = False
    question_posee_le: str = ""     # horodatage de la question/relance en attente de réponse
    reponses: list[AnswerRecord] = Field(default_factory=list)
    statut: Literal["en_cours", "termine"] = "en_cours"
    demarre_le: str = ""
    termine_le: str = ""


class CriterionVerdict(BaseModel):
    """Verdict du LLM sur UN critère du barème d'une question, jamais un score."""

    critere_id: str
    criterion: str
    raisonnement: str = ""
    statut: Statut
    citation: str = ""
    citation_verifiee: bool = False


class EvaluatedAnswer(BaseModel):
    """Une question évaluée : ses verdicts par critère + le score qui en découle."""

    question_id: str
    criteres: list[CriterionVerdict] = Field(default_factory=list)
    score: float = 0.0

    def calculer_score(self, question: Question) -> float:
        """Score 0-100 : Σ(poids du critère × statut). Poids déjà normalisés à 1.0."""
        poids_par_critere = {item.criterion: item.weight for item in question.rubric}
        somme = sum(
            poids_par_critere.get(v.criterion, 0.0) * POIDS_STATUT[v.statut]
            for v in self.criteres
        )
        return round(100 * somme, 1)


class InterviewEvaluation(BaseModel):
    """Analyse complète d'un entretien mené : chaque réponse notée contre son barème."""

    candidat: str
    poste: str
    reponses_evaluees: list[EvaluatedAnswer] = Field(default_factory=list)
    questions_echouees: list[str] = Field(default_factory=list)
    erreurs: dict[str, str] = Field(default_factory=dict)
    score_global: float = 0.0
    points_forts: list[str] = Field(default_factory=list)
    lacunes: list[str] = Field(default_factory=list)
    recommandation: str = ""
    provider: str = ""
    genere_le: str = ""
    version_contrat: str = "1.0"
