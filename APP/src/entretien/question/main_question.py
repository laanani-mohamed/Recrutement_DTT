"""
main_question.py
================
Module principal d'orchestration des providers LLM pour la préparation
du plan d'entretien à partir d'un CV et d'une fiche de poste.

Utilisation :
    from src.entretien.question import generate_question_plan, PROVIDERS

    plan = generate_question_plan(cv_json, job_description, provider="groq")
    print(plan.questions[0].question)
"""

import sys
from typing import Optional, Sequence

from src.entretien.contracts import QuestionPlan
from src.entretien.question.gemini_provider import call_llm as _appel_gemini
from src.entretien.question.groq_provider import call_llm as _appel_groq
from src.entretien.question.ollama_provider import call_llm as _appel_ollama
from src.entretien.question.openrouter_provider import call_llm as _appel_openrouter
from src.entretien.question.pipeline import Progression, run

PROVIDERS: dict[str, dict] = {
    "groq": {
        "label": "Groq (qwen3.6-27b)",
        "description": "Ultra rapide · Mode JSON natif · Recommandé pour le plan d'entretien",
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
        "description": "100 % privé · Sans mode JSON : barèmes plus inégaux, réparation fréquente",
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


def generate_question_plan(
    cv_json: dict,
    job_description: str,
    provider: str = "groq",
    api_key: str = None,
    model: str = None,
    scoring_json: Optional[dict] = None,
    sections: Optional[Sequence[str]] = None,
    on_progress: Optional[Progression] = None,
) -> QuestionPlan:
    """
    Construit un plan d'entretien structuré à partir du CV et de la fiche de poste.

    Args:
        cv_json: CV structuré produit par src.convert_json.
        job_description: Fiche de poste en texte libre.
        provider: "groq" | "gemini" | "ollama" | "openrouter".
        api_key: Clé API du provider (ignorée pour ollama).
        model: Nom du modèle, si l'on veut surcharger celui par défaut.
        scoring_json: Sortie de src.scoring — ses lacunes alimentent les points à sonder.
        sections: Sous-ensemble de sections à générer (toutes par défaut).
        on_progress: Callback (etape, fraction) pour l'affichage de la progression.

    Returns:
        QuestionPlan validé. Les sections en échec sont listées dans
        plan.sections_echouees — la fonction ne lève pas d'exception pour autant.
    """
    if provider not in PROVIDERS:
        raise ValueError(
            f"Provider inconnu : '{provider}'. "
            f"Choisissez parmi : {', '.join(PROVIDERS.keys())}"
        )

    info = PROVIDERS[provider]
    print(f"[Entretien] Provider : {info['badge']} {info['label']}", file=sys.stderr)

    appel_provider = info["appel"]

    def appel(system: str, user: str, max_tokens: int) -> str:
        return appel_provider(
            system, user, max_tokens=max_tokens, api_key=api_key, model=model
        )

    return run(
        appel,
        cv_json,
        job_description,
        provider=provider,
        scoring_json=scoring_json,
        sections=sections,
        on_progress=on_progress,
    )


# ------------------------------------------------------------------
# Test direct : python -m src.entretien.question.main_question groq
# ------------------------------------------------------------------
if __name__ == "__main__":
    prov = sys.argv[1] if len(sys.argv) > 1 else "groq"

    cv_demo = {
        "nom_complet": "Mohamed Laanani",
        "titre_poste": "Data Engineer",
        "resume": "5 ans d'expérience sur des pipelines de données à fort volume.",
        "competences": ["Python", "SQL", "Spark", "Airflow", "Docker"],
        "langues": [{"langue": "Français", "niveau": "C2"}],
        "experience": [
            {
                "poste": "Data Engineer",
                "entreprise": "TechCorp",
                "debut": "2021",
                "fin": "2026",
                "description": "Pipelines Spark traitant 2 To/jour, orchestration Airflow.",
            }
        ],
        "formation": [
            {"diplome": "Master Informatique", "etablissement": "ENSIAS", "annee": "2021"}
        ],
        "certifications": [],
    }

    poste_demo = (
        "Data Engineer confirmé. Indispensable : Python, Spark, modélisation de données, "
        "orchestration Airflow. Souhaitable : dbt, AWS, Terraform."
    )

    plan = generate_question_plan(cv_demo, poste_demo, provider=prov)
    print(plan.model_dump_json(indent=2))
