"""
main_scoring.py
================
Module principal d'orchestration des providers LLM pour le scoring CV / Job Description.
-----------------------------------------------------------------------------------------------
Le LLM ne produit jamais de score global : il statue exigence par exigence
(satisfait/partiel/absent) avec citation à l'appui, et le score est calculé
ensuite en Python — déterministe, auditable, jamais halluciné.

Utilisation :
    from src.scoring import score_cv, PROVIDERS

    carte = score_cv(cv_json, job_description, provider="groq")
    print(carte.score_global, carte.verdicts)
"""

import sys
from typing import Optional

from src.scoring.contracts import ScoreCard
from src.scoring.gemini_provider import call_llm as _appel_gemini
from src.scoring.groq_provider import call_llm as _appel_groq
from src.scoring.ollama_provider import call_llm as _appel_ollama
from src.scoring.openrouter_provider import call_llm as _appel_openrouter
from src.scoring.pipeline import Progression, run

PROVIDERS: dict[str, dict] = {
    "groq": {
        "label": "Groq (qwen-2.5-32b)",
        "description": "Ultra rapide · Mode JSON natif · Recommandé",
        "env_key": "GROQ_API_KEY",
        "signup_url": "https://console.groq.com",
        "badge": "⚡",
        "appel": _appel_groq,
    },
    "gemini": {
        "label": "Google Gemini Flash",
        "description": "Très précis · Mode JSON natif",
        "env_key": "GEMINI_API_KEY",
        "signup_url": "https://aistudio.google.com",
        "badge": "🔮",
        "appel": _appel_gemini,
    },
    "ollama": {
        "label": "Ollama (Local)",
        "description": "Exécution locale (100% privé) — nécessite Ollama installé",
        "env_key": "OLLAMA_MODEL",
        "signup_url": "https://ollama.com",
        "badge": "🦙",
        "appel": _appel_ollama,
    },
    "openrouter": {
        "label": "OpenRouter (auto)",
        "description": "Accès à 50+ modèles gratuits via 1 clé",
        "env_key": "OPENROUTER_API_KEY",
        "signup_url": "https://openrouter.ai",
        "badge": "🌐",
        "appel": _appel_openrouter,
    },
}


def score_cv(
    cv_json: dict,
    job_description: str,
    provider: str = "groq",
    api_key: str = None,
    model: str = None,
    on_progress: Optional[Progression] = None,
) -> ScoreCard:
    """
    Évalue un CV (JSON) face à une fiche de poste, exigence par exigence.

    Args:
        cv_json: Dictionnaire JSON structuré représentant le CV.
        job_description: Description de poste en texte libre.
        provider: "groq" | "gemini" | "ollama" | "openrouter".
        api_key: Clé API du provider (ignorée pour ollama).
        model: Nom du modèle, si l'on veut surcharger celui par défaut.
        on_progress: Callback (etape, fraction) pour l'affichage de la progression.

    Returns:
        ScoreCard : verdicts par exigence, score_global calculé en Python,
        points_forts/lacunes dérivés des verdicts, recommandation textuelle
        (jamais une décision d'embauche).
    """
    if provider not in PROVIDERS:
        raise ValueError(
            f"Provider inconnu : '{provider}'. "
            f"Choisissez parmi : {', '.join(PROVIDERS.keys())}"
        )

    info = PROVIDERS[provider]
    print(f"[Scoring] Provider : {info['badge']} {info['label']}", file=sys.stderr)

    appel_provider = info["appel"]

    def appel(system: str, user: str, max_tokens: int) -> str:
        return appel_provider(system, user, max_tokens=max_tokens, api_key=api_key, model=model)

    return run(appel, cv_json, job_description, provider=provider, on_progress=on_progress)


# ------------------------------------------------------------------
# Test direct : python -m src.scoring.main_scoring groq
# ------------------------------------------------------------------
if __name__ == "__main__":
    cv_demo = {
        "nom_complet": "Mohamed Laanani",
        "titre_poste": "Data Engineer",
        "resume": "5 ans d'expérience sur des pipelines de données à fort volume.",
        "competences": ["Python", "SQL", "Airflow", "Docker"],
        "experience": [
            {
                "poste": "Data Engineer",
                "entreprise": "TechCorp",
                "resume": "Pipelines de données à fort volume.",
                "description": "Développement de pipelines batch en Python orchestrés par Airflow, traitant 500 Go/jour.",
            }
        ],
        "formation": [
            {"diplome": "Master Informatique", "etablissement": "ENSIAS", "annee": "2021"}
        ],
    }
    poste_demo = "Data Engineer confirmé. Indispensable : Python, Spark, Airflow. Souhaitable : dbt."

    prov = sys.argv[1] if len(sys.argv) > 1 else "groq"
    carte = score_cv(cv_demo, poste_demo, provider=prov)
    print(carte.model_dump_json(indent=2))
