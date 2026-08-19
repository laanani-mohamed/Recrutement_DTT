"""
llmwhisperer_ocr.py
====================
Méthode d'extraction : LLMWhisperer (API cloud Unstract)
---------------------------------------------------------
Utilise l'API LLMWhisperer pour extraire le texte d'un PDF
page par page, via OCR haute qualité dans le cloud.

Dépendances :
    - llmwhisperer-client  : client officiel de l'API LLMWhisperer
    - pypdfium2            : lecture du nombre de pages du PDF

Variables d'environnement supportées :
    - LLMWHISPERER_BASE_URL   : URL de base de l'API (optionnel)
    - LLMWHISPERER_API_KEY    : clé d'accès à l'API (optionnel, fallback dans le code)
    - LLMWHISPERER_MODE       : mode OCR (high_quality | form | low_cost | native_text)
    - LLMWHISPERER_OUTPUT_MODE: format de sortie (layout_preserving | text)
    - LLMWHISPERER_WAIT_TIMEOUT : timeout d'attente en secondes

Utilisation :
    from src.extraction.llmwhisperer_ocr import extract_with_llmwhisperer
    text = extract_with_llmwhisperer("/chemin/vers/cv.pdf")
"""

import os
import sys
import pypdfium2 as pdfium
from unstract.llmwhisperer import LLMWhispererClientV2


# ------------------------------------------------------------------
# Configuration du client LLMWhisperer
# Les valeurs peuvent être surchargées via des variables d'environnement
# ------------------------------------------------------------------
_client = LLMWhispererClientV2(
    base_url=os.environ.get(
        "LLMWHISPERER_BASE_URL",
        "https://llmwhisperer-api.us-central.unstract.com/api/v2",
    ),
    api_key=os.environ.get(
        "LLMWHISPERER_API_KEY",
        "Q2XMy6HE69ceXRMMujvi_NhUWx20QVoOkO6dGD5t0RA",  # clé de démo, à remplacer
    ),
)

# Mode OCR : high_quality (défaut), form, low_cost, native_text
DEFAULT_MODE = os.environ.get("LLMWHISPERER_MODE", "high_quality")

# Format de sortie : layout_preserving (défaut) ou text
DEFAULT_OUTPUT_MODE = os.environ.get("LLMWHISPERER_OUTPUT_MODE", "layout_preserving")

# Timeout d'attente pour l'API (en secondes)
DEFAULT_TIMEOUT = int(os.environ.get("LLMWHISPERER_WAIT_TIMEOUT", "200"))


def _ocr_page(pdf_path: str, page_num_1_indexed: int) -> str:
    """
    Extrait le texte d'une page spécifique d'un PDF via LLMWhisperer.

    Args:
        pdf_path (str): Chemin absolu ou relatif vers le fichier PDF.
        page_num_1_indexed (int): Numéro de page à extraire (commence à 1).

    Returns:
        str: Texte extrait (préservant la mise en page si output_mode=layout_preserving).
    """
    result = _client.whisper(
        file_path=pdf_path,
        wait_for_completion=True,
        wait_timeout=DEFAULT_TIMEOUT,
        mode=DEFAULT_MODE,
        output_mode=DEFAULT_OUTPUT_MODE,
        pages_to_extract=str(page_num_1_indexed),
    )
    extraction = result.get("extraction") or {}
    return extraction.get("result_text") or ""


def extract_with_llmwhisperer(pdf_path: str) -> str:
    """
    Extrait le texte complet d'un PDF via LLMWhisperer, page par page.

    Le résultat est une chaîne de texte qui concatène le contenu
    de toutes les pages, séparées par des séparateurs visuels.

    Args:
        pdf_path (str): Chemin vers le fichier PDF à traiter.

    Returns:
        str: Texte complet extrait du PDF.

    Raises:
        FileNotFoundError: Si le fichier PDF n'existe pas.
        Exception: Si l'API LLMWhisperer retourne une erreur.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"Fichier PDF introuvable : {pdf_path}")

    pdf = pdfium.PdfDocument(pdf_path)
    total_pages = len(pdf)
    pdf.close()

    all_text_parts = []

    for page_idx in range(total_pages):
        page_num = page_idx + 1
        print(
            f"[LLMWhisperer] Traitement page {page_num}/{total_pages} "
            f"(mode={DEFAULT_MODE}, output_mode={DEFAULT_OUTPUT_MODE})...",
            file=sys.stderr,
        )
        page_text = _ocr_page(pdf_path, page_num_1_indexed=page_num)
        all_text_parts.append(
            f"\n--- Page {page_num} ---\n{page_text}"
        )

    return "\n".join(all_text_parts)


# ------------------------------------------------------------------
# Point d'entrée pour test direct du module
# Usage : python -m src.extraction.llmwhisperer_ocr /chemin/cv.pdf
# ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python llmwhisperer_ocr.py <chemin_vers_pdf>")
        sys.exit(1)

    chemin_pdf = sys.argv[1]
    texte = extract_with_llmwhisperer(chemin_pdf)
    print(texte)
