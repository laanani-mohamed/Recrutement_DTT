"""Provider Groq pour l'évaluation des réponses d'entretien."""

import os
import sys

from groq import Groq

from src.shared.errors import CleApiManquante

DEFAULT_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.6-27b")


def call_llm(
    system: str,
    user: str,
    max_tokens: int = 2000,
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
    print(f"[Groq] Évaluation avec {modele}...", file=sys.stderr)

    try:
        response = Groq(api_key=key).chat.completions.create(
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
