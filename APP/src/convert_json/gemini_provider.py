"""
gemini_provider.py
===================
Provider LLM : Google Gemini Flash 2.0
---------------------------------------
Utilise l'API Google Gemini pour analyser le texte d'un CV
et retourner un JSON structuré avec les informations clés.

Avantages :
    - Gratuit : 1 500 req/jour, 1M tokens/minute (Gemini Flash)
    - Supporte les très longs contextes (1M tokens)
    - Extraction JSON native via response_mime_type

Dépendances :
    - google-genai : SDK officiel Google Gemini (nouveau SDK 2025)

Variable d'environnement :
    - GEMINI_API_KEY : clé API Google AI Studio (https://aistudio.google.com)

Utilisation :
    from src.convert_json.gemini_provider import classify_with_gemini
    result = classify_with_gemini(cv_text)
"""

import os
import json
import sys
from google import genai
from google.genai import types


# ------------------------------------------------------------------
# Modèle Gemini utilisé (peut être surchargé via env)
# gemini-2.0-flash-lite : le plus rapide et gratuit
# ------------------------------------------------------------------
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Prompt d'instruction pour l'extraction JSON des CVs
PROMPT_TEMPLATE = """Analyse ce CV et extrais les informations clés.
Retourne UNIQUEMENT un JSON valide suivant exactement cette structure :

{{
  "nom_complet": "string",
  "email": "string ou null",
  "telephone": "string ou null",
  "localisation": "string ou null",
  "titre_poste": "string ou null",
  "resume": "string (résumé du profil en 2-3 phrases)",
  "competences": ["liste", "de", "skills"],
  "langues": [{{"langue": "string", "niveau": "string"}}],
  "experience": [
    {{
      "poste": "string",
      "entreprise": "string",
      "debut": "string ou null",
      "fin": "string ou null",
      "resume": "string ou null (ta synthèse en 1 phrase de cette expérience)",
      "description": "string ou null (texte ORIGINAL du CV pour cette expérience, copié mot à mot)"
    }}
  ],
  "formation": [
    {{
      "diplome": "string",
      "etablissement": "string",
      "annee": "string ou null"
    }}
  ],
  "certifications": ["liste", "de", "certifications"],
  "liens": {{
    "linkedin": "string ou null",
    "github": "string ou null",
    "portfolio": "string ou null"
  }}
}}

RÈGLE ABSOLUE sur "description" : c'est une CITATION, pas une synthèse. Recopie le texte
du CV tel quel pour cette expérience (mêmes mots, même ordre), sans corriger, reformuler
ni compléter. "resume" est ta synthèse ; "description" est la citation brute, mot pour mot.
Si le CV ne détaille pas cette expérience par du texte, "description" est null.

CV à analyser :
{cv_text}"""


def classify_with_gemini(cv_text: str, api_key: str = None) -> dict:
    """
    Analyse un texte de CV via l'API Google Gemini et retourne un dict JSON structuré.

    Args:
        cv_text (str): Texte brut extrait du CV.
        api_key (str): Clé API Gemini. Si None, utilise GEMINI_API_KEY depuis l'environnement.

    Returns:
        dict: Dictionnaire JSON avec les informations structurées du CV.

    Raises:
        ValueError: Si la clé API est manquante.
        RuntimeError: Si l'API Gemini retourne une erreur ou un JSON invalide.
    """
    # Récupération de la clé API
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "Clé API Gemini manquante. "
            "Définissez GEMINI_API_KEY ou passez api_key en paramètre.\n"
            "Obtenir une clé gratuite : https://aistudio.google.com"
        )

    # Initialisation du client avec le nouveau SDK google-genai
    client = genai.Client(api_key=key)

    print(f"[Gemini] Analyse du CV avec {DEFAULT_MODEL}...", file=sys.stderr)

    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=PROMPT_TEMPLATE.format(cv_text=cv_text),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",  # Force la réponse JSON
                temperature=0.1,
                max_output_tokens=4096,
            ),
        )
    except Exception as e:
        raise RuntimeError(f"Erreur API Gemini : {e}")

    raw = response.text

    # Parsing du JSON retourné
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Gemini a retourné un JSON invalide : {e}\n"
            f"Réponse brute : {raw[:500]}"
        )


# ------------------------------------------------------------------
# Test direct : python -m src.convert_json.gemini_provider
# ------------------------------------------------------------------
if __name__ == "__main__":
    exemple = "Mohamed LAANANI, Data Engineer, 5 ans d'expérience. Skills: Python, SQL, Spark."
    result = classify_with_gemini(exemple)
    print(json.dumps(result, ensure_ascii=False, indent=2))
