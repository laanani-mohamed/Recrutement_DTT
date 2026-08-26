import os
import json
import sys
import re
from openai import OpenAI

# ------------------------------------------------------------------
# Configuration Ollama Local
# ------------------------------------------------------------------
OLLAMA_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")

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
      "description": "string ou null"
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

Réponds UNIQUEMENT avec le JSON, sans markdown, sans explication."""

def clean_json_response(raw_text: str) -> str:
    cleaned = re.sub(r"```json\s*", "", raw_text)
    cleaned = re.sub(r"```\s*", "", cleaned)
    return cleaned.strip()

def classify_with_ollama(cv_text: str, model: str = None) -> dict:
    modele = model or DEFAULT_MODEL
    
    # Ollama is compatible with OpenAI API on port 11434 by default
    client = OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key="ollama", # dummy key required by OpenAI client
    )

    print(f"[Ollama] Analyse du CV avec {modele}...", file=sys.stderr)

    try:
        response = client.chat.completions.create(
            model=modele,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Voici le CV à analyser :\n\n{cv_text}"},
            ],
            temperature=0.1,
            max_tokens=4096,
            # response_format={"type": "json_object"}, # Some local models might not support this perfectly, better rely on the prompt + clean_json_response
        )
    except Exception as e:
        raise RuntimeError(f"Erreur API Ollama (vérifiez qu'Ollama est lancé et que le modèle '{modele}' est installé) : {e}")

    raw = response.choices[0].message.content

    if raw is None:
        raise RuntimeError("Ollama API returned empty content.")

    cleaned_raw = clean_json_response(raw)

    try:
        return json.loads(cleaned_raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Ollama a retourné un JSON invalide : {e}\n"
            f"Réponse brute : {raw[:500]}"
        )
