"""
openrouter_provider.py
=======================
Provider LLM : OpenRouter (accès multi-modèles via 1 clé API)
--------------------------------------------------------------
Utilise l'API OpenRouter pour analyser le texte d'un CV
et retourner un JSON structuré avec les informations clés.

OpenRouter donne accès à des dizaines de modèles gratuits via
une interface compatible OpenAI (même code, autre base_url).

Modèles gratuits recommandés sur OpenRouter :
    - meta-llama/llama-3.3-70b-instruct:free
    - mistralai/mistral-7b-instruct:free
    - google/gemma-3-27b-it:free
    - deepseek/deepseek-r1-0528:free

Dépendances :
    - openai : SDK OpenAI (utilisé comme client compatible)

Variable d'environnement :
    - OPENROUTER_API_KEY : clé API OpenRouter (https://openrouter.ai)
    - OPENROUTER_MODEL   : modèle à utiliser (optionnel)

Utilisation :
    from src.convert_json.openrouter_provider import classify_with_openrouter
    result = classify_with_openrouter(cv_text)
"""

import os
import json
import sys
from openai import OpenAI


# ------------------------------------------------------------------
# Configuration OpenRouter
# Base URL officielle d'OpenRouter (compatible OpenAI)
# ------------------------------------------------------------------
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# openrouter/free : slug officiel qui route vers le meilleur modèle gratuit
# Doc : https://openrouter.ai/docs/models → utiliser "openrouter/free" pour routage auto
DEFAULT_MODEL = os.environ.get(
    "OPENROUTER_MODEL",
    "openrouter/auto"
)

# Prompt système pour l'extraction JSON des CVs
SYSTEM_PROMPT = """Tu es un expert en analyse de CV.
Ton rôle est d'extraire les informations clés d'un CV et de les retourner UNIQUEMENT sous forme de JSON valide, sans texte supplémentaire.

Le JSON doit suivre exactement cette structure :
{
  "nom_complet": "string",
  "email": "string ou null",
  "telephone": "string ou null",
  "localisation": "string ou null",
  "titre_poste": "string ou null",
  "resume": "string (résumé du profil en 2-3 phrases)",
  "competences": ["liste", "de", "skills"],
  "langues": [{"langue": "string", "niveau": "string"}],
  "experience": [
    {
      "poste": "string",
      "entreprise": "string",
      "debut": "string ou null",
      "fin": "string ou null",
      "resume": "string ou null (ta synthèse en 1 phrase de cette expérience)",
      "description": "string ou null (texte ORIGINAL du CV pour cette expérience, copié mot à mot)"
    }
  ],
  "formation": [
    {
      "diplome": "string",
      "etablissement": "string",
      "annee": "string ou null"
    }
  ],
  "certifications": ["liste", "de", "certifications"],
  "liens": {
    "linkedin": "string ou null",
    "github": "string ou null",
    "portfolio": "string ou null"
  }
}

RÈGLE ABSOLUE sur "description" : c'est une CITATION, pas une synthèse. Recopie le texte
du CV tel quel pour cette expérience (mêmes mots, même ordre), sans corriger, reformuler
ni compléter. "resume" est ta synthèse ; "description" est la citation brute, mot pour mot.
Si le CV ne détaille pas cette expérience par du texte, "description" est null.

Réponds UNIQUEMENT avec le JSON, sans markdown, sans explication."""


def classify_with_openrouter(cv_text: str, api_key: str = None, model: str = None) -> dict:
    """
    Analyse un texte de CV via l'API OpenRouter et retourne un dict JSON structuré.

    OpenRouter est compatible avec le SDK OpenAI — la seule différence
    est la base_url et la clé API.

    Args:
        cv_text (str): Texte brut extrait du CV.
        api_key (str): Clé API OpenRouter. Si None, utilise OPENROUTER_API_KEY.
        model (str): Modèle à utiliser. Si None, utilise DEFAULT_MODEL.

    Returns:
        dict: Dictionnaire JSON avec les informations structurées du CV.

    Raises:
        ValueError: Si la clé API est manquante.
        RuntimeError: Si l'API retourne une erreur ou un JSON invalide.
    """
    # Récupération de la clé API
    key = api_key or os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise ValueError(
            "Clé API OpenRouter manquante. "
            "Définissez OPENROUTER_API_KEY ou passez api_key en paramètre.\n"
            "Obtenir une clé gratuite : https://openrouter.ai"
        )

    modele = model or DEFAULT_MODEL

    # Le client OpenAI pointe vers OpenRouter
    client = OpenAI(
        api_key=key,
        base_url=OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": "https://github.com/dataTeam/cv-classifier",
            "X-Title": "CV Classifier",
        },
    )

    print(f"[OpenRouter] Analyse du CV avec {modele}...", file=sys.stderr)

    try:
        response = client.chat.completions.create(
            model=modele,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Voici le CV à analyser :\n\n{cv_text}"},
            ],
            temperature=0.1,
            max_tokens=4096,
            # Note : response_format JSON non supporté par tous les modèles gratuits
            # On s'appuie sur le prompt système pour forcer le JSON
        )
    except Exception as e:
        raise RuntimeError(f"Erreur API OpenRouter : {e}")

    raw = response.choices[0].message.content

    # Parsing du JSON retourné
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"OpenRouter a retourné un JSON invalide : {e}\n"
            f"Réponse brute : {raw[:500]}"
        )


# ------------------------------------------------------------------
# Test direct : python -m src.convert_json.openrouter_provider
# ------------------------------------------------------------------
if __name__ == "__main__":
    exemple = "Mohamed LAANANI, Data Engineer, 5 ans d'expérience. Skills: Python, SQL, Spark."
    result = classify_with_openrouter(exemple)
    print(json.dumps(result, ensure_ascii=False, indent=2))
