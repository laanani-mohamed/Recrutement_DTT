"""Provider Groq pour le scoring CV / fiche de poste."""

import os
import sys

from openai import OpenAI

from src.shared.errors import CleApiManquante

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = os.environ.get("GROQ_MODEL", "qwen-2.5-32b")


def call_llm(
    system: str,
    user: str,
    max_tokens: int = 4000,
    api_key: str = None,
    model: str = None,
) -> str:
    """Appelle Groq et retourne le texte brut de la réponse."""
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        raise CleApiManquante(
            "Clé API Groq manquante. Collez-la dans le champ ci-contre, "
            "ou définissez GROQ_API_KEY dans l'environnement.\n"
            "Clé gratuite : https://console.groq.com"
        )

    modele = model or DEFAULT_MODEL
    print(f"[Groq] Scoring avec {modele}...", file=sys.stderr)

    try:
        response = OpenAI(api_key=key, base_url=GROQ_BASE_URL).chat.completions.create(
            model=modele,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.1,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        raise RuntimeError(f"Erreur API Groq : {e}")

    return response.choices[0].message.content or ""
