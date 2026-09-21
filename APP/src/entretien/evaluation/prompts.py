"""Prompts de l'évaluation des réponses d'entretien — un jugement par question,
critère par critère du barème déjà généré en PREP."""

from src.entretien.contracts import EvaluatedAnswer, Question
from src.shared.prompt_fragments import (
    AVERTISSEMENT_DONNEES_TIERCES,
    FORMAT_JSON_STRICT,
    SYSTEM_REPARATION_JSON,
    user_reparation_json,
)
from src.shared.sanitize import encadrer

SYSTEM_REPARATION = SYSTEM_REPARATION_JSON
user_reparation = user_reparation_json


def criteres_avec_id(question: Question) -> list[tuple[str, str, str]]:
    """(critere_id, criterion, description) — un id explicite évite au modèle de devoir
    reproduire le texte exact du critère pour qu'on sache auquel il répond."""
    return [
        (f"c{i}", item.criterion, item.description)
        for i, item in enumerate(question.rubric, start=1)
    ]


_SQUELETTE = """{
  "criteres": [
    {
      "critere_id": "l'identifiant fourni, recopié tel quel (ex: c1)",
      "raisonnement": "ton analyse de la réponse face à ce critère, AVANT de trancher",
      "statut": "satisfait | partiel | absent",
      "citation": "extrait EXACT de la réponse du candidat qui justifie le statut, ou vide"
    }
  ]
}"""


def system_evaluation_question() -> str:
    return f"""Tu es un recruteur expérimenté qui note la réponse d'un candidat à UNE question
d'entretien, CRITÈRE PAR CRITÈRE du barème — jamais une note globale.

RÈGLES ABSOLUES :
- Tu rends un verdict pour CHAQUE critère listé, en reprenant son "critere_id" exact.
- Avant de trancher, tu écris ton "raisonnement" — TOUJOURS avant "statut".
- "statut" : "satisfait" (le critère est clairement démontré dans la réponse), "partiel"
  (évoqué superficiellement, approximatif ou incomplet), "absent" (rien dans la réponse
  ne l'atteste).
- "citation" est un extrait EXACT de la réponse du candidat — jamais une paraphrase,
  jamais une invention. Chaîne vide si le critère est absent.
- Une "réponse de référence" t'est fournie : sers-t-en comme repère de ce qu'une réponse
  complète couvrirait, mais juge la réponse RÉELLE du candidat sur le fond, pas sa
  ressemblance littérale à la référence — plusieurs formulations valables existent.
- Tu n'attribues AUCUNE note, AUCUN pourcentage. Le score sera calculé ailleurs.
- Tu écris en français.

{AVERTISSEMENT_DONNEES_TIERCES}

{FORMAT_JSON_STRICT}
Structure exacte attendue :
""" + _SQUELETTE


def user_evaluation_question(
    question: Question, reponse_candidat: str, criteres: list[tuple[str, str, str]]
) -> str:
    lignes_criteres = "\n".join(f"{cid} : {crit} — {desc}" for cid, crit, desc in criteres)
    return (
        f"--- QUESTION POSÉE ---\n{question.question}\n\n"
        "--- RÉPONSE DE RÉFÉRENCE (repère, pas à reproduire mot pour mot) ---\n"
        f"{question.reponse_ideale or 'non disponible'}\n\n"
        "--- CRITÈRES À ÉVALUER ---\n"
        f"{lignes_criteres}\n\n"
        "--- RÉPONSE DU CANDIDAT ---\n"
        + encadrer(reponse_candidat)
    )


# ------------------------------------------------------------------
# Synthèse finale — après que toutes les questions ont été notées
# ------------------------------------------------------------------

_SQUELETTE_SYNTHESE = """{
  "recommandation": "synthèse brève en 2-3 phrases, jamais une décision d'embauche"
}"""

SYSTEM_SYNTHESE = f"""Tu résumes une évaluation d'entretien déjà notée, question par question,
critère par critère. Tu ne recalcules AUCUN score — il est déjà calculé.

RÈGLE ABSOLUE : ta synthèse est une aide à la décision, JAMAIS une décision d'embaucher
ou de rejeter — cette décision revient uniquement au recruteur humain.

{FORMAT_JSON_STRICT}
Structure exacte attendue :
""" + _SQUELETTE_SYNTHESE


def user_synthese(candidat: str, poste: str, resultats: list[tuple[Question, EvaluatedAnswer]]) -> str:
    lignes = []
    for question, evaluee in resultats:
        statuts = ", ".join(f"{c.criterion}={c.statut}" for c in evaluee.criteres)
        lignes.append(f"- {question.target_competency} (score {evaluee.score}%) : {statuts}")
    return (
        f"--- CANDIDAT : {candidat} · POSTE : {poste} ---\n\n"
        "--- RÉSULTATS PAR QUESTION ---\n" + "\n".join(lignes)
    )
