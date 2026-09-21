"""Moteur de conduite de l'entretien : déroule le QuestionPlan, ne réfléchit jamais.

Toute l'intelligence (questions, barèmes, relances) a été calculée en phase PREP.
Ici, zéro appel LLM : la décision « relance ou question suivante » est une
heuristique déterministe sur le texte de la réponse.
"""

from datetime import datetime, timezone
from typing import Optional

from src.entretien.contracts import AnswerRecord, InterviewSession, Question, QuestionPlan
from src.shared.sanitize import tokenize

SEUIL_MOTS = 15
SEUIL_RECOUVREMENT = 0.15


def _maintenant() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _duree_secondes(debut_iso: str, fin_iso: str) -> float:
    try:
        debut = datetime.fromisoformat(debut_iso)
        fin = datetime.fromisoformat(fin_iso)
        return max(0.0, round((fin - debut).total_seconds(), 1))
    except (ValueError, TypeError):
        return 0.0


def formater_horodatage(horodatage_iso: str) -> str:
    """Date et heure:minute, lisibles pour un recruteur — pas l'ISO-8601 complet stocké."""
    if not horodatage_iso:
        return "—"
    try:
        return datetime.fromisoformat(horodatage_iso).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return horodatage_iso


def formater_duree(secondes: float) -> str:
    """Durée de réponse lisible : "42 s" ou "1 min 12 s"."""
    total = max(0, round(secondes))
    if total < 60:
        return f"{total} s"
    minutes, reste = divmod(total, 60)
    return f"{minutes} min {reste:02d} s" if reste else f"{minutes} min"


def reponse_semble_superficielle(
    reponse: str, question: Question, seuil_mots: int = SEUIL_MOTS
) -> bool:
    """Une réponse est jugée superficielle si elle est courte OU si elle ne
    recoupe quasiment aucun mot des critères du barème.

    Seuil de recouvrement volontairement bas (15%) : une reformulation légitime
    ne doit pas déclencher une relance inutile — mieux vaut sous-relancer que
    harceler un candidat qui a déjà bien répondu.
    """
    mots_reponse = reponse.split()
    if len(mots_reponse) < seuil_mots:
        return True

    texte_criteres = " ".join(f"{r.criterion} {r.description}" for r in question.rubric)
    mots_criteres = tokenize(texte_criteres)
    if not mots_criteres:
        return False

    recouvrement = len(tokenize(reponse) & mots_criteres) / len(mots_criteres)
    return recouvrement < SEUIL_RECOUVREMENT


def demarrer(plan: QuestionPlan) -> InterviewSession:
    """Crée une session d'entretien à partir d'un plan déjà généré et validé."""
    horodatage = _maintenant()
    session = InterviewSession(plan=plan, demarre_le=horodatage, question_posee_le=horodatage)
    if not plan.questions:
        # Plan vide (toutes les sections ont échoué en PREP) : rien à dérouler.
        session.statut = "termine"
        session.termine_le = horodatage
    return session


def question_courante(session: InterviewSession) -> Optional[Question]:
    """La Question en cours (principale ou avec relance en attente). None si terminé."""
    if session.cursor >= len(session.plan.questions):
        return None
    return session.plan.questions[session.cursor]


def texte_a_poser(session: InterviewSession) -> Optional[str]:
    """Le texte exact à afficher au candidat : la question, ou sa relance si en attente."""
    question = question_courante(session)
    if question is None:
        return None
    if session.relance_utilisee and question.followups:
        return question.followups[0]
    return question.question


def soumettre_reponse(session: InterviewSession, texte: str) -> InterviewSession:
    """Enregistre la réponse du candidat, décide relance ou avance le curseur.

    Une seule relance par question, jamais plus : si `relance_utilisee` était déjà
    vraie, cette réponse répond forcément à la relance — on avance sans y repenser.
    """
    if session.statut == "termine":
        return session

    question = question_courante(session)
    if question is None:
        return session

    maintenant = _maintenant()
    reponse_a_une_relance = session.relance_utilisee
    session.reponses.append(
        AnswerRecord(
            question_id=question.id,
            reponse=texte,
            est_relance=reponse_a_une_relance,
            horodatage=maintenant,
            duree_reponse_s=_duree_secondes(session.question_posee_le, maintenant),
        )
    )

    if reponse_a_une_relance:
        session.cursor += 1
        session.relance_utilisee = False
    elif question.followups and reponse_semble_superficielle(texte, question):
        session.relance_utilisee = True
    else:
        session.cursor += 1
        session.relance_utilisee = False

    if session.cursor >= len(session.plan.questions):
        session.statut = "termine"
        session.termine_le = maintenant
    else:
        # Une nouvelle question ou relance est désormais affichée : le chrono redémarre.
        session.question_posee_le = maintenant

    return session
