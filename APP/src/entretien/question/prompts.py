"""Prompts de la phase de préparation des questions."""

import json

from src.entretien.contracts import InterviewBrief, LIBELLES_SECTION, QUOTA_PAR_SECTION
from src.shared.prompt_fragments import (
    AVERTISSEMENT_DONNEES_TIERCES as _AVERTISSEMENT,
    FORMAT_JSON_STRICT as _FORMAT,
    SYSTEM_REPARATION_JSON,
    user_reparation_json,
)
from src.shared.sanitize import encadrer

# ------------------------------------------------------------------
# Étape B — génération des questions d'une section
# ------------------------------------------------------------------

CONSIGNES_SECTION: dict[str, str] = {
    "intro": (
        "Question d'ouverture sur le parcours. Elle met le candidat à l'aise tout en "
        "vérifiant un fait précis et vérifiable de son CV."
    ),
    "comportemental": (
        "Situations réellement vécues, méthode STAR. Fais raconter un épisode concret "
        "du passé du candidat, jamais une opinion générale ni un cas hypothétique."
    ),
    "technique": (
        "Vérifie la maîtrise réelle des exigences indispensables du poste, en partant "
        "de ce que le candidat déclare avoir fait. Creuse le comment et le pourquoi."
    ),
    "mise_en_situation": (
        "Problème concret et réaliste du poste visé, que le candidat n'a pas encore "
        "rencontré. Évalue le raisonnement, pas une réponse mémorisée."
    ),
    "cloture": (
        "Projection dans le poste, motivation, disponibilité. Laisse la place aux "
        "questions du candidat."
    ),
}

_SQUELETTE_SECTION = """{
  "questions": [
    {
      "target_competency": "la compétence précise évaluée",
      "difficulty": 3,
      "question": "la question posée au candidat",
      "ancrage_cv": "le fait exact du CV qui justifie cette question",
      "ancrage_poste": "l'exigence ou l'extrait exact de la fiche de poste que cette question vérifie",
      "rubric": [
        {"criterion": "critère observable", "weight": 2, "description": "ce qui distingue une réponse qui satisfait ce critère"},
        {"criterion": "autre critère observable", "weight": 1, "description": "..."}
      ],
      "followups": ["relance à poser si la réponse reste en surface"],
      "reponse_ideale": "une réponse de référence complète, couvrant tous les critères du barème"
    }
  ]
}"""


def system_section(section: str) -> str:
    quota = QUOTA_PAR_SECTION.get(section, 2)
    return f"""Tu es un recruteur expérimenté qui prépare un entretien structuré.

Tu rédiges les questions de la section « {LIBELLES_SECTION.get(section, section)} ».
Consigne de section : {CONSIGNES_SECTION.get(section, "")}

RÈGLES ABSOLUES :
- Chaque question est ANCRÉE dans un fait précis du CV, cité tel quel dans "ancrage_cv".
  Une question qu'on pourrait poser à n'importe quel candidat est un échec.
- Chaque question est AUSSI ANCRÉE dans la fiche de poste : cite tel quel, dans "ancrage_poste",
  l'exigence ou l'extrait exact du poste que la question vérifie.
- Chaque question porte son barème "rubric" : 2 à 4 critères OBSERVABLES, vérifiables en
  lisant la réponse. Jamais de critère vague comme « bonne réponse » ou « bon niveau ».
- Chaque question porte 1 à 3 relances "followups" qui creusent si la réponse reste vague.
- Chaque question porte une "reponse_ideale" : une réponse de référence qui couvrirait tous
  les critères du barème. Elle servira à noter les vraies réponses plus tard — reste réaliste,
  pas une réponse parfaite artificielle.
- Tu n'attribues AUCUNE note et AUCUN score. Tu prépares les questions et leur grille.
- Tu écris en français.

{_AVERTISSEMENT}

{_FORMAT}
Produis exactement {quota} question(s). Structure exacte attendue :
""" + _SQUELETTE_SECTION


def user_section(cv_propre: dict, brief: InterviewBrief, jd_propre: str) -> str:
    return (
        "--- POSTE À POURVOIR ---\n"
        f"Intitulé : {brief.job.titre}\n"
        f"Exigences indispensables : {', '.join(brief.job.must_have) or 'non précisées'}\n"
        f"Compétences souhaitables : {', '.join(brief.job.nice_to_have) or 'aucune'}\n\n"
        "--- POINTS À SONDER EN PRIORITÉ ---\n"
        f"Écarts détectés au scoring : {', '.join(brief.probe_targets) or 'aucun'}\n"
        f"Points forts à confirmer : {', '.join(brief.points_forts) or 'aucun'}\n\n"
        "--- FICHE DE POSTE (texte original, pour citer \"ancrage_poste\" mot à mot) ---\n"
        + encadrer(jd_propre) + "\n\n"
        "--- CV DU CANDIDAT ---\n"
        + encadrer(json.dumps(cv_propre, ensure_ascii=False, indent=2))
    )


# ------------------------------------------------------------------
# Réparation d'une sortie invalide — voir src.shared.prompt_fragments
# ------------------------------------------------------------------

SYSTEM_REPARATION = SYSTEM_REPARATION_JSON
user_reparation = user_reparation_json
