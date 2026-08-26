import os
import json
import sys
import re

from google import genai
from google.genai import types

# ------------------------------------------------------------------
# Configuration Gemini
# ------------------------------------------------------------------
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")

SYSTEM_PROMPT = """Tu es un expert en recrutement technique. Ton rôle est d'évaluer l'adéquation entre un profil candidat (fourni en JSON) et une offre d'emploi.

Tu dois retourner UNIQUEMENT un objet JSON valide, sans aucun texte avant ou après, ni balises markdown.
Évalue les scores sur 100.

Le JSON doit suivre exactement cette structure :
{
  "score_global": 0,
  "score_competences": 0,
  "explication_competences": "Brève explication justifiant le score des compétences",
  "score_experience": 0,
  "explication_experience": "Brève explication justifiant le score de l'expérience",
  "score_formation": 0,
  "explication_formation": "Brève explication justifiant le score de la formation",
  "points_forts": ["liste", "des", "points forts"],
  "lacunes": ["liste", "des", "compétences manquantes"],
  "recommandation": "Résumé clair et concis de ton évaluation"
}"""


def clean_json_response(raw_text: str) -> str:
    cleaned = re.sub(r"```json\s*", "", raw_text)
    cleaned = re.sub(r"```\s*", "", cleaned)
    return cleaned.strip()


def score_with_gemini(cv_json: dict, job_description: str, api_key: str = None) -> dict:
    key = api_key or os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6JfyHuPUjPj22VlGLb0thlaJKfEn0Hyv0QkKZ5SFd-21w")
    if not key:
        raise ValueError("Clé API Gemini manquante.")

    client = genai.Client(api_key=key)

    print(f"[Gemini] Analyse du matching avec {DEFAULT_MODEL}...", file=sys.stderr)

    cv_str = json.dumps(cv_json, ensure_ascii=False, indent=2)

    prompt_user = f"""
{SYSTEM_PROMPT}

--- CV DU CANDIDAT ---
{cv_str}

--- DESCRIPTION DU POSTE ---
{job_description}
    """

    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt_user,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=2048,
            ),
        )
    except Exception as e:
        raise RuntimeError(f"Erreur API Gemini : {e}")

    raw = response.text

    if raw is None:
        raise RuntimeError(f"Gemini API returned empty or null content.")

    cleaned_raw = clean_json_response(raw)

    try:
        return json.loads(cleaned_raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Gemini a retourné un JSON invalide : {e}\n"
            f"Réponse brute : {raw}"
        )
