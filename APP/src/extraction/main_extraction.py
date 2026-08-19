"""
main_extraction.py
===================
Module principal d'orchestration de l'extraction de texte PDF.
--------------------------------------------------------------
Ce module unifie les trois méthodes d'extraction disponibles
via une interface simple : extract_text(pdf_path, method).

Méthodes disponibles :
    - "llmwhisperer" : OCR cloud haute qualité (LLMWhisperer API)
    - "rapidocr"     : OCR local hors-ligne (RapidOCR + ONNX)
    - "markitdown"   : Conversion PDF→Markdown (Microsoft MarkItDown)

Utilisation :
    from src.extraction.main_extraction import extract_text, METHODS

    # Lister les méthodes disponibles
    print(METHODS)

    # Extraire avec une méthode
    text = extract_text("/chemin/vers/cv.pdf", method="markitdown")
"""

import sys
from typing import Literal

# Import des trois modules d'extraction
from src.extraction.llmwhispirer_ocr import extract_with_llmwhisperer
from src.extraction.rapid_ocr import extract_with_rapidocr
from src.extraction.markitdown_ocr import extract_with_markitdown


# ------------------------------------------------------------------
# Constante : liste des méthodes disponibles avec leurs descriptions
# ------------------------------------------------------------------
METHODS: dict[str, str] = {
    "markitdown":    "MarkItDown — Conversion PDF→Markdown, rapide, local (recommandé pour PDFs numériques)",
    "rapidocr":      "RapidOCR   — OCR local hors-ligne via ONNX (recommandé pour PDFs scannés)",
    "llmwhisperer":  "LLMWhisperer — OCR cloud haute qualité via API Unstract (meilleure précision)",
}

# Type pour l'autocomplétion et la validation
ExtractionMethod = Literal["markitdown", "rapidocr", "llmwhisperer"]


def extract_text(pdf_path: str, method: ExtractionMethod = "markitdown") -> str:
    """
    Extrait le texte d'un PDF en utilisant la méthode spécifiée.

    C'est la fonction principale à utiliser pour toute extraction.
    Elle délègue l'appel au module d'extraction approprié.

    Args:
        pdf_path (str): Chemin absolu ou relatif vers le fichier PDF.
        method (str): Méthode d'extraction à utiliser.
                      Valeurs : "markitdown" | "rapidocr" | "llmwhisperer"
                      Défaut : "markitdown" (la plus rapide et sans dépendances lourdes)

    Returns:
        str: Texte extrait du PDF.

    Raises:
        ValueError: Si la méthode spécifiée n'est pas reconnue.
        FileNotFoundError: Si le fichier PDF n'existe pas.
        Exception: Si l'extraction échoue pour une raison quelconque.

    Exemples:
        >>> text = extract_text("cv.pdf", method="markitdown")
        >>> text = extract_text("scan.pdf", method="rapidocr")
        >>> text = extract_text("formulaire.pdf", method="llmwhisperer")
    """
    if method not in METHODS:
        methodes_valides = ", ".join(METHODS.keys())
        raise ValueError(
            f"Méthode d'extraction inconnue : '{method}'. "
            f"Choisissez parmi : {methodes_valides}"
        )

    print(f"[Extraction] Méthode sélectionnée : {method}", file=sys.stderr)
    print(f"[Extraction] Fichier PDF : {pdf_path}", file=sys.stderr)

    # Dispatch vers le bon module selon la méthode choisie
    if method == "markitdown":
        return extract_with_markitdown(pdf_path)
    elif method == "rapidocr":
        return extract_with_rapidocr(pdf_path)
    elif method == "llmwhisperer":
        return extract_with_llmwhisperer(pdf_path)


# ------------------------------------------------------------------
# Point d'entrée pour test en ligne de commande
# Usage : python -m src.extraction.main_extraction /chemin/cv.pdf markitdown
# ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python main_extraction.py <chemin_pdf> [methode]")
        print(f"Méthodes disponibles : {list(METHODS.keys())}")
        sys.exit(1)

    chemin_pdf = sys.argv[1]
    methode = sys.argv[2] if len(sys.argv) > 2 else "markitdown"

    texte = extract_text(chemin_pdf, method=methode)
    print(texte)
