"""Neutralisation des contenus non fiables (CV, fiche de poste) avant envoi à un LLM.

Un candidat peut dissimuler des instructions dans son PDF en texte invisible.
Tout ce qui vient du candidat passe ici avant d'entrer dans un prompt.
"""

import json
import re
import unicodedata

CHAMPS_CV_AUTORISES = (
    "titre_poste",
    "resume",
    "competences",
    "langues",
    "experience",
    "formation",
    "certifications",
)

BALISE_OUVRANTE = "<donnees_candidat>"
BALISE_FERMANTE = "</donnees_candidat>"

# 2000 (et non quelques centaines) : la citation verbatim d'une expérience
# (champ "description") doit survivre intacte pour que la vérification de
# citation (citation_est_verifiee) reste fiable — un texte tronqué en cours
# de phrase ferait échouer à tort une citation pourtant authentique.
MAX_CHAINE = 2000
MAX_ELEMENTS = 30
MAX_TEXTE_LIBRE = 6000

# Largeur nulle et contrôles bidirectionnels : le vecteur exact du texte invisible dans un PDF.
_INVISIBLES = re.compile(r"[­​-‏‪-‮⁦-⁩﻿]")
_ESPACES = re.compile(r"\s+")
_MOT = re.compile(r"\w+", re.UNICODE)


def _degager(texte: str) -> str:
    propre = unicodedata.normalize("NFKC", texte)
    propre = _INVISIBLES.sub("", propre)
    return propre.replace(BALISE_OUVRANTE, "").replace(BALISE_FERMANTE, "")


def scrub(valeur: str) -> str:
    """Retire caractères invisibles et balises de délimitation, normalise, tronque."""
    return _ESPACES.sub(" ", _degager(str(valeur))).strip()[:MAX_CHAINE]


def _nettoyer(valeur):
    if isinstance(valeur, str):
        return scrub(valeur)
    if isinstance(valeur, bool) or isinstance(valeur, (int, float)) or valeur is None:
        return valeur
    if isinstance(valeur, dict):
        return {k: _nettoyer(v) for k, v in list(valeur.items())[:MAX_ELEMENTS]}
    if isinstance(valeur, list):
        return [_nettoyer(v) for v in valeur[:MAX_ELEMENTS]]
    return scrub(str(valeur))


def sanitize_cv(cv_json: dict) -> dict:
    """Reconstruit un CV réduit aux champs utiles à la rédaction de questions ou au scoring.

    email, telephone et liens sont écartés : inutiles ici, et autant de données
    personnelles et de surface d'attaque en moins dans les prompts.
    """
    return {
        champ: _nettoyer(cv_json[champ])
        for champ in CHAMPS_CV_AUTORISES
        if cv_json.get(champ)
    }


def sanitize_texte(texte: str) -> str:
    """Assainit un texte libre (fiche de poste) sans le tronquer au format court."""
    return _degager(texte or "").strip()[:MAX_TEXTE_LIBRE]


def encadrer(contenu: str) -> str:
    """Encadre un contenu non fiable des balises de délimitation."""
    return f"{BALISE_OUVRANTE}\n{contenu}\n{BALISE_FERMANTE}"


def _tokens(texte: str) -> set[str]:
    decompose = unicodedata.normalize("NFKD", texte.lower())
    sans_accent = "".join(c for c in decompose if not unicodedata.combining(c))
    return {mot for mot in _MOT.findall(sans_accent) if len(mot) > 2}


def citation_est_verifiee(citation: str, cv_propre: dict, seuil: float = 0.6) -> bool:
    """Vrai si la citation recoupe assez le CV réel pour ne pas être une invention.

    Utilisé pour l'ancrage des questions d'entretien (ancrage_cv) et pour les
    preuves du scoring (evidence) : même principe, même seuil.
    """
    mots_citation = _tokens(citation)
    if not mots_citation:
        return False
    mots_cv = _tokens(json.dumps(cv_propre, ensure_ascii=False))
    return len(mots_citation & mots_cv) / len(mots_citation) >= seuil
