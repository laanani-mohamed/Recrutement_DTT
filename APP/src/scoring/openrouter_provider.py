import os
import json
import sys
import re
from typing import Literal

from openai import OpenAI

# ------------------------------------------------------------------
# Configuration OpenRouter
# ------------------------------------------------------------------
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

DEFAULT_MODEL = os.environ.get(
    "OPENROUTER_MODEL",
    "openrouter/auto"
)

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
    """Nettoie la réponse du LLM au cas où il rajoute des balises Markdown."""
    cleaned = re.sub(r"```json\s*", "", raw_text)
    cleaned = re.sub(r"```\s*", "", cleaned)
    return cleaned.strip()


def score_with_openrouter(cv_json: dict, job_description: str, api_key: str = None, model: str = None) -> dict:
    key = api_key or os.environ.get("OPENROUTER_API_KEY", "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")
    if not key:
        raise ValueError("Clé API OpenRouter manquante.")

    modele = model or DEFAULT_MODEL

    client = OpenAI(
        api_key=key,
        base_url=OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": "https://github.com/dataTeam/cv-matcher",
            "X-Title": "CV Matcher",
        },
    )

    print(f"[OpenRouter] Analyse du matching avec {modele}...", file=sys.stderr)

    cv_str = json.dumps(cv_json, ensure_ascii=False, indent=2)

    prompt_user = f"""
--- CV DU CANDIDAT ---
{cv_str}

--- DESCRIPTION DU POSTE ---
{job_description}
    """

    try:
        response = client.chat.completions.create(
            model=modele,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt_user},
            ],
            temperature=0.1,
            max_tokens=2048,
        )
    except Exception as e:
        raise RuntimeError(f"Erreur API OpenRouter : {e}")

    raw = response.choices[0].message.content

    if raw is None:
        raise RuntimeError(f"OpenRouter API returned empty or null content.")

    cleaned_raw = clean_json_response(raw)

    try:
        return json.loads(cleaned_raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"OpenRouter a retourné un JSON invalide : {e}\n"
            f"Réponse brute : {raw}"
        )
