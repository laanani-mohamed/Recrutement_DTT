"""Provider OpenRouter pour l'évaluation des réponses d'entretien."""

import os
import sys

from openai import OpenAI

from src.shared.errors import CleApiManquante

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/auto")


def call_llm(
    system: str,
    user: str,
    max_tokens: int = 2000,
    api_key: str = None,
    model: str = None,
) -> str:
    """Appelle OpenRouter et retourne le texte brut de la réponse."""
    key = api_key or os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise CleApiManquante(
            "Clé API OpenRouter manquante. Collez-la dans le champ ci-contre, "
            "ou définissez OPENROUTER_API_KEY dans l'environnement.\n"
            "Clé gratuite : https://openrouter.ai"
        )

    modele = model or DEFAULT_MODEL
    print(f"[OpenRouter] Évaluation avec {modele}...", file=sys.stderr)

    try:
        response = OpenAI(
            api_key=key,
            base_url=OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "https://github.com/dataTeam/cv-matcher",
                "X-Title": "Évaluation entretien",
            },
        ).chat.completions.create(
            model=modele,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.1,
            max_tokens=max_tokens,
            # Pas de response_format : les modèles gratuits routés ne le supportent pas tous.
        )
    except Exception as e:
        raise RuntimeError(f"Erreur API OpenRouter : {e}")

    return response.choices[0].message.content or ""
