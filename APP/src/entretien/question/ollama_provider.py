"""Provider Ollama (local) pour la génération du plan d'entretien."""

import os
import sys

from openai import OpenAI

OLLAMA_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")


def call_llm(
    system: str,
    user: str,
    max_tokens: int = 3000,
    api_key: str = None,
    model: str = None,
) -> str:
    """Appelle Ollama en local et retourne le texte brut de la réponse.

    api_key est ignoré (exécution locale) : la signature reste uniforme entre providers.
    """
    modele = model or DEFAULT_MODEL
    print(f"[Ollama] Génération avec {modele}...", file=sys.stderr)

    try:
        response = OpenAI(
            base_url=OLLAMA_BASE_URL,
            api_key="ollama",  # clé factice exigée par le client OpenAI
        ).chat.completions.create(
            model=modele,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
            max_tokens=max_tokens,
            # Pas de response_format : tous les modèles locaux ne gèrent pas le mode JSON.
            # La sortie est récupérée par json_utils.parse_json_block.
        )
    except Exception as e:
        raise RuntimeError(
            f"Erreur API Ollama (vérifiez qu'Ollama est lancé et que le modèle "
            f"'{modele}' est installé) : {e}"
        )

    return response.choices[0].message.content or ""
