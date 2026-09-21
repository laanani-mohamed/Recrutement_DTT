"""Phase live : conduite de l'entretien. Déroule le QuestionPlan, ne réfléchit jamais."""

from src.entretien.live.moteur import (
    demarrer,
    formater_duree,
    formater_horodatage,
    question_courante,
    reponse_semble_superficielle,
    soumettre_reponse,
    texte_a_poser,
)

__all__ = [
    "demarrer",
    "formater_duree",
    "formater_horodatage",
    "question_courante",
    "reponse_semble_superficielle",
    "soumettre_reponse",
    "texte_a_poser",
]
