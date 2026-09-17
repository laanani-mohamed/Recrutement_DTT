"""Extraction d'un bloc JSON dans une réponse LLM non contrainte."""

import json
import re
from typing import Any

_BALISES = re.compile(r"```(?:json)?", re.IGNORECASE)
_FERMANTS = {"{": "}", "[": "]"}


def extract_json_block(raw: str) -> str:
    """Isole le premier objet ou tableau JSON complet du texte.

    Tolère un préambule ("Voici le JSON :") et les balises markdown, là où un
    simple strip de balises échoue.
    """
    texte = _BALISES.sub("", raw).strip()

    debut = next((i for i, c in enumerate(texte) if c in _FERMANTS), -1)
    if debut == -1:
        raise ValueError("Aucun bloc JSON trouvé dans la réponse du modèle.")

    ouvrant = texte[debut]
    fermant = _FERMANTS[ouvrant]
    profondeur = 0
    dans_chaine = False
    echappe = False

    for i in range(debut, len(texte)):
        c = texte[i]
        if echappe:
            echappe = False
        elif c == "\\":
            echappe = True
        elif c == '"':
            dans_chaine = not dans_chaine
        elif not dans_chaine:
            if c == ouvrant:
                profondeur += 1
            elif c == fermant:
                profondeur -= 1
                if profondeur == 0:
                    return texte[debut : i + 1]

    raise ValueError("Bloc JSON incomplet — réponse probablement tronquée.")


def parse_json_block(raw: str | None) -> Any:
    """Parse le premier bloc JSON d'une réponse LLM."""
    if not raw or not raw.strip():
        raise ValueError("Réponse vide du modèle.")
    return json.loads(extract_json_block(raw))
