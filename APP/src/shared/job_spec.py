"""Structuration d'une fiche de poste en exigences (JobSpec).

Étape commune à la préparation d'entretien et au scoring : les deux ont besoin
de la même fiche de poste structurée en must_have / nice_to_have.
"""

import sys
from typing import Callable

from src.shared.contracts import JobSpec
from src.shared.errors import CleApiManquante
from src.shared.json_utils import parse_json_block
from src.shared.prompt_fragments import AVERTISSEMENT_DONNEES_TIERCES, FORMAT_JSON_STRICT
from src.shared.sanitize import encadrer

AppelLLM = Callable[[str, str, int], str]

MAX_TOKENS_BRIEF = 900

_SQUELETTE = """{
  "titre": "intitulé du poste",
  "must_have": ["exigences indispensables, 3 à 8 éléments"],
  "nice_to_have": ["compétences souhaitables, 0 à 5 éléments"]
}"""

SYSTEM_BRIEF = f"""Tu es un expert en recrutement. Tu analyses une fiche de poste et tu en extrais les exigences.

{AVERTISSEMENT_DONNEES_TIERCES}

{FORMAT_JSON_STRICT}
Structure exacte attendue :
""" + _SQUELETTE


def user_brief(jd_propre: str) -> str:
    return "--- FICHE DE POSTE ---\n" + encadrer(jd_propre)


def build_job_spec(appel: AppelLLM, jd_propre: str) -> JobSpec:
    """Structure une fiche de poste assainie en JobSpec.

    Ne lève que CleApiManquante (erreur de configuration). Toute autre panne
    (JSON invalide, modèle qui refuse) replie sur un JobSpec minimal construit
    depuis la première ligne non vide de la fiche — mieux vaut un titre pauvre
    que faire échouer tout l'appelant pour un JobSpec.
    """
    try:
        donnees = parse_json_block(appel(SYSTEM_BRIEF, user_brief(jd_propre), MAX_TOKENS_BRIEF))
        return JobSpec.model_validate(donnees)
    except CleApiManquante:
        raise
    except Exception as e:
        print(f"[job_spec] structuration impossible ({e}) — repli sur la fiche brute", file=sys.stderr)
        premiere_ligne = next((l.strip() for l in jd_propre.splitlines() if l.strip()), "Poste")
        return JobSpec(titre=premiere_ligne[:120])
