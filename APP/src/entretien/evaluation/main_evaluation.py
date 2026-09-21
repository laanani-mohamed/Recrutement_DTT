"""
main_evaluation.py
===================
Module principal d'orchestration des providers LLM pour l'évaluation des
réponses d'un entretien mené — la phase POST.

Le LLM ne produit jamais de score : il statue critère par critère du barème
déjà généré en PREP, avec citation à l'appui. Le score est calculé en Python.

Utilisation :
    from src.entretien.evaluation import evaluate_interview, PROVIDERS

    evaluation = evaluate_interview(session, provider="groq")
    print(evaluation.score_global)
"""

import sys
from typing import Optional

from src.entretien.contracts import InterviewEvaluation, InterviewSession
from src.entretien.evaluation.gemini_provider import call_llm as _appel_gemini
from src.entretien.evaluation.groq_provider import call_llm as _appel_groq
from src.entretien.evaluation.ollama_provider import call_llm as _appel_ollama
from src.entretien.evaluation.openrouter_provider import call_llm as _appel_openrouter
from src.entretien.evaluation.pipeline import Progression, run

PROVIDERS: dict[str, dict] = {
    "groq": {
        "label": "Groq (qwen3.6-27b)",
        "description": "Ultra rapide · Mode JSON natif · Recommandé pour la notation",
        "env_key": "GROQ_API_KEY",
        "signup_url": "https://console.groq.com",
        "badge": "⚡",
        "appel": _appel_groq,
    },
    "gemini": {
        "label": "Google Gemini Flash",
        "description": "Grand contexte · Mode JSON natif · Très précis",
        "env_key": "GEMINI_API_KEY",
        "signup_url": "https://aistudio.google.com",
        "badge": "🔮",
        "appel": _appel_gemini,
    },
    "ollama": {
        "label": "Ollama (Local)",
        "description": "100 % privé · Sans mode JSON : réparation plus fréquente",
        "env_key": "OLLAMA_MODEL",
        "signup_url": "https://ollama.com",
        "badge": "🦙",
        "appel": _appel_ollama,
    },
    "openrouter": {
        "label": "OpenRouter (multi-modèles)",
        "description": "50+ modèles via 1 clé · Sans mode JSON garanti",
        "env_key": "OPENROUTER_API_KEY",
        "signup_url": "https://openrouter.ai",
        "badge": "🌐",
        "appel": _appel_openrouter,
    },
}


def evaluate_interview(
    session: InterviewSession,
    provider: str = "groq",
    api_key: str = None,
    model: str = None,
    on_progress: Optional[Progression] = None,
) -> InterviewEvaluation:
    """
    Note chaque réponse enregistrée dans la session contre le barème de sa question.

    Args:
        session: Session d'entretien menée (src.entretien.live), avec ses réponses.
        provider: "groq" | "gemini" | "ollama" | "openrouter".
        api_key: Clé API du provider (ignorée pour ollama).
        model: Nom du modèle, si l'on veut surcharger celui par défaut.
        on_progress: Callback (etape, fraction) pour l'affichage de la progression.

    Returns:
        InterviewEvaluation : chaque réponse notée critère par critère, score_global
        calculé en Python. Les questions en échec sont listées dans
        questions_echouees — la fonction ne lève pas d'exception pour autant.
    """
    if provider not in PROVIDERS:
        raise ValueError(
            f"Provider inconnu : '{provider}'. "
            f"Choisissez parmi : {', '.join(PROVIDERS.keys())}"
        )

    info = PROVIDERS[provider]
    print(f"[Évaluation] Provider : {info['badge']} {info['label']}", file=sys.stderr)

    appel_provider = info["appel"]

    def appel(system: str, user: str, max_tokens: int) -> str:
        return appel_provider(system, user, max_tokens=max_tokens, api_key=api_key, model=model)

    return run(appel, session, provider=provider, on_progress=on_progress)
