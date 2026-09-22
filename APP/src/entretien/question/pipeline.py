"""Pipeline de préparation : brief → génération par section → assemblage.

Aucun appel LLM ne produit le plan entier d'un coup : une sortie tronquée est un
JSON illisible, et perdre une section coûte moins cher que perdre le plan.
"""

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Callable, Optional, Sequence

from pydantic import TypeAdapter, ValidationError

from src.entretien.contracts import (
    SECTIONS,
    InterviewBrief,
    Question,
    QuestionPlan,
)
from src.entretien.question.prompts import (
    SYSTEM_REPARATION,
    system_section,
    user_reparation,
    user_section,
)
from src.shared.errors import CleApiManquante
from src.shared.job_spec import build_job_spec
from src.shared.json_utils import parse_json_block
from src.shared.sanitize import citation_est_verifiee, sanitize_cv, sanitize_texte

AppelLLM = Callable[[str, str, int], str]
Progression = Callable[[str, float], None]

_QUESTIONS = TypeAdapter(list[Question])

MAX_TOKENS_SECTION = 3000


def _avancer(on_progress: Optional[Progression], etape: str, fraction: float) -> None:
    if on_progress:
        on_progress(etape, fraction)


def _build_brief(
    appel: AppelLLM, jd_propre: str, scoring_json: Optional[dict]
) -> InterviewBrief:
    """Structure la fiche de poste et récupère les cibles à sonder issues du scoring."""
    scoring = scoring_json or {}
    job = build_job_spec(appel, jd_propre)

    return InterviewBrief(
        job=job,
        probe_targets=[str(x) for x in scoring.get("lacunes", [])][:8],
        points_forts=[str(x) for x in scoring.get("points_forts", [])][:8],
    )


def _parser_questions(brut: str, section: str) -> list[Question]:
    donnees = parse_json_block(brut)
    if isinstance(donnees, dict):
        donnees = donnees.get("questions", donnees)
    if not isinstance(donnees, list):
        raise ValueError("Le JSON ne contient pas de liste de questions.")

    for item in donnees:
        if isinstance(item, dict):
            item["section"] = section  # le modèle se trompe parfois de section
    return _QUESTIONS.validate_python(donnees)


def _generer_section(
    appel: AppelLLM, section: str, cv_propre: dict, brief: InterviewBrief, jd_propre: str
) -> list[Question]:
    """Génère les questions d'une section, avec une unique tentative de réparation."""
    brut = appel(
        system_section(section), user_section(cv_propre, brief, jd_propre), MAX_TOKENS_SECTION
    )

    try:
        return _parser_questions(brut, section)
    except (ValueError, ValidationError) as premiere:
        detail = (
            json.dumps(premiere.errors(), ensure_ascii=False, default=str)[:1500]
            if isinstance(premiere, ValidationError)
            else str(premiere)
        )
        print(f"[{section}] sortie invalide, tentative de réparation…", file=sys.stderr)
        repare = appel(SYSTEM_REPARATION, user_reparation(brut, detail), MAX_TOKENS_SECTION)
        return _parser_questions(repare, section)


def _assembler(
    resultats: list,
    cibles: Sequence[str],
    cv_propre: dict,
    cv_json: dict,
    jd_propre: str,
    brief: InterviewBrief,
    provider: str,
) -> QuestionPlan:
    ordre = {section: i for i, section in enumerate(cibles)}
    resultats.sort(key=lambda r: ordre.get(r[0], 99))

    questions: list[Question] = []
    echouees: list[str] = []
    erreurs: dict[str, str] = {}
    vues: set[str] = set()
    compteurs: dict[str, int] = {}

    for section, lot, erreur in resultats:
        if erreur is not None:
            print(f"[{section}] abandonnée : {erreur}", file=sys.stderr)
        if erreur is not None or not lot:
            echouees.append(section)
            erreurs[section] = str(erreur) if erreur else "Le modèle n'a produit aucune question."
            continue

        for q in lot:
            cle = q.question.strip().lower()
            if not cle or cle in vues:
                continue
            vues.add(cle)
            compteurs[section] = compteurs.get(section, 0) + 1
            q.id = f"q_{section}_{compteurs[section]:02d}"
            q.ancrage_verifie = citation_est_verifiee(q.ancrage_cv, cv_propre)
            q.ancrage_poste_verifie = citation_est_verifiee(q.ancrage_poste, jd_propre)
            questions.append(q)

    return QuestionPlan(
        candidat=str(cv_json.get("nom_complet") or "Candidat"),
        poste=brief.job.titre,
        brief=brief,
        questions=questions,
        sections_echouees=echouees,
        erreurs=erreurs,
        provider=provider,
        genere_le=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


def run(
    appel: AppelLLM,
    cv_json: dict,
    job_description: str,
    provider: str,
    scoring_json: Optional[dict] = None,
    sections: Optional[Sequence[str]] = None,
    on_progress: Optional[Progression] = None,
) -> QuestionPlan:
    """Produit un plan d'entretien.

    Une section ratée est signalée dans le plan, jamais levée. Seule une erreur
    de configuration (CleApiManquante) remonte : elle affecterait les cinq
    sections, et la dégrader reviendrait à masquer sa cause.
    """
    cibles = tuple(sections) if sections else SECTIONS
    cv_propre = sanitize_cv(cv_json)
    jd_propre = sanitize_texte(job_description)

    _avancer(on_progress, "Analyse de la fiche de poste", 0.1)
    brief = _build_brief(appel, jd_propre, scoring_json)

    def executer(section: str):
        try:
            return section, _generer_section(appel, section, cv_propre, brief, jd_propre), None
        except CleApiManquante:
            raise
        except Exception as e:
            return section, [], e

    resultats: list = []
    total = max(len(cibles), 1)

    if provider == "ollama":
        # Un modèle local ne gagne rien à être sollicité en parallèle.
        for section in cibles:
            resultats.append(executer(section))
            _avancer(on_progress, f"Section {section}", 0.1 + 0.8 * len(resultats) / total)
    else:
        with ThreadPoolExecutor(max_workers=min(4, total)) as pool:
            futurs = [pool.submit(executer, section) for section in cibles]
            for futur in as_completed(futurs):
                resultats.append(futur.result())
                _avancer(
                    on_progress,
                    f"Section {resultats[-1][0]}",
                    0.1 + 0.8 * len(resultats) / total,
                )

    plan = _assembler(resultats, cibles, cv_propre, cv_json, jd_propre, brief, provider)
    _avancer(on_progress, "Plan assemblé", 1.0)
    return plan
