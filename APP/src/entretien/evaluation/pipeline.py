"""Pipeline d'évaluation : note chaque réponse d'entretien contre son barème,
question par question. Le score est toujours calculé en Python, jamais par le LLM.
"""

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Callable, Optional

from pydantic import TypeAdapter, ValidationError

from src.entretien.contracts import (
    CriterionVerdict,
    EvaluatedAnswer,
    InterviewEvaluation,
    InterviewSession,
    Question,
)
from src.entretien.evaluation.prompts import (
    SYSTEM_REPARATION,
    SYSTEM_SYNTHESE,
    criteres_avec_id,
    system_evaluation_question,
    user_evaluation_question,
    user_reparation,
    user_synthese,
)
from src.shared.errors import CleApiManquante
from src.shared.json_utils import parse_json_block
from src.shared.sanitize import citation_est_verifiee, sanitize_texte

AppelLLM = Callable[[str, str, int], str]
Progression = Callable[[str, float], None]

_CRITERES = TypeAdapter(list[CriterionVerdict])

MAX_TOKENS_CRITERE = 1500
MAX_TOKENS_SYNTHESE = 400

SEUIL_POINT_FORT = 70
SEUIL_LACUNE = 40


def _avancer(on_progress: Optional[Progression], etape: str, fraction: float) -> None:
    if on_progress:
        on_progress(etape, fraction)


def _maintenant() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _reponse_complete(session: InterviewSession, question_id: str) -> str:
    """Concatène la réponse principale et la relance éventuelle d'une question."""
    morceaux = [
        f"[Relance] {r.reponse}" if r.est_relance else r.reponse
        for r in session.reponses
        if r.question_id == question_id
    ]
    return "\n\n".join(morceaux)


def _parser_criteres(brut: str, index: dict[str, tuple[str, str]]) -> list[CriterionVerdict]:
    donnees = parse_json_block(brut)
    if not isinstance(donnees, dict) or "criteres" not in donnees:
        raise ValueError("Le JSON ne contient pas de champ 'criteres'.")

    bruts = donnees["criteres"]
    if not isinstance(bruts, list):
        raise ValueError("'criteres' n'est pas une liste.")

    retenus = []
    for item in bruts:
        if not isinstance(item, dict):
            continue
        cid = str(item.get("critere_id", ""))
        meta = index.get(cid)
        if meta is None:
            continue  # id halluciné, non demandé : on l'ignore plutôt que de planter
        criterion, _description = meta
        item["critere_id"] = cid
        item["criterion"] = criterion
        retenus.append(item)

    if not retenus:
        raise ValueError("Aucun verdict exploitable (ids non reconnus).")

    return _CRITERES.validate_python(retenus)


def _completer_criteres_manquants(
    criteres: list[CriterionVerdict], index: dict[str, tuple[str, str]]
) -> list[CriterionVerdict]:
    """Un critère non traité par le modèle est compté 'absent' plutôt qu'ignoré : un
    score calculé sur un sous-ensemble des critères gonflerait artificiellement la note."""
    vus = {c.critere_id for c in criteres}
    for cid, (criterion, _description) in index.items():
        if cid not in vus:
            criteres.append(
                CriterionVerdict(
                    critere_id=cid,
                    criterion=criterion,
                    raisonnement="Non évalué par le modèle (absent de sa réponse).",
                    statut="absent",
                )
            )
    return criteres


def _evaluer_question(
    appel: AppelLLM, question: Question, reponse_candidat: str
) -> EvaluatedAnswer:
    """Note une question. Les appels LLM ne sont jamais dans un bloc qui avalerait
    CleApiManquante (sous-classe de ValueError) : une erreur de configuration doit
    remonter, pas être confondue avec un JSON mal formé."""
    criteres_ids = criteres_avec_id(question)
    index = {cid: (crit, desc) for cid, crit, desc in criteres_ids}
    reponse_propre = sanitize_texte(reponse_candidat)

    brut = appel(
        system_evaluation_question(),
        user_evaluation_question(question, reponse_propre, criteres_ids),
        MAX_TOKENS_CRITERE,
    )

    try:
        criteres = _parser_criteres(brut, index)
    except (ValueError, ValidationError) as premiere:
        detail = (
            json.dumps(premiere.errors(), ensure_ascii=False, default=str)[:1500]
            if isinstance(premiere, ValidationError)
            else str(premiere)
        )
        print(f"[evaluation] {question.id} : sortie invalide, réparation… ({detail})", file=sys.stderr)
        repare = appel(SYSTEM_REPARATION, user_reparation(brut, detail), MAX_TOKENS_CRITERE)
        try:
            criteres = _parser_criteres(repare, index)
        except (ValueError, ValidationError) as e:
            print(f"[evaluation] {question.id} : réparation infructueuse : {e}", file=sys.stderr)
            criteres = []

    criteres = _completer_criteres_manquants(criteres, index)
    for c in criteres:
        c.citation_verifiee = bool(c.citation) and citation_est_verifiee(c.citation, reponse_propre)

    evaluee = EvaluatedAnswer(question_id=question.id, criteres=criteres)
    evaluee.score = evaluee.calculer_score(question)
    return evaluee


