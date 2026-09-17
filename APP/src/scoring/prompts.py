"""Prompts du scoring CV / fiche de poste — un verdict par exigence."""

import json

from src.shared.contracts import JobSpec
from src.shared.prompt_fragments import (
    AVERTISSEMENT_DONNEES_TIERCES,
    FORMAT_JSON_STRICT,
    SYSTEM_REPARATION_JSON,
    user_reparation_json,
)
from src.shared.sanitize import encadrer

SYSTEM_REPARATION = SYSTEM_REPARATION_JSON
user_reparation = user_reparation_json

_SQUELETTE = """{
  "verdicts": [
    {
      "requirement_id": "l'identifiant fourni, recopié tel quel (ex: req_1)",
      "raisonnement": "ton analyse du CV face à cette exigence, AVANT de trancher",
      "status": "satisfait | partiel | absent",
      "evidence": "citation EXACTE du CV justifiant le statut, ou vide si absent",
      "source_field": "experience | formation | competences | certifications | aucun"
    }
  ],
  "recommandation": "synthèse brève en 2-3 phrases, jamais une décision d'embauche"
}"""


def system_verdict() -> str:
    return f"""Tu es un recruteur expérimenté et rigoureux. Tu évalues un CV face à une fiche
de poste, EXIGENCE PAR EXIGENCE — jamais par un score global.

RÈGLES ABSOLUES :
- Tu rends un verdict pour CHAQUE exigence listée, dans l'ordre, en reprenant son
  "requirement_id" exact.
- Avant de trancher, tu écris ton "raisonnement" — TOUJOURS avant "status" dans ta réponse.
  Tu analyses d'abord, tu conclus ensuite.
- "evidence" est TOUJOURS une CITATION EXACTE tirée du CV — jamais du champ "resume", qui
  est déjà une reformulation. Elle peut venir de "description" (narration d'une expérience
  réelle), de "competences", "formation" ou "certifications" (mentions déclaratives).
  N'invente jamais une citation. Si rien dans le CV ne mentionne l'exigence, "evidence"
  est une chaîne vide.
- "status" dépend de la NATURE de la preuve, pas seulement de sa présence :
  - "satisfait" : l'exigence est démontrée par une narration concrète dans "description"
    (le candidat a réellement utilisé cette compétence dans un contexte décrit).
  - "partiel" : l'exigence n'apparaît QUE dans une liste déclarative ("competences",
    "formation", "certifications"), sans narration prouvant un usage réel — une
    compétence listée sans contexte n'est pas la preuve d'une expérience appliquée.
  - "absent" : rien dans le CV ne mentionne l'exigence.
- Tu n'attribues AUCUN score, AUCUN pourcentage, AUCUNE note globale. Seul le statut par
  exigence compte — le score sera calculé ailleurs.
- "recommandation" est une synthèse brève, jamais une décision d'embaucher ou de rejeter :
  la décision revient au recruteur humain.
- Tu écris en français.

{AVERTISSEMENT_DONNEES_TIERCES}

{FORMAT_JSON_STRICT}
Structure exacte attendue :
""" + _SQUELETTE


def user_verdict(cv_propre: dict, job: JobSpec, exigences: list[tuple[str, str, str]]) -> str:
    """exigences : liste de (requirement_id, texte, categorie)."""
    lignes = [f"{rid} [{cat}] : {texte}" for rid, texte, cat in exigences]
    return (
        f"--- POSTE : {job.titre} ---\n\n"
        "--- EXIGENCES À ÉVALUER (une par une) ---\n"
        + "\n".join(lignes)
        + "\n\n--- CV DU CANDIDAT ---\n"
        + encadrer(json.dumps(cv_propre, ensure_ascii=False, indent=2))
    )
