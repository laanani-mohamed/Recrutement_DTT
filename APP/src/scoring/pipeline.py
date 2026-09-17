"""Pipeline de scoring : JobSpec → verdict par exigence → score calculé en Python.

Le LLM ne voit jamais le score final avant qu'il soit calculé — il ne fait que
statuer sur chaque exigence, avec citation à l'appui.
"""

import json
import sys
from datetime import datetime, timezone
from typing import Callable, Optional

from pydantic import TypeAdapter, ValidationError

from src.scoring.contracts import RequirementVerdict, ScoreCard
from src.scoring.prompts import SYSTEM_REPARATION, system_verdict, user_reparation, user_verdict
from src.shared.errors import CleApiManquante
from src.shared.job_spec import build_job_spec
from src.shared.json_utils import parse_json_block
from src.shared.sanitize import citation_est_verifiee, sanitize_cv, sanitize_texte

AppelLLM = Callable[[str, str, int], str]
Progression = Callable[[str, float], None]

_VERDICTS = TypeAdapter(list[RequirementVerdict])

MAX_TOKENS_VERDICT = 4000


def _avancer(on_progress: Optional[Progression], etape: str, fraction: float) -> None:
    if on_progress:
        on_progress(etape, fraction)


def _exigences_avec_id(job) -> list[tuple[str, str, str]]:
    """Numérote les exigences : un requirement_id explicite évite au modèle de devoir
    reproduire le texte exact de l'exigence pour qu'on sache à laquelle il répond."""
    exigences = []
    for i, texte in enumerate(job.must_have, start=1):
        exigences.append((f"req_m{i}", texte, "must_have"))
    for i, texte in enumerate(job.nice_to_have, start=1):
        exigences.append((f"req_n{i}", texte, "nice_to_have"))
    return exigences


def _parser_verdicts(
    brut: str, index: dict[str, tuple[str, str]]
) -> tuple[list[RequirementVerdict], str]:
    """index : requirement_id -> (texte_original, categorie)."""
    donnees = parse_json_block(brut)
    if not isinstance(donnees, dict) or "verdicts" not in donnees:
        raise ValueError("Le JSON ne contient pas de champ 'verdicts'.")

    bruts = donnees["verdicts"]
    if not isinstance(bruts, list):
        raise ValueError("'verdicts' n'est pas une liste.")

    retenus = []
    for item in bruts:
        if not isinstance(item, dict):
            continue
        rid = str(item.get("requirement_id", ""))
        meta = index.get(rid)
        if meta is None:
            continue  # id halluciné, non demandé : on l'ignore plutôt que de planter
        texte, categorie = meta
        item["requirement_id"] = rid
        item["requirement"] = texte  # texte d'origine, jamais l'écho potentiellement altéré du modèle
        item["categorie"] = categorie
        retenus.append(item)

    if not retenus:
        raise ValueError("Aucun verdict exploitable (ids non reconnus).")

    return _VERDICTS.validate_python(retenus), str(donnees.get("recommandation", ""))


def _completer_verdicts_manquants(
    verdicts: list[RequirementVerdict], index: dict[str, tuple[str, str]]
) -> list[RequirementVerdict]:
    """Une exigence non évaluée par le modèle est traitée comme absente plutôt
    qu'ignorée : un score calculé sur un sous-ensemble des exigences gonflerait
    artificiellement le résultat pour un CV mal couvert par le modèle."""
    vus = {v.requirement_id for v in verdicts}
    for rid, (texte, categorie) in index.items():
        if rid not in vus:
            verdicts.append(
                RequirementVerdict(
                    requirement_id=rid,
                    requirement=texte,
                    categorie=categorie,
                    raisonnement="Non évalué par le modèle (absent de sa réponse).",
                    status="absent",
                )
            )
    return verdicts


def run(
    appel: AppelLLM,
    cv_json: dict,
    job_description: str,
    provider: str,
    on_progress: Optional[Progression] = None,
) -> ScoreCard:
    """Produit une ScoreCard. Ne lève que CleApiManquante (erreur de configuration)."""
    cv_propre = sanitize_cv(cv_json)
    jd_propre = sanitize_texte(job_description)
    candidat = str(cv_json.get("nom_complet") or "Candidat")

    _avancer(on_progress, "Analyse de la fiche de poste", 0.15)
    job = build_job_spec(appel, jd_propre)

    exigences = _exigences_avec_id(job)
    if not exigences:
        return ScoreCard(
            candidat=candidat,
            poste=job.titre,
            job=job,
            recommandation="Aucune exigence exploitable n'a pu être extraite de la fiche de poste.",
            provider=provider,
            genere_le=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )

    index = {rid: (texte, cat) for rid, texte, cat in exigences}

    _avancer(on_progress, "Évaluation des exigences", 0.4)
    brut = appel(system_verdict(), user_verdict(cv_propre, job, exigences), MAX_TOKENS_VERDICT)

    try:
        verdicts, recommandation = _parser_verdicts(brut, index)
    except (ValueError, ValidationError) as premiere:
        detail = (
            json.dumps(premiere.errors(), ensure_ascii=False, default=str)[:1500]
            if isinstance(premiere, ValidationError)
            else str(premiere)
        )
        print(f"[scoring] sortie invalide, tentative de réparation… ({detail})", file=sys.stderr)
        _avancer(on_progress, "Réparation de la réponse", 0.6)
        repare = appel(SYSTEM_REPARATION, user_reparation(brut, detail), MAX_TOKENS_VERDICT)
        try:
            verdicts, recommandation = _parser_verdicts(repare, index)
        except (ValueError, ValidationError) as e:
            print(f"[scoring] réparation infructueuse : {e}", file=sys.stderr)
            verdicts, recommandation = [], "Évaluation impossible : réponse du modèle inexploitable."

    verdicts = _completer_verdicts_manquants(verdicts, index)

    _avancer(on_progress, "Vérification des citations", 0.85)
    for v in verdicts:
        v.evidence_verifiee = bool(v.evidence) and citation_est_verifiee(v.evidence, cv_propre)

    carte = ScoreCard(
        candidat=candidat,
        poste=job.titre,
        job=job,
        verdicts=verdicts,
        points_forts=[v.requirement for v in verdicts if v.status == "satisfait"],
        lacunes=[v.requirement for v in verdicts if v.status in ("absent", "partiel")],
        recommandation=recommandation,
        provider=provider,
        genere_le=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    carte.score_global = carte.calculer_score()

    _avancer(on_progress, "Score calculé", 1.0)
    return carte
