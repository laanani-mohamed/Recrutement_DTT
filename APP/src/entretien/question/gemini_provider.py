"""Provider Google Gemini pour la génération du plan d'entretien."""

import os
import sys

from google import genai
from google.genai import types

from src.shared.errors import CleApiManquante

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")


def call_llm(
    system: str,
    user: str,
    max_tokens: int = 3000,
    api_key: str = None,
    model: str = None,
) -> str:
    """Appelle Gemini et retourne le texte brut de la réponse."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise CleApiManquante(
            "Clé API Gemini manquante. Collez-la dans le champ ci-contre, "
            "ou définissez GEMINI_API_KEY dans l'environnement.\n"
            "Clé gratuite : https://aistudio.google.com"
        )

    modele = model or DEFAULT_MODEL
    print(f"[Gemini] Génération avec {modele}...", file=sys.stderr)

    # Le client doit rester référencé : construit en temporaire, il est fermé par le
    # ramasse-miettes avant que la requête n'aboutisse.
    client = genai.Client(api_key=key)

    try:
        response = client.models.generate_content(
            model=modele,
            contents=f"{system}\n\n{user}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3,
                max_output_tokens=max_tokens,
            ),
        )
    except Exception as e:
        raise RuntimeError(f"Erreur API Gemini : {e}")

    return response.text or ""
