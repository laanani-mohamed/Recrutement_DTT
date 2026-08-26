"""
main_convert_json.py
====================
Module principal d'orchestration des providers LLM pour la conversion de CV en JSON structuré.
-----------------------------------------------------------------------------------------------
Ce module unifie les trois providers disponibles via une interface simple :
    convert_cv(cv_text, provider, api_key) → dict JSON

Providers disponibles :
    - "groq"        : Groq API (qwen/qwen3.6-27b) — ultra rapide, 6k req/jour gratuit
    - "gemini"      : Google Gemini Flash 2.0 / 3.5 — grand contexte, 1.5k req/jour gratuit
    - "openrouter"  : OpenRouter (multi-modèles gratuits via 1 clé)

Utilisation :
    from src.convert_json import convert_cv, PROVIDERS

    result = convert_cv(cv_text, provider="groq", api_key="gsk_...")
    print(result["nom_complet"])
    print(result["competences"])
"""

import sys
from typing import Literal

# Import des trois modules providers
from src.convert_json.groq_provider       import classify_with_groq
from src.convert_json.gemini_provider     import classify_with_gemini
from src.convert_json.openrouter_provider import classify_with_openrouter
from src.convert_json.ollama_provider     import classify_with_ollama


# ------------------------------------------------------------------
# Constante : liste des providers disponibles avec leurs descriptions
# ------------------------------------------------------------------
PROVIDERS: dict[str, dict] = {
    "groq": {
        "label":       "Groq (qwen3.6-27b)",
        "description": "Ultra rapide · 6 000 req/jour gratuit · Meilleur pour extraction JSON",
        "env_key":     "GROQ_API_KEY",
        "signup_url":  "https://console.groq.com",
        "badge":       "⚡",
    },
    "gemini": {
        "label":       "Google Gemini Flash",
        "description": "Grand contexte (1M tokens) · 1 500 req/jour gratuit · Très précis",
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
        "label":       "OpenRouter (multi-modèles)",
        "description": "Accès à 50+ modèles gratuits via 1 clé · Llama, Mistral, Gemma...",
        "env_key":     "OPENROUTER_API_KEY",
        "signup_url":  "https://openrouter.ai",
        "badge":       "🌐",
    },
}

# Type pour l'autocomplétion
ProviderName = Literal["groq", "gemini", "openrouter"]


def convert_cv(cv_text: str, provider: ProviderName = "groq", api_key: str = None) -> dict:
    """
    Analyse un texte de CV avec le provider LLM spécifié et retourne
    un dictionnaire JSON structuré avec toutes les informations du candidat.

    Args:
        cv_text (str): Texte brut extrait du CV (via les modules d'extraction).
        provider (str): Provider LLM à utiliser.
                        Valeurs : "groq" | "gemini" | "openrouter"
                        Défaut : "groq" (le plus rapide et précis pour le JSON)
        api_key (str): Clé API du provider. Si None, utilise la variable
                       d'environnement correspondante (ex: GROQ_API_KEY).

    Returns:
        dict: Dictionnaire JSON structuré contenant :
            - nom_complet, email, telephone, localisation
            - titre_poste, resume
            - competences (liste)
            - langues (liste de dicts langue/niveau)
            - experience (liste de postes)
            - formation (liste de diplômes)
            - certifications (liste)
            - liens (linkedin, github, portfolio)

    Raises:
        ValueError: Si le provider est inconnu ou si la clé API est manquante.
        RuntimeError: Si l'API retourne une erreur ou un JSON invalide.
    """
    if provider not in PROVIDERS:
        providers_valides = ", ".join(PROVIDERS.keys())
        raise ValueError(
            f"Provider inconnu : '{provider}'. "
            f"Choisissez parmi : {providers_valides}"
        )

    info = PROVIDERS[provider]
    print(
        f"[convert_json] Provider : {info['badge']} {info['label']}",
        file=sys.stderr,
    )

    # Dispatch vers le bon module selon le provider choisi
    if provider == "groq":
        return classify_with_groq(cv_text, api_key=api_key)
    elif provider == "gemini":
        return classify_with_gemini(cv_text, api_key=api_key)
    elif provider == "openrouter":
        return classify_with_openrouter(cv_text, api_key=api_key)
    elif provider == "ollama":
        return classify_with_ollama(cv_text, model=api_key)


# Alias pour compatibilité
classify_cv = convert_cv


# ------------------------------------------------------------------
# Point d'entrée pour test en ligne de commande
# Usage : python -m src.convert_json.main_convert_json groq "texte du CV..."
# ------------------------------------------------------------------
if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print(f"Usage : python main_convert_json.py <provider> [texte_cv]")
        print(f"Providers disponibles : {list(PROVIDERS.keys())}")
        sys.exit(1)

    prov = sys.argv[1]
    texte = sys.argv[2] if len(sys.argv) > 2 else "Jean Dupont, développeur Python 5 ans."
    result = convert_cv(texte, provider=prov)
    print(json.dumps(result, ensure_ascii=False, indent=2))
