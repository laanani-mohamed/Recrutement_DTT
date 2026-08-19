"""
markitdown_ocr.py
==================
Méthode d'extraction : MarkItDown (conversion PDF → Markdown)
--------------------------------------------------------------
Utilise la bibliothèque MarkItDown de Microsoft pour convertir
un PDF en texte Markdown structuré, sans IA ni appel API externe.
Fonctionne entièrement en local via pdfplumber.

Avantage : rapide, simple, préserve la structure du texte.
Limitation : peut échouer sur les PDF purement scannés (pas de texte natif).

Dépendances :
    - markitdown[pdf]  : convertit PDF → Markdown (Microsoft)
    - pdfplumber       : backend de lecture PDF utilisé par MarkItDown

Utilisation :
    from src.extraction.markitdown_ocr import extract_with_markitdown
    text = extract_with_markitdown("/chemin/vers/cv.pdf")
"""

import os
import sys
from markitdown import MarkItDown


# ------------------------------------------------------------------
# Initialisation du convertisseur MarkItDown
# Aucune clé API ni modèle IA requis
# ------------------------------------------------------------------
_converter = MarkItDown()


def extract_with_markitdown(pdf_path: str) -> str:
    """
    Extrait le texte d'un PDF et le convertit en Markdown via MarkItDown.

    MarkItDown utilise pdfplumber pour extraire le texte natif du PDF
    et le formate en Markdown (titres, listes, tableaux si détectés).

    Note : Cette méthode est idéale pour les PDFs avec texte numérique
    (non scannés). Pour les scans, préférez LLMWhisperer ou RapidOCR.

    Args:
        pdf_path (str): Chemin vers le fichier PDF à traiter.

    Returns:
        str: Contenu du PDF converti en texte Markdown.

    Raises:
        FileNotFoundError: Si le fichier PDF n'existe pas.
        Exception: Si MarkItDown échoue à convertir le fichier.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"Fichier PDF introuvable : {pdf_path}")

    print("[MarkItDown] Conversion du PDF en Markdown...", file=sys.stderr)
    resultat = _converter.convert(pdf_path)

    texte = resultat.text_content
    if not texte or not texte.strip():
        raise RuntimeError(
            "MarkItDown n'a extrait aucun texte. "
            "Le PDF est peut-être un scan — essayez RapidOCR ou LLMWhisperer."
        )

    return texte


# ------------------------------------------------------------------
# Point d'entrée pour test direct du module
# Usage : python -m src.extraction.markitdown_ocr /chemin/cv.pdf
# ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python markitdown_ocr.py <chemin_vers_pdf>")
        sys.exit(1)

    chemin_pdf = sys.argv[1]
    texte = extract_with_markitdown(chemin_pdf)
    print(texte)
