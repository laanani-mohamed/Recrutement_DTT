"""
groq_provider.py
=================
Provider LLM : Groq (llama-3.3-70b-versatile)
-----------------------------------------------
Utilise l'API Groq pour analyser le texte d'un CV
et retourner un JSON structuré avec les informations clés.

Avantages :
    - Gratuit : 6 000 requêtes/jour et 500 000 tokens/minute
    - Ultra rapide (inferencing sur LPU)
    - Compatible API OpenAI → facile à utiliser

Dépendances :
    - groq  : SDK officiel Groq (compatible OpenAI)

Variable d'environnement :
    - GROQ_API_KEY : clé API Groq (https://console.groq.com)

Utilisation :
    from src.convert_json.groq_provider import classify_with_groq
    result = classify_with_groq(cv_text)
"""

import os
import json
import sys
from groq import Groq


# ------------------------------------------------------------------
# Modèle Groq utilisé
# qwen/qwen3.6-27b : modèle disponible avec tier gratuit, excellent pour JSON
# ------------------------------------------------------------------
DEFAULT_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.6-27b")

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


def classify_with_groq(cv_text: str, api_key: str = None) -> dict:
    """
    Analyse un texte de CV via l'API Groq et retourne un dict JSON structuré.

    Args:
        cv_text (str): Texte brut extrait du CV.
        api_key (str): Clé API Groq. Si None, utilise GROQ_API_KEY depuis l'environnement.

    Returns:
        dict: Dictionnaire JSON avec les informations structurées du CV.

    Raises:
        ValueError: Si la clé API est manquante.
        RuntimeError: Si l'API Groq retourne une erreur ou un JSON invalide.
    """
    # Récupération de la clé API
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        raise ValueError(
            "Clé API Groq manquante. "
            "Définissez GROQ_API_KEY ou passez api_key en paramètre.\n"
            "Obtenir une clé gratuite : https://console.groq.com"
        )

    client = Groq(api_key=key)

    print(f"[Groq] Analyse du CV avec {DEFAULT_MODEL}...", file=sys.stderr)

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Voici le CV à analyser :\n\n{cv_text}"},
            ],
            temperature=0.6,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        raise RuntimeError(f"Erreur API Groq : {e}")

    raw = response.choices[0].message.content

    # Parsing du JSON retourné
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Groq a retourné un JSON invalide : {e}\n"
            f"Réponse brute : {raw[:500]}"
        )


# ------------------------------------------------------------------
# Test direct : python -m src.convert_json.groq_provider
# ------------------------------------------------------------------
if __name__ == "__main__":
    exemple = "Mohamed LAANANI, Data Engineer, 5 ans d'expérience. Skills: Python, SQL, Spark."
    result = classify_with_groq(exemple)
    print(json.dumps(result, ensure_ascii=False, indent=2))
