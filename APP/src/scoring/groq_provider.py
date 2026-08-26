import os
import json
import sys
import re

from openai import OpenAI

# ------------------------------------------------------------------
# Configuration Groq
# ------------------------------------------------------------------
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = os.environ.get("GROQ_MODEL", "qwen-2.5-32b") # Using a standard model available on Groq, qwen is good for struct output, or llama-3.3-70b-versatile

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


def score_with_groq(cv_json: dict, job_description: str, api_key: str = None) -> dict:
    key = api_key or os.environ.get("GROQ_API_KEY", "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")
    if not key:
        raise ValueError("Clé API Groq manquante.")

    client = OpenAI(
        api_key=key,
        base_url=GROQ_BASE_URL,
    )

    print(f"[Groq] Analyse du matching avec {DEFAULT_MODEL}...", file=sys.stderr)

    cv_str = json.dumps(cv_json, ensure_ascii=False, indent=2)

    prompt_user = f"""
--- CV DU CANDIDAT ---
{cv_str}

--- DESCRIPTION DU POSTE ---
{job_description}
    """

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt_user},
            ],
            temperature=0.1,
            max_tokens=2048,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        raise RuntimeError(f"Erreur API Groq : {e}")

    raw = response.choices[0].message.content

    if raw is None:
        raise RuntimeError(f"Groq API returned empty or null content.")

    cleaned_raw = clean_json_response(raw)

    try:
        return json.loads(cleaned_raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Groq a retourné un JSON invalide : {e}\n"
            f"Réponse brute : {raw}"
        )