def _evaluer_avec_isolation(appel: AppelLLM, session: InterviewSession, question: Question):
    """Isole l'échec d'une question : les autres questions restent évaluées.
    Seule CleApiManquante remonte — elle affecterait toutes les questions."""
    try:
        reponse = _reponse_complete(session, question.id)
        return question, _evaluer_question(appel, question, reponse), None
    except CleApiManquante:
        raise
    except Exception as e:
        return question, None, e


def run(
    appel: AppelLLM,
    session: InterviewSession,
    provider: str,
    on_progress: Optional[Progression] = None,
) -> InterviewEvaluation:
    """Note chaque réponse enregistrée contre son barème. Ne lève que CleApiManquante."""
    questions_par_id = {q.id: q for q in session.plan.questions}
    ids_dans_ordre = list(dict.fromkeys(r.question_id for r in session.reponses))
    questions_repondues = [questions_par_id[qid] for qid in ids_dans_ordre if qid in questions_par_id]

    if not questions_repondues:
        return InterviewEvaluation(
            candidat=session.plan.candidat,
            poste=session.plan.poste,
            recommandation="Aucune réponse enregistrée à évaluer.",
            provider=provider,
            genere_le=_maintenant(),
        )

    total = len(questions_repondues)
    triplets: list[tuple[Question, Optional[EvaluatedAnswer], Optional[Exception]]] = []

    _avancer(on_progress, "Notation des réponses", 0.1)
    if provider == "ollama":
        for i, question in enumerate(questions_repondues, start=1):
            triplets.append(_evaluer_avec_isolation(appel, session, question))
            _avancer(on_progress, f"Notation {i}/{total}", 0.1 + 0.7 * i / total)
    else:
        with ThreadPoolExecutor(max_workers=min(4, total)) as pool:
            futurs = [pool.submit(_evaluer_avec_isolation, appel, session, q) for q in questions_repondues]
            for i, futur in enumerate(as_completed(futurs), start=1):
                triplets.append(futur.result())
                _avancer(on_progress, f"Notation {i}/{total}", 0.1 + 0.7 * i / total)

    ordre = {q.id: i for i, q in enumerate(session.plan.questions)}
    triplets.sort(key=lambda t: ordre.get(t[0].id, 99))

    resultats: list[tuple[Question, EvaluatedAnswer]] = []
    questions_echouees: list[str] = []
    erreurs: dict[str, str] = {}
    for question, evaluee, erreur in triplets:
        if erreur is not None or evaluee is None:
            print(f"[evaluation] {question.id} abandonnée : {erreur}", file=sys.stderr)
            questions_echouees.append(question.id)
            erreurs[question.id] = str(erreur) if erreur else "Échec inconnu."
            continue
        resultats.append((question, evaluee))

    _avancer(on_progress, "Synthèse", 0.9)
    try:
        if resultats:
            brut_synthese = appel(
                SYSTEM_SYNTHESE,
                user_synthese(session.plan.candidat, session.plan.poste, resultats),
                MAX_TOKENS_SYNTHESE,
            )
            recommandation = str(parse_json_block(brut_synthese).get("recommandation", ""))
        else:
            recommandation = "Aucune question n'a pu être notée."
    except CleApiManquante:
        raise
    except Exception as e:
        print(f"[evaluation] synthèse impossible : {e}", file=sys.stderr)
        recommandation = ""

    scores = [e.score for _, e in resultats]
    score_global = round(sum(scores) / len(scores), 1) if scores else 0.0
    points_forts = [q.target_competency for q, e in resultats if e.score >= SEUIL_POINT_FORT]
    lacunes = [q.target_competency for q, e in resultats if e.score <= SEUIL_LACUNE]

    evaluation = InterviewEvaluation(
        candidat=session.plan.candidat,
        poste=session.plan.poste,
        reponses_evaluees=[e for _, e in resultats],
        questions_echouees=questions_echouees,
        erreurs=erreurs,
        score_global=score_global,
        points_forts=points_forts,
        lacunes=lacunes,
        recommandation=recommandation,
        provider=provider,
        genere_le=_maintenant(),
    )
    _avancer(on_progress, "Évaluation terminée", 1.0)
    return evaluation
