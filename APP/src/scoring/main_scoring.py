"""
main_scoring.py
================
Module principal d'orchestration des providers LLM pour le scoring CV / Job Description.
-----------------------------------------------------------------------------------------------
Ce module unifie les trois providers disponibles via une interface simple :
    score_cv(cv_json, job_description, provider, api_key) → dict JSON

Providers disponibles :
    - "groq"        : Groq API (qwen-2.5-32b)
    - "gemini"      : Google Gemini Flash
    - "openrouter"  : OpenRouter (openrouter/auto)

Utilisation :
    from src.scoring import score_cv, PROVIDERS

    result = score_cv(cv_json, job_description, provider="groq")
    print(result["score_global"])
"""

import sys
from typing import Literal

# Import des trois modules providers
from src.scoring.groq_provider       import score_with_groq
from src.scoring.gemini_provider     import score_with_gemini
from src.scoring.openrouter_provider import score_with_openrouter
from src.scoring.ollama_provider     import score_with_ollama


# ------------------------------------------------------------------
# Constante : liste des providers disponibles avec leurs descriptions
# ------------------------------------------------------------------
PROVIDERS: dict[str, dict] = {
    "groq": {
        "label":       "Groq (qwen-2.5-32b)",
        "description": "Ultra rapide · Meilleur pour JSON structuré",
        "env_key":     "GROQ_API_KEY",
        "signup_url":  "https://console.groq.com",
        "badge":       "⚡",
    },
    "gemini": {
        "label":       "Google Gemini Flash",
        "description": "Très précis · Rapide",
        "env_key":     "GEMINI_API_KEY",
        "signup_url":  "https://aistudio.google.com",
        "badge":       "🔮",
    },
    "ollama": {
        "label":       "Ollama (Local)",
        "description": "Exécution locale (100% privé) — nécessite Ollama installé",
        "env_key":     "OLLAMA_MODEL",
        "signup_url":  "https://ollama.com",
        "badge":       "🦙",
    },
    "openrouter": {
        "label":       "OpenRouter (auto)",
        "description": "Accès à 50+ modèles gratuits via 1 clé",
        "env_key":     "OPENROUTER_API_KEY",
        "signup_url":  "https://openrouter.ai",
        "badge":       "🌐",
    },
}

ProviderName = Literal["groq", "gemini", "openrouter"]


def score_cv(cv_json: dict, job_description: str, provider: ProviderName = "groq", api_key: str = None) -> dict:
    """
    Analyse un CV (format JSON) et une description de poste avec le provider LLM spécifié
    et retourne un dictionnaire JSON structuré avec le scoring.

    Args:
        cv_json (dict): Dictionnaire JSON structuré représentant le CV.
        job_description (str): Description de poste.
        provider (str): Provider LLM à utiliser ("groq", "gemini", "openrouter").
        api_key (str): Clé API du provider (optionnelle).

    Returns:
        dict: Dictionnaire JSON structuré contenant le scoring, les points forts, etc.
    """
    if provider not in PROVIDERS:
        providers_valides = ", ".join(PROVIDERS.keys())
        raise ValueError(
            f"Provider inconnu : '{provider}'. "
            f"Choisissez parmi : {providers_valides}"
        )

    info = PROVIDERS[provider]
    print(
        f"[Scoring] Provider : {info['badge']} {info['label']}",
        file=sys.stderr,
    )

    if provider == "groq":
        return score_with_groq(cv_json, job_description, api_key=api_key)
    elif provider == "gemini":
        return score_with_gemini(cv_json, job_description, api_key=api_key)
    elif provider == "openrouter":
        return score_with_openrouter(cv_json, job_description, api_key=api_key)
    elif provider == "ollama":
        return score_with_ollama(cv_json, job_description, model=api_key)
